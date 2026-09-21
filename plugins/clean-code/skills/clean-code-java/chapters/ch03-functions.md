# Chapter 3: Functions

## Core Idea
**The first rule of functions is that they should be small. The second rule is that they
should be smaller than that.** A function does one thing when every statement in it sits
exactly one level of abstraction below the function's own name.

## Frameworks Introduced

- **Small!** — functions should hardly ever be 20 lines long; 2–4 lines is the target.
  - How: extract until you cannot extract a function whose name is more than a
    restatement of its body.
  - **Blocks and indenting**: the body of an `if`/`else`/`while` should be **one line**,
    and that line should probably be a function call. Therefore the **indent level of a
    function should not be greater than one or two.**

- **Do One Thing** — *FUNCTIONS SHOULD DO ONE THING. THEY SHOULD DO IT WELL. THEY SHOULD
  DO IT ONLY.*
  - **The operational test**: a function does one thing if it does only those steps that
    are one level of abstraction below its stated name.
  - **The second test**: you can no longer extract a function from it with a name that is
    not merely a restatement of its implementation [G34].
  - **The third test**: a function you can divide into *sections* (declarations,
    initializations, sieve) is doing more than one thing. Functions that do one thing
    cannot be reasonably divided into sections.

- **One Level of Abstraction per Function** — never mix `getHtml()` (high),
  `PathParser.render(pagePath)` (mid) and `.append("\n")` (low) in one body.
  - Why it fails otherwise: readers can't tell essential concept from detail, and — like
    broken windows — once details mix in, more details accrete.

- **The Stepdown Rule** — code reads as a top-down narrative; every function is followed
  by those at the next level of abstraction, so you descend one level at a time.
  - How: phrase each function as a **TO paragraph**. *"TO include the setups and
    teardowns, we include setups, then the test page content, then the teardowns. TO
    include the setups, we include the suite setup if this is a suite, then the regular
    setup. TO include the suite setup, we search the parent hierarchy for 'SuiteSetUp'
    and add an include statement with that path."* If the paragraph doesn't read
    naturally, the abstraction level is wrong.

- **Command Query Separation** — a function either **does** something or **answers**
  something, never both.
  - The tell: `if (set("username", "unclebob"))` — is `set` a verb or an adjective?
  - The fix: `if (attributeExists("username")) { setAttribute("username", "unclebob"); }`

- **Prefer Exceptions to Returning Error Codes** — error codes are a subtle CQS violation
  that force the caller to handle the error immediately, producing deep nesting.
  - Also avoids **the `Error.java` dependency magnet**: an error enum that everything
    imports must be recompiled and redeployed on every change, so programmers stop adding
    new codes and start reusing wrong ones. New *exceptions* are just derivatives — added
    without recompiling anyone (this is OCP).

- **Extract Try/Catch Blocks** — **error handling is one thing**, so a function that
  handles errors does nothing else.
  - The concrete rule: **if the keyword `try` appears in a function, it must be the very
    first word in that function, and nothing may follow the `catch`/`finally` blocks.**

- **Don't Repeat Yourself (DRY)** — *duplication may be the root of all evil in software.*
  - Martin's framing: Codd's normal forms, OO base classes, structured programming, AOP,
    and component-oriented programming are all, in part, strategies for eliminating
    duplication. Since the invention of the subroutine, the history of the field has been
    an attempt to eliminate duplication from source code.

## Reference Table: function arguments

| Arity | Name | Verdict |
|---|---|---|
| 0 | niladic | **Ideal** |
| 1 | monadic | Next best |
| 2 | dyadic | Acceptable at a cost — convert to monadic where you can |
| 3 | triadic | **Avoid where possible** — think very carefully |
| 4+ | polyadic | Requires very special justification — *and then shouldn't be used anyway* |

**The three legitimate monadic forms** (anything else confuses the reader):

| Form | Shape | Example |
|---|---|---|
| Ask a question about the argument | `boolean f(X)` | `boolean fileExists("MyFile")` |
| Transform the argument and **return** it | `Y f(X)` | `InputStream fileOpen("MyFile")` |
| Event (input, no output; alters system state) | `void f(X)` | `void passwordAttemptFailedNtimes(int attempts)` |

Rules that follow from the table:
- **A transformation must return its result.** `StringBuffer transform(StringBuffer in)`
  beats `void transform(StringBuffer out)` even if the body just returns its input.
- **Dyads that are ordered components of one value are fine** — `new Point(0,0)`. Dyads
  with no natural cohesion or ordering are not — `writeField(outputStream, name)`,
  `assertEquals(expected, actual)`.
- **Converting a dyad to a monad**: make the method a member of one argument
  (`outputStream.writeField(name)`), make the argument a field of the current class, or
  extract a class that takes it in the constructor (`FieldWriter`).
- **Argument objects**: when a function needs 3+ arguments, some of them are probably a
  concept that deserves a name. `makeCircle(Point center, double radius)` beats
  `makeCircle(double x, double y, double radius)`. This is not cheating.
- **Varargs count as one argument** if treated identically — `String.format(String, Object...)`
  is dyadic. `void triad(String name, int count, Integer... args)` is the limit.
- **Keyword form**: encode argument names into the function name to kill ordering
  mistakes — `assertExpectedEqualsActual(expected, actual)`.

## Anti-patterns

- **Flag arguments** — *passing a boolean into a function is a truly terrible practice.*
  It proclaims the function does two things. Split it: `renderForSuite()` and
  `renderForSingleTest()`, not `render(true)`.
- **Output arguments** — `appendFooter(s)`: is `s` the footer or the target? Anything
  that forces you to check the signature is a cognitive break. In OO, `this` *is* the
  output argument: prefer `report.appendFooter()`. If a function must change state,
  it changes the state of its owning object.
- **Side effects** — *side effects are lies.* `checkPassword()` that also calls
  `Session.initialize()` creates a hidden **temporal coupling**: it can only be called
  when it's safe to wipe the session. Renaming it `checkPasswordAndInitializeSession`
  makes the coupling honest but violates "do one thing" — so remove the side effect.
- **Switch statements in business logic** — by nature they do N things, violate SRP (more
  than one reason to change) and OCP (must change when a type is added), and the same
  structure then replicates across `isPayday`, `deliverPay`, and the rest.
- **Dogmatic single-entry/single-exit** — Dijkstra's rules pay off only in *large*
  functions. In small functions an occasional multiple `return`, `break`, or `continue`
  is harmless and often more expressive. `goto` only makes sense in large functions, so
  avoid it entirely.

## Worked Example 1: `testableHtml` → `SetupTeardownIncluder`

The book's flagship refactor. **Before** (FitNesse `HtmlUtil.java`), ~35 lines: nested
`if`s controlled by a flag, magic strings, four near-copies of the same include
algorithm, three different abstraction levels in one body — unreadable in three minutes.

**After a few extractions and renames:**

```java
public static String renderPageWithSetupsAndTeardowns(
        PageData pageData, boolean isSuite) throws Exception {
    boolean isTestPage = pageData.hasAttribute("Test");
    if (isTestPage) {
        WikiPage testPage = pageData.getWikiPage();
        StringBuffer newPageContent = new StringBuffer();
        includeSetupPages(testPage, newPageContent, isSuite);
        newPageContent.append(pageData.getContent());
        includeTeardownPages(testPage, newPageContent, isSuite);
        pageData.setContent(newPageContent.toString());
    }
    return pageData.getHtml();
}
```

**Still not done** — this has two levels of abstraction, so shrink again:

```java
public static String renderPageWithSetupsAndTeardowns(
        PageData pageData, boolean isSuite) throws Exception {
    if (isTestPage(pageData))
        includeSetupAndTeardownPages(pageData, isSuite);
    return pageData.getHtml();
}
```

The final `SetupTeardownIncluder` class turns every remaining argument into a field, so
the private methods become niladic and read as TO paragraphs:

```java
private void includeSetupAndTeardownPages() throws Exception {
    includeSetupPages();
    includePageContent();
    includeTeardownPages();
    updatePageContent();
}
private void includeSetupPages() throws Exception {
    if (isSuite) includeSuiteSetupPage();
    includeSetupPage();
}
private void includeSuiteSetupPage() throws Exception {
    include(SuiteResponder.SUITE_SETUP_NAME, "-setup");
}
private void includeSetupPage() throws Exception {
    include("SetUp", "-setup");
}
```

Note the **consistent phraseology**: `includeSetupAndTeardownPages`, `includeSetupPages`,
`includeSuiteSetupPage`, `includeSetupPage`. Seeing that sequence, you immediately ask
"where are `includeTeardownPages`, `includeSuiteTeardownPage`, `includeTeardownPage`?" —
and they exist. That is Ward's *"pretty much what you expected."*

## Worked Example 2: burying a switch behind a factory

**Before** — grows with every new employee type, and this shape will be duplicated in
`isPayday`, `deliverPay`, and every other type-dependent operation:

```java
public Money calculatePay(Employee e) throws InvalidEmployeeType {
    switch (e.type) {
        case COMMISSIONED: return calculateCommissionedPay(e);
        case HOURLY:       return calculateHourlyPay(e);
        case SALARIED:     return calculateSalariedPay(e);
        default: throw new InvalidEmployeeType(e.type);
    }
}
```

**After** — one switch, in the basement of an Abstract Factory, never seen again:

```java
public abstract class Employee {
    public abstract boolean isPayday();
    public abstract Money calculatePay();
    public abstract void deliverPay(Money pay);
}

public interface EmployeeFactory {
    Employee makeEmployee(EmployeeRecord r) throws InvalidEmployeeType;
}

public class EmployeeFactoryImpl implements EmployeeFactory {
    public Employee makeEmployee(EmployeeRecord r) throws InvalidEmployeeType {
        switch (r.type) {
            case COMMISSIONED: return new CommissionedEmployee(r);
            case HOURLY:       return new HourlyEmployee(r);
            case SALARIED:     return new SalariedEmployee(r);
            default: throw new InvalidEmployeeType(r.type);
        }
    }
}
```

**The rule**: a switch is tolerable only if it appears **once**, is used to **create
polymorphic objects**, and is **hidden behind an inheritance relationship** so the rest
of the system cannot see it [G23].

## Worked Example 3: error codes → exceptions → extracted try/catch

```java
// Deeply nested, error handling tangled with the happy path:
if (deletePage(page) == E_OK) {
    if (registry.deleteReference(page.name) == E_OK) {
        if (configKeys.deleteKey(page.name.makeKey()) == E_OK) {
            logger.log("page deleted");
        } else { logger.log("configKey not deleted"); }
    } else { logger.log("deleteReference from registry failed"); }
} else { logger.log("delete failed"); return E_ERROR; }
```

Exceptions separate the happy path from the error path; then extract the blocks so each
function does one thing:

```java
public void delete(Page page) {                       // all about error processing
    try {
        deletePageAndAllReferences(page);
    } catch (Exception e) {
        logError(e);
    }
}

private void deletePageAndAllReferences(Page page) throws Exception {   // all about deleting
    deletePage(page);
    registry.deleteReference(page.name);
    configKeys.deleteKey(page.name.makeKey());
}

private void logError(Exception e) { logger.log(e.getMessage()); }
```

## Mental Models

- **Think of a function as a TO paragraph** in a top-down narrative. If you can't write
  the paragraph, the function isn't at one level of abstraction.
- **Functions are the verbs of a domain-specific language; classes are the nouns.** The
  art of programming is the art of language design. Master programmers think of systems
  as *stories to be told*, not programs to be written.
- **Long descriptive name > short enigmatic name > long descriptive comment.** Don't fear
  a long function name; don't fear spending time on it — try several and read the code
  with each. Hunting for a good name often produces a favorable restructuring.
- **Arguments are hard, and hardest of all to test.** Testing every combination of two
  arguments is challenging; of three, daunting; of zero, trivial.

## How you actually get there

Nobody writes these functions on the first pass. Martin's own process: write it long,
clumsy, nested, badly named and duplicated — **but with a unit test suite covering every
clumsy line** — then massage it: split functions, change names, eliminate duplication,
shrink and reorder methods, break out whole classes, all while keeping tests green.
*"I don't write them that way to start. I don't think anyone could."*

## Key Takeaways

1. **Small, then smaller.** Blocks are one line; indent depth ≤ 2.
2. **One level of abstraction per function** — verify with the TO-paragraph test.
3. **Zero arguments is ideal**; three is already a design smell; flags are banned.
4. **No side effects, no output arguments** — change your own object's state instead.
5. **Separate command from query.**
6. **Throw exceptions, don't return error codes**, and extract try/catch bodies so `try`
   is the first word in the function.
7. **Kill duplication** — it is the root of most evil here.
8. **Bury switches in factories** and dispatch polymorphically.
9. **Write it dirty, then refactor under green tests.** The rules describe the
   destination, not the first draft.

## Connects To
- **Ch2 (Meaningful Names)**: extraction is mostly naming; the two chapters are one skill.
- **Ch7 (Error Handling)**: expands "prefer exceptions" into a full strategy.
- **Ch9 (Unit Tests)**: the green test suite is what makes aggressive extraction safe.
- **Ch10 (Classes)**: when a function's arguments become fields, you have found a class.
- **Ch17 (Smells)**: G30 "Functions Should Do One Thing", G34 "Functions Should Descend
  Only One Level of Abstraction", G23 "Prefer Polymorphism to If/Else or Switch/Case".
- **SRP / OCP**: the switch example is the canonical violation of both.
