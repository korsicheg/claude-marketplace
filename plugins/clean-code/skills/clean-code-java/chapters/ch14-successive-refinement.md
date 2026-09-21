# Chapter 14: Successive Refinement
*A case study of a command-line argument parser*

## Core Idea
**To write clean code, you must first write dirty code and then clean it.** This chapter
shows a module that started well, did not scale, and was then refactored — in hundreds of
tiny test-verified steps, never a rewrite. *"It is not enough for code to work."*

## Frameworks Introduced

- **Successive Refinement** — the grade-school composition process applied to code: rough
  draft, second draft, several subsequent drafts, final version.
  - *"Programming is a craft more than it is a science."*
  - Martin's own admission up front: *"I did not simply write this program from beginning
    to end in its current form. More importantly, I am not expecting you to be able to
    write clean and elegant programs in one pass."*

- **The Stop Rule** — the chapter's most transferable judgment call. Martin had two more
  argument types to add and could see they would make things much worse:
  > *"If I bulldozed my way forward, I could probably get them to work, but I'd leave
  > behind a mess that was too large to fix. If the structure of this code was ever going
  > to be maintainable, now was the time to fix it. **So I stopped adding features and
  > started refactoring.**"*
  - **The trigger to look for:** he had just noticed that *each new argument type
    required new code in three separate places* — parse the schema element, parse and
    convert the command-line value, and a `getXXX` method. **"Many different types, all
    with similar methods — that sounds like a class to me."** That observation is what
    produced the `ArgumentMarshaler` concept.

- **Incrementalism (and its justification)** — *"One of the best ways to ruin a program is
  to make massive changes to its structure in the name of improvement. Some programs never
  recover from such 'improvements.' The problem is that it's very hard to get the program
  working the same way it worked before."*
  - The discipline that prevents it is **TDD's central doctrine: keep the system running
    at all times.** *"I am not allowed to make a change to the system that breaks that
    system."*
  - The prerequisite: a suite of automated tests runnable on a whim. For `Args`, Martin
    had **JUnit unit tests plus FitNesse acceptance tests written as wiki pages** —
    *"created while I was building the festering pile."* The tests came first, during the
    mess, not after.

## Worked Example: the refactoring, step by step

This is the chapter's real content — not the final code, but the *sequence*.

**Step 0 — the rough draft "works" and is messy.** The first-draft `Args` accumulated one
field per concern:

```java
private Set<Character> unexpectedArguments = new TreeSet<Character>();
private Map<Character, Boolean> booleanArgs = new HashMap<Character, Boolean>();
private Map<Character, String>  stringArgs  = new HashMap<Character, String>();
private Map<Character, Integer> intArgs     = new HashMap<Character, Integer>();
private Set<Character> argsFound = new HashSet<Character>();
private char errorArgumentId = '\0';
private String errorParameter = "TILT";
private ErrorCode errorCode = ErrorCode.OK;
```

**One `Map` per type** — that is the duplication the whole refactor removes.

**Step 1 — add the skeleton where it cannot break anything.** Append the new concept to
the end of the existing mess:

```java
private class ArgumentMarshaler {
    private boolean booleanValue = false;
    public void setBoolean(boolean value) { booleanValue = value; }
    public boolean getBoolean() { return booleanValue; }
}
private class BooleanArgumentMarshaler extends ArgumentMarshaler { }
private class StringArgumentMarshaler  extends ArgumentMarshaler { }
private class IntegerArgumentMarshaler extends ArgumentMarshaler { }
```

*"Clearly, this wasn't going to break anything."*

**Step 2 — the smallest modification that could possibly break the least.** Change one
map's value type:

```java
private Map<Character, ArgumentMarshaler> booleanArgs =
    new HashMap<Character, ArgumentMarshaler>();
```

This broke a few statements — *exactly the three places predicted*: parse, set, and get.

**Step 3 — tests fail. Fix that before anything else.** `booleanArgs.get('y')` now returns
null where a `falseIfNull` guard used to protect against it. *"Incrementalism demanded
that I get this working quickly before making any other changes."*

The fix is itself done in three sub-steps, each one verified:

```java
// a) remove the now-useless falseIfNull (tests still fail the SAME way
//    — which confirms no NEW errors were introduced)
public boolean getBoolean(char arg) {
    return booleanArgs.get(arg).getBoolean();
}

// b) extract the marshaler into a variable; shorten the name, since the long
//    one was "badly redundant and cluttered up the function" [N5]
public boolean getBoolean(char arg) {
    Args.ArgumentMarshaler am = booleanArgs.get(arg);
    return am.getBoolean();
}

// c) move the null check to where it now belongs
public boolean getBoolean(char arg) {
    Args.ArgumentMarshaler am = booleanArgs.get(arg);
    return am != null && am.getBoolean();
}
```

**Notice the technique in (a):** removing the guard and observing that *the tests fail in
exactly the same way as before* is how he proves the change introduced nothing new. That
is a debugging move worth stealing.

**Step 4 — repeat for String, then Integer.** *"Adding String arguments was very similar…
There shouldn't be any surprises."* Note his honesty about an intermediate state: *"I seem
to be putting all the marshalling implementation in the `ArgumentMarshaler` base class
instead of distributing it to the derivatives."* The intermediate design is knowingly
imperfect — that is allowed, because it is on the way.

## The destination

The final `Args` has **one** map, and adding a type means adding a marshaler:

```java
public class Args {
    private Map<Character, ArgumentMarshaler> marshalers;
    private Set<Character> argsFound;
    private ListIterator<String> currentArgument;

    public Args(String schema, String[] args) throws ArgsException {
        marshalers = new HashMap<Character, ArgumentMarshaler>();
        argsFound = new HashSet<Character>();
        parseSchema(schema);
        parseArgumentStrings(Arrays.asList(args));
    }

    private void parseSchemaElement(String element) throws ArgsException {
        char elementId = element.charAt(0);
        String elementTail = element.substring(1);
        validateSchemaElementId(elementId);
        if (elementTail.length() == 0)
            marshalers.put(elementId, new BooleanArgumentMarshaler());
        else if (elementTail.equals("*"))
            marshalers.put(elementId, new StringArgumentMarshaler());
        else if (elementTail.equals("#"))
            marshalers.put(elementId, new IntegerArgumentMarshaler());
        else if (elementTail.equals("##"))
            marshalers.put(elementId, new DoubleArgumentMarshaler());
        else if (elementTail.equals("[*]"))
            marshalers.put(elementId, new StringArrayArgumentMarshaler());
        else
            throw new ArgsException(INVALID_ARGUMENT_FORMAT, elementId, elementTail);
    }

    public boolean getBoolean(char arg) {
        return BooleanArgumentMarshaler.getValue(marshalers.get(arg));
    }
    public String getString(char arg) {
        return StringArgumentMarshaler.getValue(marshalers.get(arg));
    }
    // getInt, getDouble, getStringArray follow the identical shape
}
```

```java
public interface ArgumentMarshaler {
    void set(Iterator<String> currentArgument) throws ArgsException;
}
```

And the client usage the whole design serves:

```java
public static void main(String[] args) {
    try {
        Args arg = new Args("l,p#,d*", args);
        boolean logging = arg.getBoolean('l');
        int port = arg.getInt('p');
        String directory = arg.getString('d');
        executeApplication(logging, port, directory);
    } catch (ArgsException e) {
        System.out.printf("Argument error: %s\n", e.errorMessage());
    }
}
```

*"Notice that you can read this code from the top to the bottom without a lot of jumping
around or looking ahead."*

## Mental Models

- **"The majority of the changes were deletions."** A lot of code moved *out* of `Args`
  into `ArgsException`, and the marshalers moved into their own files.
- **"Much of good software design is simply about partitioning — creating appropriate
  places to put different kinds of code."**
- **Not every partition is clean, and that's honest.** Martin asks whether error-message
  formatting really belongs in `ArgsException`: *"Frankly, it's a compromise."* It's an
  SRP violation to keep it in `Args`, but canned messages are convenient, and users who
  dislike them must write their own. **Trade-offs get named, not hidden.**
- **Cleanup cost grows superlinearly with time.** *"If you made a mess in a module in the
  morning, it is easy to clean it up in the afternoon. Better yet, if you made a mess
  five minutes ago, it's very easy to clean it up right now."* As code rots, modules
  *"insinuate themselves into each other, creating lots of hidden and tangled
  dependencies,"* and breaking those is long and arduous.
- **Bad code is uniquely unrecoverable among project problems:** *"Bad schedules can be
  redone, bad requirements can be redefined. Bad team dynamics can be repaired. But bad
  code rots and ferments, becoming an inexorable weight that drags the team down."*

## Anti-patterns

- **Stopping at "it works."** *"Programmers who satisfy themselves with merely working
  code are behaving unprofessionally."* Freshman programmers move on the moment the
  program works, leaving it in whatever state it happened to reach; *"most seasoned
  programmers know that this is professional suicide."*
- **The big-bang restructure** — massive structural change in the name of improvement,
  from which some programs never recover.
- **Bulldozing through** when you can already see the next two features will make it
  worse.
- **"I don't have time to improve the structure"** — Martin's direct reply: *"I
  disagree."*

## Key Takeaways

1. **Write it dirty, then clean it.** Expect a rough draft; plan for the second and third.
2. **Build the test suite while building the mess** — unit tests *and* acceptance tests.
3. **Stop adding features the moment you can see the structure won't hold.** The signal:
   each new case requires parallel edits in several fixed places.
4. **"Many types with similar methods" is a class trying to be born.**
5. **Refactor in a large number of very tiny changes**, each keeping the system working.
6. **Add the new abstraction as a harmless skeleton first**, then migrate one use at a
   time.
7. **When a change breaks tests, fix that before making any other change.**
8. **Failing "in exactly the same way" is evidence** that you introduced nothing new.
9. **Clean up the same day — ideally the same five minutes.** Never let the rot start.

## Connects To
- **Ch3 (Functions)**: *"I don't write them that way to start"* — the same confession,
  the same method.
- **Ch9 (Unit Tests)**: the suite that makes incrementalism possible.
- **Ch10 (Classes)**: SRP-driven partitioning; the `Version` and `Sql` extractions.
- **Ch12 (Emergence)**: refactor every few lines under green tests.
- **Ch16 (Refactoring SerialDate)**: the same discipline applied to someone else's code.
- **Ch2 (Names)**: the `argumentMarshaller` → `am` shortening is the scope-length rule [N5].
