---
name: clean-code-typescript
description: "Knowledge base from \"clean-code-typescript\" by labs42io — Robert C. Martin's Clean Code principles adapted for TypeScript. Use when writing or reviewing TypeScript and you need rules for naming, function arguments, SOLID worked in TS, type vs interface, readonly/Readonly/as const immutability, unions instead of instanceof, generators, enums, async/await and Promise.all, Error handling and Failable result types, ESLint/Prettier formatting, import organization, and when NOT to write a comment. Part of the clean-code skill family; for Python-specific idioms use clean-code-python, for JavaScript-specific idioms use clean-code-javascript, for the original book (Java examples, plus the smells catalogue and refactoring case studies) use clean-code-java. For any other language, including YAML, Terraform, SQL and Bash, use clean-code-universal."
---

<!-- argument-hint: [topic, principle name like LSP, or chapter number] -->

# clean-code-typescript
**Source**: [labs42io/clean-code-typescript](https://github.com/labs42io/clean-code-typescript) — principles from Robert C. Martin's *Clean Code*, adapted for TypeScript; inspired by ryanmcdermott/clean-code-javascript
**Size**: ~10,300 words · **Chapters**: 11 · **Generated**: 2026-09-18

## How to Use This Skill

- **Without arguments** — the core rules below are the working set for writing TypeScript.
- **With a topic** — ask about `immutability`, `type vs interface`, `Promise.all`, `SOLID`; I read the relevant chapter first.
- **With a principle** — ask about `LSP` or `DIP` → [ch06](chapters/ch06-solid.md).
- **With a chapter** — ask for `ch03`.
- **Fastest path while coding** — [cheatsheet.md](cheatsheet.md): thresholds, decision rules, tells.

**Not a style guide.** Formatting is a tooling problem (ESLint + Prettier), not a judgement one.
The source states outright that *"not every principle herein has to be strictly followed, and
even fewer will be universally agreed upon."* Treat these as a touchstone with judgement
attached; [cheatsheet.md](cheatsheet.md) lists the exceptions the source grants explicitly.

---

## Core Rules for Writing TypeScript

### Functions — one rule, many tells
**"Functions should do one thing" is by far the most important rule in software engineering.**
Everything below is a *detector* for violations of it:

- **Arguments: ≤2 ideal, 3 avoid, 4+ → a destructured options object** with a `type` alias. The
  stated reason is testing — each argument multiplies the case matrix combinatorially.
  Destructuring also gives named parameters, shows which properties are used, clones *primitive*
  values (**objects and arrays are NOT cloned**), and lets TS warn on unused properties.
- **No flag arguments** — a boolean parameter is two functions that got merged. Split them.
- **One level of abstraction per body.** Orchestration (`tokenize(code)` then `parse(tokens)`)
  never mixes with mechanics.
- **`instanceof` chain → union type** with one shared method. **`switch` on a type field →
  subclass + override.** In TypeScript, type checking at runtime is a type-system failure.
- **Clone, don't mutate** an argument: `return [...cart, item]`, not `cart.push(item)`. Centralize
  unavoidable side effects in **one** service. Cloning big objects costs — see `immutable-js`.
- **Prefer functional pipelines** (`filter`/`map`/`reduce`) to loops; each step gets a name.
- **Encapsulate conditionals** into named predicates; prefer positive over negative conditionals.
- **Never write to globals** — subclass (`class MyArray<T> extends Array<T>`), never
  `Array.prototype.x = ...`; prototype writes clash silently and surface in production.
- **Delete dead code** (git remembers). **Don't over-optimize** — the engine already does.
- **Use generators** (`function*` + `yield`, consumed by `for-of`) when the *consumer* should
  decide how many items to take.

**Duplication, with its stated exception**: deduplicate within a domain; *"bad abstractions can
be worse than duplicate code."* When two implementations **in different modules live in
different domains** and merely resemble each other, **keep both copies** — extraction creates an
indirect dependency between them. The test is not "is this duplicated" but **"do these share a
reason to change?"**

### Names
- Names differ to tell the reader **what the difference offers** — `(value, left, right)`, never
  `(a1, a2, a3)`.
- **If you can't pronounce it, rename it.** **One word per concept** — `getUser()`, not
  `getUserInfo`/`getUserDetails`/`getUserData`.
- Every meaningful literal becomes a **`SNAKE_CASE` named constant** (`MILLISECONDS_PER_DAY`, not
  `86400000`); let ESLint find them.
- **Don't repeat the type's name in its fields** — `car.make`, not `car.carMake`. Test the name
  **at the use site**, not in the declaration.
- **Destructuring is free naming**: `for (const [id, user] of users)`.
- **Default arguments over short circuiting** — `count: number = 10` puts the default where
  callers read it.
- **`enum` when you care that values are *distinct*, not what they literally are.**

### Types & immutability — the TypeScript-specific core
- **`type` for unions/intersections; `interface` for `extends`/`implements`.** The source says
  there is **no strict rule** beyond that — pick one and be consistent.
- **The immutability ladder**: `readonly prop` → `Readonly<T>` → `ReadonlyArray<T>` /
  `readonly T[]` → **`as const`**.
  - `const array: number[]` still lets **`push()`** through — use `ReadonlyArray<T>`.
  - Plain `readonly` does **not** protect a literal you **return** — only `as const` does
    (`return { value } as const`). This is the rung people miss.
  - **All of it is erased at runtime.** It protects your code from itself; it is not a freeze.
- **Default to `private readonly` parameter properties**: `constructor(private readonly radius: number) {}`.
  `public` is TS's default and usually the wrong one.
- **Accessors on objects with behavior**: a `get`/`set` pair means a new validation rule changes
  **one setter and no callers**. Skip them on plain data bags.

### SOLID, with its TS tell and fix
| Principle | Rule | Tell | Fix |
|---|---|---|---|
| **SRP** | one reason to change | class name needs "and" | extract a class, hold as field |
| **OCP** | open to extension, closed to modification | `instanceof` chain in a consumer | `abstract` method + subclasses; new variants edit **zero** existing code |
| **LSP** | subtypes substitute cleanly | override maintains a private invariant → `.setWidth(4).setHeight(5).getArea()` returns **25, should be 20** | abstract **sibling** parent; make them peers — fix the hierarchy, not the override |
| **ISP** | no client depends on what it doesn't use | `throw new Error('Fax not supported.')` | split into role interfaces (`Printer`/`Fax`/`Scanner`) |
| **DIP** | both levels depend on abstractions; abstractions don't depend on details | `private readonly f = new XmlFormatter()` | `interface` + constructor injection; IoC container = **InversifyJS** |

**DIP ≠ DI.** DI is the usual mechanism. And the second half of DIP is the half people skip: the
abstraction must be shaped by **what the consumer needs**, not extracted mechanically from the
concrete class.

### Classes
- **Size is measured in responsibilities, not lines.**
- **Group methods by which field they touch — that grouping *is* the class boundary.** The tell
  for low cohesion: a caller forced to construct a dependency it will never use.
- **Composition is the default.** Inherit only if **all three**: is-a (say it aloud — "an employee
  *has* tax data" settles it), real base-class reuse, *and* you want base changes to propagate.
- **Return `this`** (not the class name — `this` survives subclassing) from mutators to chain;
  one terminal method (`build()`) ends the chain.

### Async
- **Ladder: callbacks → promises → `async`/`await`.** `async`/`await` is the default; the concrete
  win over callbacks is **one error path instead of one per nesting level**.
- **Promisify, don't hand-wrap**: `util.promisify`, `pify`, `es6-promisify`.
- **Consecutive `await`s that don't consume each other's results are accidental serialization** —
  use one `Promise.all` and latency becomes the *max*, not the sum. But `Promise.all` **fails
  fast** on the first rejection and **does not cancel** the rest.
- **`Promise.race` for "first settled"** — that's how you build a timeout.

### Errors
- **Thrown errors are a good thing.** **Always `new Error(...)`**, never a string — a string has
  no **`stack`** and confuses whoever catches it upstream. Same for `Promise.reject`.
- **A `try/catch` is a claim that an error may occur** — so an empty `catch` contradicts itself,
  and **`console.log(error)` is not handling** (it "can get lost in a sea of things printed to
  the console"). Use a real logger **and a code path**.
- **Never leave a rejection unhandled.**
- **`Failable<R, E>`** = `{ isError: false, value: R } | { isError: true, error: E }` puts failure
  in the *signature* so the compiler forces the caller to narrow. Cost: it doesn't propagate —
  every layer unwraps and rewraps, and there's no stack unless `E` carries one.

### Formatting & comments
- **DO NOT ARGUE over formatting** — *"a waste of time and money for engineers."* Commit
  **ESLint + Prettier** (`typescript-eslint`; migrate off TSLint with `tslint-to-eslint-config`).
- **Case encodes category**: `PascalCase` types · `camelCase` values/members · `SNAKE_CASE` constants.
- **Newspaper rule — the one thing no linter does for you**: public entry point first, each helper
  directly below its first caller.
- **`import type` for type-only imports** — erased at runtime, so it **breaks dependency cycles**.
  That's correctness, not style. Six blank-line-separated import groups; **path aliases** kill
  `../../../`.
- **A comment is an apology for code that didn't express itself.** Delete it by improving the
  code — the comment usually *contains the name you need*. No commented-out code, no journal
  comments, no `//////` banners (IDE folding does that). **`// TODO` is the one endorsed form**,
  and it is not an excuse for bad code.
  Note the author's own hedge: *"Good code **mostly** documents itself"* — **mostly** is
  italicized in the source. Each prohibition is scoped to a specific bad kind, and `// TODO`
  is positively endorsed; the source never claims comments are always illegitimate. What it
  does not do is *enumerate* the **why**-comment kinds — `clean-code-java` ch04 names them
  (intent, warning of consequences, amplification, legal headers) if you want that list.

### Tests
- **"Testing is more important than shipping."** Target **100% statement *and* branch coverage**
  with a real coverage tool, before launching a feature or refactoring one.
- **Three Laws of TDD**: no production code without a failing test; no more test than suffices to
  fail — **compilation failures are failures**, which in TS *is* the red step; no more production
  code than passes that one test.
- **F.I.R.S.T.** — Fast, Independent, Repeatable, Self-Validating, Timely. Use the letters to name
  what's wrong with a painful suite; "hard to write at all" is a **design** signal (inject
  dependencies), not a testing one.
- **One concept, one assert per test.** A reassigned `let subject` is the tell.
- **Name tests after behaviour, not data** — `'should handle leap year'`, not `'2/29/2020'`.

---

## Chapter Index

| # | Title | Key Content |
|---|-------|----------------|
| [ch01](chapters/ch01-introduction.md) | Introduction | 3 R's, wet-clay model, guidelines-as-touchstone *(thin — a framing note)* |
| [ch02](chapters/ch02-variables.md) | Variables | meaningful/pronounceable/searchable names, mental mapping, unneeded context, default args, `enum` for intent |
| [ch03](chapters/ch03-functions.md) | Functions | do one thing, argument budget, options objects, flags, side effects, duplication + its exception, unions over `instanceof`, generators, dead code |
| [ch04](chapters/ch04-objects-and-data-structures.md) | Objects and Data Structures | accessors, `private`/`protected`, the immutability ladder (`readonly`/`Readonly<T>`/`ReadonlyArray<T>`/`as const`), `type` vs `interface` |
| [ch05](chapters/ch05-classes.md) | Classes | size = responsibility, high cohesion/low coupling, composition over inheritance + the 3-condition test, method chaining with `this` |
| [ch06](chapters/ch06-solid.md) | SOLID | SRP, OCP, LSP (Square–Rectangle), ISP (role interfaces), DIP (constructor injection, InversifyJS) |
| [ch07](chapters/ch07-testing.md) | Testing | three laws of TDD, F.I.R.S.T., single concept per test, intention-revealing test names, coverage |
| [ch08](chapters/ch08-concurrency.md) | Concurrency | callbacks → promises → `async`/`await`, promisify, `Promise.all`/`race`/`resolve`/`reject` |
| [ch09](chapters/ch09-error-handling.md) | Error Handling | always `Error`, never swallow a catch or a rejection, `Failable<R, E>` |
| [ch10](chapters/ch10-formatting.md) | Formatting | don't argue/automate, ESLint configs, capitalization, newspaper rule, import groups + `import type`, path aliases |
| [ch11](chapters/ch11-comments.md) | Comments | comments as apology, no commented-out/journal/banner comments, `// TODO` |

## Topic Index

- **`as const` / const assertions** → ch04
- **`async`/`await`** → ch08, ch09
- **Callbacks / callback hell** → ch08
- **Capitalization / casing** → ch10, ch02
- **Classes (size, cohesion, coupling)** → ch05, ch06
- **Comments** → ch11, ch02, ch03
- **Composition vs inheritance** → ch05
- **Conditionals (avoid, encapsulate, negative)** → ch03, ch06
- **Coverage** → ch07
- **Dead code** → ch03, ch11
- **Dependency injection / DIP** → ch06, ch05
- **Duplication / DRY** → ch03, ch06
- **`enum`** → ch02
- **Error / throwing / rejecting** → ch09, ch08
- **ESLint / Prettier / TSLint migration** → ch10
- **`Failable<R, E>` / result types** → ch09, ch04
- **F.I.R.S.T.** → ch07
- **Flag arguments** → ch03
- **Function arguments** → ch03, ch07
- **Generators / iterators** → ch03
- **Getters and setters** → ch04
- **Immutability (`readonly`, `Readonly<T>`, `ReadonlyArray<T>`)** → ch04, ch03
- **`import type` / import organization** → ch10
- **`instanceof` / type checking** → ch03, ch06
- **ISP / role interfaces** → ch06
- **LSP / Square–Rectangle** → ch06
- **Magic numbers / named constants** → ch02, ch10
- **Method chaining / fluent interfaces** → ch05
- **Naming** → ch02, ch03, ch07, ch10
- **Newspaper rule / vertical ordering** → ch10
- **OCP** → ch06, ch03
- **Options objects / destructuring** → ch03, ch02
- **Path aliases / tsconfig `paths`** → ch10
- **Polymorphism over `switch`** → ch03, ch06
- **`private` / `protected` / parameter properties** → ch04, ch05
- **`Promise.all` / `Promise.race`** → ch08
- **Promisify** → ch08
- **Side effects / mutation** → ch03, ch04
- **SOLID** → ch06, ch03, ch05
- **SRP** → ch06, ch05, ch07
- **TDD (three laws)** → ch07
- **Testing** → ch07, ch06, ch03
- **`// TODO`** → ch11
- **`type` vs `interface`** → ch04, ch09
- **Union types** → ch04, ch03, ch09

## Supporting Files

- [cheatsheet.md](cheatsheet.md) — thresholds, if/then decision rules, decision trees, tells & smells, and the judgment calls the source explicitly allows
- [patterns.md](patterns.md) — every concrete technique with when/how/trade-offs
- [glossary.md](glossary.md) — all key terms with chapter references

## Related Skills — the clean-code family

- **`clean-code-java`** — Robert C. Martin's original *Clean Code* (17 chapters + Appendix A).
  Go there for what this source omits: the **66-item smells-and-heuristics catalogue** (G/N/F/T
  tags), the long-form **refactoring case studies**, **boundaries** (wrapping third-party code),
  **systems**, **emergence** (Beck's four rules of simple design), the deep **concurrency
  hazards** treatment (deadlock conditions, execution models), the **legitimate comment
  categories**, **never return/pass null** + Special Case objects, and harder function
  thresholds (**hardly ever 20 lines, 2–4 target, indent depth ≤ 2**, Command Query Separation).
- **Use this skill when the code in front of you is TypeScript**; reach for `clean-code-java`
  for **rationale, thresholds, and heuristic tags** — they apply regardless of language.
- **`clean-code-universal`** — the family's shared core, distilled from Martin's book across
  its Java, TypeScript, JavaScript and Python adaptations, with **every rule tagged by
  tier**: Tier 1 assumes only a name and some verification you can run, Tier 2 binds only
  where a specific construct exists, and Tier 3 — the TS idiom this skill owns, `as const`
  and the rest — is named there only so it can be routed back here. **Use it for any
  language the family does not cover** — Go, Rust, C#, C++, Kotlin, Ruby, PHP, Swift, Scala
  — **and for configuration and infrastructure-as-code, which no sibling covers at all**:
  YAML (Kubernetes, Helm, CI pipelines), Terraform/HCL, SQL, Bash and Dockerfile.

---

## Scope & Limits

Covers this source only — a ~10,300-word community guide, **not the book**. It is far shorter
than Martin's *Clean Code* and omits most of it; where a rule here is terser, `clean-code-java`
has the fuller version, and each chapter's "Connects To" names the specific gap.

Two things to know before applying it literally:
- **The comments chapter is terse rather than absolutist.** It hedges (*"Good code **mostly**
  documents itself"*) and endorses `// TODO`, but it only names *what*-comments as targets and
  never enumerates the legitimate **why**-comment kinds. `clean-code-java` ch04 has that list.
- **Some examples are dated or imprecise.** `abstract async` (ch06's OCP example) is not valid
  TypeScript; the `request` library used in ch08 is deprecated; ch11's `Date.now` is missing its
  call parentheses. The *principles* hold — copy the shape, not the snippet verbatim.

Judgment is explicitly reserved on formatting, `type` vs `interface`, cross-domain duplication,
and maximal cohesion. No source images were read.
