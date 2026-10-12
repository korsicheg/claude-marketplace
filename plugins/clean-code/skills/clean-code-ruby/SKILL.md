---
name: clean-code-ruby
description: "Knowledge base from \"clean-code-ruby\" by Alex Jiao (uohzxela) et al. — Robert C. Martin's Clean Code principles adapted for Ruby. Use when writing or reviewing Ruby and you need rules for naming and magic numbers, keyword arguments and the two-argument limit, default arguments vs ||, flag parameters, side effects and argument mutation, Enumerable over loops, predicate methods and unless, replacing case/is_a? with polymorphism and duck typing, accessors and attr_accessor, avoiding fluent interfaces, composition over inheritance, SOLID via implicit contracts, one-expectation RSpec tests, rescuing and raising with context, and RuboCop. Part of the clean-code skill family; for the original book (Java examples, smells catalogue, refactoring case studies) use clean-code-java; for another language use its sibling (clean-code-typescript, -javascript, -python, -php, -csharp, -go, -dart, -swift); for any other language, including Rust, Kotlin, C++, Scala, YAML, Terraform, SQL and Bash, use clean-code-universal."
---

<!-- argument-hint: [topic, principle name like LSP, or chapter number] -->

# clean-code-ruby
**Source**: [uohzxela/clean-code-ruby](https://github.com/uohzxela/clean-code-ruby) (commit `6687800`, MIT) — *Clean Code* concepts adapted for Ruby; inspired by ryanmcdermott/clean-code-javascript
**Author**: Alex Jiao (uohzxela) + 22 contributors | **Size**: ~5,800 words · 37 rules · **Chapters**: 11 | **Targets**: Ruby 2.4+ (pre-3.0 idiom; some examples assume Rails' ActiveSupport) | **Generated**: 2026-10-12

## How to Use This Skill

- **Without arguments** — load the core rules below for reference
- **With a topic** — ask about `keyword arguments`, `side effects`, `fluent interfaces`, `duck typing`, `LSP`; I find and read the relevant chapter
- **With a chapter** — ask for `ch06`; I load that chapter file
- **Browse** — ask "what chapters do you have?" for the full index

When you ask about something not covered below, I read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

### The root rule
**Methods should do one thing.** The guide calls this "by far the most important rule in software engineering" — "If you take nothing else away from this guide other than this, you'll be ahead of many developers." Every other rule is a *detector* for breaking it: a third argument, a boolean flag, mixed abstraction levels, a `case` on a type, an `is_a?` chain, a mutated `$global`.

**Test**: if you can only describe the method using "and", split it.

### The quality standard — and the port's own caveat
Judge code on whether it is **readable, reusable, refactorable**. These are **guidelines, not laws**, and explicitly **not a style guide**. The maintainer adds a candid warning: "The examples are largely ported over from JavaScript so they may not be idiomatic." Take the **principle** from the rule and the **idiom** from Ruby; where an example looks like JavaScript (`initialize` returning `self`, chainable `set_*` methods), fix the example.

### What makes this adaptation distinct: duck typing, with tests as the referee
Where the Python adaptation has `mypy` catch violations, the Ruby guide has neither interfaces nor a type checker, and says so. Its abstractions are **implicit contracts** — "the methods and properties that an object/class exposes to another object/class."

- **Type checks are replaced, not enforced.** An `is_a?` chain becomes one message every type answers (`vehicle.move`). For primitives the guide mentions contracts.ruby, but mostly argues against checks — hand-rolled guards buy only "faux 'type-safety'". Instead: "Keep your Ruby clean, write good tests, and have good code reviews."
- **So tests carry the load a type checker carries elsewhere**: "Testing is more important than shipping," with 100% of statements **and branches** as the target.
- **The port's ledger against its parent** (46 rules → 37): it **reverses** "Use method chaining" into **"Avoid fluent interfaces"**, **replaces** "Don't ignore rejected promises" with **"Provide context with exceptions"**, and **drops** nine, including both concurrency rules (the TOC still skips number 8) and prototype patching. ch01 has the full table.

### Naming (ch02)
- Name the concept, not the format: `yyyymmdstr` → `current_date`.
- **One word per concept**, suffixes included: `user_info`/`user_data`/`user_record` → `user`; `starts_at`/`start_at`/`start_time` → `starts_at`.
- Hoist magic numbers to **capitalized constants**: `Timeout::timeout(86_400)` → `SECONDS_IN_A_DAY`.
- Destructure, don't index: `_, city, zip_code = regex.match(address).to_a`.
- Name block parameters fully (`|location|`, not `|l|`); drop repeated context (`car[:color]`).
- **Default arguments over `||`** — but a default fires only when the argument is *omitted*; an explicit `nil` or `false` passes straight through, while `||` replaces both.

### Methods (ch03)
- **≤2 arguments ideally**; more causes "a combinatorial explosion" of test cases. First ask whether the method does too much, or whether "a higher-level object will suffice". The Ruby answer is **keyword arguments** (`def create_menu(title:, body:)`, Ruby 2.1+): the signature documents itself, and a missing keyword raises `ArgumentError` naming it.
- **Name the action**: `add_to_date` → `add_month_to_date`.
- **One level of abstraction**, descending: `interpret` → `tokenize`, `lex`, `parse`.
- **No flags**: `create_file` / `create_temp_file`.
- **Side effects**: don't mutate `$globals`; centralize unavoidable effects in one service, "One and only one." Ruby passes **references by value**, so `cart.push(item)` changes the caller's array (the guide's shopping-cart retry bug). Return `cart + [item]`; use Hamster when copies get expensive.
- **Blocks over loops**: "Ruby isn't a functional language in the way that Haskell is, but it has a functional flavor" — `sum`, `select`, `map`, `each_with_object` instead of accumulators.

### Conditionals, types and duplication (ch04) — climb only as far as needed
Compound condition → **`?` predicate method** (`send_message?`) · `if !x.blank?` → **`unless`** or **`present?`** · `case @type` → **a subclass per case** · `is_a?` chain → **one shared message** · primitive type guards → **contracts.ruby, or nothing**.

**Remove duplication — carefully**: "Bad abstractions can be worse than duplicate code, so be careful!" **Delete dead code**: "It will still be safe in your version history."

### Objects and classes (ch05–ch06)
- **Accessors, not hashes.** Instance variables are private; a reader is `def balance`, a writer is `def balance=(amount)` — the seam for validation, logging and lazy loading. Use **`attr_accessor`** when they're "absolutely trivial" (data-like objects, ActiveRecord models), though the guide warns it is "in some situations … a code smell."
- **Avoid fluent interfaces.** Returning `self` for chaining breaks encapsulation and decorators, is "harder to mock in a test suite", and "makes diffs of commits harder to read." Chaining stays fine for builders such as ActiveRecord queries.
- **Composition over inheritance.** Inherit only when all three hold: genuine **is-a** ("Human->Animal vs. User->UserDetails"), real **code reuse**, and base changes you **want** to propagate. `EmployeeTaxData < Employee` fails all three.

### SOLID through implicit contracts (ch07)
- **SRP** — "There should never be more than one reason for a class to change." Split authentication (`UserAuth`) out of `UserSettings`.
- **OCP** — "open for extension, but closed for modification" (Meyer). Give every adapter one message (`request(url)`); never `case @adapter.name` in the consumer.
- **LSP** — a parent must be replaceable by a child "without getting incorrect results." `Square < Rectangle` returns 25 where 20 was expected, because `width=` and `height=` can't keep a square's invariant. Make both siblings under `Shape`, dimensions fixed at construction.
- **ISP** — "Clients should not be forced to depend upon interfaces that they do not use." Ruby "doesn't have interfaces so this principle doesn't apply as strictly", but the interface is still real: it is **the set of messages a client sends**. Split `Car` (for `Driver`) from `CarInternals` (for `Mechanic`).
- **DIP** — inject collaborators through `initialize`; the abstraction is whatever message they answer (`request_item`). `SomeClass.new` inside `initialize` is the tell — and the guide's own SRP fix still does it.

### Tests, errors, formatting, comments (ch08–ch11)
- **RSpec, one expectation per `it`**, shared setup via `let`; a framework *and* a coverage tool; coverage before launching *or refactoring*.
- **"Thrown errors are a good thing!"** A `begin/rescue` means "you should have a plan, or create a code path": `logger.error(err)` at `Logger::ERROR`, notify the user, report to a service like Honeybadger — "OR do all three!" Never `logger.info(err)` alone. **Raise with context**: `fail ArgumentError, 'Missing user' unless user` — a class callers can rescue by, a message people can read.
- **"DO NOT ARGUE over formatting"** — use RuboCop. Keep capitalization consistent (it carries meaning in Ruby; freeze constant collections) and keep **callers directly above callees**.
- **No commented-out code, no journal comments** — "Use `git log` to get history!"

---

## Chapter Index

| # | Title | Key Rules |
|---|-------|-----------|
| [ch01](chapters/ch01-introduction.md) | Introduction | 3 Rs, guidelines not laws, ported-from-JavaScript caveat, the 46→37 ledger |
| [ch02](chapters/ch02-variables.md) | Variables | one vocabulary, constants, explanatory variables, mental mapping, default arguments |
| [ch03](chapters/ch03-methods.md) | Methods | keyword arguments, do one thing, abstraction levels, flags, side effects, Enumerable |
| [ch04](chapters/ch04-duplication-conditionals-and-types.md) | Methods, continued — Duplication, Conditionals, Type-Checking and Dead Code | bad abstractions, predicate methods, `unless`, polymorphism, duck typing, dead code |
| [ch05](chapters/ch05-objects-and-data-structures.md) | Objects and Data Structures | readers and writers, `attr_accessor` and its smell |
| [ch06](chapters/ch06-classes.md) | Classes | avoid fluent interfaces, composition over inheritance |
| [ch07](chapters/ch07-solid.md) | SOLID | SRP, OCP, LSP (Square/Rectangle), ISP, DIP, implicit contracts |
| [ch08](chapters/ch08-testing.md) | Testing | statement and branch coverage, single expectation per test |
| [ch09](chapters/ch09-error-handling.md) | Error Handling | don't ignore rescued errors, raise with class and message |
| [ch10](chapters/ch10-formatting.md) | Formatting | RuboCop, consistent capitalization, `.freeze`, caller above callee |
| [ch11](chapters/ch11-comments.md) | Comments | no commented-out code, no journal comments |

## Topic Index

- **3 Rs (readable, reusable, refactorable)** → ch01
- **Abstraction levels** → ch03
- **ActiveSupport (`present?`, `blank?`)** → ch04
- **`attr_accessor` / `attr_reader`** → ch05, ch06
- **Bad abstractions** → ch04
- **`begin` / `rescue`, `Logger`** → ch09
- **Capitalization / `.freeze`** → ch10, ch02
- **Commented-out code / journal comments** → ch11
- **Composition vs inheritance** → ch06, ch04
- **Conditionals (avoiding)** → ch04
- **contracts.ruby** → ch04
- **Coverage** → ch08
- **Dead code** → ch04, ch11
- **Default arguments** → ch02
- **Dependency injection / DIP** → ch07
- **Duck typing / implicit contracts** → ch04, ch07
- **Duplication (DRY)** → ch04
- **`Enumerable` / functional style** → ch03
- **`fail` / `raise`, error classes** → ch09
- **Flags (boolean parameters)** → ch03
- **Fluent interfaces / method chaining** → ch06
- **Getters and setters (readers, writers)** → ch05
- **Global variables (`$`)** → ch03
- **ISP** → ch07
- **`is_a?` (type-checking)** → ch04
- **Keyword arguments / argument count** → ch03
- **LSP / Square-Rectangle** → ch07
- **Magic numbers / constants** → ch02, ch10
- **Mental mapping** → ch02
- **Naming** → ch02, ch03
- **Negative conditionals / `unless`** → ch04
- **Newspaper rule** → ch10
- **OCP** → ch07
- **Polymorphism** → ch04, ch07
- **Predicate methods (`?`)** → ch04, ch03
- **Reference passed by value** → ch03
- **RSpec / `let`** → ch08
- **RuboCop** → ch10
- **Side effects / mutating arguments** → ch03
- **SOLID** → ch07
- **SRP** → ch07
- **TDD** → ch08

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions and chapter refs
- [patterns.md](patterns.md) — 31 concrete refactoring techniques with trade-offs
- [cheatsheet.md](cheatsheet.md) — thresholds, decision trees, the conditional ladder, tells & smells

## Related Skills — the clean-code family

- **`clean-code-java`** — Robert C. Martin's original *Clean Code*, the book itself and the family's canonical source. Go there for what this guide omits or treats in a line — concurrency, comments in full, F.I.R.S.T. and TDD, exceptions vs. return codes — and for the **66-item smells-and-heuristics catalogue** and the refactoring case studies.
- **`clean-code-javascript`** — Ryan McDermott's guide, **this one's parent document**. Use it for JavaScript, and for the rules the Ruby port dropped: prototype patching (the analogue of monkey-patching, which this guide never addresses), business-logic-only comments, positional markers, and the async ladder.
- **`clean-code-typescript`** — labs42io's adaptation. Use it for TypeScript: `readonly`/`as const` immutability, `type` vs `interface`, discriminated unions instead of `instanceof` chains, and `Failable<R, E>` result types.
- **`clean-code-python`** — Rigel Di Scala's adaptation. Use it for Python: type hints, parameter objects, ABCs and mixins, and `mypy` as the LSP referee — the type-checked counterpoint to this guide's duck typing.
- **`clean-code-php`** — from piotrplenik/clean-code-php. Use it for PHP; it carries this guide's "Avoid fluent interfaces" rule with the same four costs and the same Marco Pivetta citation.
- **`clean-code-csharp`** — from thangchung/clean-code-dotnet. Use it for C# and .NET.
- **`clean-code-go`** — from Pungyeon's *Clean Go Code*. Use it for Go.
- **`clean-code-dart`** — from williambarreiro/clean-code-dart. Use it for Dart.
- **`clean-code-swift`** — from MaatheusGois/clean-code-swift. Use it for Swift.
- **`clean-code-universal`** — the family's shared core, every rule tagged by the construct it assumes. Use it for languages with no sibling (Rust, Kotlin, C++, Scala) and for YAML, Terraform/HCL, SQL, Bash and Dockerfile; from Ruby, for the fuller treatment of failure, comments and verification that this guide covers thinly.

---

## Scope & Limits

Covers the clean-code-ruby README only — **37 rules** in ten sections (~5,800 words, translations excluded). It is **not a style guide**; formatting goes to RuboCop. The examples are ported from JavaScript and, by the maintainer's own note, "may not be idiomatic" (`initialize` returning `self`, `set_*` methods, `INITIAL_VALUE = 0` passed to `sum`); the chapters flag these, and report the rules as written.

**What the source does not cover**, though a Ruby reader might expect it:
- **Concurrency** — no threads, `Mutex`, Fibers or Ractors; the parent's section was cut.
- **Modules and mixins** — no `include`, `extend`, `Comparable` or module design; "module" appears only in the generic sense.
- **Metaprogramming** — no `method_missing`, `respond_to_missing?`, `define_method` or DSLs.
- **Monkey-patching and refinements** — the parent's rule against patching built-ins was dropped, with no replacement.
- **Blocks as an API** — blocks appear only as `Enumerable` arguments; no `yield`, `Proc` or lambdas.
- **Visibility and value objects** — no `private`/`protected`, `Struct` or `Data`; privacy is one code comment.
- **Static typing** — no RBS, Sorbet or Steep; type-checking advice points to contracts.ruby.
- **Exceptions in depth** — no custom hierarchies, `ensure`, `retry`, or `Exception` vs `StandardError`.
- **Comments and testing** — two negative comment rules, nothing on when to write one; one testing rule.

**Version and framework assumptions.** Ruby 2.1 for keyword arguments, 2.4 for its `sum` example; it predates Ruby 3.0's separation of positional and keyword arguments, so check "hash of arguments" advice against current semantics. `present?`/`blank?` are Rails' ActiveSupport.

**Tensions inside the source**, recorded rather than resolved: the DRY fix ends on a `case employee.type` that "Avoid conditionals" would remove; the SRP fix constructs `UserAuth.new` inside `initialize`, which DIP calls a hard-coded dependency; the fluent-interface fix adds `attr_accessor`, which ch05 flags as a possible smell; and "pass data to the method by instance variables" sits uneasily with the side-effects rules. For these and the gaps above, go to **clean-code-java** (canonical) or **clean-code-universal**.

**Licence.** MIT. The `LICENSE` file reads "Copyright (c) 2016 Ryan McDermott", inherited from the JavaScript parent; the Ruby guide's maintainer is uohzxela (GitHub name Alex Jiao). No source images were read (the README has one, a comic).
