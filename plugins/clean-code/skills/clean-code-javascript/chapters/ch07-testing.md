# Chapter 7: Testing

## Core Idea
"**Testing is more important than shipping.**" Without adequate tests you cannot know that a ship didn't break something — so hit your coverage goal before launching or refactoring any feature, and give each test **one concept**.

*(A short chapter — one named rule plus the coverage argument — but the argument is the chapter's real content.)*

## Frameworks Introduced
- **Testing is more important than shipping**: the chapter's opening claim and its organizing principle.
  - When to use: whenever schedule pressure argues for skipping tests.
  - How: treat "are we at our coverage goal?" as a release gate, not a nice-to-have.
  - Why: with no or inadequate tests, "every time you ship code you won't be sure that you didn't break anything."
- **100% coverage as the confidence target**: all **statements and branches**.
  - When to use: as the default aim; "deciding on what constitutes an adequate amount is up to your team."
  - How: a great testing framework is not enough — you also need a **good coverage tool** (the guide points to Istanbul).
  - What it buys: "very high confidence and developer peace of mind."
- **Single concept per test**: one behavior per `it` block.
  - When to use: every test.
  - How: split a multi-assertion test into separately-named `it` blocks — `"handles 30-day months"`, `"handles leap year"`, `"handles non-leap year"` instead of one `"handles date boundaries"`.
  - Why it works: a failure names the broken concept immediately, and no assertion can hide behind an earlier failure in the same block.
- **TDD is optional; coverage is not**: "If your preferred method is Test Driven Development (TDD), that is great, but the main point is to just make sure you are reaching your coverage goals before launching any feature, or refactoring an existing one."
  - When to use: pick the workflow your team prefers; hold the outcome fixed.

## Key Concepts
- **Coverage (statement and branch)** — the proportion of statements and of conditional branches exercised by the suite; branch coverage is the one people forget.
- **Coverage tool** — instrumentation that measures the above (e.g. Istanbul); distinct from the test framework.
- **Single concept per test** — one `it`, one behavior, one reason to fail.
- **Test Driven Development (TDD)** — writing the test first; endorsed but explicitly not required.
- **Regression confidence** — the property that lets you refactor; the actual product of a test suite.

## Mental Models
- **Think of tests as the licence to refactor.** Every rule in Ch 2–6 asks you to change working code. The suite is what makes that safe rather than reckless.
- **Use the test name as the failure message.** `"handles leap year"` tells you what broke; `"handles date boundaries"` tells you to go read the test.
- **Think of one assertion block as one hostage.** The first failing assertion in a multi-concept test hides every later one — you fix, re-run, and discover the next.
- **"No excuse" is literal.** "There's no excuse to not write tests. There are plenty of good JS test frameworks" — tooling scarcity is not an argument.

## Anti-patterns
- **Shipping with inadequate tests**: you lose the ability to know whether a release broke anything.
- **Multi-concept tests**: one `it("handles date boundaries")` asserting 30-day months, leap years, and non-leap years — three reasons to fail under one name, with the later two masked by the first.
- **Reusing a mutable `let date` across assertions** in one test: state from concept one leaks into concept two.
- **Counting statement coverage only**: branch coverage is named explicitly; an `if` whose else-path never runs is uncovered regardless of statement percentage.
- **Framework without a coverage tool**: you have tests but no evidence of what they reach.
- **Arguing TDD vs not instead of writing tests**: the guide is deliberately agnostic on method and firm on the outcome.

## Code Examples
Single concept per test:

```javascript
// Bad — one test, three concepts, shared mutable state
import assert from "assert";

describe("MomentJS", () => {
  it("handles date boundaries", () => {
    let date;

    date = new MomentJS("1/1/2015");
    date.addDays(30);
    assert.equal("1/31/2015", date);

    date = new MomentJS("2/1/2016");
    date.addDays(28);
    assert.equal("02/29/2016", date);

    date = new MomentJS("2/1/2015");
    date.addDays(28);
    assert.equal("03/01/2015", date);
  });
});

// Good — three tests, three names, each with its own const
import assert from "assert";

describe("MomentJS", () => {
  it("handles 30-day months", () => {
    const date = new MomentJS("1/1/2015");
    date.addDays(30);
    assert.equal("1/31/2015", date);
  });

  it("handles leap year", () => {
    const date = new MomentJS("2/1/2016");
    date.addDays(28);
    assert.equal("02/29/2016", date);
  });

  it("handles non-leap year", () => {
    const date = new MomentJS("2/1/2015");
    date.addDays(28);
    assert.equal("03/01/2015", date);
  });
});
```
- **What it demonstrates**: splitting also upgrades `let date` to three separate `const` bindings — the single-concept rule removes shared mutable state as a side effect.

## Reference Tables

| Aspect | Guide's position |
|---|---|
| Priority | Testing > shipping |
| Coverage target | 100% of statements **and** branches |
| Who decides "adequate" | Your team |
| Tooling needed | Test framework **+** a coverage tool (e.g. Istanbul) |
| TDD | Great if you prefer it; not required |
| Non-negotiable | Reach coverage goals **before** launching or refactoring |
| Test granularity | One concept per test |

What the bad/good split buys:

| Property | One multi-concept test | Three single-concept tests |
|---|---|---|
| Failure tells you what broke | No | Yes, from the name |
| Later assertions still run after a failure | No | Yes |
| Shared mutable state | `let date` reused | Three `const`s |
| Concepts countable from the report | No | Yes |

## Worked Example
Take the bad `"handles date boundaries"` test and trace a real regression: someone breaks leap-year handling so `2/1/2016 + 28 days` yields `"02/28/2016"`.

**With the single test:**
1. Run the suite. One failure: `MomentJS handles date boundaries`.
2. The name does not say which boundary. Open the test, read three blocks, find the failing `assert.equal`.
3. Fix leap years. Re-run.
4. Now the **third** assertion fails — it never ran before, because assertion two threw. Non-leap-year handling was broken by the same change.
5. Two round-trips to learn there were two defects.

**With the three tests:**
1. Run the suite. Two failures, named: `handles leap year`, `handles non-leap year`.
2. Both defects are visible in the first report; `handles 30-day months` is confirmed green, so the change's blast radius is known immediately.

The difference isn't tidiness — it's that the split test suite reports **all** the damage on the first run, which is exactly the "am I sure I didn't break anything?" question the chapter opens with.

## Key Takeaways
1. Testing outranks shipping — without tests, every release is a guess.
2. Aim for **100% statement and branch coverage**; your team sets "adequate", but branches are part of the measure.
3. A test framework alone is insufficient — add a coverage tool to see what you actually reach.
4. Write tests for every new feature/module as you introduce them.
5. **One concept per test**, with a name that identifies the concept; multi-concept tests mask failures.
6. TDD is welcome but optional; hitting coverage before launch or refactor is not.

## Connects To
- **Ch 3 (Functions)**: the ≤2 argument rule exists to avoid a combinatorial explosion of test cases; "do one thing" is the production-code twin of "single concept per test".
- **Ch 6 (SOLID)**: DIP's injected collaborators are what make units testable in isolation; LSP violations like Square/Rectangle are caught by tests, since JS has no compiler to catch them.
- **Ch 1 (Introduction)**: tests are the safety net that makes the "chisel away imperfections" refactoring loop possible.
- **Istanbul**: the coverage tool the guide links for measuring statements and branches.
