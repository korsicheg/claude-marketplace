# Chapter 7: Testing

## Core Idea
**"Testing is more important than shipping."** Without adequate tests you cannot ship without
fearing you broke something — so aim at **100% coverage (all statements and branches)**, keep
**one concept per test**, and name each test so its failure message tells you what broke.

## Frameworks Introduced

- **The Three Laws of TDD** — verbatim:
  1. **You are not allowed to write any production code unless it is to make a failing unit
     test pass.**
  2. **You are not allowed to write any more of a unit test than is sufficient to fail, and;
     compilation failures are failures.**
  3. **You are not allowed to write any more production code than is sufficient to pass the one
     failing unit test.**
  - When to use: whenever you choose TDD. The source's position is notably permissive — *"If
     your preferred method is Test Driven Development (TDD), that is great, but the main point
     is to just make sure you are reaching your coverage goals before launching any feature, or
     refactoring an existing one."*
  - **The TypeScript-specific consequence of law 2**: *compilation failures are failures.* A test
    referencing a type or method that doesn't exist yet **is** a failing test — you have
    satisfied law 2 without writing an assertion. That is the red step in TS.

- **F.I.R.S.T. — the five properties of clean tests:**
  | Letter | Property | What it requires |
  |---|---|---|
  | **F** | **Fast** | Tests should be fast **because we want to run them frequently** |
  | **I** | **Independent** | Tests must not depend on each other — **same output run alone or all together in any order** |
  | **R** | **Repeatable** | Repeatable in **any environment**; "there should be no excuse for why they fail" |
  | **S** | **Self-Validating** | A test answers **Passed or Failed** — you never compare log files |
  | **T** | **Timely** | Written **before** the production code; write them after and "you might find writing tests too hard" |
  - How to use it: when a test suite is painful, name which letter is broken. Slow → F. Order-
    dependent → I. Green locally, red in CI → R. Needs a human to read output → S. Hard to write
    at all → T (the code wasn't designed for testing).

- **Single concept per test** — *"Tests should also follow the Single Responsibility Principle.
  Make only one assert per unit test."*
  - When to use: any `it()` block with more than one assertion, or with a reassigned subject.
  - How: split into one `it()` per concept and name each after the concept.

- **The name of the test should reveal its intention** — *"When a test fails, its name is the
  first indication of what may have gone wrong."*
  - How: name the behaviour, not the data. `'2/29/2020'` → `'should handle leap year'`;
    `'throws'` → `'should throw when format is invalid'`.

## Key Concepts
- **Coverage (statements and branches)** — the metric the source anchors on; 100% is *"how you
  achieve very high confidence and developer peace of mind."* A **coverage tool** (Istanbul is
  the named example) is required alongside the test framework.
- **Adequate amount of tests** — explicitly **up to your team** to define.
- **TDD (Test Driven Development)** — the three laws above; endorsed but not mandated.
- **Self-validating** — pass/fail with no human interpretation of output.
- **Single concept per test** — SRP applied to an `it()` block.
- **Compilation failure as a test failure** — TS-specific reading of TDD law 2.

## Mental Models
- **"There's no excuse to not write tests."** The source pre-empts the tooling excuse: there are
  plenty of good JS test frameworks **with typings support for TypeScript**. Pick what the team
  prefers, then **always write tests for every new feature/module you introduce.**
- **Treat the test name as the failure message.** You read it at 2am with no context. `Calendar
  › 2/29/2020` tells you nothing; `Calendar › should handle leap year` tells you where to look.
- **Think of multiple asserts in one `it()` as a truncated report.** The first failure hides the
  rest — a leap-year bug masks the non-leap-year bug, and you fix one, re-run, and get surprised.
- **Use F.I.R.S.T. as a diagnostic vocabulary, not a slogan.** Its value is that it turns "the
  tests are annoying" into a specific, fixable letter.
- **"Timely" is a design claim, not scheduling advice.** If tests are hard to write after the
  fact, the code has a dependency-injection problem (ch06 DIP), not a testing problem.
- **Coverage is a floor for shipping, not a goal in itself** — the source ties it to *"before
  launching any feature, or refactoring an existing one."*

## Code Examples

Single concept per test — the split that makes failures legible:

```ts
import { assert } from 'chai';

// Bad — three concepts, one test, a reassigned subject.
describe('AwesomeDate', () => {
  it('handles date boundaries', () => {
    let date: AwesomeDate;

    date = new AwesomeDate('1/1/2015');
    assert.equal('1/31/2015', date.addDays(30));

    date = new AwesomeDate('2/1/2016');
    assert.equal('2/29/2016', date.addDays(28));

    date = new AwesomeDate('2/1/2015');
    assert.equal('3/1/2015', date.addDays(28));
  });
});

// Good — one concept each, and `const` instead of a reassigned `let`.
describe('AwesomeDate', () => {
  it('handles 30-day months', () => {
    const date = new AwesomeDate('1/1/2015');
    assert.equal('1/31/2015', date.addDays(30));
  });

  it('handles leap year', () => {
    const date = new AwesomeDate('2/1/2016');
    assert.equal('2/29/2016', date.addDays(28));
  });

  it('handles non-leap year', () => {
    const date = new AwesomeDate('2/1/2015');
    assert.equal('3/1/2015', date.addDays(28));
  });
});
```
- **What it demonstrates**: `let date` reassigned three times is the tell. Each subject wants its
  own `it()` — and once split, each gets a `const`, which is ch04's immutability rule arriving
  for free.

Names that reveal intention:

```ts
// Bad — the failure output is a date and a verb.
describe('Calendar', () => {
  it('2/29/2020', () => { /* ... */ });
  it('throws', () => { /* ... */ });
});

// Good — the failure output is a sentence about behaviour.
describe('Calendar', () => {
  it('should handle leap year', () => { /* ... */ });
  it('should throw when format is invalid', () => { /* ... */ });
});
```

## Reference Tables

| Suite symptom | Broken F.I.R.S.T. letter | Likely fix |
|---|---|---|
| Nobody runs them locally | **F**ast | isolate from I/O, network, sleeps |
| Green alone, red in a full run (or vice versa) | **I**ndependent | remove shared mutable state / fixture order |
| Green locally, red in CI | **R**epeatable | remove environment, clock and locale assumptions |
| Someone must read the log to judge it | **S**elf-Validating | assert the thing you were eyeballing |
| Writing the test is harder than the feature | **T**imely | inject dependencies (ch06 DIP); write test first |

| Test-name smell | Rewrite as |
|---|---|
| `it('2/29/2020')` (the data) | `it('should handle leap year')` (the behaviour) |
| `it('throws')` (the mechanism) | `it('should throw when format is invalid')` (the trigger) |
| `it('works')` | name the one concept it asserts |

## Worked Example
**The three laws of TDD run once, in TypeScript** — including the compilation-failure step,
which is the part unique to a typed language.

Goal: `AwesomeDate#addDays`.

**Law 2, iteration 1 — write only enough test to fail.** In TypeScript, this is enough:

```ts
it('handles 30-day months', () => {
  const date = new AwesomeDate('1/1/2015');
  assert.equal('1/31/2015', date.addDays(30));
});
```

`AwesomeDate` does not exist. `tsc` fails. **That is a failing test** — law 2 says so
explicitly. No assertion needed to be evaluated; the red step is the type error.

**Law 1 + 3, iteration 1 — write only enough production code to pass that one test:**

```ts
class AwesomeDate {
  constructor(private readonly value: string) {}
  addDays(days: number): string { return '1/31/2015'; }   // sufficient. Nothing more.
}
```

This looks absurd, and it is *supposed* to: law 3 forbids more. The hardcoded return is a
placeholder that the next failing test will delete.

**Law 2, iteration 2 — the next concept, as its own `it()` (single concept per test):**

```ts
it('handles leap year', () => {
  const date = new AwesomeDate('2/1/2016');
  assert.equal('2/29/2016', date.addDays(28));
});
```

Red again — the hardcode returns the wrong string. Now law 3 permits real arithmetic, because
only real arithmetic passes both tests.

**Why it works**: each law bounds one step, so you never write untested production code and never
write a test bigger than the code that will satisfy it. The hardcoded intermediate is not
sloppiness — it is the proof that the *second* test earned the real implementation.

**Why each test got its own `it()`**: had both assertions lived in one block, the second failure
would have been hidden behind the first, and the red→green cycle would have stopped telling you
which concept you were working on.

**Failure mode**: the laws are strict about *order*, not about design. TDD does not stop you
building an untestable class — if `addDays` needed a clock or a DB, law 1 would have you inject
it (ch06 DIP) or you'd be writing integration tests and calling them units.

## Key Takeaways
1. **Testing is more important than shipping** — no tests means no confidence you didn't break
   something.
2. Target **100% statement and branch coverage** with a real coverage tool; "adequate" is your
   team's call, but coverage goals are met **before launching or refactoring**.
3. **The three laws of TDD**: no production code without a failing test; no more test than
   suffices to fail (**compilation failures count**); no more code than passes that one test.
4. **F.I.R.S.T.** — Fast, Independent, Repeatable, Self-Validating, Timely. Use the letters to
   name what's wrong with a painful suite.
5. **One concept, one assert per test** — SRP for tests. A reassigned subject is the tell.
6. **Name tests after behaviour, not data** — the name is the first thing you read when it fails.
7. **No excuse for skipping tests**: JS/TS frameworks with typings support are plentiful; pick
   one the team likes and test every new module.
8. Hard-to-write tests are a **design** signal, not a testing one.

## Connects To
- **Ch 6 (SOLID / DIP)**: injected abstractions are what make a unit testable in isolation —
  the mechanism behind F.I.R.S.T.'s *Timely*.
- **Ch 3 (Functions)**: the argument budget is justified *by testing* — "a combinatorial
  explosion where you have to test tons of different cases." Pure functions are the easiest unit.
- **Ch 2 (Variables)** and **Ch 11 (Comments)**: "the name should reveal its intention" is the
  same rule applied to tests; a well-named test needs no comment.
- **Ch 4 (Objects and Data Structures)**: `const` per test subject falls out of the single-
  concept split.
- **`clean-code-java` ch09 (Unit Tests)**: the fuller treatment — **the three laws in their
  original form**, F.I.R.S.T., **one assert per test** *with its stated softening* (one
  *concept* per test is the real rule), the **BUILD-OPERATE-CHECK** structure, domain-specific
  testing languages, and *"test code is just as important as production code."*
