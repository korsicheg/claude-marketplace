# Clean Code — Universal Decision Cheatsheet

The fast path while working. Every line compresses a chapter and nothing here is new; where a rule
binds only if the language supplies a construct, the construct is named — that is what **Tier 2**
means ([ch01](chapters/ch01-what-survives-translation.md)).

## Identify the three things first (non-imperative file)

Your entry point for a Terraform module, a Helm chart, a manifest, a pipeline, a query or a script.
Answer all three **before** quoting a rule at the file; an unanswered one gives you the
approximation ch01 calls worse than an absent rule.

```
1. What is the unit?             module · chart · object · job · step · CTE · view · function ·
                                 image · build stage — anything you can name and reuse      (ch03)
2. What is the verification rung?  unit → integration → contract → policy → plan/diff → schema →
                                 lint. Own the highest the ecosystem gives you, and never claim
                                 a rung you do not run                                      (ch08)
3. What is the failure mechanism?  exception · returned error value · exit code · plan-time abort ·
                                 none of its own — a manifest has probes, restartPolicy and
                                 admission instead                                          (ch06)
```

**Then price the rule before you apply it** (ch09): **free** — a `locals` rename, a deleted comment,
a reordered block · **a state operation** — a `moved` block (**Terraform 1.1+**), `terraform state
mv`, apply-new-then-delete-old · **destructive** — a `DROP VIEW`, a resource replacement, a prune,
and a `removed` block that lacks `lifecycle { destroy = false }` (**Terraform 1.7+**), which
destroys the real object. **A Tier 1 rule is never quoted as free.**

## Thresholds the sources commit to

| Thing | Limit | Source | Tier |
|---|---|---|---|
| Unit length | *"hardly ever 20 lines"*; **2–4** the target | `clean-code-java`; no adaptation names a number | **Tier 1** signal — the number is Java-calibrated (ch03) |
| Nesting / indent depth | **≤ 2**; an `if` or loop body is one line, usually a call | `clean-code-java` | **Tier 2** — a branching construct. It counts control flow the author chose, not indentation: a clean Deployment nests 7 on schema alone, so a bare manifest is out of scope (ch03) |
| Unit inputs (arity) | **0 · 1 · 2 · 3 avoid · 4+ never** | `clean-code-java`. **Recorded disagreement**: all three adaptations flatten it to ≤2, with 4+ forcing a parameter object | **Tier 2** — a parameter list (ch03) |
| Duplication | **three repeated lines** already clear the bar | `clean-code-java` ch12 | **Tier 1** (ch04) |
| Module size | **responsibilities, not lines**: ~25 words with no "if", "and", "or", "but" | `clean-code-java` ch10 | **Tier 1** — SRP (ch05) |
| File length | ~**200** typical, **500** upper, *"desirable, not a hard rule"* | `clean-code-java` ch05 | **Java-era** — a formatter default; the signal transfers, the number does not (ch07) |
| Line width | ≤ **120** | `clean-code-java` ch05 — Martin's own setting | **Java-era** — a formatter default (ch07) |
| Asserts per check | minimize; **one *concept* per check** | `clean-code-java` ch09 | ch08 states it; **not a ch01 row** |
| Coverage | **the book sets no number.** **Recorded disagreement**: `clean-code-typescript` and `clean-code-javascript` target 100% of statements and branches | `clean-code-java` argues from the TDD cycle and reads coverage as a map of what you have *not* checked | **Tier 2** — a test runner (ch08) |
| Switches per selection type | **exactly one**, and its cases create the polymorphic objects | `clean-code-java` `G23` | **Tier 2** — a substitutability mechanism (ch05) |
| Kubernetes label **value** | **63 characters** — a longer value is rejected, not truncated (executed on kubectl **v1.33.9**) | ch09 | platform limit, not a book figure (ch09) |

## Before writing a comment

```
Can a better name say it?                        → rename; that is the whole rename test      (ch07)
Can a named constant or an explanatory variable say it?
                                                 → name the value, then delete the comment    (ch02)
Is it a section marker inside a unit?            → extract that section; the marker is its name
Is it on a closing brace / at the end of a block?→ shorten the unit until its end is visible
Is it a change log, a dated entry or a byline?   → DELETE — `git log` and `git blame` hold it
                                                   accurately and cannot rot              [C1]
Is it commented-out code or configuration?       → DELETE on sight; source control remembers [C5].
                                                   In Terraform, commenting a resource out is a
                                                   DELETION, not a pause: gone from the
                                                   configuration, still in state, so the next plan
                                                   proposes to destroy the live object      (ch09)
Is it a banner (`##### NETWORKING #####`)?       → DELETE; a file needing signposts is too big (ch05)
Is it WHY, a warning of consequences, an amplification, or a TODO with a stated plan?
                                                 → KEEP, and write it well
Is the name one you do not own — a schema key like `terminationGracePeriodSeconds`?
                                                 → the rename test cannot be run, so the comment is
                                                   the only carrier of the why: KEEP it      (ch09)
Otherwise                                        → you are commenting bad code; fix the code
```

**"Rename" is never free in configuration** — a Terraform label *is* an address and a
`metadata.name` *is* an identity; see *Naming decision rules* below for what the rename carries.

## Duplication decision

```
Name a change you expect. Does it land on both copies, for the SAME reason?           (ch04)

  Yes, same domain                  → EXTRACT now, even at three lines
  Yes, but different modules in different domains
                                    → KEEP BOTH — the cross-domain exception; extraction buys an
                                      indirect dependency nobody asked for
  Near-miss, consumer never reads the difference
                                    → massage them identical, extract, drop the distinction
  Near-miss, consumer branches on the difference
                                    → keep both, or extract only the step they genuinely share
  Same shape, different types       → extract the shape, leave the types alone            [G5]

  The merge needs a flag, or pushes past three inputs?
                                    → ABANDON the merge; the parameter list is the variation
                                      confessing                                          (ch03)

In configuration, extraction re-addresses what it moves (ch09): folding resources behind a keyed
`for_each` or a module changes every address, so carry the move — one `moved` block PER INSTANCE
(**Terraform 1.1+**) or a `terraform state mv` — delete the old blocks in the SAME commit, and gate
on `Plan: 0 to add, 0 to change, 0 to destroy` before applying. An unkeyed `count` is
index-addressed: removing a middle element re-indexes every later one and plans destroy-and-create
for each.
```

## Failure handling

```
Is the "failure" a business case with a defined answer?                                   (ch06)
                              → Special Case object or an empty collection; no failure at all
Would you return an absent-value sentinel?  → don't: Special Case, empty collection, or raise
Would you PASS one?           → forbid it; a sentinel argument is a bug. In HCL an argument set to
                                `null` equals omitting it; in a Kubernetes strategic-merge patch a
                                `null` DELETES that field, so it removes live configuration
Does the language raise?      → raise your own type; the message names the operation AND its
                                subject; narrow the caught type to what is actually raised
Does it return failures (Go, Rust `Result`, TS `Failable`)?
                              → it does NOT propagate: wrap with the operation at every layer
No construct at all?          → exit codes: `set -euo pipefail`, a distinct code per case, a stderr
                                line naming the command and its input
Declarative?                  → the design is PLACEMENT: reject at schema, plan or admission time
                                rather than in production
About to quiet a step to make it green?
                              → never. `|| true`, `2>/dev/null`, `try()` round a lookup,
                                `continue-on-error: true` with no following check, an
                                `ignore_changes` over a field that keeps drifting — each trades a
                                loud failure for a quiet wrong state
```

## Naming decision rules

- **If a name needs a comment, rename it.** One test, no construct assumed — it reaches a
  Kubernetes manifest and a Rust crate identically (ch02).
- **Length is proportional to scope.** `i` in a two-line loop is right, and so is `each.key` inside
  a `for_each`; a root `local` or a values key every consumer sets earns the long name.
- **Test the name at the use site**, never at the declaration. That is where the stutter shows:
  `resource "aws_s3_bucket" "logs"`, never `"logs_bucket"`, because the address already says the type.
- **One word per concept, and never one word for two concepts.** `timeoutSeconds` everywhere, never
  `timeout` beside it.
- **Searchable beats short.** `grep` is the compiler you do not have in a config repo, so an
  unsearchable key or a bare `3` cannot be changed safely at scale.
- **No noise words** — `Manager`, `Processor`, `Data`, `Info`, `config:`, `utils`, `common`. Usually
  the tell of aggregated responsibility, which is ch05's problem wearing a name.
- **The name carries the side effects, or the effect goes** [`N7`] — a `check_config` that rewrites
  the config is not a check, and removing the effect beats lengthening the name (ch03).
- **Add context by enclosure; prefix only as a last resort**, and never repeat the container's name
  inside its members.
- **Every meaningful literal becomes a named constant**, derivation included (`60 * 60 * 24`), and
  a floating tag is a magic value that changes without a commit — `latest`, `node:20`,
  `actions/checkout@v4` and `@main` are all mutable, so pin the digest or the 40-character SHA and
  accept the bump bot you now need (ch09).
- **A rename in configuration is a state operation, not a search-and-replace** (ch09): a Terraform
  label *is* the address, so the rename carries a `moved` block (**1.1+**) or a `terraform state mv`
  or the plan proposes **destroy-and-create**; a changed `metadata.name` under `kubectl apply`
  **creates a second object** and leaves the first live, so delete the old one **by name**.
- **The most expensive label rename** is a Deployment's `spec.selector`, which is **immutable** in
  `apps/v1`, so the API server refuses it. Delete-and-recreate takes the Pods with it;
  `kubectl delete deployment X --cascade=orphan` (on v1.33.9) keeps them serving through the
  cutover — and the orphaned ReplicaSets are then deleted by name, **once the new Pods are
  serving**. ch09 prices it.

## Tells and smells

| If you see… | You're probably in… | Do |
|---|---|---|
| A name that needs a comment | a naming failure, not a documentation gap (ch02, ch07) | rename, then delete the comment |
| The same three lines twice | duplication, once they share a reason to change [`G5`] | run the duplication decision above; extract if it passes |
| A boolean argument, or `create_bucket = true` driving a `count` | one unit doing two things [`F3`] | split it into two named entry points (ch03) |
| A section comment inside a unit | a unit waiting to be extracted [`G30`] | extract it; the marker is already its name |
| A unit whose name contains "and", or a vague verb (`handle`, `process`) | the split point, announced (ch03) | split where the "and" is |
| `if`/`switch` on a type, repeated elsewhere | a missing polymorphism [`G23`] | one switch, creating the variants — **unless nothing can be dispatched to**, as in HCL and SQL, where the rule does not apply (ch05) |
| `utils`, `common`, `helpers`, `misc` | an extraction that never found its idea (ch04) | name the idea, or keep the copies |
| Units that must be called in a fixed order | hidden temporal coupling [`G31`] | bucket brigade — each produces what the next consumes |
| The same N edits in the same N places per new case | the stop rule firing (ch10) | stop adding cases; extract first |
| A 900-line values file, a 300-line template | ch03's size signal and ch05's SRP (ch09) | split by workload — free, because it changes what humans read, not what is rendered |
| `latest`, `node:20`, `@v4`, `version: "*"` | a magic value that changes without a commit (ch09) | pin by digest or 40-character SHA, with the readable version in a trailing comment — except a chart dependency, which pins to an **exact chart version** rather than a digest |
| A module whose every argument is `var.x` | a pass-through that abstracts nothing (ch03, ch04) | name the decision it should be making — or remove it, which **re-addresses every resource inside it** (`module.x.aws_s3_bucket.this` → `aws_s3_bucket.this`), so it needs a `moved` block (**1.1+**) or a `terraform state mv`, or the plan proposes destroy-and-create |
| A commented-out resource block | a deletion wearing a comment's clothes (ch07, ch09) [`C5`] | decide it: delete the configuration **and read the plan**, since removal destroys the live object — or, to stop managing it without deleting it, a `removed` block carrying `lifecycle { destroy = false }` (**Terraform 1.7+**) or a `terraform state rm` |
| A manifest nothing else mentions | **not** proof it is dead (ch07) | a `Service` selects Pods by **label**, so prove it by what selects it, then delete it by name — removing the file alone orphans the live object |
| `try()` round a lookup, `\|\| true`, `continue-on-error: true` | the empty handler, per ecosystem (ch06) | handle it or let it fail; a quiet wrong state is the one trade never worth making |
| Fifteen `variable` blocks | a module doing several things (ch03) | one `object({...})` variable with `optional()` attributes (**Terraform 1.3+**) |
| `SELECT *` in a view | unexpressed intent and an ISP breach (ch02, ch05) | name the columns — **and price the narrowing first**: in PostgreSQL `CREATE OR REPLACE VIEW` cannot drop columns and `DROP VIEW` defaults to `RESTRICT`, refusing while dependents exist (both executed on 18.6), so narrowing takes a `CASCADE` that drops those dependents with it — enumerate them first. The `*` is expanded **when the view is created** (also executed), so a later base-table column never appears |
| A green pipeline nobody can name the rung of | claiming a rung you do not run (ch08) | state the rung in the PR, in the tool's own words |
| A Conftest suite with no `--namespace` | a gate that evaluates `main`, matches nothing and **exits 0** (ch08) | pass the namespace your package declares, or `--all-namespaces`, or move the policy to `package main` — then make the suite fail once on purpose |
| `force_destroy = true` added to make a plan succeed | the guard telling you the step was not structural (ch10) | remove the flag and fix the step |

## Priority order when rules conflict

```
1. The verification you have passes   ← never traded away                            (ch01, ch08)
2. No duplication                                                                          (ch04)
3. Expresses intent                                                                  (ch02, ch03)
4. Minimizes the number of units and types   ← never overrides 1–3                         (ch05)
```

Rule 1 is the book's *"runs all the tests"*, **generalized**: the plan applies cleanly, the schema
validates, the policy suite passes, the linter is quiet. A design that does not verify is not
simple. Rule 4 never merges two well-named units to have fewer of them — and an interface per class
is the same dogma inverted: *"Such dogma should be resisted and a more pragmatic approach adopted."*

## Judgment calls the sources explicitly allow

- **Magic numbers in a formula the reader already holds** — *"There are some formulae in which
  constants are simply better written as raw numbers"*: `hourlyRate * 8`, `feetWalked / 5280.0`,
  `radius * PI * 2`. **π is the counter-case**, because nobody proofreads a literal they recognize.
  Not a licence for `86400000`, a bare `0.85`, or a repeated `"PENDING"` (ch02).
- **Multiple assertions in one check**, when forcing one would need a base class or a harness —
  *"too much mechanism for such a minor issue."* The rule that survives is one *concept* per check
  (ch08).
- **Loosening encapsulation for a test, as a last resort** — an allowance this skill's chapters do
  not carry, so it is routed rather than restated: the text is `clean-code-java` **ch10**, which
  states it and attributes the idea to its own ch9.
- **Test code may be inefficient; it may never be unclean.** Efficiency is the only dimension where
  the standard differs — *"But they never involve issues of cleanliness."* (ch08)
- **No speculative splitting.** Apply OCP when the change arrives, not before; an interface for a
  capability nobody implements is a maintenance obligation bought against a guess (ch05).
- **Cross-domain duplication stays duplicated** — *"Bad abstractions can be worse than duplicate
  code, so be careful!"* Two implementations in different modules in different domains that merely
  resemble each other keep both copies (ch04).
- **Feature Envy is sometimes a necessary evil the book allows** — a unit working through another
  module's accessors on data that genuinely belongs there (ch05) [`G14`].
- **The adaptations' standing licence**: *"Not every principle herein has to be strictly followed,
  and even fewer will be universally agreed upon"* — permission to override a rule **with a stated
  reason**, never by accident. The tiers never grant it: a tier says whether a rule *can* reach the
  artifact, never whether it should be obeyed (ch01).

## Where this skill stops

- **The 66-item smells-and-heuristics catalogue lives in `clean-code-java` ch17** and is
  deliberately not duplicated here. Ask it for a tag — `G5`, `G23`, `G30`, `N7`, `T9`. Its
  **`J1`–`J3` items are Java-bound by definition** (wildcard imports, inherited constants, `enum`s),
  so they have no universal form and no row in ch01's table.
- **By language**: Java → `clean-code-java`, canonical wherever two siblings disagree · Python →
  `clean-code-python` · TypeScript → `clean-code-typescript` · JavaScript → `clean-code-javascript`.
  Every other language, and every configuration format, is this skill's.
- **Tier 3 is a routing decision, not a gap** (ch01): language-specific idiom — `as const`,
  `@dataclass`, checked exceptions, `Promise.all` — belongs to the sibling that owns the language.
