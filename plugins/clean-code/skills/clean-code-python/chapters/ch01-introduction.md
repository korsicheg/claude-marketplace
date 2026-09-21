# Chapter 1: Introduction

## Core Idea
Robert C. Martin's *Clean Code* principles, adapted for Python: a guide to producing **readable, reusable, and refactorable** software. Explicitly **not a style guide** — it governs structure and design, not whitespace.

## Frameworks Introduced
- **The 3 Rs (readable, reusable, refactorable)**: the stated quality standard for every rule in the guide.
  - When to use: as the tie-breaker when two designs both "work". If a change improves none of the three, it's taste, not cleanliness.
  - How: name which of the three a proposed change improves. If you can't, don't make the change on cleanliness grounds.
- **Guidelines, not laws**: "Not every principle herein has to be strictly followed, and even fewer will be universally agreed upon."
  - When to use: whenever a rule collides with a real constraint (performance, a framework's API, a deadline).
  - How: override deliberately and state the reason. Never override by accident or by ignorance of the rule.

## Key Concepts
- **Readable** — a reader can reconstruct intent without running the code or asking the author.
- **Reusable** — the unit can be called from a second site without modification.
- **Refactorable** — the unit can be changed without a cascade of edits elsewhere.
- **Not a style guide** — formatting, line length, and quote style are out of scope; use a formatter and a linter for those.
- **Adaptation lineage** — derived from [clean-code-javascript](https://github.com/ryanmcdermott/clean-code-javascript) by Ryan McDermott, itself derived from Martin's book.
- **Collective experience** — the rules are "codified over many years of collective experience by the authors of *Clean Code*", not invented for this document.

## Mental Models
- **Think of the rules as detectors, not commandments.** Nearly every rule downstream ("no flags", "≤2 arguments", "one level of abstraction") is a *symptom test* for the single root rule in Ch 3: functions should do one thing.
- **Use the type checker as the referee.** This adaptation's distinguishing move: where the JavaScript original relies on discipline, the Python version repeatedly shows **mypy catching the violation mechanically**. Side effects (Ch 3) and LSP breaks (Ch 6) both surface as type errors. If a rule can be enforced by `mypy`, enforce it there rather than in review.
- **Python is also an OOP language** — when a cluster of functions keeps taking the same entity as its first argument, that entity wants to be a class with methods, properties, or instance attributes (Ch 2).

## Anti-patterns
- **Treating the guide as a style guide**: it says outright it is not one. Arguing formatting under its banner wastes the authority the structural rules earn.
- **Strict, unexamined application**: the text pre-empts this — these are guidelines. Mechanical enforcement without judgment produces its own mess (see Ch 9: "bad abstractions can be worse than duplicate code").
- **Assuming JavaScript advice transfers unchanged**: Python has dataclasses, `NamedTuple`, `TypedDict`, ABCs, generators, properties, and descriptors. The Python rules route through those, not through closures and prototypes.

## Reference Tables

| Property | Target version | Notes |
|---|---|---|
| Language | Python 3.7+ | Badge advertises 3.8+; one rule (`TypedDict`) is 3.8+ only |
| Type checker | `mypy` | Used throughout as the enforcement mechanism |
| Test runner | `pytest` | All README snippets are executed in CI via `conftest.py` |
| Scope | Structure & design | Not formatting — "This is not a style guide" |

## Worked Example
The guide's own repository demonstrates its central claim — that these rules are mechanically checkable. Its `requirements.txt` is exactly two lines:

```
pytest
mypy
```

Every Python block in the README is extracted and executed by `conftest.py` under `pytest`, and type-checked with `mypy`. This is why several "Bad" examples carry a `# type: ignore` pragma — without it, the *bad* code fails the project's own CI, which is the point being made. The side-effects example (Ch 3) spells the mechanism out:

```python
# MyPy will spot the problem, complaining about 'Incompatible types in
# assignment: (expression has type "List[str]", variable has type "str")'
```

**What it demonstrates**: the guide does not merely assert its rules — it wires them to tooling that fails the build. Adopt the same posture: prefer a rule a checker can enforce over a rule that lives only in a review comment.

## Key Takeaways
1. Judge code on **readable, reusable, refactorable**. Name which R a change improves before defending it.
2. These are **guidelines**. Override them with a stated reason; never by accident.
3. This is **not a style guide** — automate formatting separately and keep this document's authority for structure.
4. **Prefer mechanical enforcement.** Where `mypy` can catch a violation, that's the right place for the rule.
5. Python's own features (dataclasses, ABCs, generators, properties) are the vehicle for these principles — don't transliterate Java or JavaScript solutions.
6. When several functions share an entity, reach for a **class**; the guide's "Even better" tier is usually object-oriented.

## Connects To
- **Ch 3**: "Functions should do one thing" is the root rule the rest of the guide detects violations of.
- **Ch 4–8**: SOLID, worked through Python's ABCs, mixins, and duck typing.
- **Ch 9**: DRY, plus the critical caveat that a bad abstraction beats no abstraction only sometimes.
- **clean-code-javascript**: the direct parent document; the Python version replaces closure-privacy and prototype advice with type hints and ABCs.
