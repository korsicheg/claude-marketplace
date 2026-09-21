# Chapter 1: What Survives Translation

## Core Idea
Clean Code's rules are not uniformly portable, and pretending they are is why "apply clean
code to this YAML" produces platitudes. Some rules need nothing but a name; some need a
parameter list, a subtype or a test runner; some are idiom belonging to one language. Sorting
every rule by **what it assumes about the language** is what makes the other nine chapters
usable on a Helm chart, a Terraform module and a Rust crate alike. That sort is done once,
here, in the table below — the rest of the skill cites it rather than re-deciding it.

## Frameworks Introduced

- **The Three Tiers.** Every rule in this skill is tagged by its assumptions, and the tag is
  part of the rule.
  - **Tier 1 — invariant.** *What it means*: the rule assumes exactly two things, and every
    language and every configuration format supplies both — that you can **name** something,
    and that you have **some verification you can run**, even where that verification is only
    a formatter, a schema check, or a committed golden render you re-run. Nothing beyond those
    two: no functions, no types, no classes, no exceptions, no test runner. **Run** is the
    operative word: ch08 defines a check as *"anything **executable** that returns a pass or a
    fail over an artifact"*, so a colleague reading the diff is not one — an executable check is
    re-runnable by construction, which is what the refactoring protocol (ch10) spends.
    *How to apply*: as written. There is no translation step, because there is no construct to
    go looking for first.
    *Failure mode it fixes*: the reviewer who says "Clean Code doesn't really apply to config"
    and stops there.
  - **Tier 2 — conditional.** *What it means*: the rule binds wherever a **specific** construct
    exists — a callable with a parameter list, a type system, a substitutability mechanism, an
    exception, a test runner, a thread — and is stated in terms of the construct rather than the
    keyword ("the subtype", never `class`).
    *How to apply*: identify the construct first (below), then apply the rule to it. Where the
    construct is absent the rule does not apply, and this skill says so rather than
    approximating it.
    *Failure mode it fixes*: approximation — LSP "applied" to a Kubernetes manifest, which
    yields advice nobody can act on and discredits the rules that did apply.
  - **Tier 3 — out of scope, by name.** *What it means*: language-specific idiom — `as const`,
    `@dataclass`, checked exceptions, `Promise.all`.
    *How to apply*: route to the sibling skill that owns the language. Where no sibling exists,
    derive the local idiom from the governing Tier 1/Tier 2 rule instead of guessing at it.
    *Failure mode it fixes*: silence. Naming Tier 3 is what lets you tell "this skill has no
    rule here" from "this skill forgot".

- **The Construct Question.** For any Tier 2 rule, ask: *what plays the part of the callable /
  the parameter list / the subtype / the exception / the test runner here?*
  - *How*: name the candidate out loud, then check it. A Terraform module's `variable` blocks
    are a parameter list, so the arity budget binds. `terraform plan` read as a diff is the
    verification, so Beck's rule 1 binds. A Helm chart has no subtype, so **LSP does not apply**
    — and that is the answer, not a prompt to invent one.
  - *The rule*: if nothing plays the part, the rule is **out of scope here**, not approximated.
    A rule stretched past its construct is worse than an absent rule: it cannot be checked, and
    it teaches the reader to discount the ones that can.

## Key Concepts

- **The Tier 1 floor is a name — not a name and an invocation.** Take the weakest case in the
  family: a bare Kubernetes manifest. It is named (`kind` plus `metadata.name`) and it is
  *applied*; nothing ever calls it, and there is no call site at which to read its name. Every
  Tier 1 rule still binds anyway, because naming is the part that is universal and invocation is
  not. `metadata.name: svc-1` is unsearchable and reveals no intention in exactly the way the
  naming rules describe. A single manifest *file* bundling a Deployment, a Service and a
  ConfigMap does three things, and do-one-thing catches it on an artifact nothing calls, because
  what a unit does is measured against its *name* rather than against a call. The size signal
  catches the same file for a different reason: its lines are counted in the artifact itself, so
  it needs no call site either. **Nesting depth is the one that does not follow**, and the audit
  demoted it — a manifest's depth is set by the schema rather than by the author, so there is
  nothing there to measure judgment against. And `kubectl apply --dry-run=server` is the
  verification. So the floor is a name plus some verification, and nothing else. ch03 defines a
  *unit of work* on exactly this floor — anything you can name and reuse — and states a narrower
  **case**, a unit you can name **and** invoke, as the precondition for the four Tier 2 rules
  over a unit's inputs and its return. The term assumes no more than this floor does; only those
  four rules need the caller.
- **The 3 Rs — readable, reusable, refactorable.** The acceptance test for a change, from the
  TypeScript and Python adaptations rather than from the book: name which R a change buys before
  defending it on cleanliness grounds. A change that buys none is rearrangement.
- **The wet-clay model.** Code starts as a first draft and is shaped in review — *"beat up the
  code instead"* of the author. It is the adaptations' framing of the habit ch10 owns as write it
  dirty, then clean it.
- **Heuristics with judgment — and a recorded disagreement.** The adaptations grant an explicit
  licence: *"Not every principle herein has to be strictly followed, and even fewer will be
  universally agreed upon"* — a touchstone, not a linter. `clean-code-java` frames the same
  material as disciplines driven by values, and hedges in the opposite direction: *"clean code is
  not written by following a set of rules."* It licenses no rule; it denies the list is
  sufficient. Java is canonical, so the tiers carry no licence to skip a rule — they tell you
  whether a rule *can* apply, never whether it should be obeyed. The adaptations' licence stands
  as what it is: permission to override a rule **with a stated reason**, never by accident. Note
  also that `clean-code-python` omits testing, comments, error handling and formatting entirely,
  so a sibling's silence is never evidence that a rule does not exist.
- **Single ownership within the family.** Each rule is stated in one chapter, named in the table
  below, and cited from everywhere else. The siblings predate this skill and still restate the
  shared rules in their own words; that is drift the family tolerates, not licence to add more.

## Mental Models

- **A rule's tier is a property of its assumptions, not of its importance.** The arity budget is
  Tier 2 and you check it by counting; SRP is Tier 1 and it takes a design argument to settle.
  The tier tells you whether a rule *reaches* the artifact in front of you — never how much it
  matters when it does.
- **Tier 2 is not "optional".** Conditional describes the precondition, not the force. Wherever
  its construct exists a Tier 2 rule binds exactly as hard as a Tier 1 rule; a Go function has a
  parameter list, so the arity budget is not advisory there.
- **Tier 3 is a routing decision, not a gap.** The question a Tier 3 rule answers is "whose
  rule is this?" — and the answer is a sibling skill, or a derivation from the Tier 1/Tier 2 rule
  above it. It is never "nobody's".

## Reference Table: the tier assignment

**This table is the skill's index of record for tiering.** ch02–ch10 cite it; a rule's tier is
not re-decided in the chapter that states it. *What it assumes* is a closed vocabulary: a Tier 1
row assumes only **a name** and/or **some verification**, and a Tier 2 row names the one
construct that can be absent, at the narrowest true grain. ch09 owns no row — it applies these
rows per ecosystem. Tier 3 has no rows by construction: it is the set of idioms this skill
declines, characterised above and routed in **Connects To**.

| Rule | Tier | What it assumes | Owning chapter |
|---|---|---|---|
| Intention-revealing names | Tier 1 | a name | ch02 |
| Name length proportional to scope | Tier 1 | a name | ch02 |
| One word per concept, never pun | Tier 1 | a name | ch02 |
| Searchable names | Tier 1 | a name | ch02 |
| No noise words (`Manager`, `Data`, `Info`) | Tier 1 | a name | ch02 |
| The name must include the side effects | Tier 1 | a name | ch02 |
| Magic values become named constants, with the book's stated exceptions | Tier 1 | a name | ch02 |
| Duplication and the same-reason-to-change test | Tier 1 | a name | ch04 |
| The bad-abstraction caveat, and the cross-domain exception | Tier 1 | a name | ch04 |
| Do one thing = one level of abstraction below the unit's name | Tier 1 | a name | ch03 |
| Size as a smell signal | Tier 1 | a name | ch03 |
| SRP — one, and only one, reason to change | Tier 1 | a name | ch05 |
| Comments: the default is don't, plus the legitimate kinds | Tier 1 | a name | ch07 |
| No commented-out code, journals, bylines or banners | Tier 1 | some verification | ch07 |
| Delete dead code | Tier 1 | some verification | ch07 |
| Formatting is tooling's job, and the team's style wins | Tier 1 | some verification | ch07 |
| Vertical ordering: newspaper rule, related things close | Tier 1 | a name | ch07 |
| Boy Scout Rule | Tier 1 | some verification | ch10 |
| LeBlanc's Law — later equals never | Tier 1 | some verification | ch10 |
| Beck's four rules as the conflict resolver, rule 1 generalized to "the verification you have passes" | Tier 1 | a name + some verification | ch01 |
| Write it dirty, then clean it | Tier 1 | some verification | ch10 |
| Tiny steps under green verification | Tier 1 | some verification | ch10 |
| The stop rule | Tier 1 | a name | ch10 |
| Nesting depth as a smell signal | Tier 2 | a branching construct | ch03 |
| Input count and the arity budget | Tier 2 | a parameter list | ch03 |
| No flag inputs | Tier 2 | a parameter list | ch03 |
| No output arguments | Tier 2 | a parameter list | ch03 |
| Command/query separation | Tier 2 | a return value | ch03 |
| Data vs. behavior, and the axis-of-change test | Tier 2 | an object (behaviour bound to data) | ch05 |
| Law of Demeter and tell-don't-ask | Tier 2 | an object (behaviour bound to data) | ch05 |
| OCP — open for extension, closed for modification | Tier 2 | a substitutability mechanism | ch05 |
| LSP — the subtype is accepted unchanged | Tier 2 | a substitutability mechanism | ch05 |
| ISP — no client depends on what it does not use | Tier 2 | a declared interface | ch05 |
| DIP, with injection and a consumer-shaped abstraction | Tier 2 | an injectable abstraction | ch05 |
| Polymorphism instead of a type switch | Tier 2 | a substitutability mechanism | ch05 |
| Exception and failure-propagation mechanics | Tier 2 | an exception | ch06 |
| Absent-value handling and special-case objects | Tier 2 | an absent-value sentinel | ch06 |
| Automated tests, TDD's three laws, F.I.R.S.T. | Tier 2 | a test runner | ch08 |
| Concurrency | Tier 2 | a thread | ch05 |

**39 rows: 23 Tier 1 and 16 Tier 2** — one row per rule, except where a rule's parts have
different constructs and so become separate rows: the single
`OCP, LSP, ISP, DIP` bullet is four rows, and *size and nesting depth* is two, for the reason the
audit found and ch03 states.

**The Tier-1 audit has run, and it split one row.** Each Tier 1 row had to hold for YAML and HCL
*unchanged*; 22 of the 23 did. *Size and nesting depth as smell signals* did not, and is the
demotion: **size** is counted on the artifact and stays Tier 1, while **nesting depth** needs a
branching construct and is now Tier 2, because a minimal, entirely clean Kubernetes Deployment
nests **seven** levels deep on schema-imposed structure alone — so against a threshold of ≤ 2 the
signal fires on every object that exists, including the clean ones, and a signal that always fires
carries no information. Demotion only, never promotion.

**Which constructs the declarative languages actually supply** — the fact ch09 builds on. HCL
supplies a parameter list (a module's `variable` blocks), a return value and a declared interface
(its `output`s), an injectable abstraction (pass the data source in rather than reading it
inside), an absent-value sentinel (`null`), a test runner (`terraform test`) and a **branching
construct** (`dynamic` blocks, conditional expressions, `for` expressions); it supplies no
object, no substitutability mechanism, no thread, and no exception — its `validation`,
`precondition` and `postcondition` blocks abort rather than propagate, and `try()`/`can()`
suppress rather than catch. A bare YAML manifest supplies
only the absent-value sentinel, and none of the other ten — it has no branching construct either,
which is why the nesting row does not reach it and the size row still does. Rows whose construct is missing do
not apply there, and ch09 says so per ecosystem instead of approximating.

**Concurrency's construct is a thread**, and **its row is housed in ch05**, as a decoupling
concern: its clean-code content is keeping concurrency code separate and shared data small,
which is SRP and dependency work.

## Anti-patterns

- **Approximating a Tier 3 idiom into a language that lacks it.** "Define interfaces for your
  Terraform modules" — HCL has no interface construct. It has module inputs and outputs, and the
  rule that binds them is ISP over the output surface. The invented idiom is unactionable and
  unenforceable, and it costs you the rule that would have worked.
- **Treating Tier 2 as advisory.** A four-variable Bash function is over the arity budget, not
  exempt because Bash is "just scripting". The construct is there; the rule binds.
- **Silently promoting a rule to Tier 1 because it feels universal.** Command/query separation
  feels like a law until you try to state it for a manifest that returns nothing. The test for
  Tier 1 is survival: applied literally and unchanged to a Kubernetes manifest and a Terraform
  module, does the rule still say something checkable? If it needs a hedge to survive, it is
  Tier 2 with a construct you have not named yet.
- **Demoting by omission.** Dropping a rule you could not place does the same damage as a wrong
  tier, minus the evidence. No rule is dropped: every one has a row in the table above.

## Key Takeaways

1. **Every Tier 1 rule holds for YAML and HCL unchanged.** No construct hunt first — a name and
   a runnable verification are already there. That is the promise the tiering buys.
2. **A Tier 2 rule does not bind until you have named its construct.** Ask the construct
   question, and accept "nothing plays that part here" as a real answer.
3. **Beck's rule 1 generalizes to "the verification you have passes."** The book's *"runs all
   the tests"* is the test-runner instance of it. The plan applies cleanly, the schema validates,
   the policy suite passes, the linter is quiet — a design that does not verify is not simple.
4. **Tier is about assumptions, never importance.** Arity is Tier 2 and trivial to check; SRP is
   Tier 1 and hard.
5. **The Tier 1 floor is a name, not a name and an invocation.** A bare manifest is named and
   applied but never invoked, and every Tier 1 rule reaches it anyway.
6. **The table above is the index of record.** Chapters cite it; they do not re-tier. A tier
   changes by audit, downward, with the demotion written down.
7. **Name which R you are buying** — readable, reusable, refactorable — and override a rule only
   with a stated reason.

## Connects To
- **[ch02 — names and magic values](ch02-names-and-magic-values.md)**: the six Tier 1 naming
  rows, plus named constants and the exceptions the book grants.
- **[ch03 — units of work](ch03-units-of-work.md)**: the unit defined construct-independently,
  one thing and size at Tier 1, plus the five Tier 2 rows — nesting depth, and the four over a
  unit's inputs and its return.
- **[ch04 — duplication and abstraction](ch04-duplication-and-abstraction.md)**: the
  same-reason-to-change test and the bad-abstraction caveat.
- **[ch05 — structure and dependencies](ch05-structure-and-dependencies.md)**: SRP at Tier 1,
  plus data-vs-behavior, Demeter, the four SOLID rows, polymorphism and concurrency at Tier 2.
- **[ch06 — failure](ch06-failure.md)**: failure propagation and absent values.
- **[ch07 — comments and formatting](ch07-comments-and-formatting.md)**: comments and the
  legitimate kinds, commented-out code, dead code, formatting delegation, vertical ordering.
- **[ch08 — verification](ch08-verification.md)**: F.I.R.S.T., TDD's three laws, and what
  verification means where there is no test runner.
- **[ch09 — declarative and config](ch09-declarative-and-config.md)**: where the construct
  question gets answered per ecosystem — YAML, Kubernetes/Helm, CI pipelines, Terraform/HCL, SQL,
  Bash, Dockerfile. It owns no row and applies all of them; the one-row-per-rule mapping is
  [references/declarative-translation.md](../references/declarative-translation.md).
- **[ch10 — improving existing code](ch10-improving-existing-code.md)**: the four Tier 1 rows of
  the refactoring protocol, plus the Boy Scout Rule as the habit that carries it.
- **`clean-code-java` ch17** — the **66-item smells-and-heuristics catalogue**, deliberately not
  duplicated here; ask it for a tag such as `G30` or `N7`. Its `J1`–`J3` items are **Java-bound
  by definition** — wildcard imports, inherited constants, and `enum`s — so they have no
  universal form to distil and hold no row above.
- **The siblings, by language**: Java → `clean-code-java`, which is the book itself and is
  canonical wherever two siblings disagree · Python → `clean-code-python` · TypeScript →
  `clean-code-typescript` · JavaScript → `clean-code-javascript`. Every other language, and every
  configuration format, is this skill's.
