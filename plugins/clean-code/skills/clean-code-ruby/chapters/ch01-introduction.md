# Chapter 1: Introduction

## Core Idea
Robert C. Martin's *Clean Code* principles, adapted for Ruby: "a guide to producing readable, reusable, and refactorable software in Ruby." Explicitly **not a style guide**, and explicitly a **port** — the maintainer warns up front that "the examples are largely ported over from JavaScript so they may not be idiomatic."

## Frameworks Introduced
- **The 3 Rs (readable, reusable, refactorable)**: the stated quality standard for every rule in the guide.
  - When to use: as the tie-breaker when two designs both work. If a change improves none of the three, it's taste, not cleanliness.
  - How: name which R a proposed change improves before defending it.
- **Guidelines, not laws**: "Not every principle herein has to be strictly followed, and even fewer will be universally agreed upon. These are guidelines and nothing more."
  - When to use: whenever a rule collides with a real constraint — a framework's conventions (Rails, ActiveRecord), a performance budget, a deadline.
  - How: override deliberately, with a stated reason. The guide offers itself as "a touchstone by which to assess the quality of the Ruby code that you and your team produce", not a gate.
- **Wet clay — first drafts are expected**: "Every piece of code starts as a first draft, like wet clay getting shaped into its final form." Imperfections are chiselled away in peer review. "Don't beat yourself up for first drafts that need improvement. Beat up the code instead!"
  - When to use: in code review, and when deciding whether a draft is shippable.
  - How: review the code, not the author; expect the second pass.
- **The ported-from-JavaScript caveat**: the README's own note — examples "may not be idiomatic", and readers are invited to report non-idiomatic Ruby as an issue.
  - When to use: whenever an example's *shape* looks odd for Ruby (a `self` returned from `initialize`, a constant named `INITIAL_VALUE = 0`).
  - How: take the **principle** from the rule and the **idiom** from Ruby. Where they conflict, the principle wins and the example is the thing to fix.

## Key Concepts
- **Readable** — a reader can reconstruct intent without running the code or asking the author.
- **Reusable** — the unit can be called from a second site without modification.
- **Refactorable** — the unit can be changed without a cascade of edits elsewhere.
- **Not a style guide** — indentation, quotes, and line length are delegated to a formatter; the guide names RuboCop (Ch 10).
- **Adaptation lineage** — "Inspired by clean-code-javascript" (Ryan McDermott), itself derived from Martin's book.
- **Collective experience** — the rules are "codified over many years of collective experience by the authors of *Clean Code*", not invented for this document.
- **A young craft** — "Our craft of software engineering is just a bit over 50 years old, and we are still learning a lot."

## Mental Models
- **Think of the rules as detectors, not commandments.** Nearly every downstream rule — two arguments or fewer, no flags, one level of abstraction, no `case` on a type — is a symptom test for the root rule in Ch 3: *methods should do one thing*.
- **The referee in Ruby is the test suite and the reviewer.** Where the JavaScript parent relies on discipline and the Python adaptation leans on `mypy`, this guide explicitly rejects hand-rolled type checks ("faux type-safety") and closes the loop with "Keep your Ruby clean, write good tests, and have good code reviews" (Ch 4). That puts more weight on Ch 8's coverage demand than in any typed sibling.
- **Duck typing is the substrate.** Ruby has no interfaces, so every abstraction in this guide — the `move` message in Ch 4, the `request` adapter in Ch 7, the `request_item` contract — is an **implicit contract**: the set of messages one object sends another.

## Anti-patterns
- **Treating the guide as a style guide**: it says outright it is not one. Spend formatting arguments on a RuboCop config, not on this document's authority.
- **Copying the examples verbatim as idiom**: the maintainer disclaims exactly this. Several snippets carry JavaScript habits (Ch 6's chainable `initialize`, Ch 3's `INITIAL_VALUE`).
- **Strict, unexamined application**: the guide pre-empts it — "guidelines and nothing more." Mechanical enforcement produces its own mess (Ch 4: "Bad abstractions can be worse than duplicate code").

## Reference Tables

| Property | Value | Notes |
|---|---|---|
| Language | Ruby, implied **2.4+** | Names Ruby 2.1 for required keyword arguments; its `sum` example needs `Array#sum` (2.4); no Ruby 3 features |
| Rails assumptions | `present?`, `blank?` | ActiveSupport methods used in Ch 4's conditional examples; not core Ruby |
| Test framework | RSpec | `describe` / `let` / `it` / `expect(...).to eq(...)` (Ch 8) |
| Coverage tool | Coveralls | "a good coverage tool" (Ch 8) |
| Formatter / linter | RuboCop | "Use one!" (Ch 10) |
| Gems named | Hamster (persistent collections), contracts.ruby (runtime contracts) | Ch 3, Ch 4 |
| Error reporting | stdlib `Logger`; Honeybadger as the third-party example | Ch 9 |
| Size | ~5,800 words, **37 rules** in 10 sections | 11 chapters in this skill (Methods split in two) |
| Licence | MIT | The `LICENSE` file's copyright line still reads "Ryan McDermott", carried over from the JavaScript parent |

## Worked Example
**Reading the table of contents as an artifact.** The README's own TOC shows the port's surgery:

```
  6. [SOLID](#solid)
  7. [Testing](#testing)
  9. [Error Handling](#error-handling)
  10. [Formatting](#formatting)
```

Item **8 is missing**. In the JavaScript parent, section 8 is *Concurrency* (callbacks → Promises → async/await). The Ruby port deleted it and kept the numbering. The same ledger applies rule by rule — JavaScript's 46 rules became Ruby's 37:

| Change | JavaScript parent | Ruby port |
|---|---|---|
| **Dropped** (9) | Concurrency ×2 (Promises, async/await); "Don't write to global functions" (prototype patching); "Don't over-optimize"; "Set default objects with Object.assign"; closure-based "private members"; "Prefer ES6 classes"; "Only comment business logic"; "Avoid positional markers" | — |
| **Reversed** (1) | "Use method chaining" | **"Avoid fluent interfaces"** (Ch 6) |
| **Replaced** (1) | "Don't ignore rejected promises" | **"Provide context with exceptions"** (Ch 9) |
| **Re-voiced** | argument objects; `!isNotX()`; `instanceof` | keyword arguments (Ch 3); `unless` (Ch 4); `is_a?` (Ch 4) |

**What it demonstrates**: what the port *omits* is as informative as what it says. Monkey-patching core classes — the Ruby analogue of JavaScript's prototype-patching rule — went out with that rule, and nothing replaced it. The Scope & Limits section of SKILL.md lists every such gap.

## Key Takeaways
1. Judge code on **readable, reusable, refactorable**; name which R a change improves.
2. These are **guidelines** — override with a stated reason, never by accident.
3. This is **not a style guide**; automate formatting with RuboCop (Ch 10).
4. The examples are **ported from JavaScript** and may not be idiomatic — keep the principle, fix the idiom.
5. Without a type checker, **tests and review are the enforcement mechanism**; that is why Ch 8 demands coverage.
6. Ruby's abstractions are **implicit contracts** — the messages an object answers. Every SOLID chapter builds on that.

## Connects To
- **Ch 3**: "Methods should do one thing" is the root rule the rest of the guide detects violations of.
- **Ch 4**: the "faux type-safety" argument and the closing "write good tests, and have good code reviews."
- **Ch 6**: the one rule that reverses the JavaScript parent.
- **Ch 7**: SOLID through duck typing and implicit contracts.
- **Ch 8**: coverage as the guarantee a dynamic language otherwise lacks.
- **clean-code-javascript** (ryanmcdermott): the parent document; the ledger above is the diff against it.
