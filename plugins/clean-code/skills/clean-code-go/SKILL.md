---
name: clean-code-go
description: "Knowledge base from \"Clean Go Code\" by Lasse Martin Jakobsen (Pungyeon) — Robert C. Martin's Clean Code principles adapted for Go. Use when writing or reviewing Go and you need rules for doc vs why comments, naming functions by depth and variables by scope, 5–8 line functions and early returns out of indentation hell, 1–2 parameter signatures and Options structs, globals and variable shadowing, sentinel errors over magic strings, nil-safe getters, pointer scope and mutability, closures vs interfaces, compile-time interface checks, the embedded-interface trap, accept interfaces/return concrete types, and hiding interface{}. Part of the clean-code skill family; for the original book (Java examples, smells catalogue, refactoring case studies) use clean-code-java; for another language use its sibling (clean-code-typescript, -javascript, -python, -php, -csharp, -ruby, -dart, -swift); for any other language, including Rust, Kotlin, C++, Scala, YAML, Terraform, SQL and Bash, use clean-code-universal."
---

<!-- argument-hint: [topic, rule name like shadowing or sentinel errors, or chapter number] -->

# clean-code-go
**Source**: [Pungyeon/clean-go-article](https://github.com/Pungyeon/clean-go-article) — *Clean Go Code*, "a reference for the Go community that aims to help developers write cleaner code" (no licence file, commit `f18fd5f`, 2023-01-31)
**Author**: Lasse Martin Jakobsen (Pungyeon) + 15 contributors, chiefly Aleksandr Hovhannisyan | **Size**: ~12,200 words · 16 rules · **Chapters**: 10 | **Targets**: pre-generics Go (≤ 1.17; written 2019, before Go 1.18's type parameters — uses `interface{}`, `ioutil.Discard`, and `errors.Is` from 1.13) | **Generated**: 2026-10-12

## How to Use This Skill

- **Without arguments** — the core rules below are the working set for writing and reviewing Go.
- **With a topic** — ask about `shadowing`, `sentinel errors`, `pointers`, `embedded interfaces`; I read the relevant chapter first.
- **With a chapter** — ask for `ch06`; I load that chapter file.
- **Browse** — ask "what chapters do you have?" for the full index.
- **Fastest path while coding** — [cheatsheet.md](cheatsheet.md): thresholds, decision rules, ladders, tells.

Code in the chapters is **lightly corrected to valid Go**; the article's snippets carry typos (each chapter says which). Copy the shape, and check Scope & Limits for what is dated.

---

## Core Frameworks & Mental Models

### The root rule: write for the reader who has to decode it
*"We don't read code, we decode it"* (Peter Seibel, quoted in the preface). The goals are readability, testability and maintainability, and the main lever is **short functions** — "typically 5–8 lines in Go" — for **comprehension**, not deduplication. A clean refactor often *adds* lines: "we cannot measure the cleanliness of our code by the number of lines it uses."

### What makes the Go take distinct: scope and mutability are the unifying idea
The JavaScript, Python and TypeScript siblings organise around classes and SOLID. This article has neither; it keeps returning to **how far a value reaches and who can change it** — its summary asks you to "limit the scope of a variable as much as possible" and to limit pointers' "scope and mutability to an absolute minimum."
- **Names follow scope, in opposite directions.** Functions get *more* specific deeper in the call tree (`Parse` → `parseJSON` → `fileExtension`); variables get *less* specific as scope narrows (`beerBrands` → `b`). Short names belong where scope is tiny. Never name a variable after its type — "you wouldn't name your pets 'dog' or 'cat'" (Dave Cheney).
- **No mutable globals** — they "don't belong in clean code."
- **Shadowing is a scope bug, not a syntax bug.** `val, err := …` inside a `case` declares a new `val`. Delete the wide `var` and extract a function that *returns* the value.
- **Declare at first use**, then name the setup as a constructor (`NewSenderChannel()`).
- **A pointer parameter expands scope** — "*almost* … to the global level."
- **Unexported field behind methods** is Go's tool for public immutability (there is no `const struct`) and for nil safety.

### Return early — push the code to the left
Nested `if x, ok := …; ok {` ladders are **indentation hell**, common around `interface{}` type assertions. Return each failure at once so the happy path runs down the left margin. *"If the `value, err :=` pattern is repeated more than once in a function"*, split it; the result reads in **onion layers**, 3–5 lines at a time.

### Signatures: one or two parameters
*"Function signatures should only contain one or two input parameters"*; three only exceptionally. Past that, an **Options struct**: named fields replace argument-label comments, order stops mattering, and zero values become the defaults (`QueueDeclare(QueueOptions{Name: "hello"})`). **Wrap** third-party signatures you can't change.

### Errors are values — make them comparable
Never make callers match `err.Error()` text (a **magic string**). Export **sentinel errors** (`var ErrItemNotFound = errors.New(…)`) and compare with `errors.Is`. Return a defined `NullItem` with nil-able fields initialised rather than `Item{}` — though "in many scenarios, invoking a panic will actually be preferable." For dynamic detail, the author keeps a sentinel inside an `ErrorDetails` type, a design that predates idiomatic `%w` wrapping (see Scope & Limits).

### nil, pointers and mutability
"Things break when you try to access methods or properties of a `nil` value": avoid returning `nil`, and hide nil-able fields behind a **nil-safe getter** (`app.Cache()` creates the cache on first use). Use mutability "only … when it's necessary." The pointer test is **ownership**: a store that keeps a caller's pointer, or returns its own, lets other code rewrite its data (the article's password-clearing bug). **Stores take values and return values**; a pointer is fine when "the function invoker remains the sole owner." Shared pointers across goroutines risk data races.

### Interfaces and composition, not inheritance
- **Implicit satisfaction** makes interfaces hard to see, so keep them **small** — which also makes mocks four lines long.
- **Assert at compile time**: `var _ io.Writer = &NullWriter{}` — "generally the preferred solution."
- **Embed structs for shared fields**, built by one constructor, so a new field or method reaches every embedding type in one change.
- **Never embed an interface to claim it.** `type NullWriter struct{ io.Writer }` compiles and panics on the first `Write`; overriding one method of an embedded `io.ReadCloser` leaves `Close` calling `nil`. "Go doesn't support inheritance."
- **Accept interfaces, return concrete types** — Postel's law: *"Be conservative in what you do; be liberal in what you accept from others."*

### Closures and the empty `interface{}`
A function value is "an input parameter like any other": replace a growing operation `switch` with one, and use a **closure factory** (`concat(data)`) when operations need different inputs. Simple operation → closure; once its logic "becomes complex, one should strongly consider using an interface instead." `interface{}` turns Go into "a dynamically typed language": fine *inside* a concrete-typed API (`fmt.Println`, `json.Decode`), never as your public contract — use concrete types, or a **typed wrapper** with a single cast point.

### Ground rules
- **`gofmt`**: "homogeneous code is more important than having complete expressive freedom" — from an author who dislikes some of its choices.
- **Comments**: doc-comment exported identifiers; any other comment must say **why**, not how — and usually a rename says it better.
- **TDD**: test, pass, refactor, repeat. **No fanaticism**: a codebase is never fully clean, "in the same way that your office desk probably isn't either."

---

## Chapter Index

| # | Title | Key Rules |
|---|-------|-----------|
| [ch01](chapters/ch01-introduction.md) | Introduction | decode not encode, `gofmt` homogeneity, TDD cycle, the summary as a checklist, no fanaticism |
| [ch02](chapters/ch02-comments.md) | Comments | doc vs other comments, why not how, tutorial comments, rename instead of comment |
| [ch03](chapters/ch03-naming.md) | Naming | function names by depth, variable names by scope, keep the verb, no type names |
| [ch04](chapters/ch04-functions.md) | Functions | 5–8 lines, indentation hell, push left, `value, err :=` rule, Options struct, wrappers |
| [ch05](chapters/ch05-variables.md) | Variables | no globals, shadowing, return don't reassign, declare at use, unexported fields |
| [ch06](chapters/ch06-return-values-and-errors.md) | Return Values and Errors | magic strings, sentinel errors, `errors.Is`, `NullItem`, `ErrorDetails` |
| [ch07](chapters/ch07-nil-and-pointers.md) | Nil Values and Pointers | nil-safe getter, pointer scope, ownership, values in/values out |
| [ch08](chapters/ch08-closures.md) | Closures Are Function Pointers | function parameters, closure factories, closure vs interface |
| [ch09](chapters/ch09-interfaces.md) | Interfaces and Composition | small interfaces, `var _ I = &T{}`, embedded structs, embedded-interface trap, accept interfaces |
| [ch10](chapters/ch10-empty-interface.md) | The Empty `interface{}` | dynamic typing, `json.Decode`, generic store smell, typed wrapper |

## Topic Index

- **Accept interfaces, return concrete types** → ch09
- **`any` / generics (dated)** → ch10, ch08
- **Closures / function values** → ch08
- **Comments (doc, why, tutorial)** → ch02
- **Compile-time interface assertion** → ch09
- **Composition / embedded structs** → ch09
- **Constructors (`NewX`)** → ch05, ch09
- **Data races** → ch07
- **Declaration at use** → ch05
- **Defined values / `NullItem`** → ch06
- **Early return / push left** → ch04
- **Embedded interfaces** → ch09
- **`errors.Is`** → ch06
- **`ErrorDetails` / dynamic errors** → ch06
- **Function length** → ch04
- **Function naming** → ch03
- **Global variables** → ch05
- **`gofmt`** → ch01
- **Immutability (unexported fields)** → ch05
- **Indentation hell** → ch04, ch10
- **Inheritance (absence of)** → ch09
- **Interfaces (small, implicit)** → ch09
- **`interface{}`** → ch10, ch04
- **Magic strings** → ch06
- **Mocking / `NullWriter`** → ch09
- **Mutability** → ch07, ch05
- **nil / nil-safe getter** → ch07, ch06
- **Onion layering** → ch04
- **Options struct** → ch04
- **Ownership (pointers)** → ch07
- **Parameters (count)** → ch04
- **Pointers** → ch07
- **Postel's law** → ch09
- **Sentinel errors** → ch06
- **Shadowing** → ch05
- **TDD** → ch01
- **Type assertions** → ch04, ch10
- **Typed wrapper** → ch10
- **Variable naming** → ch03
- **Variable scope** → ch05, ch07
- **Wrapping third-party code** → ch04, ch10
- **Zero values** → ch04, ch06

## Supporting Files

- [cheatsheet.md](cheatsheet.md) — thresholds, decision rules, escalation ladders, tells & smells, and the judgment calls the article leaves open
- [patterns.md](patterns.md) — 23 concrete techniques with when/how/trade-offs
- [glossary.md](glossary.md) — all key terms with chapter references

## Related Skills — the clean-code family

- **`clean-code-java`** — Robert C. Martin's original *Clean Code*, the book itself (17 chapters + Appendix A) and the family's canonical reference. Go there for everything this article omits — classes and SRP, SOLID, boundaries, systems, concurrency, the full comment taxonomy, unit-test discipline — and for the **66-item smells-and-heuristics catalogue** and the long-form **refactoring case studies**.
- **`clean-code-typescript`** — labs42io's adaptation. Use it when the code is TypeScript; also the home of the `Failable<R, E>` result type, a contrasting answer to Go's error values.
- **`clean-code-javascript`** — Ryan McDermott's guide. Use it when the code is JavaScript, or for closures and SOLID in a language without interfaces.
- **`clean-code-python`** — Rigel Di Scala's adaptation. Use it when the code is Python; its duck-typed dependency inversion is the family's nearest relative of Go's implicit interfaces.
- **`clean-code-php`** — adapted from piotrplenik/clean-code-php. Use it when the code is PHP.
- **`clean-code-csharp`** — adapted from thangchung/clean-code-dotnet. Use it when the code is C#/.NET.
- **`clean-code-ruby`** — adapted from uohzxela/clean-code-ruby. Use it when the code is Ruby.
- **`clean-code-dart`** — adapted from williambarreiro/clean-code-dart. Use it when the code is Dart or Flutter.
- **`clean-code-swift`** — adapted from MaatheusGois/clean-code-swift. Use it when the code is Swift.
- **`clean-code-universal`** — the family's shared core, distilled from Martin's book across its adaptations, with every rule tagged by tier (Tier 3, language idiom — here sentinel errors, `var _ I = &T{}`, unexported fields — is routed back to this skill). **Use it for any language the family does not cover** — Rust, Kotlin, C++, Scala and the rest — and for configuration and infrastructure-as-code: YAML (Kubernetes, Helm, CI pipelines), Terraform/HCL, SQL, Bash and Dockerfile.

---

## Scope & Limits

Covers the *Clean Go Code* article only — one ~12,200-word README, 16 rule sections (the `gofmt` note, TDD, and 14 topics under "Introduction to Clean Code" and "Clean Go"). It is **an independent article in Martin's spirit** (it quotes him once), not a section-by-section port of the book, and its thresholds are the author's own: he concedes that the parameter rule, "much like the rule that our functions should only be 5–8 lines long, … can seem quite extreme at first."

**What it omits.** Concurrency beyond a data-race note (goroutines, channels, `context`, `sync`); testing beyond the four-step TDD loop (no table-driven tests, `testing` package guidance or benchmarks); package design and naming (package names, MixedCaps, receiver names, getters without `Get`); SOLID, classes-equivalent design and DRY; `defer`, `panic`/`recover` policy, and error-string style; linters and `go vet`. Use **clean-code-java** for the principles and Effective Go / Go Code Review Comments for the idiom.

**What is dated.**
- **Pre-generics.** The closures and empty-interface chapters are framed by "the lack of generics," and the article says to use another language if you need them. Go 1.18 added type parameters and `any`; reach for those before `interface{}`. The typed-wrapper advice still holds around libraries whose APIs take `any`.
- **Errors.** It uses `errors.Is` but never `%w`, `errors.As`, `Unwrap` or `errors.Join`, and its `ErrorDetails` type is invisible to `errors.Is` because it lacks `Unwrap()`. Since Go 1.13, `fmt.Errorf("…: %w", ErrItemNotFound)` plus `errors.Is`/`errors.As` is the standard way to keep a dynamic error comparable.
- **`ioutil.Discard`** is `io.Discard` since Go 1.16.

**What is inaccurate in the source** (corrected or flagged in the chapters): it credits the doc-comment rule to `gofmt` (it comes from Effective Go and linters); its one-line naming rule ("the more specific the function, the more general its name") contradicts its own examples and summary — follow the examples; it gives "one or two" parameters in the body but "2–3" in the summary; it says `closer.ReadCloser.Close()` won't panic (it does); and many snippets don't compile as printed (`return Item, nil`, `[]bytes`, `err.Type()` on an `error`, a value where a pointer receiver is needed). Two caveats it never raises: the nil-safe getter's lazy initialisation isn't safe for concurrent first use, and returning a struct by value copies it shallowly.

**Licence.** The repository has no LICENSE file. Following the family's practice with its other adaptations, this skill paraphrases the article and quotes it only briefly, with attribution. No source images were read (the article has none).
