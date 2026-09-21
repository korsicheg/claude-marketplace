---
name: clean-code-java
description: "Knowledge base from \"Clean Code: A Handbook of Agile Software Craftsmanship\" by Robert C. Martin et al. (Java examples). Use when writing or reviewing code and you need Uncle Bob's rules for naming, function size, comments (when NOT to write one), formatting, error handling, classes/SRP, unit tests/TDD, refactoring, and the smells-and-heuristics catalogue. Part of the clean-code skill family; for Python-specific idioms use clean-code-python, for TypeScript-specific idioms use clean-code-typescript, for JavaScript-specific idioms use clean-code-javascript instead. For any other language, including YAML, Terraform, SQL and Bash, use clean-code-universal."
---

<!-- argument-hint: [topic, framework name, heuristic tag like G30, or chapter number] -->

# Clean Code: A Handbook of Agile Software Craftsmanship
**Authors**: Robert C. Martin with Michael Feathers, Tim Ottinger, Jeff Langr, Brett Schuchert, James Grenning, Kevin Dean Wampler (Object Mentor)
**Source**: ~129,000 words · **Chapters**: 17 + Appendix A · **Generated**: 2026-09-18

## How to Use This Skill

- **Without arguments** — the core rules below are the working set for writing code.
- **With a topic** — ask about `comments`, `function length`, `error handling`, `SRP`; I read the relevant chapter first.
- **With a heuristic tag** — ask about `G30` or `N7`; see [ch17](chapters/ch17-smells-and-heuristics.md), the full 66-item catalogue.
- **With a chapter** — ask for `ch03`.
- **Fastest path while coding** — [cheatsheet.md](cheatsheet.md): thresholds, decision rules, tells.

---

## Core Rules for Producing Code

### Comments — the default is *don't*
**Comments are always failures.** Before writing one, try to delete it by improving the code:
a better function name, an explanatory variable, an extracted method. Then:

- **Never write**: redundant restatements of code, section markers inside functions, closing-brace comments, change logs, bylines, commented-out code (*"an abomination"* — delete it, source control remembers), mandated per-function Javadoc, HTML in comments, noise like `/** Default constructor. */`.
- **Only write**: legal headers, **intent** (why this decision), **warning of consequences**, **amplification** of something that looks inconsequential but isn't, TODOs with a stated plan, and public-API Javadoc.
- **The test**: *if a name requires a comment, the name does not reveal its intent* — rename instead.
- A section comment inside a function marks a **function waiting to be extracted**. A closing-brace comment means **shorten the function**.

### Functions
- **Small, then smaller.** Hardly ever 20 lines; 2–4 is the target. `if`/`while` bodies are one line — a call. **Indent depth ≤ 2.**
- **Do one thing** = every statement sits **exactly one level of abstraction below the function's name**. Verify with the TO-paragraph test: *"TO renderPage, we check X, then we do Y."*
- **Arguments**: 0 ideal, 1 good, 2 costly, 3 avoid, 4+ never. **No flag arguments** — split the function. **No output arguments** — change your own object's state.
- **Command Query Separation**: do something *or* answer something, never both.
- **`try` must be the first word in its function**, with nothing after `catch`/`finally`. Error handling is one thing.
- **Prefer exceptions to error codes.**
- **Kill duplication** — *"may be the root of all evil in software."* Even three duplicated lines are worth extracting.

### Names
- Length ∝ scope. Single letters only in tiny local scopes.
- Classes are **nouns**; methods are **verbs**; accessors use `get`/`set`/`is`.
- **One word per concept; never pun.** No `Manager`/`Processor`/`Super`/`Data`/`Info` in class names.
- **No encodings** — no Hungarian, no `m_`, no `I` on interfaces.
- **Replace magic numbers with named constants** — but `hourlyRate * 8` and `radius * Math.PI * 2` read better raw. π does not: nobody proofreads a literal they recognize.
- **The name must include the side effects.** `getOos()` that also creates it is `createOrReturnOos`.

### Error handling
- **Never return null; never pass null.** Use a **Special Case object** or `Collections.emptyList()`. Code drowning in null checks has *too many*, not too few.
- **Prefer unchecked exceptions** in application code (checked ones are an OCP violation that cascades signature changes upward). Reserve checked for critical libraries.
- Every exception carries **the operation that failed and the failure type** — a stack trace can't tell you intent.
- **Wrap third-party APIs** and translate their many exception types into one of yours.

### Classes & design
- **SRP**: one, and only one, reason to change. Size is measured in **responsibilities**, not lines. If you can't name the class concisely, or can't describe it in ~25 words without "and"/"or"/"but", it's too big.
- **The extraction loop**: extract small functions → promote shared locals to fields → cohesion drops → **split the class**. Repeat. That loop is how good structure emerges.
- **Objects hide data and expose behavior; data structures do the opposite.** Choose by axis of change: new **types** → objects; new **operations** → procedures. **Never build a hybrid.** Don't auto-generate getters and setters.
- **Bury switches in an Abstract Factory** and dispatch polymorphically. ONE SWITCH per selection type.
- **DIP**: depend on injected abstractions. If it's hard to test, it's too coupled — testability is a design smell detector.
- **Apply OCP when a change actually arrives**, not speculatively.

### Formatting
- Files ~200 lines (500 max); lines ≤ 120. Blank lines between concepts, none inside a tightly related group.
- **Caller above callee**; related things vertically close. Instance variables at the top, locals near use, loop counters in the loop.
- Never collapse a scope to one line. **Don't column-align** — the urge to align means the list is too long, i.e. the class should be split.
- **The team's style wins over yours.** Encode it in the formatter.

### Tests
- **Test code is held to production standards of cleanliness** — efficiency is the *only* dimension where the standard differs. Dirty tests are worse than no tests: they get abandoned, then the production code rots.
- **Three Laws of TDD**: no production code without a failing test; no more test than suffices to fail; no more code than suffices to pass. ~30-second cycles.
- **Build-Operate-Check** structure; **one concept per test**, minimal asserts.
- **F.I.R.S.T.** — Fast, Independent, Repeatable, Self-Validating, Timely.

### Refactoring
- **Write it dirty, then clean it.** Nobody produces the final form in one pass — *"I don't write them that way to start. I don't think anyone could."*
- **Refactor in many tiny changes under green tests**, never a big-bang restructure. Add the new abstraction as a harmless skeleton, migrate one use at a time, fix any break before proceeding, and expect to reverse earlier steps.
- **Stop adding features** the moment each new case requires parallel edits in the same N places — that's a class trying to be born.
- **Boy Scout Rule**: every check-in leaves the code strictly better. **LeBlanc's Law**: *later equals never.*

### When rules conflict (Beck's four rules of simple design, in priority order)
**1. Runs all the tests → 2. No duplication → 3. Expresses intent → 4. Minimizes classes and methods.**
Rule 4 never overrides 1–3. Don't merge well-named functions just to have fewer, and resist dogma like "an interface for every class."

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-clean-code.md) | Clean Code | Boy Scout Rule, LeBlanc's Law, Beck's four rules, Primal Conundrum |
| [ch02](chapters/ch02-meaningful-names.md) | Meaningful Names | Intention-revealing names, scope-length rule, one word per concept, don't pun |
| [ch03](chapters/ch03-functions.md) | Functions | Small!, Do One Thing, Stepdown Rule, TO paragraphs, CQS, argument arity, DRY |
| [ch04](chapters/ch04-comments.md) | Comments | Good/bad comment catalogue, "comments are failures", explain yourself in code |
| [ch05](chapters/ch05-formatting.md) | Formatting | Newspaper metaphor, vertical openness/density/distance, Team Rules |
| [ch06](chapters/ch06-objects-and-data-structures.md) | Objects and Data Structures | Data/Object Anti-Symmetry, Law of Demeter, tell-don't-ask, DTO, hybrids |
| [ch07](chapters/ch07-error-handling.md) | Error Handling | Try-catch-first, unchecked exceptions, Special Case Pattern, don't return/pass null |
| [ch08](chapters/ch08-boundaries.md) | Boundaries | Learning tests, wrap/adapt, write the interface you wish you had |
| [ch09](chapters/ch09-unit-tests.md) | Unit Tests | Three Laws of TDD, Build-Operate-Check, testing DSL, dual standard, F.I.R.S.T. |
| [ch10](chapters/ch10-classes.md) | Classes | SRP, naming & 25-word tests, cohesion, OCP, DIP, the extraction loop |
| [ch11](chapters/ch11-systems.md) | Systems | Separate construction from use, DI/IoC, POJOs, cross-cutting concerns, no BDUF |
| [ch12](chapters/ch12-emergence.md) | Emergence | The four rules of simple design, reuse in the small, Template Method |
| [ch13](chapters/ch13-concurrency.md) | Concurrency | SRP for threads, limit shared data, execution models, testing threaded code |
| [ch14](chapters/ch14-successive-refinement.md) | Successive Refinement | Write dirty then clean, the Stop Rule, incrementalism |
| [ch15](chapters/ch15-junit-internals.md) | JUnit Internals | A 14-step heuristic-by-heuristic refactoring; analysis/synthesis split |
| [ch16](chapters/ch16-refactoring-serialdate.md) | Refactoring SerialDate | First make it work then make it right, coverage-driven bug hunting, review ethic |
| [ch17](chapters/ch17-smells-and-heuristics.md) | **Smells and Heuristics** | **The full catalogue: C1–C5, E1–E2, F1–F4, G1–G36, J1–J3, N1–N7, T1–T9** |
| [ch18](chapters/ch18-appendix-a-concurrency-ii.md) | Appendix A: Concurrency II | Atomicity, CAS, method-dependency bugs, four deadlock conditions, ConTest |

## Topic Index

- **Abstract Factory** → ch03, ch11, ch16 · **Adapter** → ch08
- **Arguments (count, flags, output)** → ch03, ch17 (F1–F3, G15)
- **Boy Scout Rule** → ch01, ch15, ch16
- **Boundaries / third-party code** → ch08, ch07
- **Classes (size, cohesion, SRP)** → ch10, ch12
- **Comments** → ch04, ch17 (C1–C5)
- **Concurrency** → ch13, ch18
- **Deadlock** → ch18, ch13
- **Dependency Injection / DIP** → ch10, ch11
- **Duplication / DRY** → ch03, ch12, ch17 (G5)
- **Error handling / exceptions** → ch07, ch03
- **Feature Envy** → ch06, ch17 (G14)
- **Formatting** → ch05, ch17 (G10, G24)
- **Functions** → ch03, ch17 (F1–F4, G30, G34)
- **Law of Demeter / train wrecks** → ch06, ch17 (G36)
- **Magic numbers** → ch17 (G25), ch02, ch16
- **Naming** → ch02, ch17 (N1–N7)
- **Null (returning, passing)** → ch07
- **Objects vs data structures** → ch06
- **OCP / SOLID** → ch10, ch11, ch07
- **Polymorphism over switch** → ch03, ch06, ch17 (G23)
- **Refactoring case studies** → ch14, ch15, ch16
- **Simple design (four rules)** → ch12, ch01
- **Systems / architecture** → ch11
- **Temporal coupling** → ch03, ch15, ch17 (G31)
- **Template Method / Strategy** → ch12, ch17 (G5)
- **Test coverage** → ch16, ch17 (T2, T8)
- **Unit tests / TDD** → ch09, ch12, ch16

## Supporting Files

- [cheatsheet.md](cheatsheet.md) — thresholds, decision rules, tells & smells, refactoring protocol, and the judgment calls the book explicitly allows
- [patterns.md](patterns.md) — every concrete technique with when/how/trade-offs
- [glossary.md](glossary.md) — all key terms with chapter references

## Related Skills — the clean-code family

- **`clean-code-typescript`** — the same principles adapted for TypeScript by labs42io, with
  TS-native material this book predates: `readonly`/`Readonly<T>`/`as const` immutability,
  `type` vs `interface`, discriminated unions instead of `instanceof` chains, generics,
  `enum`, destructured option objects, iterators/generators, `async`/`await`, the
  `Failable<R, E>` result type, and ESLint/Prettier for formatting. **Use it when the code
  in front of you is TypeScript**; the SOLID chapter there shows each principle in TS.
- **This skill (`clean-code-java`)** is the canonical source: it is the only one of the two
  with the full 66-item smells-and-heuristics catalogue (ch17), the long-form refactoring
  case studies (ch14–ch16), boundaries (ch08), systems (ch11), emergence (ch12), and the
  deep concurrency treatment (ch13, ch18). Reach for it for **rationale, thresholds, and
  the heuristic tags** even when writing TypeScript.
- **`clean-code-universal`** — the family's shared core, distilled from this book across its
  Java, TypeScript, JavaScript and Python adaptations, with **every rule tagged by tier**:
  Tier 1 assumes only that you can name something and run some verification, Tier 2 binds
  only where a specific construct exists (a callable, a subtype, an exception, a test
  runner), and Tier 3 is language idiom, named there only so it can be routed back to the
  sibling that owns it. **Use it for any language this family does not cover** — Go, Rust,
  C#, C++, Kotlin, Ruby, PHP, Swift, Scala — **and for configuration and
  infrastructure-as-code, which no sibling covers at all**: YAML (Kubernetes, Helm, CI
  pipelines), Terraform/HCL, SQL, Bash and Dockerfile.

---

## Scope & Limits

Covers the book only. Examples are Java (2008), and **Chapter 11 is dated** — its EJB2/EJB3
and Spring-XML specifics are historical; its principles are not. The heuristics are
**heuristics with judgment attached**, and Martin says so himself: *"Clean code is not
written by following a set of rules. You don't become a software craftsman by learning a
list of heuristics. Professionalism and craftsmanship come from values that drive
disciplines."* Where a rule has a stated exception, the chapter files record it.
No source images were read.
