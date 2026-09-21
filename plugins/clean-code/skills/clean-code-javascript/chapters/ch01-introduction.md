# Chapter 1: Introduction

## Core Idea
These are Robert C. Martin's *Clean Code* principles adapted to JavaScript — guidelines for producing **readable, reusable, and refactorable** software, not a style guide and not hard rules.

## Frameworks Introduced
- **The 3 Rs of software architecture**: code quality is judged on whether it is Readable, Reusable, and Refactorable.
  - When to use: as the acceptance test for any refactor — if a change improves none of the three, it is taste, not cleanliness.
  - How: ask of each change (1) can a new reader follow it? (2) can another module call it? (3) can I change it without touching callers?
- **Guidelines, not laws**: "Not every principle herein has to be strictly followed, and even fewer will be universally agreed upon."
  - When to use: whenever a rule in this guide collides with a real constraint (performance, framework idiom, team convention).
  - How: treat each rule as a default you may override with a stated reason — not as a lint error to satisfy blindly.
- **The wet-clay model of code**: every piece of code starts as a first draft, like wet clay getting shaped into its final form; imperfections are chiselled away in peer review.
  - When to use: when reviewing your own or others' first drafts.
  - How: expect a draft to be rough; make the review the shaping step, not the shaming step.

## Key Concepts
- **Readable** — a reader who did not write the code can follow its intent without running it.
- **Reusable** — the unit can be called from a second place without modification.
- **Refactorable** — internals can change without breaking callers.
- **Touchstone** — these guidelines are a standard for *assessing* code quality, not a mechanical checklist.
- **Not a style guide** — formatting is explicitly out of scope; automate that (see Ch 10).

## Mental Models
- **Think of code as wet clay, not carved stone.** A first draft is *supposed* to need reshaping. Ship the draft to review; let review chisel it.
- **Use "beat up the code, not yourself."** Criticism attaches to the artifact, never the author. This is the review norm the guide asks for.
- **Think of the craft as ~50 years old.** Architecture has millennia of settled rules; software does not. Hold every rule here with proportional humility.
- **Knowing ≠ being good.** Reading these guidelines doesn't make you a better developer, and years of practice won't make you mistake-free. The value is in application and review, not recall.

## Anti-patterns
- **Treating the guide as a style guide**: it isn't one — arguing over quotes and tabs here misses the point entirely (Ch 10 says automate that instead).
- **Dogmatic enforcement**: applying a rule with no regard for context produces code that satisfies the letter of the guide and none of the 3 Rs.
- **Perfectionism on first drafts**: refusing to share code until it's clean removes the peer review step that actually makes it clean.
- **Expecting universal agreement**: "even fewer will be universally agreed upon" — demanding consensus on every rule stalls teams.

## Worked Example
The guide's own framing, applied as a review conversation:

> **Reviewer:** "This function is doing three things and the middle one is a database call."
>
> **Author (wrong response):** "Sorry, I'm bad at this."
> **Author (guide's response):** "Agreed — the draft got away from me. Splitting the lookup out."

The distinction is the whole cultural point of the introduction: the code took the hit, not the person. The author then reshapes (Ch 3, *Functions should do one thing*) rather than defending the draft.

Applied as an assessment, the same snippet against the 3 Rs:

| Question | Before split | After split |
|---|---|---|
| Readable? | No — intent buried in a loop | Yes — `emailActiveClients` names itself |
| Reusable? | No — the filter is welded in | Yes — `isActiveClient` is callable alone |
| Refactorable? | No — changing the filter edits the loop | Yes — filter changes in one place |

Three "no"s becoming three "yes"es is what justifies the refactor. If the answers hadn't changed, the change would have been taste.

## Key Takeaways
1. Judge code by **readable, reusable, refactorable** — not by whether it matches a rule in a list.
2. These are **guidelines**, deliberately non-universal; override them with a stated reason, never by accident.
3. This is **not a style guide** — automate formatting and stop arguing about it (Ch 10).
4. First drafts are supposed to be rough; peer review is the shaping step.
5. **Beat up the code, not the coder** — criticism attaches to the artifact.
6. The rules are codified collective experience from *Clean Code*, adapted for JavaScript — not laws derived from first principles.

## Connects To
- **Ch 3 (Functions)**: "Functions should do one thing" is called the single most important rule — the introduction's humility does not extend to that one.
- **Ch 10 (Formatting)**: explicitly discharges the "this is a style guide" reading — DO NOT ARGUE over formatting.
- **Robert C. Martin, *Clean Code***: the source these principles are adapted from; see the `clean-code-java` skill for the original Java treatment.
- **clean-code-typescript**: the sibling adaptation; Ch 3's "avoid type-checking (part 2)" points at TypeScript directly.
