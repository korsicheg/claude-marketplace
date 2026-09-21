# Chapter 16: Refactoring `SerialDate`

## Core Idea
**First make it work, then make it right.** A full professional review of someone else's
good open-source code (`org.jfree.date.SerialDate` by David Gilbert): raise test coverage
first, use coverage gaps and test-failure *patterns* to find real bugs, then refactor
top-to-bottom running the whole suite after every change.

## The ethic of code review — stated explicitly

Martin opens by naming what he is doing and why it is legitimate:

> *"For all intents and purposes, this is 'good code.' And I am going to rip it to
> pieces. This is not an activity of malice… What I am about to do is nothing more and
> nothing less than **a professional review**. It is something that we should all be
> comfortable doing. **And it is something we should welcome when it is done for us.** It
> is only through critiques like these that we will learn. **Doctors do it. Pilots do it.
> Lawyers do it. And we programmers need to learn how to do it too.**"*

He also credits the author: Gilbert *"had the courage and good will to offer his code to
the community at large for free… invited public usage and public scrutiny. This was well
done!"* **Review the code, credit the person.**

## Phase 1 — First, Make It Work

- **Measure coverage before believing the tests.** The existing `SerialDateTests` all
  passed — but Clover reported only **91 of 185 executable statements (~50%)** covered
  [T2], *"a patchwork quilt, with big gobs of unexecuted code."* A "Find Usages" on
  `monthCodeToQuarter` showed it was **never called at all** [F4], so of course no test
  touched it.
- **Write an independent suite** — Martin wrote his own from scratch, reaching **170/185
  (92%)**, *with some tests deliberately left commented out* because they encode
  behavior he believes the class *should* have. **Failing tests as a specification.**
- **Be explicit about what's a conceit.** He flags that his first few commented-out tests
  were *"a bit of conceit on my part. The program was not designed to pass these tests,
  but the behavior seemed obvious [G2] to me."* And he leaves `'tues'`/`'thurs'`
  commented out because *"it's not clear to me that [they] ought to be supported."*
  **Uncertainty is recorded, not resolved by fiat.**

### The four defects found, and how each was found

| Defect | How it surfaced | Fix |
|---|---|---|
| `testWeekdayCodeToString` case-sensitive | Obvious expected behavior [G2]; test was trivial to write [T3] | `equalsIgnoreCase` |
| `stringToMonthCode` rejects valid names | Failing tests that *clearly should pass* [G2] | loop over both `shortMonthNames` and `monthNames` with `equalsIgnoreCase` |
| **`getFollowingDayOfWeek` off by one** | A commented-out test: Dec 25 2004 was a Saturday; the following Saturday is Jan 1 2005, but the method **returned Dec 25 itself** [G3][T1] | `if (baseDOW >= targetWeekday)` — *"a typical boundary condition error"* [T5] |
| **`getNearestDayOfWeek` algorithm just wrong** | Two independent signals (below) | rewritten entirely |

**The `getNearestDayOfWeek` diagnosis is the most instructive passage in the chapter**,
because two different kinds of evidence converge:

1. **The pattern of which tests fail is itself information** [T7]. Martin's initial tests
   didn't all pass, so he added more until the shape was visible: *"It shows that the
   algorithm fails if the nearest day is in the future."* — a boundary condition [T5].
2. **The pattern of test coverage is information too** [T8]. Clover showed **line 719
   never executes**, meaning the `if` on line 718 is *always false*. Reading the code
   confirms it: `adjust` is always negative and so can never be ≥ 4. **Dead code proved
   by coverage, then by inspection.**

```java
// The right algorithm:
int delta = targetDOW - base.getDayOfWeek();
int positiveDelta = delta + 7;
int adjust = positiveDelta % 7;
if (adjust > 3)
    adjust -= 7;
return SerialDate.addDays(adjust, base);
```

**A telling detail [T6]:** the change history at the top of the file records that "bugs"
had already been fixed in `getPreviousDayOfWeek`, `getFollowingDayOfWeek`, and
`getNearestDayOfWeek`. **Repeated repairs in the same place mean the algorithm, not the
line, is wrong.**

- Last fix: `weekInMonthToString` and `relativeToString` **throw
  `IllegalArgumentException` instead of returning an error string.**

## Phase 2 — Then Make It Right

Walked top to bottom. **"I will be running all of the JCommon unit tests… after every
change I make."**

| Finding | Heuristic | Action |
|---|---|---|
| Change history in the file header | **C1** | Delete — *"a leftover from the 1960s. We have source code control tools that do this for us now."* Copyrights and licenses stay |
| Long import list | **J1** | `java.text.*`, `java.util.*` |
| HTML inside Javadoc | **G1** | *"This comment has four languages in it: Java, English, Javadoc, and html."* Source positioning is lost when Javadoc renders; wrap in `<pre>` |
| The name `SerialDate` | **N1, N2** | Two objections: "serial number" is inaccurate (it's an **ordinal**/relative offset, not a product identifier), and **the name implies an implementation on an abstract class** — *"there is good reason to hide the implementation!"* Renamed **`DayDate`** (`Date` and `Day` were taken) |
| `extends MonthConstants` | **J2** | Inheriting for constants is *"an old trick… but it's a bad idea."* Replaced with an `enum Month` |
| `serialVersionUID` | **G4** | Deleted — automatic control is safer. *"I'd much rather debug an `InvalidClassException` than the odd behavior that would ensue if I forgot to change the `serialVersionUID`"* |
| Redundant comments | **C2** | Deleted — *"redundant comments are just places to collect lies and misinformation"* |
| `SERIAL_LOWER_BOUND`/`UPPER_BOUND` | **N1, G6** | Renamed `EARLIEST_DATE_ORDINAL`/`LATEST_DATE_ORDINAL`, then **moved down to `SpreadsheetDate`** — a code search proved nothing else in JCommon used them |
| Base class creating its derivative | **G7** | `addDays` → `createInstance` → **`new SpreadsheetDate`**. *"It's generally a bad idea for base classes to know about their derivatives."* Fixed with an **Abstract Factory**, `DayDateFactory` |
| Magic number `1` for months/days | **G25** | `Month.JANUARY.toInt()`, `Day.SUNDAY.toInt()` |

```java
public abstract class DayDate implements Comparable, Serializable {
    public static enum Month {
        JANUARY(1), FEBRUARY(2), MARCH(3), APRIL(4), MAY(5), JUNE(6),
        JULY(7), AUGUST(8), SEPTEMBER(9), OCTOBER(10), NOVEMBER(11), DECEMBER(12);

        Month(int index) { this.index = index; }

        public static Month make(int monthIndex) {
            for (Month m : Month.values())
                if (m.index == monthIndex)
                    return m;
            throw new IllegalArgumentException("Invalid month index " + monthIndex);
        }
        public final int index;
    }
```

**The enum's payoff, and its honest price:** *"It took me an hour to make all the
changes."* In return, every function that took an `int` month now takes a `Month`, which
**deletes `isValidMonthCode` entirely and all the month-code error checking** such as in
`monthCodeToQuarter` [G5]. **Making illegal states unrepresentable removes validation
code.**

## The dilemma worth studying: abstract class vs. implementation limits

`MINIMUM_YEAR_SUPPORTED` / `MAXIMUM_YEAR_SUPPORTED` "clearly" belong in
`SpreadsheetDate` [G6] — except `RelativeDayOfWeekRule.getDate` uses them to validate
its year argument. *"The dilemma is that a user of an abstract class needs information
about its implementation."*

Normally you'd get implementation facts from an *instance* of a derivative, but `getDate`
isn't **passed** a `DayDate` — it **returns** one, so something must be creating it.
Tracing it back: `getPreviousDayOfWeek`/`getNearestDayOfWeek`/`getFollowingDayOfWeek` →
`addDays` → `createInstance` → `new SpreadsheetDate`.

**Resolution: an Abstract Factory.** `DayDateFactory` both creates the instances *and*
answers questions about the implementation (max/min dates) — giving the caller what it
needs *"without polluting `DayDate` itself."*

## Mental Models

- **Coverage is a diagnostic instrument, not a score.** Never-executed lines point at
  dead conditionals; the *shape* of the uncovered map points at untested behavior.
- **The pattern of failing tests is a debugging tool.** Add cases until the boundary
  becomes visible.
- **Repeated bug fixes in one function mean the algorithm is wrong.**
- **Naming carries design information.** `SerialDate` failed twice over: inaccurate term,
  *and* wrong level of abstraction for an abstract class.
- **"Make it work" and "make it right" are sequential, not simultaneous** — and neither
  is optional.
- **The counterintuitive coverage result at the end:** coverage *fell* to 84.9% — *"not
  because less functionality is being tested; rather it is because the class has shrunk
  so much that the few uncovered lines have a greater weight."* 45 of 53 statements
  covered; the rest *"so trivial that they weren't worth testing."* **A percentage can
  drop while quality rises.**
- **Martin publishes the dissent.** In a footnote he records that several reviewers
  disagreed with deleting `serialVersionUID`, calls it *"a fair point,"* and states his
  reasoning: a clear-cut failure beats an undefined, possibly silent one. *"The real
  moral of this story is that you should not expect to deserialize across versions."*

## Key Takeaways

1. **Measure coverage before trusting a passing suite.**
2. **Write your own independent tests**, including failing ones that specify desired
   behavior; leave genuinely unclear cases commented out rather than guessing.
3. **Read the coverage map and the failure pattern** — both find bugs that reading code
   alone misses.
4. **A function with a history of repeated "bug fixes" needs a new algorithm.**
5. **Throw exceptions instead of returning error strings.**
6. **Replace constant-holder inheritance with enums** — and watch validation code
   disappear.
7. **Move constants down to the class that actually uses them**, verified by search.
8. **Never let a base class instantiate its derivatives** — use an Abstract Factory.
9. **Delete change-history comments; keep copyrights.**
10. **Run the full suite after every change**, and leave the code cleaner than you found
    it — knowing the next person will clean it further.

## Connects To
- **Ch1 (Clean Code)**: the Boy Scout Rule, applied to a stranger's library.
- **Ch4 (Comments)**: change histories, redundant comments, HTML in Javadoc.
- **Ch9 (Unit Tests)**: the `addMonths` "one concept per test" example comes from this
  same `SerialDate` suite.
- **Ch14 / Ch15**: the other refactoring case studies — same discipline, different scale.
- **Ch17 (Smells)**: every bracketed tag here (C1, C2, G1–G7, G25, J1, J2, N1, N2,
  T1–T8, F4) is an entry in that catalogue.
- **Appendix B**: the full `SerialDate`/`DayDate` source listings before and after.
- **GoF** (Abstract Factory); **Fowler, *Refactoring***; **Beck, *Smalltalk Best Practice
  Patterns***; **Simmons, *Hardcore Java***.
