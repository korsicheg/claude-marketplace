# Chapter 1: Introduction

## Core Idea
These are Robert C. Martin's *Clean Code* principles re-expressed in TypeScript: a guide to
**readable, reusable, and refactorable** software — explicitly **not a style guide**, and
explicitly **not a rule set to follow strictly**.

> *This chapter is genuinely thin* — it is a one-page framing note, not a content chapter.
> Its value is the licence-to-judge it grants, which calibrates how to read every other chapter.

## Frameworks Introduced
- **The 3 R's of software architecture**: code is good to the extent it is **R**eadable,
  **R**eusable, and **R**efactorable.
  - When to use: as the acceptance test for any refactor. If a change doesn't improve one of
    the three, you are rearranging, not improving.
  - How: name the R you are buying before you start. "This extraction buys refactorability
    because the switch becomes one dispatch point."
- **The wet-clay model of code**: every piece of code starts as a first draft and is chiselled
  into final form during peer review.
  - When to use: when you are tempted to perfect code before showing it, or to be harsh about
    a colleague's first draft.
  - How: ship the draft, then **"beat up the code instead"** of the author. The review is the
    shaping step, not a verdict.
- **Guidelines-as-touchstone**: use these rules to *assess* the quality of code you and your
  team produce, not to adjudicate it.
  - How: when a rule and a concrete situation conflict, the situation wins and you record why.

## Key Concepts
- **Style guide** — rules about layout and syntax (brace position, quote style). This guide is
  deliberately *not* one; automate that with ESLint/Prettier instead (see ch10).
- **Readable** — a later reader reconstructs intent without asking the author.
- **Reusable** — a unit can be lifted into a new context without dragging its neighbours along.
- **Refactorable** — a change can be made safely because its blast radius is knowable.
- **First draft** — working code that has not yet been shaped; the expected, normal output of
  a first pass.
- **Touchstone** — a reference standard used for comparison, not a gate.

## Mental Models
- **Think of these principles as a touchstone, not a linter.** A linter fails a build; a
  touchstone tells you how far from the ideal you are and lets you decide if the distance is
  paid for.
- **Use "not every principle has to be strictly followed" as real permission.** The guide says
  outright that **even fewer will be universally agreed upon**. Disagreement inside a team is
  an expected outcome, not a defect in the team.
- **Think of the craft as ~50 years old.** Architecture has had millennia to develop hard
  rules; software has not. Expect the rules to be provisional and expect to outgrow some.
- **Knowing the rules ≠ being good.** The guide states plainly that knowing these "won't
  immediately make you a better software developer, and working with them for many years
  doesn't mean you won't make mistakes."

## Anti-patterns
- **Treating the guide as a style guide**: it isn't one, and using it to argue brace placement
  wastes the time that ch10 tells you to spend on tooling instead.
- **Rule-lawyering a review**: citing a principle as an authority rather than arguing the
  concrete cost to readability/reusability/refactorability. The guide grants the author the
  right to disagree.
- **Perfectionism on a first draft**: refusing to open a PR until the code is clean. The clay
  is meant to be shaped *in review*.
- **Beating yourself up for first drafts that need improvement**: named and rejected in the
  source. Beat up the code.

## Worked Example
The source's own framing, applied to a review comment. Same objection, two ways:

```ts
// The code under review
function createMenu(title: string, body: string, buttonText: string, cancellable: boolean) {
  // ...
}
```

**Rule-lawyered (what the Introduction warns against):**
> "Clean Code says 2 arguments max. This violates it. Please fix."

Cites authority, asserts a threshold as a law, gives the author nothing to weigh.

**Touchstone-style (what the Introduction asks for):**
> "Four positional args means a caller writes `createMenu('Foo', 'Bar', 'Baz', true)` — at the
> call site nothing says what `true` is, and testing this needs 2⁴ combinations of arg order to
> feel safe. An options object buys **readability** at the call site and drops the arg-order
> test surface. Worth it here? If `cancellable` is the only one that ever varies, maybe just
> split the function instead."

Names the concrete cost, names which R it buys, and leaves the decision with the author —
including the possibility that the reviewer's suggestion is the wrong fix. That is what
"touchstone by which to assess" means in practice.

## Key Takeaways
1. The target is **readable, reusable, refactorable** — not "compliant".
2. This is **not a style guide**. Formatting is a tooling problem (ch10), not a judgement problem.
3. The rules are **guidelines with judgement attached**; the source says not all of them are
   even universally agreed upon.
4. **First drafts are supposed to need work.** Review is the shaping step.
5. Argue concrete costs, not rule citations. A principle is evidence, not a verdict.
6. Every rule in the following chapters inherits this licence to be overridden with a reason —
   and several chapters (duplication in ch03, `type` vs `interface` in ch04, inheritance in
   ch05, formatting in ch10) state their own exceptions explicitly.

## Connects To
- **Ch 3 (Functions)**: "Remove duplicate code" carries the clearest stated exception — bad
  abstractions can be worse than duplication — which is this chapter's licence in action.
- **Ch 10 (Formatting)**: "*DO NOT ARGUE* over formatting" is the direct consequence of this
  not being a style guide.
- **`clean-code-java` ch01 + ch17**: Martin's original framing and the closing statement that
  *"clean code is not written by following a set of rules"* — the same point, stated harder.
- **The Boy Scout Rule** (`clean-code-java` ch01): the incremental-improvement habit that the
  wet-clay model implies but this chapter never names.
