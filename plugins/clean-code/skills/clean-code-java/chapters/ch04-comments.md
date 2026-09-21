# Chapter 4: Comments

> *"Don't comment bad code — rewrite it."* — Kernighan & Plaugher

## Core Idea
**Comments are always failures.** They exist because we could not figure out how to
express ourselves in code. Every comment you write should feel like a small defeat;
every comment you *eliminate* by improving the code is a win. The only truly good comment
is the comment you found a way not to write.

## Frameworks Introduced

- **The Comment Test**: before writing a comment, ask *"can I express this in code
  instead?"* In most cases the answer is to extract a function or introduce an
  explanatory variable whose name says exactly what the comment would have said.
  - How: it takes only a few seconds of thought to turn most intent into code.

- **Comments Do Not Make Up for Bad Code**: the urge to comment is a signal that the code
  is confusing. *"Ooh, I'd better comment that!" — No! You'd better clean it!*
  - How: spend the comment-writing budget on cleaning the mess instead. Clear code with
    few comments beats cluttered code with many comments, always.

- **The Only Source of Truth Is the Code**: comments rot because programmers cannot
  realistically maintain them. The older a comment is, and the farther from the code it
  describes, the more likely it is simply wrong.
  - **Inaccurate comments are far worse than no comments at all** — they delude, mislead,
    set expectations that will never be met, and codify rules that should no longer be
    followed.

## Reference Table: the complete good/bad comment catalogue

### Good comments (the short list)

| Type | When it earns its place | Caveat |
|---|---|---|
| **Legal** | Copyright / license header required by policy | Refer to an external license; never inline a legal tome. Let the IDE collapse it. |
| **Informative** | Explains something the code genuinely can't, e.g. what regex a `Pattern` is meant to match | Usually better fixed by renaming (`responderInstance` → `responderBeingTested`) or by moving the code into a dedicated class |
| **Explanation of Intent** | Documents *why* a decision was made, not what the code does | The highest-value category — "we are greater because we are the right type" |
| **Clarification** | Translates an obscure argument/return value you **cannot alter** (standard library, third-party) | High risk of being wrong; verify carefully, and only when there is no better way |
| **Warning of Consequences** | "`SimpleDateFormat` is not thread safe, so we create each instance independently" | Prevents a well-meaning optimizer from breaking things |
| **TODO** | Explains a degenerate implementation and what its future should be | **Never an excuse to leave bad code in the system.** Scan and eliminate regularly. |
| **Amplification** | Marks something that looks inconsequential but isn't ("the trim is real important") | — |
| **Javadoc for a public API** | A well-described public API is genuinely valuable | Javadocs can be just as misleading, nonlocal and dishonest as any other comment |

### Bad comments (where most comments live)

| Anti-pattern | Why it fails |
|---|---|
| **Mumbling** | A comment whose meaning requires reading another module has failed to communicate and is not worth the bits it consumes |
| **Redundant** | Takes longer to read than the code and is *less precise* than the code; invites the reader to accept vagueness in place of understanding |
| **Misleading** | "returns when `this.closed` is true" — it doesn't; it waits for a blind timeout then throws. Sends the next reader into a debugging session |
| **Mandated** | A rule that every function needs a javadoc produces clutter, lies and disorganization |
| **Journal** | Change logs at the top of a module. Source control does this. **Remove them completely** |
| **Noise** | `/** Default constructor. */`, `/** The day of the month. */` — we learn to skip them, then they lie as the code changes |
| **Scary noise** | Noise plus a cut-paste error (`/** The version. */ private String info;`). If the author wasn't paying attention writing it, why should the reader profit from it? |
| **Position markers / banners** | `// Actions ///////////////` — a banner works only because it's rare. Overuse them and they become background noise |
| **Closing-brace comments** | `} //while`, `} //try` — if you want these, **shorten the function instead** |
| **Attributions and bylines** | `/* Added by Rick */` — source control knows this and stays accurate; the comment won't |
| **Commented-out code** | *Few practices are as odious.* Others won't dare delete it, assuming it matters. It gathers like dregs. **Just delete it. Source control remembers. Promise.** |
| **HTML in comments** | An abomination — makes comments unreadable in the one place they must be readable, the editor. Adornment is the *tool's* job, not the programmer's |
| **Nonlocal information** | A comment describing a default port in a setter that has no control over that default. Nothing keeps the two in sync |
| **Too much information** | Pasting RFC 2045's base64 encoding prose into a test module. Cite the RFC number and stop |
| **Inobvious connection** | If a comment needs its own explanation, it has failed ("plus filter bytes… and an extra 200 bytes" — what's a filter byte? why 200?) |
| **Function headers** | A well-chosen name on a small function that does one thing beats a header comment |
| **Javadocs in nonpublic code** | Anathema. The extra formality is cruft and distraction for internal classes |

## Worked Example 1: replace the comment with a function

```java
// Check to see if the employee is eligible for full benefits
if ((employee.flags & HOURLY_FLAG) && (employee.age > 65))
```

becomes

```java
if (employee.isEligibleForFullBenefits())
```

**What it demonstrates:** the comment was a function name waiting to be written.

## Worked Example 2: replace the comment with explanatory variables

```java
// does the module from the global list <mod> depend on the
// subsystem we are part of?
if (smodule.getDependSubsystems().contains(subSysMod.getSubSystem()))
```

becomes

```java
ArrayList moduleDependees = smodule.getDependSubsystems();
String ourSubSystem = subSysMod.getSubSystem();
if (moduleDependees.contains(ourSubSystem))
```

**What it demonstrates:** naming intermediate values is often cheaper than a comment, and
it cannot go stale.

## Worked Example 3: vent-comment → extracted function

Frustration produced `//Give me a break!` in a nested catch. The fix is structural, not
textual:

```java
private void startSending() {
    try {
        doSending();
    } catch (SocketException e) {
        // normal. someone stopped the request.        <- a legitimate comment
    } catch (Exception e) {
        addExceptionAndCloseResponse(e);               <- the noise comment's cause, removed
    }
}

private void addExceptionAndCloseResponse(Exception e) {
    try {
        response.add(ErrorResponder.makeExceptionString(e));
        response.closeAll();
    } catch (Exception e1) {
    }
}
```

**What it demonstrates:** *"Replace the temptation to create noise with the determination
to clean your code."*

## Worked Example 4: `GeneratePrimes` → `PrimeGenerator`

The chapter's capstone. The "well-documented" original carries a javadoc with a biography
of Eratosthenes, an `@author`/`@version` byline, and inline section markers
(`// declarations`, `// initialize array to true`, `// sieve`, `// how many primes are
there?`, `// bump count.`, `// return the primes`) over one-letter variables `s`, `f`,
`i`, `j`.

**The key insight: every section comment marks a function that wants to be extracted.**
Kent Beck's refactoring turns each one into a named method:

```java
public class PrimeGenerator {
    private static boolean[] crossedOut;
    private static int[] result;

    public static int[] generatePrimes(int maxValue) {
        if (maxValue < 2)
            return new int[0];
        else {
            uncrossIntegersUpTo(maxValue);
            crossOutMultiples();
            putUncrossedIntegersIntoResult();
            return result;
        }
    }

    private static void crossOutMultiples() {
        int limit = determineIterationLimit();
        for (int i = 2; i <= limit; i++)
            if (notCrossed(i))
                crossOutMultiplesOf(i);
    }

    private static int determineIterationLimit() {
        // Every multiple in the array has a prime factor that
        // is less than or equal to the root of the array size,
        // so we don't have to cross out multiples of numbers
        // larger than that root.
        double iterationLimit = Math.sqrt(crossedOut.length);
        return (int) iterationLimit;
    }
    // ...
}
```

**Two comments survive out of a dozen**, and Martin justifies each:
- The class-level algorithm summary — arguably redundant with `generatePrimes` itself,
  kept only because it eases the reader into the algorithm.
- The square-root rationale — *"almost certainly necessary. I could find no simple
  variable name, nor any different coding structure that made this point clear."*

Note his honesty about even that one: he wonders aloud whether the square-root
optimization is *"a conceit"* — whether computing the root saves more time than everyone
will spend understanding it. **The bar for keeping a comment is that high.**

## Mental Models

- **A comment is a receipt for a failure of expression.** Pat yourself on the back when
  you express intent in code; grimace when you write a comment.
- **Comments lie — not intentionally, but structurally.** Code moves, splits, and merges;
  comments get orphaned. The `HTTP_DATE_REGEXP` example: new fields were inserted
  between a constant and its explanatory comment, which now describes something else.
- **A section comment inside a function is an extraction waiting to happen.** So is a
  closing-brace comment (shorten the function) and a function-header comment (rename it).
- **"Why," not "what."** Code already says what. Comments earn their place only by
  explaining intent, warning of consequences, or amplifying non-obvious importance.
- **Source control is the right home** for change logs, bylines, and old code.

## Key Takeaways

1. **Try to delete the comment by improving the code first** — extract a function, name
   a variable, rename the method. This is the default move.
2. **Never comment bad code — rewrite it.**
3. **Delete commented-out code on sight.** Source control has it.
4. **Delete journal comments, bylines, and noise comments** wherever you find them.
5. **Keep: legal headers, intent, warnings of consequence, amplification, TODOs with a
   plan, and public-API javadoc.** That is close to the whole list.
6. **No mandated-comment policies** — "every function must have a javadoc" manufactures
   lies at scale.
7. **A comment that needs its own explanation has already failed.**
8. **Redundant is bad; misleading is worse.** A stale comment costs a debugging session.

## Connects To
- **Ch2 (Meaningful Names)**: "if a name requires a comment, the name does not reveal its
  intent" — the same rule from the other side.
- **Ch3 (Functions)**: extraction is the mechanism by which most comments are deleted;
  the `generatePrimes` sections are the "Sections within Functions" smell in Ch3.
- **Ch17 (Smells)**: C1 "Inappropriate Information", C2 "Obsolete Comment",
  C3 "Redundant Comment", C4 "Poorly Written Comment", C5 "Commented-Out Code".
- **Ch14 / Ch16**: full refactorings where comment removal falls out of the restructuring.
