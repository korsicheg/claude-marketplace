---
name: clean-code-dart
description: "Knowledge base from \"clean-code-dart\" by William Barreiro — Robert C. Martin's Clean Code principles adapted for Dart (and Flutter code). Use when writing or reviewing Dart and you need rules for const/final and lowerCamelCase constants, const defaults instead of ??, named required parameters, flag parameters, side effects (spread, not mutation), fold/where, overrides instead of is-chains, getters/setters only for logic, _ privacy, cascades, composition over inheritance, SOLID with abstract classes and implements, one-concept package:test tests, async/await over then, typed catch with stack traces, and when NOT to write a comment. Part of the clean-code skill family; for the original book (Java examples, smells catalogue, refactoring case studies) use clean-code-java; for another language use its sibling (clean-code-typescript, -javascript, -python, -php, -csharp, -go, -ruby, -swift); for any other language, including Rust, Kotlin, C++, Scala, YAML, Terraform, SQL and Bash, use clean-code-universal."
---

<!-- argument-hint: [topic, principle name like LSP, or chapter number] -->

# clean-code-dart
**Source**: [williambarreiro/clean-code-dart](https://github.com/williambarreiro/clean-code-dart) — "Clean Code concepts adapted for Dart"; a port of ryanmcdermott/clean-code-javascript (MIT, commit `aa80293`, 2023-03-11)
**Author**: William Barreiro (williambarreiro), sole contributor; the MIT copyright line also names Ryan McDermott, author of the JavaScript original | **Size**: ~5,600 words · 39 rules · **Chapters**: 11 | **Targets**: Dart 2.17+ with sound null safety, pre-Dart 3 (inferred from `required`, `String?` and super parameters; the guide names no version) | **Generated**: 2026-10-12

## How to Use This Skill

- **Without arguments** — load the core rules below for reference
- **With a topic** — ask about `cascades`, `_ privacy`, `named parameters`, `UnimplementedError`, `Future errors`; I find and read the relevant chapter
- **With a chapter** — ask for `ch06`; I load that chapter file
- **Browse** — ask "what chapters do you have?" for the full index

When you ask about something not covered below, I read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

### The root rule
**Functions should do one thing.** The guide calls it "by far the most important rule in software engineering" — "If you take nothing else away from this guide other than this, you'll be ahead of many developers." Every other rule is a *detector* for breaking it: a third argument, a `bool` flag, mixed abstraction levels, a vague name, a `switch` or `is` chain on a type.

**Test**: if you can only describe it using "and", split it.

### The quality standard — the 3 Rs
Judge code on whether it is **readable, reusable, refactorable**. "This is not a style guide," and the rules are "guidelines and nothing more" — override with a stated reason, never by accident. Style belongs to *Effective Dart*, which the guide recommends instead of arguing: "DO NOT ARGUE over formatting."

### What makes this adaptation distinct: Dart syntax where JavaScript needed discipline
A close port of clean-code-javascript — same chapters, mostly the same examples. What changes is the mechanism each rule reaches for:

- **Named `required` parameters** replace the destructured options object: `getMenu({required String title, …})`, called as `getMenu(title: 'Foo', …)`. Clear at both ends, and a missing argument is a compile error — but they don't shrink the test matrix the arguments rule worries about; for that, bundle into a class.
- **`const`, `final` and type inference** carry intent: "Declare them as const if the value is known at compile time; Declare as final if the variable is assigned just once; Use lowerCamelCase."
- **Default parameter values must be `const`** — "so you cannot use them on every case." Constant fallback → `{String breweryName = 'Hipster Brew Co.'}`, non-nullable; computed fallback → `String?` + `??`.
- **The type system referees side effects.** The global-mutation Bad example has to declare `dynamic name` to compile at all; return values instead, and build new lists with `[...cart, item]`.
- **`_` replaces closures for privacy** — set from a public named parameter through the initializer list (`: _name = name`). Dart privacy is per *library* (file), not per class, a detail the guide doesn't mention.
- **Cascades (`..`) replace `return this`.** The guide's `Car` class is identical in Bad and Good; only the call site changes.
- **SOLID gets real keywords**: `abstract class` as the interface, `extends` for behaviour (OCP, LSP), `implements` for contracts (ISP, DIP), `@override` everywhere. The Dart tell: an implementer that uses "the famous `throw UnimplementedError()`" is breaking ISP.
- **`Future` + `async`/`await`** replaces Promises; **`on Exception catch (e, s)`** keeps the type and the stack trace; **`package:test`**'s `group`/`test`/`expect` replaces `describe`/`it`.

**Two reversals of the parent** — don't carry these JavaScript habits over:
1. **Getters and setters only when necessary**: "Unlike other languages, in Dart it is recommended to use getters and setters only when there is some logic before using the attribute." A field and a getter look the same to callers, so start with the field.
2. **Constants are lowerCamelCase**: `daysInWeek`. The parent's Good `DAYS_IN_WEEK` is in this guide's Bad block, and "Use consistent capitalization" becomes "Use the *correct* capitalization".

### Naming
- **Meaningful, pronounceable, searchable**: `yyyymmdstr` → `currentDate`; `32` → `const setupTimeInMinutes = 32;`.
- **One noun per entity**: `getUserInfo`/`getClientData`/`getCustomerRecord` → `getUser`.
- **Explanatory `final`s** for positional values (`final city = address[1];`); no mental mapping (`l` → `location`); no repeated context (`Car(carMake:)` → `Car(make:)`).

### Functions
- **≤2 arguments** ideally; three "should be avoided"; more "should be consolidated".
- **One level of abstraction**; extract levels into typed helpers (`List<String> tokenize(…)`, `List<Node> lexer(…)`).
- **Pipelines of tear-offs**: `clients.where(isActiveClient).forEach(email);`. **`fold<int>`** over accumulator loops, since `reduce` can't change the result type.
- **No flag parameters**: `createFile` / `createTempFile`.
- **Centralize unavoidable effects** — "Have one service that does it. One and only one."
- **Deduplicate — carefully**: "Bad abstractions can be worse than duplicate code." The guide's own merged `buildEmployeeCard` keeps an `is` chain its OCP rule calls Bad (ch03 works through it).
- **Named, positive predicates** (`isFileValid`); **subclass overrides** instead of a `switch` on a type; **delete dead code**.

### Objects and classes
- **Cascade what you own**: `Car(…)..color = 'pink'..save();`.
- **Composition over inheritance**: `extends` only for genuine is-a, reusable base code, and changes you *want* to propagate. Otherwise hold a field — nullable when optional (`EmployeeTaxData? taxData`).

### SOLID with abstract classes
- **SRP** — "There should never be more than one reason for a class to change." Split `UserAuth` out of `UserSettings`.
- **OCP** — "open for extension, but closed for modification." An `is` chain over subtypes → an abstract `getArea()` each subtype overrides.
- **LSP** — base and child "can be used interchangeably without getting incorrect results." `Square extends Rectangle` returns 25 where 20 is expected; make both siblings of an abstract `Shape`.
- **ISP** — "Clients should not be forced to depend upon interfaces that they do not use." `throw UnimplementedError()` → split the abstract class (`Book`, `DownloadableBook`).
- **DIP** — depend on an `abstract class`, receive it through `required this.requester`, construct `InventoryRequesterV2()` at the top level.

### Testing, async, errors, formatting, comments
- **"Testing is more important than shipping."** 100% statement and branch coverage is the ideal; **one concept per `test`**, grouped by unit with `group`.
- **`async`/`await` instead of `.then`**, inside a named function with a typed `Future<T>`.
- **"Thrown errors are a good thing!"** Every `catch` (and `.onError`) needs a plan: `log(…, error: e, stackTrace: s)`, `notifyUserOfError(e, s)` or `reportErrorToService(e, s)`.
- **Capitalization per *Effective Dart***: lowerCamelCase for values, constants and functions; UpperCamelCase for classes, enum types, typedefs, type parameters. **Callers directly above callees.**
- **"Comments are an apology, not a requirement."** Comment only business-logic complexity; no commented-out code, journal comments or `/////` banners.

---

## Chapter Index

| # | Title | Key Rules |
|---|-------|-----------|
| [ch01](chapters/ch01-introduction.md) | Introduction | 3 Rs, guidelines not laws, a port of clean-code-javascript, inferred Dart version |
| [ch02](chapters/ch02-variables.md) | Variables | `const`/`final`, searchable names, explanatory variables, `const` default values vs `??` |
| [ch03](chapters/ch03-functions.md) | Functions | do one thing, named `required` params, flags, side effects, spread, `fold`, polymorphism, DRY |
| [ch04](chapters/ch04-objects-and-data-structures.md) | Objects and Data Structures | accessors only for logic, `_` library privacy, initializer lists |
| [ch05](chapters/ch05-classes.md) | Classes | cascade notation, composition over inheritance, nullable composition |
| [ch06](chapters/ch06-solid.md) | SOLID | SRP, OCP, LSP, ISP (`UnimplementedError`), DIP; `extends` vs `implements` |
| [ch07](chapters/ch07-testing.md) | Testing | testing over shipping, coverage, `group`/`test` per concept |
| [ch08](chapters/ch08-concurrency.md) | Concurrency | `async`/`await` instead of `.then`, typed `Future<T>` |
| [ch09](chapters/ch09-error-handling.md) | Error Handling | `on Exception catch (e, s)`, three options, `Future.onError` |
| [ch10](chapters/ch10-formatting.md) | Formatting | don't argue, *Effective Dart* capitalization, callers above callees |
| [ch11](chapters/ch11-comments.md) | Comments | business logic only, no commented-out code, journals or banners |

## Topic Index

- **`??` (if-null)** → ch02
- **`@override`** → ch06
- **Abstract classes** → ch06
- **Abstraction levels** → ch03
- **Arguments (function)** → ch03
- **async / await** → ch08, ch09
- **Capitalization** → ch10, ch02
- **Cascade notation (`..`)** → ch05
- **Comments** → ch11
- **Composition vs inheritance** → ch05, ch06
- **Conditionals (avoiding)** → ch03, ch06
- **`const` / `final`** → ch02
- **Coverage** → ch07
- **Dead code** → ch03, ch11
- **Default parameter values** → ch02
- **Dependency injection / DIP** → ch06
- **Duplication / DRY** → ch03
- **`dynamic`** → ch03
- ***Effective Dart*** → ch10, ch02, ch04
- **Error handling** → ch09
- **`Exception` vs `Error`** → ch09
- **`extends` vs `implements`** → ch06, ch05
- **Flags (boolean parameters)** → ch03
- **Flutter (`Widget`)** → ch03
- **`fold` / `where`** → ch03
- **Formatting** → ch10
- **`Future` / `.then`** → ch08, ch09
- **`Future.onError`** → ch09
- **Getters and setters** → ch04
- **`group` / `test` / `expect`** → ch07
- **Initializer lists** → ch04, ch06
- **ISP / `UnimplementedError`** → ch06
- **`log` (`dart:developer`)** → ch09
- **LSP / Square–Rectangle** → ch06
- **Magic numbers** → ch02
- **Mental mapping** → ch02
- **Named parameters / `required`** → ch03, ch02
- **Naming** → ch02, ch03
- **Newspaper order (callers above callees)** → ch10
- **Null safety (`T?`, `required`)** → ch02, ch05, ch03
- **OCP** → ch06
- **`package:test`** → ch07
- **Polymorphism** → ch03, ch06
- **Privacy (`_`)** → ch04
- **Side effects** → ch03
- **SOLID** → ch06
- **Spread (`...`)** → ch03
- **SRP** → ch06
- **Super parameters** → ch05, ch06
- **Tear-offs** → ch03
- **Testing / TDD** → ch07
- **3 Rs (readable, reusable, refactorable)** → ch01
- **Type tests (`is`)** → ch03, ch06

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions and chapter refs
- [patterns.md](patterns.md) — 27 concrete refactoring techniques with trade-offs
- [cheatsheet.md](cheatsheet.md) — thresholds, decision trees, escalation ladder, tells & smells, JavaScript habits to drop

## Related Skills — the clean-code family

- **`clean-code-java`** — Robert C. Martin's original *Clean Code*, the book itself (17 chapters + Appendix A) and the family's canonical reference. Go there for what this guide leaves thin or out — unit-test craft and TDD, concurrency proper, error-handling strategy, boundaries, systems, emergence — and for the **66-item smells-and-heuristics catalogue** and the long-form **refactoring case studies**.
- **`clean-code-javascript`** — Ryan McDermott's guide, **the direct parent this one was ported from** (the README's first line says so). Go there for the seven rules the port dropped (avoid type-checking ×2, don't over-optimize, don't write to global functions, `Object.assign` defaults, ES2015 classes, Promises over callbacks) and the reasoning behind the two rules it reverses.
- **`clean-code-typescript`** — labs42io's adaptation. Use it when the code is TypeScript, or for typed-language material this guide lacks: the immutability ladder (`readonly` → `as const`), unions instead of `instanceof` chains, and the `Failable<R, E>` result type.
- **`clean-code-python`** — Rigel Di Scala's adaptation. Use it when the code is Python; also the family's treatment of mixins and of a type checker (mypy) as the LSP referee, neither of which this guide covers.
- **`clean-code-php`** — adapted from piotrplenik/clean-code-php. Use it when the code is PHP.
- **`clean-code-csharp`** — adapted from thangchung/clean-code-dotnet. Use it when the code is C#/.NET.
- **`clean-code-go`** — adapted from Pungyeon's *Clean Go Code*. Use it when the code is Go.
- **`clean-code-ruby`** — adapted from uohzxela/clean-code-ruby. Use it when the code is Ruby.
- **`clean-code-swift`** — adapted from MaatheusGois/clean-code-swift. Use it when the code is Swift.
- **`clean-code-universal`** — the family's shared core, distilled from Martin's book across its adaptations, with **every rule tagged by tier**: Tier 1 assumes only that you can name something and run some verification, Tier 2 binds only where a specific construct exists, and Tier 3 is language idiom owned by the matching sibling — for Dart's cascades, `_` privacy and `const` defaults, that is this skill. **Use it for any language the family does not cover** — Rust, Kotlin, C++, Scala and the rest — **and for configuration and infrastructure-as-code, which no sibling covers at all**: YAML (Kubernetes, Helm, CI pipelines), Terraform/HCL, SQL, Bash and Dockerfile.

---

## Scope & Limits

Covers the clean-code-dart guide only — its README, 39 rules in 10 sections (introduction aside), written February–March 2023. It is **not a style guide**: it defers to *Effective Dart* and never mentions `dart format`, `dart analyze`, lint packages or `analysis_options.yaml`. It is a close port of clean-code-javascript (46 rules); the seven it dropped have no Dart replacement.

**Testing and concurrency are one rule each.** Testing is "single concept per test" plus a coverage paragraph; concurrency is "async/await instead of then" — `Future`s only, with nothing on `Stream`s, `async*`, isolates, `Future.wait` or shared state. For depth, use **clean-code-java** (ch. 9 and ch. 13 + Appendix A).

**It is not a Flutter guide.** Flutter appears once, in the duplicate-code example (`Widget`, `CustomCard`). Nothing on widget composition, `build` method size, `const` constructors, state management or widget tests. The rules apply to Flutter code because it is Dart code, and no further.

**Dart features it doesn't cover**: mixins (`with`), extension methods, generics, enums (named only), factory and `const` constructors, `late`, `!` and null-safety practice beyond `?`, `??` and `required`, doc comments (`///`), equality and `hashCode`, and immutability tools — its "great libraries" link is JavaScript's immutable-js, a leftover from the parent.

**It predates Dart 3** (May 2023): no records, patterns or destructuring, `sealed` or `interface`/`base`/`final` class modifiers, or switch expressions. Where the guide replaces an `is` chain or a type `switch` with overrides, Dart 3's `sealed` classes with an exhaustive `switch` are now a compiler-checked alternative for closed hierarchies; the guide doesn't weigh them, and this skill doesn't add a rule for them.

**Some snippets wouldn't compile as printed, and a few explanations are loose**: the merged `buildEmployeeCard` uses undefined `manager`/`developer` (ch03); `_` is library-private, not class-private as the guide says (ch04); `log` is called "isn't much better", then offered as Option 1 (ch09); SRP's Good builds the `UserAuth` that DIP would inject (ch06); some examples use untyped parameters and `forEach` with function literals, which *Effective Dart* advises against. The Dart version is inferred from the examples; the guide states none. No source images were read.
