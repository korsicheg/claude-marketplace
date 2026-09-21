---
name: clean-code-javascript
description: "Knowledge base from \"clean-code-javascript\" by Ryan McDermott — Robert C. Martin's Clean Code principles adapted for JavaScript. Use when writing or reviewing JavaScript and you need rules for naming and magic numbers, function arguments and the do-one-thing rule, flag parameters, side effects and argument mutation, replacing conditionals with polymorphism, closure privacy and getters/setters, ES6 classes and method chaining, composition over inheritance, SOLID in an untyped language, single-concept tests, callbacks vs Promises vs async/await, error handling, formatting, and when NOT to write a comment. Part of the clean-code skill family; for Python-specific idioms use clean-code-python, for TypeScript-specific idioms use clean-code-typescript, for the original book (Java examples, smells catalogue, refactoring case studies) use clean-code-java. For any other language, including YAML, Terraform, SQL and Bash, use clean-code-universal."
---

<!-- argument-hint: [topic, principle name like LSP, or chapter number] -->

# clean-code-javascript
**Source**: [ryanmcdermott/clean-code-javascript](https://github.com/ryanmcdermott/clean-code-javascript) — software engineering principles from Robert C. Martin's *Clean Code*, adapted for JavaScript
**Size**: ~7,400 words · 46 rules · **Chapters**: 11 · **Generated**: 2026-09-18

## How to Use This Skill

- **Without arguments** — load the core rules below for reference
- **With a topic** — ask about `side effects`, `LSP`, `async`, `comments`; I find and read the relevant chapter
- **With a chapter** — ask for `ch03`; I load that chapter file
- **Browse** — ask "what chapters do you have?" for the full index

When you ask about something not covered below, I read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

### The root rule
**Functions should do one thing.** The guide calls this "by far the most important rule in software engineering" — "If you take nothing else away from this guide other than this, you'll be ahead of many developers." Almost every other rule here is a *detector* for violating it: a flag parameter, a fourth argument, mixed abstraction levels, and a `switch` on a type all mean the function does more than one thing.

**Test**: if you can only describe it using "and", split it.

### The quality standard — the 3 Rs
Judge code on whether it is **readable, reusable, refactorable**. If a change improves none of the three, it's taste, not cleanliness. These are **guidelines, not laws** — "even fewer will be universally agreed upon." Override with a stated reason, never by accident. And this is explicitly **not a style guide**.

### Naming
- Make names **meaningful, pronounceable, searchable**. `yyyymmdstr` → `currentDate`.
- **One concept, one word** — `getUserInfo`/`getClientData`/`getCustomerRecord` → `getUser`. Synonym drift breeds duplicate implementations.
- Hoist every meaningful literal to a named constant: `setTimeout(blastOff, 86400000)` → `MILLISECONDS_PER_DAY`. Enforce with ESLint `no-magic-numbers`.
- No mental mapping (`l` → `location`), no repeated context (`car.carColor` → `car.color`).
- Prefer default parameters to `||` — but a default parameter fires only on `undefined`, while `||` also replaces `''`, `0`, `false`, `null`, `NaN`.

### Functions
- **≤2 arguments.** Three is avoidable; 4+ must become one destructured object — more arguments cause a combinatorial explosion of test cases. Signature destructuring clones **primitives** only; nested objects/arrays stay shared.
- **No flag parameters.** "Flags tell your user that this function does more than one thing." Split into `createFile` / `createTempFile`.
- **Never mutate arguments.** `return [...cart, item]`, not `cart.push(item)` — the guide's retry-purchase bug charges the user for an item they didn't confirm.
- **Centralize side effects**: one service per effect, "one and only one."
- **Never patch built-in prototypes** — `class SuperArray extends Array` instead of `Array.prototype.diff = ...`.
- **Remove duplication — but carefully**: "Bad abstractions can be worse than duplicate code."
- Prefer `reduce`/`map`/`filter` over accumulator loops. Delete dead code. Don't micro-optimize; the engine already did.

### Removing conditionals — escalation ladder
Compound `if` → **named predicate** · `!isNotX()` → **positive predicate** · `switch (this.type)` → **subclass per case** · `instanceof` chain → **consistent API** (`vehicle.move(...)`) · `typeof` guards on primitives → **use TypeScript**.

### Objects and classes
- Use **closures for real privacy** (`makeEmployee` returning methods over `name`): with a public field, `delete employee.name` breaks your own `getName()`.
- Accessors buy validation, logging, lazy loading, and freedom to change representation — use them when at least one applies.
- Prefer **small functions over classes** until objects get large and complex; then use **ES6 class syntax**, never the ES5 prototype ritual.
- `return this` from every method — including terminal ones like `save()` — to enable chaining.
- **Composition over inheritance.** Use `extends` only when all three hold: genuine **"is-a"** (not "has-a"), you reuse base-class code, and you *want* base changes to propagate. `class EmployeeTaxData extends Employee` is the canonical mistake.

### SOLID in an untyped language
JavaScript has **no interfaces** — abstractions are **implicit contracts** established by duck typing, so these are conventions you uphold, not rules a compiler enforces.

- **SRP** — "There should never be more than one reason for a class to change." Split by *reason to change*, not size.
- **OCP** — "open for extension, but closed for modification" (Meyer). If adding a variant edits an existing `if`, move the behavior onto the variant.
- **LSP** — subtypes must be substitutable without altering correctness. **If a subclass must override a method to preserve its own invariant, it isn't a subtype** — make both siblings under a shared parent (Square/Rectangle → `Shape`).
- **ISP** — don't force clients into fat settings objects; nest rare options and guard them.
- **DIP** — never `new` your collaborators inside a constructor; inject them, so V1→V2 is a call-site change. "Coupling … makes your code hard to refactor."

### Testing, async, errors, comments
- **"Testing is more important than shipping."** Target 100% of statements **and branches**; a framework isn't enough, add a coverage tool. TDD optional, coverage before launch/refactor non-negotiable. **One concept per test** — multi-concept tests mask later failures.
- **Callbacks → Promises → async/await is a one-way ladder.** The promise chain that was "Good" against callbacks is "Bad" against async/await. Use `async`/`await`/`try/catch`; swap in `request-promise`, `fs-extra`.
- **"Thrown errors are a good thing!"** The sin is catching without a plan. Never `catch (e) { console.log(e) }` — choose from `console.error`, `notifyUserOfError`, `reportErrorToService`, and prefer all three. `.catch()` gets identical treatment. If none of the three is warranted, delete the `try/catch`.
- **"DO NOT ARGUE over formatting"** — automate it. Keep human judgment for consistent capitalization and the **newspaper rule**: caller directly above callee.
- **"Comments are an apology, not a requirement."** Comment only genuine business-logic complexity — the *why*, never the *what*. No commented-out code, no journal comments (`git log` has it), no `////////` banners.

---

## Chapter Index

| # | Title | Key Rules |
|---|-------|-----------|
| [ch01](chapters/ch01-introduction.md) | Introduction | 3 Rs, guidelines not laws, wet-clay model |
| [ch02](chapters/ch02-variables.md) | Variables | searchable names, explanatory variables, mental mapping, default parameters |
| [ch03](chapters/ch03-functions.md) | Functions | do one thing, ≤2 args, flags, side effects, avoid conditionals, avoid type-checking |
| [ch04](chapters/ch04-objects-and-data-structures.md) | Objects and Data Structures | getters/setters, closure privacy |
| [ch05](chapters/ch05-classes.md) | Classes | ES6 classes, method chaining, composition over inheritance |
| [ch06](chapters/ch06-solid.md) | SOLID | SRP, OCP, LSP, ISP, DIP, implicit contracts |
| [ch07](chapters/ch07-testing.md) | Testing | testing > shipping, 100% coverage, single concept per test |
| [ch08](chapters/ch08-concurrency.md) | Concurrency | Promises not callbacks, async/await |
| [ch09](chapters/ch09-error-handling.md) | Error Handling | don't ignore caught errors, don't ignore rejected promises |
| [ch10](chapters/ch10-formatting.md) | Formatting | don't argue, consistent capitalization, newspaper rule |
| [ch11](chapters/ch11-comments.md) | Comments | business logic only, no dead/journal comments, no positional markers |

## Topic Index

- **Abstraction levels** → ch03
- **async / await** → ch08
- **Arguments (function)** → ch03
- **Callbacks** → ch08
- **Capitalization** → ch10
- **Chaining (method)** → ch05
- **Classes (ES6 vs ES5)** → ch05
- **Comments** → ch11
- **Composition vs inheritance** → ch05, ch06
- **Conditionals (avoiding)** → ch03
- **Coverage** → ch07
- **Dead code** → ch03, ch11
- **Default parameters** → ch02
- **Dependency injection / DIP** → ch06
- **Destructuring** → ch02, ch03
- **Duck typing / implicit contracts** → ch06
- **Duplication** → ch03
- **Error handling** → ch09, ch08
- **Flags (boolean parameters)** → ch03
- **Formatting / tooling** → ch10
- **Functional programming** → ch03
- **Getters and setters** → ch04
- **Globals (prototype patching)** → ch03
- **Immutability / cloning** → ch03
- **ISP** → ch06
- **LSP / Square-Rectangle** → ch06
- **Magic numbers** → ch02
- **Naming** → ch02, ch03
- **Newspaper rule** → ch10
- **OCP** → ch06
- **Polymorphism** → ch03, ch06
- **Privacy (closures)** → ch04
- **Promises** → ch08, ch09
- **Side effects** → ch03
- **SOLID** → ch06
- **SRP** → ch06
- **TDD** → ch07
- **Testing** → ch07
- **Type-checking / TypeScript** → ch03
- **3 Rs (readable, reusable, refactorable)** → ch01

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions and chapter refs
- [patterns.md](patterns.md) — 24 concrete refactoring techniques with trade-offs
- [cheatsheet.md](cheatsheet.md) — thresholds, decision rules, escalation ladders, tells & smells

## Related Skills — the clean-code family

- **`clean-code-java`** — Robert C. Martin's original *Clean Code*, the book itself (17 chapters + Appendix A). Go there for what this adaptation omits: the **66-item smells-and-heuristics catalogue**, the long-form **refactoring case studies**, boundaries, systems, emergence, the deep concurrency treatment, and the rationale and thresholds behind the rules here.
- **`clean-code-typescript`** — labs42io's adaptation, and where this guide's own "avoid type-checking (part 2)" rule points you: `readonly`/`Readonly<T>`/`as const` immutability, `type` vs `interface`, discriminated unions instead of `instanceof` chains, and the `Failable<R, E>` result type.
- **`clean-code-python`** — Rigel Di Scala's adaptation of this same document for Python: type hints instead of type-prefixes, the `dataclass`/`NamedTuple`/`TypedDict` parameter-object ladder, SOLID worked through ABCs and mixins, and mypy enforcing LSP mechanically.
- **`clean-code-universal`** — the family's shared core, distilled from Martin's book across its Java, TypeScript, JavaScript and Python adaptations, with **every rule tagged by tier**: Tier 1 assumes only that you can name something and run some verification, Tier 2 binds only where a specific construct exists, and Tier 3 is language idiom — prototype hygiene, closure privacy — named there only so it can be routed back here. **Use it for any language this family does not cover** — Go, Rust, C#, C++, Kotlin, Ruby, PHP, Swift, Scala — **and for configuration and infrastructure-as-code, which no sibling covers at all**: YAML (Kubernetes, Helm, CI pipelines), Terraform/HCL, SQL, Bash and Dockerfile.

---

## Scope & Limits

Covers the clean-code-javascript guide only (46 rules, ES5–ES2017 era JavaScript). It is **not a style guide** — it says so explicitly and tells you to automate formatting instead. It predates modern additions like `#private` class fields, optional chaining, and `??`, so where the text recommends closures for privacy or warns about `||` defaults, check whether a newer language feature now serves better.

Related skills: **clean-code-typescript** for TypeScript idioms (the guide's own "avoid type-checking (part 2)" points there); **clean-code-java** for Robert C. Martin's original book, including the smells-and-heuristics catalogue and refactoring case studies this adaptation omits.
