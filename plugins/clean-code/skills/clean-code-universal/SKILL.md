---
name: clean-code-universal
description: "Language-agnostic distillation of Robert C. Martin's Clean Code, cross-checked against its Java, TypeScript, JavaScript and Python adaptations. Use when writing or reviewing code in a language with no dedicated clean-code skill — Go, Rust, C#, C++, Kotlin, Ruby, PHP, Swift, Scala — and for the declarative and configuration languages the book never covers: YAML (Kubernetes, Helm, CI pipelines), Terraform/HCL, SQL, Bash, Dockerfile. Covers naming and magic values, unit size and the do-one-thing rule, duplication with the bad-abstraction caveat, SOLID stated for modules rather than classes, failure handling, when NOT to write a comment, verification where unit tests don't exist, and the refactoring protocol. The family's shared core — for Java use clean-code-java (also home of the 66-item smells-and-heuristics catalogue), Python clean-code-python, TypeScript clean-code-typescript, JavaScript clean-code-javascript."
---

<!-- argument-hint: [topic, language or file type, tier, or chapter number] -->

# Clean Code — Universal
**Sources**: Robert C. Martin et al., *Clean Code: A Handbook of Agile Software Craftsmanship*, distilled across its Java, TypeScript, JavaScript and Python adaptations
**Scope**: any language · **Chapters**: 10 · **Generated**: 2026-09-18

## How to Use This Skill

- **Without arguments** — the Core Rules below are the working set, for code in any language.
- **With a topic** — ask about `naming`, `arity`, `duplication`, `SRP`, `error handling`, `verification`; I read the relevant chapter first.
- **With a language name** — if a sibling skill owns that language, I use it instead: Java → `clean-code-java`, Python → `clean-code-python`, TypeScript → `clean-code-typescript`, JavaScript → `clean-code-javascript`. This skill is for every language that has no sibling.
- **With a config or IaC file** — YAML (Kubernetes, Helm, a CI pipeline), Terraform/HCL, SQL, Bash, Dockerfile → **go straight to [ch09](chapters/ch09-declarative-and-config.md)**, which is where the tier machinery pays off.
- **With a tier** — ask what is `Tier 1` (or 2, or 3) and I answer from ch01's tier assignment table, the index of record.
- **With a chapter** — ask for `ch03`.
- **Fastest path while coding** — [cheatsheet.md](cheatsheet.md): thresholds, decision rules, tells.

**The tier vocabulary, in one paragraph**, because a reader who stops here still needs it. Every rule in this skill is tagged by what it *assumes about the language*, not by how important it is. **Tier 1** assumes exactly two things, and every language and every configuration format supplies both: that you can **name** something, and that you have **some verification you can run** — even if that is only a formatter, a schema check, or a committed golden render you re-run. Nothing beyond those two, which is why Tier 1 applies to a Kubernetes manifest and a Rust crate identically. **Tier 2** assumes a **specific** construct — a callable with a parameter list, a type system, a substitutability mechanism, an exception, a test runner, a thread — binds wherever that construct exists, and is stated in terms of the construct rather than the keyword; where the construct is absent the rule does not apply, and this skill says so rather than approximating it. **Tier 3** is language-specific idiom — `as const`, `@dataclass`, checked exceptions — named here only so it can be excluded and routed to the sibling that owns it.

---

## Core Rules

### The three tiers

- **Tier 1 — invariant.** Assumes exactly two things, and every language and every configuration format supplies both: that you can **name** something, and that you have **some verification you can run** — even where that verification is only a formatter, a schema check, or a committed golden render you re-run. Nothing beyond those two: no functions, no types, no classes, no exceptions, no test runner. Naming, duplication, SRP, comments and the refactoring protocol land here, and they apply to a Kubernetes manifest and a Rust crate identically.
- **Tier 2 — conditional.** Binds wherever a **specific** construct exists — a callable with a parameter list, a type system, a substitutability mechanism, an exception, a test runner, a thread. Stated in terms of the construct rather than the keyword ("the subtype", never `class`; "the test runner", never `pytest`), and carrying its own translation. Apply **the construct question** first: *what plays the part of the subtype / the exception / the test runner here?* A Helm chart has no subtype, so LSP does not apply and this skill says so rather than inventing one.
- **Tier 3 — language-specific idiom.** Out of scope **by name**, so you can tell "this skill has no rule here" from "this skill forgot". Immutability keywords, decorator syntax, prototype hygiene, `Promise.all` — those belong to `clean-code-typescript`, `clean-code-python`, `clean-code-javascript` and `clean-code-java`.

**The promise this buys you: every Tier 1 rule holds for YAML and HCL unchanged** — you never have to go hunting for a construct first, because naming and a runnable verification are already there.

### Names *(Tier 1)*

- **Intention-revealing.** The name answers why the thing exists, what it does, and how it is used. `d` → `elapsedTimeInDays`. If it needs a comment to be understood, the name lost.
- **Length is proportional to scope.** Single letters only in tiny local scopes; the longer a name has to survive and the further it is read from its declaration, the longer it earns the right to be. Test the name **at the use site**, not in the declaration.
- **One word per concept; never pun.** `get`/`fetch`/`retrieve` for the same operation breeds three duplicate implementations; the same word for two different operations hides one of them. `getUserInfo`/`getUserData`/`getUserDetails` → `getUser`.
- **Searchable.** A name you cannot grep is a name you cannot change safely. `MILLISECONDS_PER_DAY` finds every call site; `86400000` finds the ones that happen to be spelled that way, and a bare `e` or `d` finds the whole file. Single letters are the ungreppable case, which is the second reason to confine them to tiny scopes.
- **No noise words.** `Manager`, `Processor`, `Data`, `Info`, `Object`, and articles carry nothing — `ProductData` and `ProductInfo` are the same name twice. Drop the noise or find the real distinction.
- **The name must include the side effects.** A `getX` that also creates X is `createOrReturnX`; a `check_*` script that also mutates is not a check. A name that omits an effect is a lie the reader has no way to detect.
- **Magic values become named constants** — **with the book's stated exceptions.** `hourlyRate * 8` reads fine raw and `radius * 2 * PI` does not need `TWO`; π itself does *not* qualify, because nobody proofreads a literal they recognize. The exception covers values the reader already holds in context, and is not a licence for `86400000` or a bare `0.85` tax rate.

### Units of work *(Tier 1 for one-thing and size; Tier 2 for nesting and arity)*

**Unit of work** is whatever this language lets you name and reuse: a function, method or procedure; a shell function; a Terraform module; a CI job; a SQL view; a Make target; a Helm template; a Kubernetes manifest, which is named and applied but never invoked. Every language and every configuration format has one, and **the rules over its name are Tier 1** — do one thing is measured against that name, and the size signal needs no call site either. The rules over its **parameter list** and its return need something that invokes it, and the nesting signal needs something that branches; those are tagged Tier 2 below.

- **Do one thing** *(Tier 1)* = every statement in the unit sits **exactly one level of abstraction below the unit's own name**. A unit that mixes orchestration (`tokenize`, then `parse`) with mechanics (the character loop inside the tokenizer) does two things by construction.
- **The TO-paragraph test, construct-independently** *(Tier 1)*: you must be able to say *"TO `do-the-thing-the-name-says`, we do X, then Y, then Z"*, where each of X, Y, Z is one named thing at the next level down. If the paragraph needs "…and then, separately, we also…", you have found the split point. This works on a Terraform module and a pipeline stage verbatim — it never mentions a function.
- **Size is a smell signal, not the rule** *(Tier 1)*. The book's numbers, calibrated on a 2008 Java codebase: a unit hardly ever over **20 lines**, **2–4** as the target. Counted on the artifact, so no call site is needed. The signal transfers everywhere; the line counts do not, since 20 lines of Java is not 20 lines of YAML. Treat it as the point where you stop and look; the one-thing test is what actually decides. (File and line-length numbers are formatting, and live in that subsection below.)
- **Nesting depth ≤ 2** *(Tier 2 — a branching construct)*. The book's gloss is the precondition: *an `if` or loop body is one line, usually a call*. What the number measures is **control flow the author chose**, not indentation — a minimal clean Kubernetes Deployment nests **seven** levels on schema-imposed structure alone, so read as raw indent depth the signal fires on every object that exists. Helm/Jinja templating, HCL `dynamic`, Bash and SQL `CASE` all supply the construct and the row binds there; **a bare manifest does not, so it is out of scope** rather than deeply nested. The Tier-1 audit demoted this row from Tier 1.
- **The arity budget** *(Tier 2 — wherever a unit takes named inputs)*: **0 ideal · 1 good · 2 costly · 3 avoid · 4+ never.** The stated reason is testing — each input multiplies the case matrix combinatorially, so the budget is really a verification budget. Over budget, bundle the inputs into one named object whose fields are the arguments; the real prize is that computation then moves onto that object.
  - **Recorded disagreement.** `clean-code-java` gives the five-rung ladder above; all three adaptations flatten it to "**≤2**, three avoidable, 4+ must become a parameter object". Java is canonical here, so the ladder stands — but the adaptations are stricter in practice, and nothing is lost by treating 3 as already over budget. ch03 carries the full note.
- **No flag inputs** *(Tier 2)*. A boolean parameter is two units that got merged — `createFile` / `createTempFile`. The flag announces that the unit does more than one thing, in the caller's own source.
- **No output arguments** *(Tier 2)*. A unit changes its own state or returns a value; it does not reach into something the caller handed it. An input that is silently an output is the hardest kind of side effect to see.
- **Side effects are named or removed** *(Tier 1)*. Where an effect is genuinely unavoidable, centralize it in **one** place — "one and only one" — so there is a single unit whose name carries it.
- **Command/query separation** *(Tier 2)*. Do something, *or* answer something, never both. `if (set("username", "bob"))` reads as a lie in every language that allows it.

### Duplication *(Tier 1)*

- **The real question is not "is this duplicated" but "do these share a reason to change?"** That is the whole test. Two fragments that will always change together are one idea written twice; two that will change for different reasons are a coincidence of shape.
- Duplication *"may be the root of all evil in software"*, and it is rule 2 of the four rules below — above expressiveness, below only verification. Even three repeated lines are worth extracting once they pass that test.
- **The bad-abstraction caveat**, stated outright by all three adaptations: *"bad abstractions can be worse than duplicate code."* Extraction creates a dependency between the call sites. A wrong extraction couples two things that must later diverge, and the cost of undoing it is paid by whoever arrives next.
- **The cross-domain exception.** Two implementations that live in **different modules in different domains** and merely resemble each other: **keep both copies.** Their resemblance is not a shared reason to change.
- **Recorded disagreement.** The book presses hard on eliminating every repeat and states no cross-domain exception; the TypeScript, JavaScript and Python adaptations all state the caveat explicitly. `clean-code-java` is canonical on the *priority* — duplication outranks expressiveness — and the adaptations supply the exception that keeps the priority from being applied blindly. Both are recorded here rather than silently merged.

### Structure and dependencies *(SRP Tier 1; the rest Tier 2)*

- **SRP** *(Tier 1)*: one, and only one, reason to change. Size is measured in **responsibilities, not lines**. **The 25-word test**: if you cannot describe the module in about 25 words without "and", "or" or "but", it is too big. This binds on a Terraform module, a Helm chart, a CI workflow and a stored procedure exactly as it binds on a class — nothing in it assumes a type system.
- **Data vs. behavior** *(Tier 2 — wherever you can choose)*: objects hide data and expose behavior; data structures expose data and have no behavior. Choose by **the axis of change** — new *types* arriving → objects; new *operations* arriving → procedures over data. **Never build the hybrid**, which is worst at both.
- **Law of Demeter** *(Tier 2 — **objects only**)*: a unit may talk to its own fields, its parameters, and what it creates — not to what those return. `a.getB().getC().doIt()` is a train wreck, and the fix is a new method on the object (*tell, don't ask*), not mechanical splitting into locals. **A chain through plain data structures is not a violation** — which is precisely why walking a YAML or JSON tree does not breach Demeter.
- **OCP** *(Tier 2)*: apply it **when a change actually arrives**, not speculatively. The tell is a type-dispatch chain living in a consumer; after the fix, the next variant edits **zero** existing files. Speculative abstraction is how you pay for flexibility you never use.
- **LSP** *(Tier 2 — wherever subtyping exists)*: a caller written against the supertype must accept every subtype unchanged. Signature compatibility is necessary and **not sufficient** — invariants and history properties count too, which is why the rectangle/square breach type-checks and still returns the wrong area. The fix is to make the two peers under a shared parent, not to patch the override.
- **ISP** *(Tier 2)*: no client depends on what it does not use. The tell is an implementation forced to throw "not supported"; the fix is role interfaces sized to what one consumer needs.
- **DIP with injection** *(Tier 2)*: both levels depend on an abstraction, and the abstraction is shaped by **what the consumer needs** rather than mechanically extracted from the concrete class — that second half is the half people skip. Inject it rather than constructing it inside. **If it is hard to verify, it is too coupled**: testability is a design-smell detector, not a testing concern.

### Failure *(Tier 2)*

- **Fail loudly.** Prefer the language's raised-failure mechanism to returned error codes — a code the caller can ignore will be ignored, and it pollutes every signature between the failure and the handler.
- **Every failure carries the operation that failed and the failure type.** A stack trace records where; it cannot record what you were trying to do. That sentence is the difference between a diagnosable incident and a guess.
- **Never swallow.** An empty catch contradicts the `try` that claimed a failure was possible, and logging is not handling — a log line with no code path behind it is a swallowed failure with extra steps.
- **Absent-value sentinels: never return one, never pass one.** `null`, `nil`, `None`, `undefined`, `-1`, `""`. Return an empty collection, or a **special-case object** that answers the question the caller actually asked so the caller needs no branch at all. Code drowning in absent-value checks has too many of them, not too few.
- **Wrap third-party failure vocabularies into one of your own.** One boundary type, translated at the edge. It decouples you from their taxonomy, and the seam it creates is what makes their API substitutable.
- Where the language has no raised-failure construct at all, the construct question applies: whatever this ecosystem uses to make a failure **visible and non-silent** is what the rule binds to — *derived*, not quoted: the book and the adaptations state the rule over an exception, and its extension to ecosystems that have none is this skill's own. ch06 names those mechanisms per ecosystem, and ch09 applies them to config.

### Comments and formatting *(Tier 1)*

- **The default is don't.** A comment is an apology for code that failed to express itself — and it usually *contains the name you need*. Try deleting it by improving the code first: a better name, an explanatory variable, an extracted unit.
- **The rename test is the whole test**: *if a name requires a comment, the name does not reveal its intent.* Rename; if the rename lands, delete the comment. There is no third outcome.
- **The legitimate kinds, enumerated**: **intent** (why this decision, not what the code does), **warning of consequences**, **amplification** of something that looks inconsequential but is not, **legal** headers, and **TODO with a stated plan**. That list is the whole allowance.
- **Never write**: commented-out code (*"an abomination"* — delete it; source control remembers), journal or changelog comments, bylines, banner comments (`////////`), closing-brace markers, or restatements of the code. A section comment inside a unit marks **a unit waiting to be extracted**; a closing-brace comment means **shorten the unit**.
- **Formatting is the formatter's job, and the team's style wins over yours.** Encode it in a formatter, commit the config, and stop arguing — arguing about it is *"a waste of time and money for engineers"*. The book's figures go in that config, and they are the **more** Java-bound of the two sets of numbers here, measured on 2008-era Java projects: files around **200 lines** and **500 max**, lines **≤ 120**. The signal transfers — a file too big to hold in your head is too big in any language — but the numbers do not: 200 lines of Helm values is unremarkable, and 120 columns is a Java-era convention. Set them per ecosystem; ch07 carries the provenance. Blank lines separate concepts; never inside a tightly related group.
- What no formatter does for you: the **newspaper rule** — the public entry point at the top, each helper directly below its first caller, caller above callee, related things vertically close. And **don't column-align**: the urge to align means the list is too long, which means the thing should be split.

### Verification *(Tier 2)*

- **F.I.R.S.T.** — **F**ast, **I**ndependent, **R**epeatable, **S**elf-validating, **T**imely. Use the letters to name what is wrong with a suite nobody runs. "Hard to verify at all" is a **design** signal — inject the dependency — not a verification one.
- **One concept per test**, with minimal assertions, structured Build-Operate-Check, and named after the behaviour rather than the data (`handles a leap year`, not `2/29/2020`). A reassigned shared subject is the tell that two concepts got merged.
- **The three laws of TDD**: no production code until a failing test exists; no more test than suffices to fail; no more production code than suffices to pass that test. Cycles of roughly thirty seconds.
- **The dual standard**: test code is held to production standards of cleanliness, and **efficiency is the only dimension where the standard differs**. Dirty tests are worse than no tests — they get abandoned, and the production code rots behind them.
- **Where there is no unit test, the verification layer is plan/diff, schema validation, policy-as-code, and lint** — *derived*, not quoted: the book names none of these tools, and this ladder is this skill's own translation of Beck's generalized rule 1 into ecosystems with no test runner. That is what "run the tests" means in a Terraform module or a Kubernetes manifest: `terraform plan` reviewed as a diff, `helm template` / `kubectl diff` against the live object, schema or CRD validation, a policy suite (OPA/Conftest), and a linter (`tflint`, `shellcheck`, `yamllint`). The rule was never "write unit tests" — it is **have a verification you can run, and run it before you go on**.

### Improving existing code *(Tier 1)*

- **Write it dirty, then clean it.** Nobody produces the final form in one pass — *"I don't write them that way to start. I don't think anyone could."* The bad first draft is expected; shipping it unchanged is the failure.
- **Tiny steps under green verification** — whatever verification you have, which is the second thing Tier 1 assumes and need not be a test suite. Add the new abstraction as a harmless skeleton, migrate one use at a time, re-run that verification after each step, fix any break before the next step, and expect to reverse earlier steps as the shape emerges. Never a big-bang restructure.
- **The stop rule**: stop adding features the moment each new case requires parallel edits in the same N places. That is a module trying to be born — extract it first, then resume the feature. The N places are the measurement; "it feels messy" is not.
- **Boy Scout Rule**: every check-in leaves the code strictly better than you found it. One renamed variable, one extracted unit. Improvement does not have to be large; it has to be constant.
- **LeBlanc's Law**: *later equals never.* A cleanup that is not in this change is not going to happen.

### When rules conflict

**Beck's four rules of simple design, in priority order:**

1. **The verification you have passes.**
2. **No duplication.**
3. **Expresses intent.**
4. **Minimizes the number of units and types.**

Rule 1 is the book's *"runs all the tests"*, **generalized** so the ladder still works where there is no test runner — it binds to whatever verification you have, the second thing Tier 1 assumes: the plan applies cleanly, the schema validates, the policy suite passes, the linter is quiet. A design that does not verify is not simple, however elegant it reads.

**Rule 4 never overrides 1–3.** Do not merge two well-named units to have fewer of them, and resist dogma in the other direction — "an interface for every class" is rule 4 violated from the opposite side. Any rule loses to every rule above it, every time; that ordering is the point of having a list at all.

---

## Chapter Index

| # | Chapter | Owns |
|---|---------|------|
| [ch01](chapters/ch01-what-survives-translation.md) | What Survives Translation | The three tiers and the full tier assignment; the family map and routing; Beck's four rules as conflict resolver; the 3 Rs; the pointer to `clean-code-java` ch17 for the catalogue, flagging `J1`–`J3` as Java-bound |
| [ch02](chapters/ch02-names-and-magic-values.md) | Names and Magic Values | Intention-revealing names, scope-length rule, one word per concept, searchability, noise words, side-effects-in-the-name, named constants and the exceptions the book grants |
| [ch03](chapters/ch03-units-of-work.md) | Units of Work | "Unit" defined construct-independently; do one thing; one level of abstraction; size at Tier 1 and nesting depth at Tier 2; input count; flag inputs; output arguments; side effects; command/query separation |
| [ch04](chapters/ch04-duplication-and-abstraction.md) | Duplication and Abstraction | DRY; the same-reason-to-change test; the bad-abstraction caveat and the cross-domain exception |
| [ch05](chapters/ch05-structure-and-dependencies.md) | Structure and Dependencies | Data vs. behavior and the axis-of-change test; Law of Demeter; SOLID restated for modules; boundaries and wrapping third-party code; **concurrency as a decoupling concern** — keep concurrency code separate, keep shared data small; Tier 2, so where the language has no thread the rule does not apply |
| [ch06](chapters/ch06-failure.md) | Failure | Fail loudly with context; never swallow; the operation-and-type rule; absent values and special-case objects; error codes vs. raised failures |
| [ch07](chapters/ch07-comments-and-formatting.md) | Comments and Formatting | When not to comment and the legitimate kinds; the rename test; **dead code** (paired with commented-out code, which this chapter owns); newspaper rule; vertical distance and density; file and line size; team style wins; delegate to the formatter |
| [ch08](chapters/ch08-verification.md) | Verification | F.I.R.S.T.; one concept per test; TDD's three laws; the dual-standard rule; **and what verification means where unit tests don't exist** — plan/diff, schema validation, policy-as-code, linting, contract tests |
| [ch09](chapters/ch09-declarative-and-config.md) | Declarative and Config Languages | Per-ecosystem application across seven — YAML, Kubernetes/Helm, CI pipelines, Terraform/HCL, SQL, Bash, Dockerfile — each section walking the Tier 1 rules and the translated Tier 2 rules. Synthesis: the book has no coverage |
| [ch10](chapters/ch10-improving-existing-code.md) | Improving Existing Code | Write dirty then clean; the refactoring protocol in tiny steps under green verification; the stop rule; Boy Scout Rule; LeBlanc's Law |

## Topic Index

Every term in [glossary.md](glossary.md) plus one entry per ch09 ecosystem, alphabetical. **†** marks a term this skill coins or redefines; the rest are inherited from the book and its adaptations.

- **25-word test** → ch05
- **Absent-value sentinel** → ch06
- **Anchors and aliases** → ch09, ch04
- **Arity budget** → ch03, ch08
- **Bad-abstraction caveat** → ch04
- **Bash** → ch09, ch06, ch03, ch05
- **Beck's four rules (Rules of Simple Design)** → ch01, ch04
- **Blast radius †** → ch09
- **Boy Scout Rule** → ch10
- **Bucket brigade** → ch03
- **Build-Operate-Check** → ch08
- **Check †** → ch08
- **CI pipelines (GitHub Actions, GitLab CI)** → ch09, ch04, ch07, ch08
- **Cohesion** → ch05
- **Command/query separation** → ch03
- **Construct question, the †** → ch01
- **Cross-domain exception** → ch04
- **Data/object anti-symmetry** → ch05
- **Dead configuration †** → ch09, ch07
- **Dependency Inversion Principle (DIP)** → ch05
- **Disinformation** → ch02
- **Do one thing** → ch03
- **Dockerfile** → ch09, ch07, ch03
- **Dual standard, the** → ch08
- **Explanatory variable** → ch07, ch02
- **Extraction loop, the** → ch05, ch09
- **Feature Envy** → ch05
- **F.I.R.S.T.** → ch08
- **Flag input (flag argument)** → ch03
- **Golden render** → ch10
- **Helm** → ch09, ch10, ch05
- **Hybrid** → ch05
- **Implicity** → ch02
- **Interface Segregation Principle (ISP)** → ch05, ch09
- **Kubernetes** → ch09, ch06, ch07, ch02
- **Law of Demeter** → ch05
- **LeBlanc's Law** → ch10
- **Liskov Substitution Principle (LSP)** → ch05
- **Magic value** → ch02
- **Module †** → ch05
- **`moved` block** → ch09, ch10
- **Newspaper rule** → ch07
- **Noise word** → ch02
- **ONE SWITCH rule** → ch05
- **Open-Closed Principle (OCP)** → ch05
- **Output argument** → ch03
- **Parallel-edits signal** → ch04, ch10
- **Parameter object** → ch03
- **Policy-as-code** → ch08, ch09
- **Prune** → ch09, ch07
- **`removed` block** → ch09, ch07
- **Rename test, the †** → ch02, ch07
- **Re-pricing step, the †** → ch09
- **Rung (verification rung) †** → ch08
- **Same-reason-to-change test †** → ch04
- **Scope-length rule** → ch02
- **Searchable name** → ch02
- **Single Responsibility Principle (SRP)** → ch05
- **Special Case object** → ch06
- **SQL** → ch09, ch05, ch02
- **State operation †** → ch09, ch10
- **Stepdown rule** → ch03, ch07
- **Stop rule, the †** → ch10
- **Tell, don't ask** → ch05
- **Temporal coupling** → ch03
- **Terraform / HCL** → ch09, ch10, ch08, ch05
- **Three laws of TDD** → ch08
- **Three questions, the †** → ch09
- **Three Rs, the** → ch01
- **Tier 1 †** → ch01
- **Tier 2 †** → ch01
- **Tier 3 †** → ch01
- **TO-paragraph test** → ch03
- **Train wreck** → ch05
- **Unit of work †** → ch03
- **Verification ladder, the †** → ch08
- **Wet-clay model** → ch01, ch10
- **Write it dirty, then clean it** → ch10
- **YAML** → ch09, ch07, ch04

## Supporting Files

- [cheatsheet.md](cheatsheet.md) — the fast path while working: the three questions to ask of a non-imperative file, the thresholds the sources commit to, the comment / duplication / failure / naming decision rules, tells and smells, the priority order when rules conflict, and the judgment calls the sources explicitly allow.
- [patterns.md](patterns.md) — one entry per technique with when, how and trade-offs; each names either the construct it needs or the rule it derives from, so a declarative technique is never offered without its parent rule.
- [glossary.md](glossary.md) — every key term in one line with the chapter that states it, **†** marking the terms this skill coins or redefines rather than inherits.
- [references/declarative-translation.md](references/declarative-translation.md) — one row per rule, columns **Rule · Tier · Imperative / OO · Functional · Declarative (YAML/HCL/SQL/Bash) · Enforced by**. Open ch09 to *learn* the mapping; open this to *apply* a rule you already know to the file in front of you. `no construct — does not apply` is a verdict in it, not a gap.

## Related Skills — the clean-code family

- **`clean-code-java`** — Robert C. Martin's original *Clean Code*, the book itself (17 chapters and Appendix A, ~129,000 words). **Use it when the code in front of you is Java**, and reach for it from any language for the three holdings this skill deliberately does not duplicate: the **66-item smells-and-heuristics catalogue** (`C1`–`C5`, `E1`–`E2`, `F1`–`F4`, `G1`–`G36`, `J1`–`J3`, `N1`–`N7`, `T1`–`T9`), the long-form **refactoring case studies** (ch14–ch16, where a real file is cleaned heuristic by heuristic), and the **deep concurrency treatment** (ch13 and Appendix A — execution models, the four deadlock conditions, atomicity and CAS). It is also canonical wherever the family disagrees.
- **`clean-code-typescript`** — labs42io's adaptation. **Use it when the code in front of you is TypeScript**, for the TS-native material that is Tier 3 here and so out of scope by name: the **immutability ladder** (`readonly` → `Readonly<T>` → `ReadonlyArray<T>` → `as const`), **`type` vs `interface`**, **discriminated unions instead of `instanceof` chains**, and the **`Failable<R, E>`** result type, which puts a failure in the signature so the compiler forces the caller to narrow.
- **`clean-code-javascript`** — Ryan McDermott's adaptation. **Use it when the code in front of you is JavaScript**, for **closure privacy** (a public field can be deleted out from under your own getter), **SOLID in an untyped language** — where the abstractions are implicit contracts you uphold rather than rules a compiler enforces — and the **conditional-removal ladder**: compound `if` → named predicate, negative → positive predicate, `switch (this.type)` → a subclass per case, `instanceof` chain → one consistent API, `typeof` guards on primitives → reach for TypeScript.
- **`clean-code-python`** — Rigel Di Scala's adaptation. **Use it when the code in front of you is Python**, for **type hints instead of type-prefixes**, the **parameter-object ladder** (positional args → bare `dict` → plain class → `NamedTuple` → `@dataclass` → `TypedDict`), **SOLID worked through ABCs and mixins**, and **mypy as the LSP referee** — where the JavaScript original relies on discipline, the Python adaptation has the type checker catch the breach mechanically.

**Use the sibling whenever the language matches.** It owns the idiom, and this skill routes Tier 3 to it by name rather than approximating it. **Use this skill for every other language** — Go, Rust, C#, C++, Kotlin, Ruby, PHP, Swift, Scala and the rest — **and for configuration and infrastructure-as-code, which no sibling covers at all**: YAML, Kubernetes, Helm, CI pipelines, Terraform/HCL, SQL, Bash and Dockerfile are exactly the languages the book predates and the three adaptations never reach, and they are what [ch09](chapters/ch09-declarative-and-config.md) exists for.

---

## Scope & Limits

**This is a distillation, not a new source.** Every rule above is traceable to the book or to one of its three adaptations — **except where it is labelled a generalization or a derivation**, which is how this skill marks the places it went beyond its sources. Three of those labels are live in the working set above: Beck's rule 1 generalized to "the verification you have passes" in `### When rules conflict`; the config verification ladder in `### Verification`; and the failure-visibility clause in `### Failure`, for ecosystems with no raised-failure construct. The **tier machinery itself** is this skill's own frame rather than anything a source states — the three tiers, the construct question, and the construct-independent definitions of *unit of work* and *module* — and [glossary.md](glossary.md) marks every term of that kind with **†**, so the list above is the labelled rules, not the whole of what this skill adds. Where the sources differ the difference is recorded rather than smoothed over. `clean-code-java` is canonical: it holds the book itself and the **66-item smells-and-heuristics catalogue**, which is deliberately *not* duplicated here. Ask it for a tag like `G30` or `N7` — and note that its `J1`–`J3` items are **Java-bound by definition** (wildcard imports, inherited constants, `enum`s), so they have no universal form to distil.

**The three adaptations are community guides of very different depth**, and terser is not the same as truer: `clean-code-typescript` is ~10,300 words, `clean-code-javascript` ~7,400, `clean-code-python` ~5,200 across 19 rules, against roughly 129,000 words of book. `clean-code-python` omits testing, error handling, comments and formatting entirely. Where a rule above is fuller than any single adaptation, that is because the book supplied it.

**The declarative material is synthesis, not extraction.** The book was published in 2008 and predates Kubernetes, Helm, Terraform, and pipeline-as-YAML altogether. No sentence in it is about a manifest. Every rule in ch09 is therefore **derived** — from a Tier 1 rule, which needs nothing but a name and a verification, or from a Tier 2 rule whose construct was identified in that ecosystem first — and ch09 labels each one with the rule it descends from. Treat an unlabelled declarative rule as a bug in this skill, not as scripture.

**How the declarative claims were verified.** Every tool behaviour stated in ch07, ch09 and ch10 was checked against that tool's own documentation, and where the tool is installed, against the tool. `kubectl` **v1.33.9** settled the `--prune` scope and alpha status, the client dry-run's need for cluster access, and the 63-character label-value limit. `psql` **18.6** settled the PostgreSQL claims, run against throwaway clusters rather than read about: that `CREATE OR REPLACE VIEW` refuses to rename, reorder or drop a column while appending one succeeds; that `DROP VIEW` defaults to RESTRICT and only `CASCADE` takes the dependent views with it; that `SELECT *` inside a view is expanded **when the view is created**, so a column added to the base table afterwards never appears in it; three-valued `NULL`; transactional DDL; and CTE inlining from PostgreSQL 12 against the `MATERIALIZED` fence that restores the old barrier. And a claim being unreachable by the obvious command is not the same as an unverifiable one: `kubectl explain` needs a cluster, but the kubectl binary **embeds the generated API field documentation**. `strings` over it recovers three distinct Deployment `revisionHistoryLimit` defaults — *"Defaults to 10."*, *"Defaults to 2."*, and an int32 maximum meaning retain every old ReplicaSet — three distinct defaults across the four API groups the binary still carries; what it cannot say is which belongs to which, and only the `2` blob carries the field name at all. Resolving the `ADRP`/`ADD` pairs that load those three strings against the binary's own function table does say: the four call sites are `apps/v1.map.init.2` and `apps/v1beta2.map.init.2` (both **10**), `apps/v1beta1.map.init.1` (**2**) and `extensions/v1beta1.map.init.3`, each of which also loads the shared `DeploymentSpec` doc string. So ch09's `apps/v1` default of **10** is settled here by inspecting the shipped binary rather than by documentation — it was the instrument's reach that needed a second pass, not the fact. **`terraform`, `helm`, `conftest` and `opa` could not be executed** in the environment where this skill was written, so every claim about them is desk-checked against documentation rather than run. Verify against your own versions before acting on a destructive one.

**The conflict rule.** Where two siblings disagree, `clean-code-java` wins and the disagreement is written down rather than silently resolved. Two of them are live in the working set above: **arity** (java's 0/1/2/3/4+ ladder against the adaptations' flat ≤2-then-parameter-object) and **duplication** (java's press to eliminate every repeat against the adaptations' stated bad-abstraction caveat and cross-domain exception).

Finally, Martin's own hedge, which applies to this file more than to his: *"Clean code is not written by following a set of rules. You don't become a software craftsman by learning a list of heuristics. Professionalism and craftsmanship come from values that drive disciplines."* Tiers tell you whether a rule *can* apply to the thing in front of you. They do not tell you that it *should*. No source images were read.
