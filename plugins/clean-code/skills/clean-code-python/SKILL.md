---
name: clean-code-python
description: "Knowledge base from \"clean-code-python\" by Rigel Di Scala (zedr) — Robert C. Martin's Clean Code principles adapted for Python. Use when writing or reviewing Python and you need rules for naming and type hints instead of type-prefixes, magic numbers, named regex capture groups, the two-argument limit and choosing between dataclass/NamedTuple/TypedDict parameter objects, flag parameters, side effects and the global keyword, generators, SOLID worked through ABCs and mixins, using mypy to enforce LSP, interface segregation with abc.ABCMeta, duck-typed dependency inversion, and DRY with the bad-abstraction caveat. Part of the clean-code skill family; for the original book (Java examples, smells catalogue, refactoring case studies) use clean-code-java, for TypeScript use clean-code-typescript, for JavaScript use clean-code-javascript. For any other language, including YAML, Terraform, SQL and Bash, use clean-code-universal."
---

<!-- argument-hint: [topic, principle name like LSP, or chapter number] -->

# clean-code-python
**Source**: [zedr/clean-code-python](https://github.com/zedr/clean-code-python) — *Clean Code* principles adapted for Python
**Author**: Rigel Di Scala (zedr) + 16 contributors | **Size**: ~5,200 words · 19 rules · **Chapters**: 9 | **Targets**: Python 3.7+ | **Generated**: 2026-09-18

## How to Use This Skill

- **Without arguments** — load the core rules below for reference
- **With a topic** — ask about `side effects`, `LSP`, `mixins`, `parameter objects`; I find and read the relevant chapter
- **With a chapter** — ask for `ch05`; I load that chapter file
- **Browse** — ask "what chapters do you have?" for the full index

When you ask about something not covered below, I read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

### The root rule
**Functions should do one thing.** The guide calls this "by far the most important rule in software engineering" — "If you take nothing else away from this guide other than this, you'll be ahead of many developers." Every other rule is a *detector* for violating it: a third argument, a boolean flag, mixed abstraction levels, a vague verb, or a `global` statement all mean the function does more than one thing.

**Test**: if you can only describe it using "and", split it.

### The quality standard — the 3 Rs
Judge code on whether it is **readable, reusable, refactorable**. If a change improves none of the three, it's taste, not cleanliness. These are **guidelines, not laws** — "even fewer will be universally agreed upon." Override with a stated reason, never by accident. And this is explicitly **not a style guide**.

### What makes this adaptation distinct: mypy is the referee
Where the JavaScript original relies on discipline, the Python version shows **the type checker catching the violation mechanically**. The whole toolchain is `pytest` + `mypy`, and every README snippet runs in CI — which is why deliberately-bad examples need `# type: ignore` to survive it.

- **LSP breaks** surface as `Signature of "get" incompatible with supertype "View"`.
- **Side effects** that change a name's type surface as `Incompatible types in assignment`.
- **ISP violations** surface as `Can't instantiate abstract class X with abstract method y`.

**Rule**: if a checker can enforce it, enforce it there rather than in review. Reserve human judgment for what mypy cannot see — invariants, history properties, and whether an abstraction is a *good* one.

### Naming
- Make names **meaningful, pronounceable, searchable**. `ymdstr` → `current_date`.
- **Annotate the type; don't spell it in the name** — `current_date: str`. The annotation is checkable; a prefix isn't.
- **One entity, one noun** — `get_user_info`/`get_client_data`/`get_customer_record` collapse to one. **Even better**: promote the shared noun to a class with an attribute, a `@property`, and a method. Synonym drift is how duplicate implementations get born (→ DRY).
- Hoist literals to module constants, **keeping the arithmetic**: `time.sleep(86400)` → `SECONDS_IN_A_DAY = 60 * 60 * 24`.
- **Name regex sub-patterns**: `(?P<city>.+?)` read as `matches['city']`. Positional access is one group-insertion away from a silent bug.
- No mental mapping (`seq`/`item` → `locations`/`location`) — "Explicit is better than implicit." No repeated context (`car.car_color` → `car.color`).
- Put fallbacks in the signature as **default arguments**, not `or` / conditional expressions.

### Functions
- **≤2 arguments** — "ideally less than three." More parameters are "usually the sign that a function is doing too much." Bundle into a typed parameter object, and the real prize follows: you can then "move some computations… into methods belonging to the new object."
- **Parameter object ladder** (best last): 4 positional → bare `dict` ("Java-esque" — bundles but forfeits type checking) → plain class → **`NamedTuple`** (immutable) → **`@dataclass`** (mutable, `astuple()`) → **`TypedDict`** (3.8+, all keys required).
- **No flag parameters.** "Flags tell your user that this function does more than one thing." `create_file` / `create_temp_file`.
- **Name the action**: `send()`, not `handle()`.
- **One level of abstraction per function** — the parent reads as a list of intentions.
- **Avoid side effects**: "anything other than take a value in and return another value or values." Watch for `global` — it breaks idempotence *and* usually the declared type. Ask **"what if I call it twice?"**
- **Centralize unavoidable effects**: "have one (and only one) service that does it."
- **Own deliberate state in a class** — "The reason why we create instances of classes is to manage state!" Expose derived values as a `@property`.
- **Reach for generators.** Once filtering is its own function, make it lazy: `Iterator` in, `Generator` out. Splitting for correctness buys performance for free.

### SOLID, in Python's own terms
- **SRP** — "A class should have only one reason to change." Split by *reason*, not size. Extract the responsibility to a function and **inject its result** through `__init__`; keep the seam a primitive. The extracted unit becoming reusable elsewhere is the *proof* the split followed a real seam.
- **OCP** — "Incorporate new features by extending the system, not by making modifications." **Design hooks deliberately**: values vary via class attributes (`content_type`), behaviour via single-responsibility hook methods (`render_body()`). Never override the orchestrating method — one rogue override freezes the base, so "we cannot introduce… additional checks in all our `View`-derived classes." **Mixins** package reusable behaviour: inherit `object`, place **before** the target, use cooperative `super()`, never instantiate alone. Django's class-based views are the reference.
- **LSP** — a function taking a supertype must accept every subtype unchanged. The Python breach is a **signature change**, and `mypy` names it. Never silence it with `# type: ignore` — you're trading a build failure for a runtime `TypeError`. **Extra data belongs in state, not in the signature** — that one move satisfies LSP and OCP together. Type compatibility is necessary but not sufficient: Liskov & Wing require invariants and history properties too.
- **ISP** — "Keep interfaces small so that users don't end up depending on things they don't need." **Python has no interfaces — it has ABCs.** Never write a stub to satisfy an abstract member ("useless code that we will need to maintain"). Segregate: shared state in a carrier base, one ABC per capability (`Loadable`, `Saveable`), implementers inherit only what they use. And don't design interfaces for features you haven't built.
- **DIP** — "Depend upon abstractions, not concrete details." **Find the narrowest contract the dependency actually requires.** `csv.writer` "just needs an object with a `.write()` method" — so a two-line `Echo` class that *returns* the value instead of buffering it deletes a page of `seek`/`truncate` workaround code and streams instead. Duck typing *is* dependency inversion here; no ABC needed. Inject collaborators, never construct them internally.

### DRY — with its caveat
Duplicate code means "more than one place to alter something." But: **"Getting the abstraction right is critical. Bad abstractions can be worse than duplicate code, so be careful!"**

Deduplicate **logic**, not appearance. If the merge would need a flag or a role branch, abandon it — the flag is the duplication telling you the variation was real. The usual case is **near-miss** duplication: ask what the *consumer* needs, and collapse distinctions the code never reads (`Developer` + `Manager` → `Employee`), keeping the domain distinction in call-site names.

---

## Chapter Index

| # | Title | Key Rules |
|---|-------|-----------|
| [ch01](chapters/ch01-introduction.md) | Introduction | 3 Rs, guidelines not laws, mypy as referee, not a style guide |
| [ch02](chapters/ch02-variables.md) | Variables | type hints over prefixes, searchable names, named capture groups, mental mapping, default arguments |
| [ch03](chapters/ch03-functions.md) | Functions | do one thing, ≤2 args, parameter-object ladder, flags, abstraction levels, side effects, generators |
| [ch04](chapters/ch04-classes-srp.md) | Classes: Single Responsibility (SRP) | one reason to change, extract + inject, narrow contracts, reusability dividend |
| [ch05](chapters/ch05-classes-ocp.md) | Classes: Open/Closed (OCP) | hook methods, class-attribute overrides, mixins, MRO, Template Method |
| [ch06](chapters/ch06-classes-lsp.md) | Classes: Liskov Substitution (LSP) | substitutability, signature compatibility, mypy gate, invariants & history properties |
| [ch07](chapters/ch07-classes-isp.md) | Classes: Interface Segregation (ISP) | ABCs not interfaces, capability ABCs, no stubs, don't design ahead of need |
| [ch08](chapters/ch08-classes-dip.md) | Classes: Dependency Inversion (DIP) | narrowest contract, duck typing, `Echo`, injection over construction |
| [ch09](chapters/ch09-dry.md) | Don't Repeat Yourself (DRY) | restaurant inventory, bad-abstraction caveat, near-miss duplication, generalization |

## Topic Index

- **ABCs / `abc.ABCMeta`** → ch07
- **Abstraction levels** → ch03
- **`abstractmethod`** → ch07
- **Arguments (function)** → ch03
- **`astuple`** → ch03
- **Bad abstractions** → ch09
- **Class attributes (as hooks)** → ch05
- **Constants (module-level)** → ch02
- **Constructor injection** → ch04, ch08
- **Dataclasses** → ch03, ch05
- **Default arguments** → ch02
- **Dependency injection / DIP** → ch08, ch04
- **DRY** → ch09
- **Duck typing** → ch08, ch07
- **Duplication** → ch09, ch02
- **Flags (boolean parameters)** → ch03
- **Generators** → ch03
- **`global` keyword** → ch03
- **Hook methods** → ch05
- **Invariants / history properties** → ch06
- **ISP** → ch07
- **Levels of abstraction** → ch03
- **LSP** → ch06
- **Magic numbers** → ch02
- **Mental mapping** → ch02
- **Mixins** → ch05
- **MRO (method resolution order)** → ch05
- **`mypy`** → ch06, ch03, ch01
- **`NamedTuple`** → ch03
- **Naming** → ch02, ch03
- **OCP** → ch05
- **Parameter objects** → ch03
- **Properties (`@property`)** → ch03, ch02
- **`typing.Protocol`** → ch07, ch08
- **Regex (named groups)** → ch02
- **Side effects** → ch03
- **Signature compatibility** → ch06
- **SOLID** → ch04–ch08
- **SRP** → ch04
- **Streaming / `StreamingHttpResponse`** → ch08
- **Substitutability** → ch06
- **Template Method** → ch05
- **3 Rs (readable, reusable, refactorable)** → ch01
- **`# type: ignore`** → ch06, ch03
- **Type hints** → ch02, ch06
- **`TypedDict`** → ch03
- **Vocabulary consistency** → ch02

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions and chapter refs
- [patterns.md](patterns.md) — 23 concrete refactoring techniques with trade-offs
- [cheatsheet.md](cheatsheet.md) — thresholds, decision trees, escalation ladders, tells & smells

## Related Skills — the clean-code family

- **`clean-code-java`** — Robert C. Martin's original *Clean Code*, the book itself (17 chapters + Appendix A). Go there for the areas this guide omits — testing and TDD, concurrency, error handling, comments and formatting — and for the **66-item smells-and-heuristics catalogue**, the long-form **refactoring case studies**, and the rationale and thresholds behind the rules here.
- **`clean-code-typescript`** — labs42io's adaptation, for the TypeScript-native material with no Python counterpart: `readonly`/`Readonly<T>`/`as const` immutability, `type` vs `interface`, discriminated unions instead of `instanceof` chains, and the `Failable<R, E>` result type.
- **`clean-code-javascript`** — Ryan McDermott's adaptation, the direct parent document this one was adapted from: closure privacy, replacing conditionals with polymorphism, composition over inheritance, and SOLID in an untyped language.
- **`clean-code-universal`** — the family's shared core, distilled from Martin's book across its Java, TypeScript, JavaScript and Python adaptations, with **every rule tagged by tier**: Tier 1 assumes only that you can name something and run some verification, Tier 2 binds only where a specific construct exists, and Tier 3 is language idiom — `@dataclass`, `NamedTuple`, `TypedDict` — named there only so it can be routed back here. **Use it for any language this family does not cover** — Go, Rust, C#, C++, Kotlin, Ruby, PHP, Swift, Scala — **and for configuration and infrastructure-as-code, which no sibling covers at all**: YAML (Kubernetes, Helm, CI pipelines), Terraform/HCL, SQL, Bash and Dockerfile.

---

## Scope & Limits

Covers the clean-code-python guide only — 19 rules across naming, functions, SOLID, and DRY. It is **not a style guide** (it says so explicitly); use `black`/`ruff` and PEP 8 for formatting. It **omits** several areas the original book covers: testing and TDD, concurrency, error handling, comments, and formatting. For those, use **clean-code-java**, which also carries the smells-and-heuristics catalogue and the refactoring case studies.

Targets Python 3.7+ and predates some newer idioms: where it reaches for `abc.ABCMeta`, `typing.Protocol` is often the better modern choice (the guide's own mixin section carries an open `FIXME` about exactly this), and `List`/`Dict`/`Union` from `typing` can now be written `list`/`dict`/`|`.

Related skills: **clean-code-java** (the original book, plus the topics this omits), **clean-code-typescript**, **clean-code-javascript** (the direct parent document this was adapted from).
