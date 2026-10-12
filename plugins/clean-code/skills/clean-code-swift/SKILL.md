---
name: clean-code-swift
description: "Knowledge base from \"clean-code-swift\" by Matheus Gois — Robert C. Martin's Clean Code principles adapted for Swift. Use when writing or reviewing Swift and you need rules for naming, if let over force unwraps, two-argument limits and struct parameter objects, defaults over an optional plus ??, flags and side effects, extensions on shared types, map/filter/reduce, enums and polymorphism over string switches and Any casts, getters/setters, method chaining, composition over inheritance, SOLID through protocols and init injection, one concept per XCTest, async/await, catch blocks that do more than print, SwiftLint formatting and comments. Part of the clean-code skill family; for the original book (Java examples, smells catalogue, refactoring case studies) use clean-code-java; for another language use its sibling (clean-code-typescript, -javascript, -python, -php, -csharp, -go, -ruby, -dart); for any other language, including Rust, Kotlin, C++, Scala, YAML, Terraform, SQL and Bash, use clean-code-universal."
---

<!-- argument-hint: [topic, principle name like DIP, or chapter number] -->

# clean-code-swift
**Source**: [MaatheusGois/clean-code-swift](https://github.com/MaatheusGois/clean-code-swift) — *Clean Code Adapted for Swift*, principles from Robert C. Martin's *Clean Code*; MIT; built on the Brazilian-Portuguese translation of Ryan McDermott's clean-code-javascript (README at commit `dea0629`)
**Author**: Matheus Gois (MaatheusGois) — sole contributor, 14 commits, Dec 2023 – Jul 2024; the LICENSE keeps the upstream line "Copyright (c) 2017 Ryan McDermott, Felipe Santos" | **Size**: ~8,850 words · 45 rules · **Chapters**: 11 | **Targets**: Swift 5.5+ (newest feature used: `async`/`await`; examples use Foundation, UIKit and XCTest; predates Swift 6) | **Generated**: 2026-10-12

## How to Use This Skill

- **Without arguments** — the core rules below are the working set for writing and reviewing Swift.
- **With a topic** — ask about `side effects`, `protocols`, `optionals`, `method chaining`, `async/await`; I read the relevant chapter first.
- **With a principle** — ask about `LSP` → [ch07](chapters/ch07-solid-srp-ocp-lsp.md), `DIP` → [ch08](chapters/ch08-solid-isp-dip.md).
- **With a chapter** — ask for `ch04`.
- **Fastest path while coding** — [cheatsheet.md](cheatsheet.md): thresholds, construct choices, tells.

**Read the source critically.** It was ported from a JavaScript guide and kept some JavaScript claims, and several Good snippets don't compile as written. [ch01](chapters/ch01-introduction.md) tabulates the JavaScript carryovers and ch02–ch11 each end with a **Source Caveats** section; the rules below are stated the way they hold in Swift.

---

## Core Frameworks & Mental Models

### The root rule
**Functions should do one thing** — "one of the most important principles in software engineering… If you remember nothing else from this guide, this principle will put you ahead of many developers." Every other function rule is a *detector*: a third argument, a `Bool` flag, mixed abstraction levels, a write to a global, a `switch` on a type string.

**Test**: if the description needs "and", split it.

### The quality standard
Judge code by whether it is **readable, reusable, refactorable**. These are guidelines — "even less are they a universal consensus" — and the guide is "not a style guide". First drafts are **wet clay**: "we carve out imperfections by reviewing with our peers." The guide pairs most Bad/Good snippets with named consequences (*Risk of Runtime Errors*, *Potential for Misuse*, *Improved Testability*); use them as review vocabulary.

### What makes the Swift adaptation distinct
- **Protocols carry SOLID.** ISP splits a fat `Styling` protocol into `StyleConfigurable` (data) and `StyleApplicable` (behaviour); DIP has `InventoryTracker` depend on a `RequesterProtocol` received in `init`; "avoid type checking" replaces `vehicle: Any` + `as?` with `vehicle: Vehicle`. Swift protocols are **explicit, compiler-checked contracts** — ignore the carried-over prose about "duck typing" and "implicit contracts". The guide never shows a protocol extension or a default implementation.
- **Value vs reference types are the implicit thread.** "Return a new value" runs through side effects (`addItemToCart(cart:item:) -> [CartItem]`), names (`-> (firstName:, lastName:)`) and pure objects (`refuel(amount:) -> Spaceship`); data bags are `struct`s (`MenuViewData`, `AppearanceConfig`), behaviour lives in classes. The guide's explanation — arrays "passed by reference" — is JavaScript's: a Swift `Array` is a **value** with copy-on-write, and the real hazards are global `var`s and shared class instances. It never discusses choosing `struct` vs `class`.
- **Optionals, `if let` and `guard`.** Bind a fallible result with `if let` and name its parts instead of force-unwrapping (*Risk of Runtime Errors*). Make a parameter **non-optional with a default** instead of `String?` + `??`. Exit early with `guard`. Model "has-a, maybe" as an optional stored property (`taxData: EmployeeTaxData?`).
- **Enums instead of strings.** Compare against cases (`car.engine == .v8`), and put per-case behaviour in an exhaustive `switch` inside the enum (`Role.description`). A `switch` on a type *string* with `default: return 0` is the Bad shape; an exhaustive switch over a closed enum is the guide's own Good one.
- **Argument labels** appear in every signature (`createMenu(viewData:)`, `addMonthToDate(month:date:)`) but no rule discusses them; the two-argument limit is stated without the readability labels add.
- **Access control**: `private` backing stores behind computed `get`/`set` properties, and `private` state behind chainable mutators. `private` is the only level the guide uses.
- **Errors and concurrency** get one rule each: every `catch` needs a plan ("`throw error` is a good thing"), and `async`/`await` replaces completion handlers. `Result` appears in one commentary line, never in code; there are no actors or `Sendable`.

### Naming
- Meaningful, pronounceable, no type tags: `currentDateStr` → `currentDate`. One vocabulary per concept: `getUserInfo`/`getClientData`/`getCustomerRecord` → `getUser`.
- Bind literals to searchable constants: `let millisecondsPerDay = 86400000` — lowerCamelCase, as the snippet writes it.
- No mental mapping (`l` → `location`); "Explicit is better than implicit." No repeated context (`User.userName` → `User.name`).

### Functions
- **≤2 arguments**; "avoid three whenever possible." At three, a `struct` parameter object with `let` properties and its free memberwise initializer. The stated reason is testing: each argument needs "detailed tests."
- **Name the action** (`addToDate` → `addMonthToDate`). **One level of abstraction** per function. **No `Bool` flags** — `createTemporaryFile` / `createPermanentFile`.
- **Remove duplication** — "more than one place to change something." Collapse near-duplicates into one function and push the differences into an `enum`.
- **Side effects**: take values, return values; for unavoidable effects, "Have one service that does it. One and only one." Return a new collection rather than mutating a shared one. Don't add generically named members (`diff`) to shared types like `Array`.
- **Functional style**: `map`/`filter`/`reduce` and `let` over accumulator loops; `$0` only in one-call closures.
- **Conditionals**: name compound conditions (`shouldShowSpinner`), state them positively (`isViewPresent`), and replace type switches with polymorphism — "When you have classes and functions that have `if` statements, you're telling your user that your function does more than one thing." Delete dead code; "It will still be safe in your version history."

### Objects and classes
- **Pure objects** don't share state: "They cannot be changed by other systems while they are being used." Changes return a new instance.
- **Getters and setters** for validation, encapsulation, logging and lazy loading — in Swift a computed property, so call sites never change.
- **Method chaining**: mutators `return self`; keep chained state `private`; validation is still your job.
- **Composition over inheritance**: inherit only when "is-a", base-class code reuse and base-wide change all hold; otherwise hold a property.

### SOLID
- **SRP** — "There should never be more than one reason for a class to change." Extract the second concern (`UserAuth`) and hold it.
- **OCP** — "open for extension but closed for modification." Each adapter implements `request(url:)`; no dispatcher comparing `adapter.name` strings (in the guide's Bad example one comparison string doesn't match its adapter's name, so that branch can never run).
- **LSP** — subtypes must work through the base type's callers "without getting incorrect results." Square/Rectangle becomes siblings under `Shape`, dimensions set once in `init`.
- **ISP** — "Clients should not be forced to depend on interfaces they do not use." One protocol per role.
- **DIP** — depend on abstractions; "Building our dependencies externally and injecting them, we can easily swap our request module."

### Testing, concurrency, errors
- "Tests are more critical than shipping." Aim for 100% statement and branch coverage; write tests for every new feature or module; **one concept per test method**.
- `async`/`await` turns a completion-handler pyramid into one `do` block. Write `func name() async` — the guide's `async func` doesn't compile.
- **Don't ignore caught errors**: `print` "is not much better because it can often get lost." Notify the user, report the error, or both — or let it propagate.

### Formatting and comments
- "The main idea is NOT to argue about formatting." Follow the Google Swift Style Guide; enforce with SwiftLint. Spaces, sparing blank lines, 80-character lines (the source's figure), consistent spacing.
- Comment only "non-obvious complexity" and business logic; delete commented-out code; avoid change markers — the guide includes `// MARK:`, a position many Swift codebases don't share.

---

## Chapter Index

| # | Title | Key Rules |
|---|-------|-----------|
| [ch01](chapters/ch01-introduction.md) | Introduction | 3 Rs, guidelines not laws, wet clay, consequence labels, JavaScript carryovers |
| [ch02](chapters/ch02-variables.md) | Variables | meaningful names, one vocabulary, searchable constants, `if let` explanatory variables, mental mapping, context |
| [ch03](chapters/ch03-functions.md) | Functions | do one thing, ≤2 args + `struct`, default arguments, names, abstraction levels, `enum` deduplication, flags |
| [ch04](chapters/ch04-side-effects-and-conditionals.md) | Side Effects, Shared Types and Conditionals | side effects, value semantics, extensions on `Array`, `map`/`reduce`, conditionals, `Any` + `as?`, dead code |
| [ch05](chapters/ch05-objects-and-data-structures.md) | Objects and Data Structures | pure objects, enums over strings, `private` backing stores |
| [ch06](chapters/ch06-classes.md) | Classes | method chaining, `@discardableResult`, composition over inheritance |
| [ch07](chapters/ch07-solid-srp-ocp-lsp.md) | SOLID: Single Responsibility, Open/Closed, Liskov Substitution | one reason to change, adapters vs string dispatch, Square/Rectangle |
| [ch08](chapters/ch08-solid-isp-dip.md) | SOLID: Interface Segregation and Dependency Inversion with Protocols | protocol per role, init injection |
| [ch09](chapters/ch09-testing-concurrency-errors.md) | Testing, Concurrency and Error Handling | coverage, one concept per test, `async`/`await`, caught errors |
| [ch10](chapters/ch10-formatting.md) | Formatting | don't argue, spaces, blank lines, line length, SwiftLint |
| [ch11](chapters/ch11-comments.md) | Comments | business-logic comments, no commented-out code, no change markers |

## Topic Index

- **3 Rs, guidelines not laws** → ch01
- **Abstraction levels** → ch03
- **`Any` / `as?`, type checking** → ch04
- **Arguments** (count, labels, `struct` parameter objects) → ch03
- **`async` / `await`, completion handlers, `Promise`** → ch09, ch07
- **Comments** (what vs why, commented-out code, `// MARK:`) → ch11
- **Composition vs inheritance** → ch06, ch07
- **Conditionals** (encapsulated, positive, polymorphic) → ch04
- **Dead code** → ch04
- **Default arguments** → ch03
- **DIP / dependency injection** → ch08
- **`@discardableResult`, method chaining** → ch06
- **Duplication** → ch03
- **Enums** → ch05, ch03, ch04
- **Error handling** (`do`/`try`/`catch`, caught errors) → ch09
- **Extensions on shared types** → ch04
- **Flags (`Bool` parameters)** → ch03
- **Formatting** (blank lines, line length, whitespace, SwiftLint, Google Swift Style Guide) → ch10
- **Functional style** (`map`/`filter`/`reduce`) → ch04, ch03
- **Getters and setters** (computed properties, `private`) → ch05, ch06
- **ISP / protocols** → ch08, ch04
- **JavaScript carryovers** → ch01, ch04, ch08
- **LSP** (Square/Rectangle) → ch07
- **Naming** (magic numbers, explanatory variables, mental mapping, one vocabulary, context) → ch02, ch03
- **OCP** (adapters, string dispatch) → ch07
- **Optionals** (`if let`, force unwrap, `guard`, `??`, optional properties) → ch02, ch03, ch04, ch06
- **Pure objects** → ch05
- **Side effects, global state** → ch04
- **SRP** → ch07
- **String comparisons** → ch05, ch07
- **Structs and value semantics** → ch03, ch04, ch05, ch08
- **Testing** (XCTest, coverage, one concept per test) → ch09
- **Tuples (labelled)** → ch04

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions and chapter refs
- [patterns.md](patterns.md) — 31 concrete refactoring techniques with trade-offs
- [cheatsheet.md](cheatsheet.md) — thresholds, construct choices, decision trees, tells & smells

## Related Skills — the clean-code family

- **`clean-code-java`** — Robert C. Martin's original *Clean Code*, the book itself, and canonical wherever the family disagrees. Go there for what this guide omits or only gestures at: the **66-item smells-and-heuristics catalogue**, the long-form **refactoring case studies**, boundaries, systems and construction, emergence, the deep concurrency treatment, the legitimate comment categories, null handling, and the harder function thresholds.
- **`clean-code-typescript`** — labs42io's adaptation; use it when the code is TypeScript. (This guide's "consider using TypeScript" line is a JavaScript carryover, not a reason to go there for Swift.)
- **`clean-code-javascript`** — Ryan McDermott's adaptation and this guide's ancestor; use it when the code is JavaScript, or to see a carried-over rule in its original form and the rules this port dropped (the bad-abstraction caveat, don't over-optimize, journal comments, rejected promises).
- **`clean-code-python`** — Rigel Di Scala's adaptation; use it when the code is Python.
- **`clean-code-universal`** — the family's shared core, with every rule tagged by tier; use it for languages with no sibling — Rust, Kotlin, C++, Scala — and for YAML, Terraform, SQL, Bash and Dockerfile.
- **`clean-code-php`** — use it when the code is PHP.
- **`clean-code-csharp`** — use it when the code is C#.
- **`clean-code-go`** — use it when the code is Go.
- **`clean-code-ruby`** — use it when the code is Ruby.
- **`clean-code-dart`** — use it when the code is Dart.

---

## Scope & Limits

**This covers one community guide, not the book**: a single ~8,850-word README with 45 rule headings (43 distinct rules; side effects and type checking each come in two parts) across 11 sections. Where a rule here is terse, `clean-code-java` has the fuller version.

**It is a port of a JavaScript guide, and it shows.** Some prose survives unchanged and is false for Swift: "Swift does not have types" and "consider using TypeScript" (type checking); arrays "passed by reference" (side effects); `Array.prototype` (extensions); "duck typing prevails" and "Swift doesn't have interfaces" (ISP, DIP); "AngularSwift"; `setTimeout`; JavaScript's "falsy" default-argument note; `Promise<Response>` with `.then`. ch01's carryover table and each later chapter's Source Caveats name them, and the rules in this skill are stated as they hold in Swift.

**Several Good snippets don't compile as written** — `class ExtendedArray: Array` (a struct), `async func`, a `Shape` without the `getArea()` its caller uses, an `AppearanceConfig` missing initializer arguments, and `Adapter`/`Airplane` bases that never declare the methods called through them — and two don't demonstrate their rule: the one-level-of-abstraction pair differs by one argument label, and the "Good" chained `Car` validates no more than the "Bad" one, though its commentary credits a `Result` the code lacks.

**What the source omits, or covers too thinly for modern Swift**:
- **Concurrency** is one rule: no actors, `Sendable`, `@MainActor`, structured concurrency (`async let`, task groups), cancellation, or Swift 6 data-race safety. It dates `async`/`await` to "iOS 13"; it arrived with Swift 5.5.
- **Errors**: no `Result` in practice, `try?`/`try!` guidance, typed throws, custom `Error` types or `defer`; the JavaScript original's "Don't ignore rejected promises" has no Swift counterpart.
- **Types**: no guidance on choosing `struct` vs `class`, `mutating`, `inout`, `final`, generics or associated types; no **protocol extensions** or default implementations; access control stops at `private` (no `private(set)`, property observers, `public`/`open`).
- **APIs**: argument labels and the Swift API Design Guidelines go undiscussed; examples use `NSRegularExpression`, not Swift `Regex`, and UIKit, not SwiftUI.
- **Testing** uses XCTest only — no Swift Testing (`@Test`, `#expect`).
- **Tools**: SwiftLint only; no swift-format. No DocC or documentation comments.
- **Dropped from the JavaScript original**: the warning that "bad abstractions can be worse than duplicate code", "don't over-optimize", journal comments, consistent capitalization, and keeping callers near callees.

**Positions to weigh rather than adopt blindly**: the ban on `// MARK:` (common Xcode practice); an 80-character line where the Google Swift Style Guide it cites uses 100 and SwiftLint's default warns at 120; and setters that reject bad input by `print`ing, against the guide's own error-handling rule.

One decorative image in the introduction was not read; the PR template (Portuguese) was read only for provenance.
