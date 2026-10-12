---
name: clean-code-csharp
description: "Knowledge base from \"clean-code-dotnet\" by Thang Chung et al. — Robert C. Martin's Clean Code principles adapted for C# and .NET. Use when writing or reviewing C# and you need rules for Hungarian notation and .NET casing, magic strings and enums, guard clauses, records as parameter objects, flag parameters and side effects, polymorphism and type patterns over type checks, singletons versus DI and IOptions, properties over public fields, composition over inheritance, SOLID through interfaces, xUnit Arrange-Act-Assert tests, async void and .Result, throw vs throw ex, .editorconfig naming rules, and #region and comment hygiene. Part of the clean-code skill family; for the original book (Java examples, smells catalogue, refactoring case studies) use clean-code-java; for another language use its sibling (clean-code-typescript, -javascript, -python, -php, -go, -ruby, -dart, -swift); for any other language, including Rust, Kotlin, C++, Scala, YAML, Terraform, SQL and Bash, use clean-code-universal."
---

<!-- argument-hint: [topic, principle name like LSP, or chapter number] -->

# clean-code-csharp
**Source**: [thangchung/clean-code-dotnet](https://github.com/thangchung/clean-code-dotnet) — "Clean Code concepts adapted for .NET/.NET Core", with C# examples; inspired by ryanmcdermott/clean-code-javascript and jupeter/clean-code-php (MIT, commit `a604cf9`, 2026-02-27)
**Author**: Thang Chung (thangchung) + 16 contributors, chiefly ngohungphuc and hippieZhou | **Size**: ~9,500 words · 53 rules · **Chapters**: 15 | **Targets**: C# 12 / .NET 8+ for the newest examples (primary constructors, collection expressions; records from C# 9); the prose is older, and the async tables date from .NET Framework 4.5 — the guide names no version | **Generated**: 2026-10-12

## How to Use This Skill

- **Without arguments** — load the core rules below for reference
- **With a topic** — ask about `async void`, `throw ex`, `singletons`, `records`, `#region`, `.editorconfig`; I find and read the relevant chapter
- **With a principle** — ask about `LSP` or `DIP` → [ch09](chapters/ch09-solid.md)
- **With a chapter** — ask for `ch12`; I load that chapter file
- **Fastest path while coding** — [cheatsheet.md](cheatsheet.md): thresholds, casing, decision trees, tells
- **Browse** — ask "what chapters do you have?" for the full index

When you ask about something not covered below, I read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

### The root rule
**Functions should do one thing.** The guide calls it "by far the most important rule in software engineering … If you take nothing else away from this guide other than this, you'll be ahead of many developers." Most other rules detect violations of it: a third parameter, a `bool` flag, a vague verb (`Handle`), orchestration mixed with loops, a `switch` on a type code, a method that rewrites shared state. **Test**: if you need "and" to describe it, split it.

### The quality standard
Judge code on whether it is **readable, reusable, refactorable**. These are "guidelines and nothing more" — "even fewer will be universally agreed upon" — so override with a stated reason, never by accident. It is explicitly **not a style guide**: formatting goes to `.editorconfig`.

**Copy the shape, not the snippet.** The source is a port of the JavaScript and PHP lists, and many examples don't compile as written (single-quoted strings, `explode`, `tokens[] = …`, `pubic`). The chapters here reproduce them lightly repaired and say what changed.

### What makes this adaptation distinct: let the type system and .NET do the work
Where the JavaScript original relies on discipline, the C# version moves the rule into a language or framework construct:
- **Type checks → signatures and interfaces.** `Combine(dynamic, dynamic)` + `TryParse` → `Combine(int, int)`. Behaviour that varies by type → an `I`-prefixed interface with one class per case (`IAirplane`, `IAdapter`). When you can't change the types, a **type pattern** (`vehicle is Bicycle bicycle`) beats `GetType() == typeof(…)` + `as`.
- **Getters and setters → properties.** Private `_balance`, get-only `Balance`, and intention-revealing mutators (`WithdrawBalance`). Default to `{ get; }`; a C# 12 **primary constructor** sets it: `class Employee(string name) { public string Name { get; } = name; }`.
- **Parameter objects → `record`s.** `public record MenuConfig(string Title, string Body, string ButtonText, bool Cancellable);` built with named arguments. Owned values too: `record EmployeeTaxData(...)` held as `EmployeeTaxData? TaxData { get; private set; }`.
- **Globals and singletons → constructor injection and the Options pattern.** `DBConnection(IOptions<DbConnectionOption> options)`, resolved from the IoC container; `Manager(IEnumerable<IEmployee> employees)` receives every registered implementation.
- **Filtering → LINQ.** `openingDays.Any(d => d == day.ToLower())`, `db.Find(clients).Where(...)`.
- **Errors → typed exceptions.** `throw;` not `throw ex;`; one `catch` per type; wrap with the original as inner exception.
- **Concurrency → `Task` and `async`/`await`, all the way.** No `async void`, no `.Result`; `WhenAll`, `WhenAny`, `Delay`.
- **Style → `.editorconfig`.** PascalCase constants, `_camelCase` private fields, `s_` statics, Allman braces — as analyzer suggestions.
- **Positional markers include `#region`.**

### Naming and variables
- Name the **purpose**, never the type or provenance: `daySinceModification`, not `d`; `listOfEmployee`, not `dataFromDb`. **No Hungarian notation** — parameters included (`pDay` → `day`).
- **Casing per symbol kind**: PascalCase types, methods, properties, constants; camelCase locals and parameters. The source's own `ADMIN_ROLE` and `ACCESS_READ` break this — follow the rule.
- **Return early**: guard clauses at the top, one flat happy path; replace value ladders with a collection and LINQ.
- **No magic strings or numbers** — they "cannot automatically be updated using refactoring tools." Use a `const` or an `enum`.
- **Searchable**: named types over anonymous objects; **named regex groups** `(?<city>…)` over indices.
- **One word per concept** (`GetUser()`), **no repeated context** (`Car.Make`), **defaults in the signature**.

### Functions
- **Arguments: 0 ideal · 1–2 ok · 3 avoid · 4+ consolidate** — "more than three leads to a combinatorial explosion" of test cases.
- **No flags** — "A flag indicates that the method has more than one responsibility." `CreateFile` / `CreateTempFile`.
- **Name the action** — `Send()`, not `Handle()`.
- **One level of abstraction**, climbed in three tiers: one method → extracted methods → separate classes injected by a primary constructor (`BetterJSAlternative(Tokenizer tokenizer, Lexer lexer)`).
- **Callers above callees** — read like a newspaper.
- **No side effects**: value in, value out. Unavoidable effects go in "one service … One and only one."
- **Delete dead code**; the history keeps it.

### Conditionals, types and global state
- **Positive predicates** (`IsDOMNodePresent`), **encapsulated conditions** (`article.IsPublished()`).
- **Avoid conditionals** with polymorphism: "When you have classes and functions that have `if` statements, you are telling your user that your function does more than one thing."
- **No global functions, no Singletons.** Button's four charges: hidden dependencies, two responsibilities (it controls its own lifecycle), tight coupling that resists fakes, and state that makes "tests need to be ordered."

### Objects and classes
- Properties give validation, logging, lazy loading and overriding later without touching callers; the source ties this to OCP.
- **Method chaining** via extension methods that return the receiver.
- **Composition over inheritance.** Inherit when it's **is-a** (not has-a), you **reuse** base code, and you **want base changes to propagate**.

### SOLID, in C#'s own terms
- **SRP** — "There should never be more than one reason for a class to change." Extract `UserAuth` from `UserSettings`.
- **OCP** — "open for extension, but closed for modification." `IAdapter.Request` replaces `if (adapterName == "ajaxAdapter")`. (The Bad example compares against `"httpNodeAdapter"` while `NodeAdapter` calls itself `"nodeAdapter"`, so that branch can never run — magic strings at work.)
- **LSP** — base and child "can be used interchangeably without getting incorrect results." Square–Rectangle: area **25, should be 20**. Make them siblings under `abstract class ShapeBase`. **Caveat**: the source's Good consumer still branches on `is Square`, contradicting its own type-checking rule; give shapes their dimensions at construction so the consumer only calls `GetArea()` (Ch 9).
- **ISP** — "Clients should not be forced to depend upon interfaces that they do not use." Role interfaces `IWorkable`, `IFeedable`, composed by interface inheritance; `Robot` implements only `IWorkable`.
- **DIP** — depend on abstractions; .NET's DI is the familiar implementation ("not identical concepts"). Inject interfaces through the constructor.

### DRY — with its caveat
"Duplicate code is bad because it means that there's more than one place to alter something." Merge near-miss duplicates over a shared abstraction (`ShowList(IEnumerable<Employee>)`). But **"Bad abstractions can be worse than duplicate code, so be careful!"** — if the merge needs a flag or a type test, don't.

### Tests, async, errors, formatting, comments
- **"Testing is more important than shipping."** 100% statement and branch coverage as the aim; **one concept per test**, Arrange–Act–Assert, xUnit `[Fact]`.
- **Async**: avoid `async void` (event handlers excepted), async all the way, `ConfigureAwait(false)` where context isn't needed; `await` for I/O, a `LongRunning` task for heavy computation. The tables date from 2013.
- **Errors**: never swallow; `throw;` to rethrow; `throw new CustomException("info", ex)` to add context; typed `catch` blocks, most specific first.
- **Formatting**: commit an `.editorconfig`.
- **Comments**: "Comments are an apology, not a requirement." WHAT → a name; WHY → keep. No banners, `#region`, commented-out code or journals.

---

## Chapter Index

| # | Title | Key Rules |
|---|-------|-----------|
| [ch01](chapters/ch01-introduction.md) | Introduction | 3 Rs, guidelines not laws, port lineage, C# version map |
| [ch02](chapters/ch02-naming.md) | Naming | bad and misleading names, Hungarian notation, casing, pronounceable, camelCase, domain names |
| [ch03](chapters/ch03-variables.md) | Variables | return early, mental mapping, magic strings, unneeded context, searchable names, `enum`s, named regex groups, default arguments |
| [ch04](chapters/ch04-functions.md) | Functions | do one thing, ≤2 args + `record`, names, abstraction ladder, newspaper order, flags, side effects, dead code |
| [ch05](chapters/ch05-conditionals-and-type-checks.md) | Conditionals and Type Checks | negative conditionals, polymorphism, type patterns, no `dynamic`, encapsulated conditionals |
| [ch06](chapters/ch06-global-state-and-singletons.md) | Global State and Singletons | no global functions, Singleton anti-pattern, `IOptions<T>`, IoC |
| [ch07](chapters/ch07-objects-and-data-structures.md) | Objects and Data Structures | properties over fields, get-only members, primary constructors |
| [ch08](chapters/ch08-classes.md) | Classes | fluent extension methods, composition over inheritance, `record` + nullable property |
| [ch09](chapters/ch09-solid.md) | SOLID | SRP, OCP, LSP (Square–Rectangle), ISP (role interfaces), DIP (constructor injection) |
| [ch10](chapters/ch10-dry.md) | Don't Repeat Yourself (DRY) | restaurant inventory, bad-abstraction caveat, merge then compact |
| [ch11](chapters/ch11-testing.md) | Testing | coverage, single concept per test, AAA, xUnit |
| [ch12](chapters/ch12-concurrency.md) | Concurrency | `async void`, async all the way, `ConfigureAwait`, `WhenAll`/`WhenAny`/`Delay`, I/O vs CPU |
| [ch13](chapters/ch13-error-handling.md) | Error Handling | `throw;` vs `throw ex;`, no swallowing, typed catch blocks, inner exceptions |
| [ch14](chapters/ch14-formatting.md) | Formatting | `.editorconfig`, naming rules, severities |
| [ch15](chapters/ch15-comments.md) | Comments | positional markers and `#region`, commented-out code, journals, WHAT vs WHY |

## Topic Index

- **3 Rs (readable, reusable, refactorable)** → ch01
- **AAA (Arrange–Act–Assert)** → ch11
- **Abstraction levels** → ch04
- **Anonymous types** → ch03
- **Arguments (function)** → ch04
- **`async void`** → ch12, ch13
- **`async`/`await`, async all the way** → ch12
- **Braces (Allman)** → ch14
- **Capitalization / casing** → ch02, ch14, ch03
- **Catch blocks (multiple, typed)** → ch13
- **Collection expressions** → ch03, ch10, ch01
- **Comments (WHAT vs WHY)** → ch15
- **Composition over inheritance** → ch08
- **`ConfigureAwait(false)`** → ch12
- **Constants (`const`)** → ch03, ch14
- **Coverage** → ch11
- **Dead code** → ch04, ch15
- **Default arguments** → ch03
- **Dependency injection / DIP** → ch09, ch06, ch04
- **DRY / duplication** → ch10
- **`dynamic`** → ch05
- **`.editorconfig`** → ch14
- **Enums** → ch03
- **Exceptions (`throw;`, inner exception)** → ch13
- **Extension methods** → ch08
- **Flags (boolean parameters)** → ch04
- **Getters and setters / properties** → ch07
- **Global functions / global state** → ch06
- **Guard clauses / return early** → ch03
- **Hungarian notation** → ch02
- **Interfaces (`I`-prefixed)** → ch05, ch09
- **ISP / role interfaces** → ch09
- **Journal comments** → ch15
- **LINQ** → ch03, ch04
- **LSP / Square–Rectangle** → ch09
- **Magic strings and numbers** → ch03
- **Mental mapping** → ch03
- **Method chaining / fluent** → ch08
- **Naming** → ch02, ch03, ch04
- **Negative conditionals** → ch05
- **Newspaper order (callers above callees)** → ch04
- **Nullable reference types** → ch08
- **OCP** → ch09, ch05
- **Options pattern / `IOptions<T>`** → ch06
- **Parameter objects** → ch04
- **Pattern matching / type patterns** → ch05, ch14
- **Polymorphism over conditionals** → ch05, ch09
- **Port artifacts** → ch01
- **Primary constructors** → ch07, ch04, ch08, ch09
- **`record`** → ch04, ch08
- **Regex (named groups)** → ch03
- **`#region`** → ch15
- **Searchable names** → ch03
- **Side effects** → ch04, ch08
- **Singleton pattern** → ch06, ch02
- **SOLID** → ch09
- **SRP** → ch09
- **`Task.WhenAll` / `WhenAny` / `Delay`** → ch12
- **Testing / xUnit** → ch11
- **`throw ex` vs `throw`** → ch13
- **Type checking (`GetType`, `is`)** → ch05
- **Unneeded context** → ch03
- **`var`** → ch14
- **Vocabulary consistency** → ch03

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions and chapter refs
- [patterns.md](patterns.md) — 30 concrete refactoring techniques with trade-offs
- [cheatsheet.md](cheatsheet.md) — thresholds, casing, decision trees, tells & smells

## Related Skills — the clean-code family

- **`clean-code-java`** — Robert C. Martin's original *Clean Code*, the book itself and the family's canonical reference. **Java is C#'s closest sibling**, so the book's examples read almost as C#. Go there for the rationale behind the rules here, for what this guide omits — TDD's three laws and F.I.R.S.T., boundaries, systems, emergence, deep concurrency, the legitimate comment kinds, never return or pass `null` — and for the **66-item smells-and-heuristics catalogue** and the **refactoring case studies**.
- **`clean-code-typescript`** — labs42io's adaptation, the family's other typed, interface-based language. Use it for TypeScript, or for typed material this guide lacks: the immutability ladder, unions instead of `instanceof`, and the `Failable<R, E>` result type as an alternative to throwing.
- **`clean-code-javascript`** — Ryan McDermott's guide, **one of this guide's two parents**. Use it for JavaScript, or to see a rule in its original form.
- **`clean-code-python`** — Rigel Di Scala's adaptation. Use it for Python; also SOLID one chapter per principle, with mypy as LSP referee.
- **`clean-code-php`** — from piotrplenik/clean-code-php (linked here under its old jupeter/ name), **this guide's other parent** and the source of the `explode` and `tokens[] =` left in some examples. Use it for PHP.
- **`clean-code-go`** — from Pungyeon's *Clean Go Code*. Use it for Go.
- **`clean-code-ruby`** — from uohzxela/clean-code-ruby. Use it for Ruby.
- **`clean-code-dart`** — from williambarreiro/clean-code-dart. Use it for Dart or Flutter.
- **`clean-code-swift`** — from MaatheusGois/clean-code-swift. Use it for Swift.
- **`clean-code-universal`** — the family's shared core, with every rule tagged by tier; Tier 3 (language idiom — here records, properties, `IOptions<T>`, `throw;`) routes back to this skill. **Use it for languages with no sibling** — Rust, Kotlin, C++, Scala — **and for YAML, Terraform/HCL, SQL, Bash and Dockerfile**, which no sibling covers.

---

## Scope & Limits

Covers the English README at commit `a604cf9`: 56 entries — 53 rules (the two-part entries count twice) and 3 framing notes. A ~9,500-word community list, **not the book**. Not used: `README-zh.md` (a translation of an older revision) and the `cheatsheets/` PDFs (book summaries from charlax/professional-programming).

**Omitted or barely touched** — mostly covered by `clean-code-java`:
- **Testing** is one rule: no TDD laws, F.I.R.S.T., test doubles or xUnit `[Theory]`.
- **Null handling**: no "don't return `null`" rule; nullable reference types appear once, and the source's own `Configuration.Get` returns `null`.
- **Errors**: no exception filters (`catch … when`), exception-type design, or `IDisposable`/`using`.
- **Comments** never mention XML doc comments (`///`) or `// TODO`.
- **Classes**: no size or cohesion rule, no Law of Demeter.
- **Immutability** (`readonly`, `init`, `required`) and **LINQ** appear only in examples; **`var`** is left undecided.

**Dated**:
- The **async tables** are from 2012–2013 (a gist citing Stephen Cleary). Since then: `async Task Main` (C# 7.1) removes the console exception; `ConfigureAwait(false)` matters mainly in libraries and UI apps; `AsyncLazy<T>`/`AsyncCollection<T>` are Nito.AsyncEx, not BCL; `ValueTask`, `IAsyncEnumerable<T>` and Channels are missing. [ch12](chapters/ch12-concurrency.md) marks these.
- **Tooling**: the README's Tools list is not offered as advice. CodeMaid has had no release since Nov 2021; Sharpen since Oct 2019, and it stops at C# 8; tslint-clean-code targets TypeScript on the deprecated TSLint. The live tooling rule is `.editorconfig` ([ch14](chapters/ch14-formatting.md)); the source doesn't say how to enforce it in a build.

**The examples are a port, and many don't compile** (single-quoted strings, `pubic`, PHP's `explode`, JavaScript's `data.length`). Chapters reproduce them **lightly repaired**, marking each repair. Where an example contradicts the source's own rules, the chapter follows the rule and says so: `ADMIN_ROLE`/`ACCESS_READ` vs PascalCase constants and the Fibonacci boundary shift ([ch03](chapters/ch03-variables.md)), a Singleton as the domain-names example ([ch02](chapters/ch02-naming.md)), the LSP fix still type-checking `is Square` ([ch09](chapters/ch09-solid.md)), and `ConvertTo32BitInt`, a no-op in C# ([ch15](chapters/ch15-comments.md)).

**Licence**: LICENSE is MIT, "Copyright (c) 2017 Thang Chung"; the README footer also states a CC0 waiver. No source images were read.
