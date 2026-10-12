---
name: clean-code-php
description: "Knowledge base from \"clean-code-php\" by Piotr Plenik et al. — Robert C. Martin's Clean Code principles adapted for PHP. Use when writing or reviewing PHP and you need rules for naming, magic numbers and bit-flag constants, return-early guard clauses, === over == and the ?? operator, typed default arguments, the two-argument limit and value objects, flag parameters, side effects, global state and Singletons, replacing switch and instanceof with interfaces, type declarations over type checks, private-by-default visibility, composition over inheritance, fluent interfaces, final classes, SOLID through interfaces, and DRY. Part of the clean-code skill family; for the original book (Java examples, smells catalogue, refactoring case studies) use clean-code-java; for another language use its sibling (clean-code-typescript, -javascript, -python, -csharp, -go, -ruby, -dart, -swift); for any other language, including Rust, Kotlin, C++, Scala, YAML, Terraform, SQL and Bash, use clean-code-universal."
---

<!-- argument-hint: [topic, principle name like LSP, or chapter number] -->

# clean-code-php
**Source**: [piotrplenik/clean-code-php](https://github.com/piotrplenik/clean-code-php) — *Clean Code* concepts adapted for PHP; inspired by ryanmcdermott/clean-code-javascript (MIT, commit `8d90132`, 2022-06-19)
**Author**: Piotr Plenik (piotrplenik) + 49 contributors, chiefly Peter Gribanov and Tomas Votruba | **Size**: ~6,300 words · 36 rules · **Chapters**: 9 | **Targets**: PHP 7.1+ (composer floor 7.2; CI lints on 8.0) | **Generated**: 2026-10-12

## How to Use This Skill

- **Without arguments** — load the core rules below for reference
- **With a topic** — ask about `fluent interfaces`, `strict_types`, `final`, `Singleton`, `??`; I find and read the relevant chapter
- **With a chapter** — ask for `ch05`; I load that chapter file
- **Browse** — ask "what chapters do you have?" for the full index

When you ask about something not covered below, I read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

### The root rule
**A function should do one thing.** In this port it has lost its own entry — but it is still the stated reason behind two rules: "Flags tell your user that this function does more than one thing," and `if` statements tell "your user that your function does more than one thing. Remember, just do one thing." Every rule below is a detector for that violation: a third argument, a boolean flag, mixed abstraction levels, a vague verb, a `global`, a type switch.

### The quality standard — the 3 Rs
Judge code on whether it is **readable, reusable, refactorable**. "This is not a style guide," and the rules are "guidelines and nothing more" — override with a stated reason, never by accident. Formatting is tooling's job: the repo lints its own README's PHP with **ECS** (Symplify's Easy Coding Standard: PSR-12, Common, Clean Code and Symplify sets).

### What makes this adaptation distinct: the keyword, not the convention
The guide is a port of clean-code-javascript. Where the parent relied on discipline, the PHP version reaches for a language feature — and adds the rules PHP's own hazards demand.

- **Types are declared, not checked.** `combine($val1, $val2)` with an `is_numeric()` guard → `combine(int $val1, int $val2): int`; untyped defaults → `string $breweryName = 'Hipster Brew Co.'`. The guide says "type declaration **or strict mode**" — and the mode matters: without `declare(strict_types=1)` in the calling file, `combine('5', '7')` still succeeds by coercion. The guide never shows that line (its linter skips the fixer), so add it yourself.
- **Comparison gets its own chapter.** PHP juggles types: `'42' != 42` is `false`. Use `===`/`!==` and `in_array(…, true)`; replace `isset()` ladders with chained `??` — which tests presence, unlike `?:`, which tests truthiness.
- **Visibility is a keyword, and `private` is the default.** "`protected` modifier are as dangerous as public" — every subclass is a dependent (after Fabien Potencier). Expose operations (`withdraw()`), not state (`public $balance`).
- **Interfaces carry every abstraction.** Every class-to-class `extends` in the guide sits in a "Bad" example; the only `abstract class` is the OCP "Bad". The fixes are always `interface` — `Airplane`, `Vehicle`, `Shape`, `Adapter`, `Employee` — including PHP's multiple interface inheritance, `interface Employee extends Feedable, Workable`.
- **`final` by default** (after Marco Pivetta) — "The only condition is that your class should implement an interface and no other public methods are defined." `final` + interface = closed to inheritance, open to substitution.
- **No fluent interfaces** — this **reverses** the JavaScript parent's "Use method chaining". `return $this` breaks encapsulation and decorators, is harder to mock, and muddies diffs. Builders (PHPUnit's mock builder, Doctrine's QueryBuilder) are the exception.
- **No hidden globals.** `global $name`, a global `config()` function, and `DBConnection::getInstance()` are one smell — a dependency missing from the signature. Construct the object once and inject it, as Symfony's container does. The Singleton gets Brian Button's four charges: hidden dependencies, SRP violation, tight coupling, order-dependent tests.
- **Flat control flow.** Return early with guard clauses, express branchy rules as data, and throw instead of returning `'Not supported'` from a typed function.

### Naming
- **Meaningful, pronounceable, searchable**: `$ymdstr` → `$currentDate`. **One vocabulary**: `getUserInfo`/`Data`/`Record`/`Profile` → `getUser()`.
- **No magic numbers**: `serialize($data, 448)` → `JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE`; `$access & 4` → `public const ACCESS_UPDATE = 4` and `User::ACCESS_UPDATE`.
- **Name regex subpatterns**: `$matches[1]` → `[, $city, $zipCode] = $matches` → **`(?<city>…)` read as `$matches['city']`**.
- **No mental mapping** (`$l`/`$li` → `foreach ($locations as $location)`); **no repeated context** (`Car::$carMake` → `Car::$make`).

### Functions
- **≤2 arguments**: "Zero arguments is the ideal case. One or two arguments is ok, and three should be avoided. Anything more than that should be consolidated" — into "a higher-level object". The guide applies it to a constructor: eight strings become `Name`, `City`, `Contact`.
- **Name the action** (`send()`, not `handle()`). **No flag parameters** (`createFile` / `createTempFile`).
- **One level of abstraction**, extracted all the way to **injected classes**: the "Bad too" rung — helper functions the parser still calls directly — is "still very complex and not testable."
- **Avoid side effects**: take a value, return a value. When one is necessary, "Have one service that does it. One and only one."
- **Conditionals**: encapsulate as predicates (`$article->isPublished()`), state them positively, and replace a `switch ($this->type)` with an interface and one class per case.
- **Remove dead code**: "It will still be safe in your version history."

### SOLID, in PHP's own terms
- **SRP** — "There should never be more than one reason for a class to change." `UserSettings` loses credential checking to `UserAuth`. *(Its "Good" version still constructs `UserAuth` internally — inject it.)*
- **OCP** — "open for extension, but closed for modification" (Meyer). Dispatch on `$adapter->getName()` → `interface Adapter { request() }` and plain delegation.
- **LSP** — the Square–Rectangle trap: same signatures, wrong area (25, not 20). Fix: sibling implementations of `Shape`, dimensions set in the constructor, **no setters**.
- **ISP** — "Clients should not be forced to depend upon interfaces that they do not use." Split `Employee` into `Workable` + `Feedable`; the robot implements only `Workable`.
- **DIP** — high-level modules depend on abstractions; in PHP practice that is **constructor injection of an interface**, the pattern frameworks like Symfony implement.

### DRY — with its caveat
"Duplicate code is bad because it means that there's more than one place to alter something." But: **"Bad abstractions can be worse than duplicate code, so be careful!"** Follow SOLID to find the abstraction, then merge into it. If the merge needs a flag, the variation is real — leave the copies apart.

---

## Chapter Index

| # | Title | Key Rules |
|---|-------|-----------|
| [ch01](chapters/ch01-introduction.md) | Introduction | 3 Rs, guidelines not laws, PHP 7.1 floor, ECS/PSR-12, adaptation map vs the JS parent |
| [ch02](chapters/ch02-variables.md) | Variables | pronounceable and searchable names, bit-flag constants, named subpatterns, return early, mental mapping |
| [ch03](chapters/ch03-comparison.md) | Comparison | `===` over `==`, strict `in_array`, `??` chains, `??` vs `?:` |
| [ch04](chapters/ch04-functions.md) | Functions | typed defaults, ≤2 arguments and value objects, flags, abstraction levels, side effects, global functions, Singleton |
| [ch05](chapters/ch05-conditionals-and-types.md) | Conditionals, Type-Checking and Dead Code | encapsulate, positive predicates, polymorphism via interfaces, type declarations and strict mode, dead code |
| [ch06](chapters/ch06-objects-and-data-structures.md) | Objects and Data Structures | encapsulation, `private` by default, `protected` as public |
| [ch07](chapters/ch07-classes.md) | Classes | composition over inheritance, avoid fluent interfaces, `final` + interface |
| [ch08](chapters/ch08-solid.md) | SOLID | SRP, OCP, LSP, ISP, DIP — each fixed with an interface |
| [ch09](chapters/ch09-dry.md) | Don't Repeat Yourself (DRY) | restaurant inventory, near-miss duplication, bad-abstraction caveat |

## Topic Index

- **Abstract classes (vs interfaces)** → ch08, ch07
- **Abstraction levels** → ch04
- **Arguments (function)** → ch04
- **Bad abstractions** → ch09
- **Bit-flag constants** → ch02
- **Builders** → ch07
- **Comparison (`===`, `==`)** → ch03
- **Composition over inheritance** → ch07
- **Constructor injection** → ch04, ch08
- **Dead code** → ch05
- **Decorators** → ch07
- **Default arguments** → ch04
- **Dependency injection / DIP** → ch08, ch04
- **DRY** → ch09
- **Duplication** → ch09
- **ECS / PSR-12** → ch01
- **Encapsulation** → ch06
- **Encapsulate conditionals** → ch05
- **`final` classes** → ch07
- **Flags (boolean parameters)** → ch04
- **Fluent interfaces / method chaining** → ch07
- **Function names** → ch04
- **`global` keyword** → ch04
- **Global functions** → ch04
- **Guard clauses / return early** → ch02
- **`in_array` strict flag** → ch03, ch02
- **`instanceof` chains** → ch05
- **Interfaces** → ch08, ch05, ch07
- **ISP** → ch08
- **LSP** → ch08
- **Magic numbers** → ch02
- **Mental mapping** → ch02
- **Naming** → ch02, ch04
- **Negative conditionals** → ch05
- **Null coalescing (`??`)** → ch03
- **OCP** → ch08
- **Polymorphism** → ch05, ch08
- **`private` / `protected` / `public`** → ch06
- **Regex (named subpatterns)** → ch02
- **Short ternary (`?:`)** → ch03, ch04
- **Side effects** → ch04
- **Singleton** → ch04
- **SOLID** → ch08
- **SRP** → ch08
- **`strict_types` / strict mode** → ch05
- **`switch` on type** → ch05
- **Type declarations** → ch05, ch04
- **Type juggling** → ch03, ch05
- **Value objects / parameter objects** → ch04
- **Version floor (PHP 7.1)** → ch01
- **Vocabulary consistency** → ch02

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions and chapter refs
- [patterns.md](patterns.md) — 23 concrete refactoring techniques with trade-offs
- [cheatsheet.md](cheatsheet.md) — thresholds, decision trees, escalation ladders, tells & smells

## Related Skills — the clean-code family

- **`clean-code-java`** — Robert C. Martin's original *Clean Code*, the book itself (17 chapters + Appendix A) and the family's canonical reference. Go there for everything this guide omits — testing and TDD, error handling, comments, formatting, boundaries, concurrency — and for the **66-item smells-and-heuristics catalogue**, the long-form **refactoring case studies**, and the rationale and thresholds behind the rules here.
- **`clean-code-javascript`** — Ryan McDermott's guide, **the direct parent this one was ported from**. Go there for the rules the PHP port dropped (don't mutate arguments, favor functional programming, don't over-optimize) and its testing, concurrency, error-handling, formatting and comments chapters — and note that its "Use method chaining" is the rule this guide reverses.
- **`clean-code-typescript`** — labs42io's adaptation. Go there when the code is TypeScript, or for typed-language material this guide lacks: the immutability ladder (`readonly` → `as const`), `type` vs `interface`, and the `Failable<R, E>` result type.
- **`clean-code-python`** — Rigel Di Scala's adaptation. Go there when the code is Python: type hints instead of type-prefixes, the `dataclass`/`NamedTuple`/`TypedDict` parameter-object ladder, SOLID through ABCs and mixins, and mypy as the LSP referee.
- **`clean-code-csharp`** — adapted from thangchung/clean-code-dotnet. Use it when the code is C#/.NET.
- **`clean-code-go`** — adapted from Pungyeon's *Clean Go Code*. Use it when the code is Go.
- **`clean-code-ruby`** — adapted from uohzxela/clean-code-ruby. Use it when the code is Ruby.
- **`clean-code-dart`** — adapted from williambarreiro/clean-code-dart. Use it when the code is Dart or Flutter.
- **`clean-code-swift`** — adapted from MaatheusGois/clean-code-swift. Use it when the code is Swift.
- **`clean-code-universal`** — the family's shared core, distilled from Martin's book across its adaptations, with **every rule tagged by tier**: Tier 1 assumes only that you can name something and run some verification, Tier 2 binds only where a specific construct exists, and Tier 3 is language idiom, out of scope there and owned by the matching sibling — for PHP's `final` + interface, `===` and `??`, that is this skill. **Use it for any language the family does not cover** — Rust, Kotlin, C++, Scala and the rest — **and for configuration and infrastructure-as-code, which no sibling covers at all**: YAML (Kubernetes, Helm, CI pipelines), Terraform/HCL, SQL, Bash and Dockerfile.

---

## Scope & Limits

Covers the clean-code-php guide only — its README, 36 rules across naming, comparison, functions, objects, classes, SOLID and DRY (three rules come in two parts, so 33 distinct ideas). It is **not a style guide**; use PSR-12 via ECS or PHP-CS-Fixer for formatting. It **omits** what the book and the JavaScript parent cover: testing, error handling (exceptions appear only incidentally), comments, formatting and concurrency — and "Functions should do one thing" survives only as a phrase inside other rules. For those, use **clean-code-java**.

**It is a PHP 7.1-era text** (last content change June 2022, snippets written for 7.1). It never mentions typed properties (7.4), `??=` (7.4), constructor promotion, union types, `match` or the nullsafe operator (8.0), enums or `readonly` properties (8.1), or readonly classes (8.2). The principles hold; the syntax has moved on. Where the guide hand-writes getters for immutable data, uses class constants for a closed set, or uses a `switch` as the "Bad", modern PHP offers more — but the guide doesn't say so, and this skill doesn't invent rules for it.

**`declare(strict_types=1)` is named ("strict mode") but never shown**, and the repo's ECS config skips the `DeclareStrictTypesFixer` and `StrictComparisonFixer`. Without strict mode, scalar declarations coerce (Ch 5).

**The snippets are style-checked, not executed**, and several would not run as written: OCP's "Bad" calls `parent::__construct()` on an abstract class with no constructor and dispatches on `'httpNodeAdapter'` while its adapter is named `'nodeAdapter'`; `Promise` there is a JavaScript leftover, not a PHP type; the Singleton "Bad" calls `new self()` without its required `$dsn`; the fluent "Bad" assigns a `void` result to `$car`. Copy the shape, not the snippet.

**A few explanations are imprecise or inherited from JavaScript**: "PHP is untyped" (it is dynamically typed, with optional declarations); the loose-comparison example's comment "The expression will always pass" (the branch never runs); ISP's introduction about "large settings objects" belongs to the JavaScript example, not the `Employee` interfaces shown; DRY points to SOLID "in the Classes section", where JavaScript keeps it; SRP's "Good" constructs its collaborator, contradicting DIP. The repo's MIT licence still reads "Copyright (c) 2016 Ryan McDermott", inherited from the parent. No source images were read.
