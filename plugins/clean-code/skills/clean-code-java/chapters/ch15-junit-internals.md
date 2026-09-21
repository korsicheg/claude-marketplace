# Chapter 15: JUnit Internals

## Core Idea
**No module is immune from improvement.** This is the Boy Scout Rule applied to code that
is *already good* — JUnit's `ComparisonCompactor`, written by Kent Beck and Erich Gamma.
The chapter is a transcript of ~15 successive refactorings, each justified by a named
heuristic from Chapter 17, ending with **some earlier decisions deliberately reversed**.

## The module under critique

`ComparisonCompactor` produces readable string-diff failure messages: given `ABCDE` and
`ABXDE`, it emits `<...B[X]D...>`. Its requirements are best read from its tests:

```java
public void testMessage() {
    String failure = new ComparisonCompactor(0, "b", "c").compact("a");
    assertTrue("a expected:<[b]> but was:<[c]>".equals(failure));
}
public void testStartSame() {
    String failure = new ComparisonCompactor(1, "ba", "bc").compact(null);
    assertEquals("expected:<b[a]> but was:<b[c]>", failure);
}
public void testNoContextStartAndEndSame() {
    String failure = new ComparisonCompactor(0, "abc", "adc").compact(null);
    assertEquals("expected:<...[b]...> but was:<...[d]...>", failure);
}
```

Martin's framing of the original: *"You might have a few complaints about this module.
There are some long expressions and some strange `+1`s and so forth. But overall this
module is pretty good."* He then shows a **"defactored"** version — the same logic with
`ctxt`, `s1`, `s2`, `pfx`, `sfx` and everything inlined — as a reminder of what it could
have looked like.

## Worked Example: the full refactoring sequence

Each step names the heuristic that motivated it. **This ordered list is the chapter's
real content** — it is a worked demonstration of how to read code critically.

| # | Change | Heuristic |
|---|---|---|
| 1 | Strip the `f` prefix from members: `fExpected` → `expected` | **N6** — scope encoding is redundant in modern environments |
| 2 | Extract the opening conditional into `shouldNotCompact()` | **G28** — encapsulate conditionals to make intent clear |
| 3 | Rename locals shadowing members: `this.expected` → `compactExpected` | **N4** — *"Why are there variables in this function that have the same names as the member variables? Don't they represent something else?"* |
| 4 | Invert to `canBeCompacted()` and flip the `if` | **G29** — *"Negatives are slightly harder to understand than positives"* |
| 5 | Rename `compact` → `formatCompactedComparison` | **N7** — the name lied: it might not compact, and it returns a *formatted message*. *"Naming this function `compact` hides the side effect of the error check"* |
| 6 | Extract `compactExpectedAndActual()` so formatting and compacting are separate | **G30** — do one thing |
| 7 | Make `findCommonPrefix`/`findCommonSuffix` *return* their values | **G11** — inconsistent conventions: two lines returned variables, two didn't |
| 8 | Rename `prefix`/`suffix` → `prefixIndex`/`suffixIndex` | **N1** — choose descriptive names; they are indices |
| 9 | Pass `prefixIndex` into `findCommonSuffix` to expose the ordering dependency | **G31** — hidden temporal coupling: *"If these two functions were called out of order, there would be a difficult debugging session ahead"* |
| 10 | **Undo step 9.** Instead merge into `findCommonPrefixAndSuffix()` which calls `findCommonPrefix()` first | **G32** — the argument was *"a bit arbitrary… It works to establish the ordering but does nothing to explain the need for that ordering. Another programmer might undo what we have done"* |
| 11 | Rewrite the ugly merged function with `charFromEnd` and `suffixOverlapsPrefix` helpers | readability |
| 12 | Rename `suffixIndex` → `suffixLength`, make it zero-based | **G33** — *"This is also the reason that there are all those `+1`s"* |
| 13 | Comment out both `if`s in `compactString`, **run the tests — they passed** — and delete them | **G9** — dead/extraneous code |
| 14 | Split `compact` into `startingEllipsis`, `startingContext`, `delta`, `endingContext`, `endingEllipsis` | one thing per function |

**Step 9 → 10 is the most instructive pair in the book on refactoring judgment:** a
correct fix for temporal coupling was rejected because it *worked without communicating
why*, and replaced with a structure that makes the ordering self-evident.

**Step 13 is the most instructive on discovering dead code:** renaming a variable to
express what it actually is (`suffixIndex` → `suffixLength`) *"calls into question both
`if` statements."* The check is empirical — comment them out, run the tests.

## The destination

```java
public class ComparisonCompactor {
    private static final String ELLIPSIS = "...";
    private static final String DELTA_END = "]";
    private static final String DELTA_START = "[";

    private int contextLength;
    private String expected;
    private String actual;
    private int prefixLength;
    private int suffixLength;

    public String formatCompactedComparison(String message) {
        String compactExpected = expected;
        String compactActual = actual;
        if (shouldBeCompacted()) {
            findCommonPrefixAndSuffix();
            compactExpected = compact(expected);
            compactActual = compact(actual);
        }
        return Assert.format(message, compactExpected, compactActual);
    }

    private boolean shouldBeCompacted() { return !shouldNotBeCompacted(); }

    private boolean shouldNotBeCompacted() {
        return expected == null || actual == null || expected.equals(actual);
    }

    // ---- analysis ----
    private void findCommonPrefixAndSuffix() {
        findCommonPrefix();
        suffixLength = 0;
        for (; !suffixOverlapsPrefix(); suffixLength++) {
            if (charFromEnd(expected, suffixLength) != charFromEnd(actual, suffixLength))
                break;
        }
    }
    private char charFromEnd(String s, int i) { return s.charAt(s.length() - i - 1); }
    private boolean suffixOverlapsPrefix() {
        return actual.length() - suffixLength <= prefixLength
            || expected.length() - suffixLength <= prefixLength;
    }
    private void findCommonPrefix() {
        prefixLength = 0;
        int end = Math.min(expected.length(), actual.length());
        for (; prefixLength < end; prefixLength++)
            if (expected.charAt(prefixLength) != actual.charAt(prefixLength))
                break;
    }

    // ---- synthesis ----
    private String compact(String s) {
        return new StringBuilder()
            .append(startingEllipsis())
            .append(startingContext())
            .append(DELTA_START)
            .append(delta(s))
            .append(DELTA_END)
            .append(endingContext())
            .append(endingEllipsis())
            .toString();
    }
    private String startingEllipsis() {
        return prefixLength > contextLength ? ELLIPSIS : "";
    }
    private String startingContext() {
        int contextStart = Math.max(0, prefixLength - contextLength);
        return expected.substring(contextStart, prefixLength);
    }
    private String delta(String s) {
        return s.substring(prefixLength, s.length() - suffixLength);
    }
    private String endingContext() {
        int contextStart = expected.length() - suffixLength;
        int contextEnd = Math.min(contextStart + contextLength, expected.length());
        return expected.substring(contextStart, contextEnd);
    }
    private String endingEllipsis() {
        return suffixLength > contextLength ? ELLIPSIS : "";
    }
}
```

**What the final structure achieves** (in Martin's own words): *"The module is separated
into a group of **analysis** functions and another group of **synthesis** functions. They
are topologically sorted so that the definition of each function appears just after it is
used. All the analysis functions appear first, and all the synthesis functions appear
last."*

## Mental Models

- **Refactoring is not monotonic.** *"If you look carefully, you will notice that I
  reversed several of the decisions I made earlier in this chapter… **Often one
  refactoring leads to another that leads to the undoing of the first.** Refactoring is
  an iterative process full of trial and error, inevitably converging on something that
  we feel is worthy of a professional."*
- **A fix that works but doesn't communicate will be undone by the next programmer.**
  That is a legitimate reason to reject it.
- **Renaming reveals bugs and dead code.** Getting `suffixIndex` → `suffixLength` right
  exposed both the stray `+1`s and two unnecessary `if` statements.
- **Analysis then synthesis** is a reusable way to organize a module: first the functions
  that figure out what's true, then the functions that build the output.
- **Tests are the permission slip.** "Comment it out and run the tests" is only a legal
  move because the tests exist.

## Anti-patterns (each is a heuristic in Ch17)

- `f`-prefixed or otherwise scope-encoded members [N6].
- Unencapsulated compound conditionals [G28].
- Locals shadowing member names [N4].
- Negative conditionals where a positive would do [G29].
- A function name that hides a side effect or misdescribes the return [N7].
- A function that both formats and computes [G30].
- Inconsistent conventions within one function [G11].
- **Hidden temporal coupling** — functions that must be called in order with nothing
  saying so [G31].
- An argument added only to force ordering, explaining nothing [G32].
- Off-by-one-inducing names that aren't what they claim (`Index` for a length) [G33].
- Extraneous conditionals that the tests prove unnecessary [G9].

## Key Takeaways

1. **Apply the Boy Scout Rule to good code too** — *"each of us has the responsibility to
   leave the code a little better than we found it."*
2. **Refactor in named, justified steps.** Every change here cites a specific heuristic.
3. **Prefer structure that communicates ordering over parameters that merely enforce it.**
4. **Expect to reverse your own earlier refactorings** — that is convergence, not failure.
5. **Rename until names are literally true**; the wrong name hides bugs and dead branches.
6. **Verify deletions empirically** — comment out, run tests, then delete.
7. **Organize a module as analysis functions then synthesis functions**, topologically
   sorted.

## Connects To
- **Ch1 (Clean Code)**: the Boy Scout Rule this chapter enacts.
- **Ch3 (Functions)**: one thing, one level of abstraction, the Stepdown Rule
  (topological sorting is exactly that).
- **Ch5 (Formatting)**: caller-above-callee vertical ordering.
- **Ch17 (Smells and Heuristics)**: every step here is a numbered entry there — the two
  chapters are best read together.
- **Ch14 / Ch16**: the other two refactoring case studies.
