# Clean Code — Universal Techniques & Patterns

One entry per technique. The general-purpose ones state the construct they need; the
config-oriented ones name the rule they derive from, as
[ch09](chapters/ch09-declarative-and-config.md) does — a declarative technique with no rule behind
it is a bug in this skill, not scripture.

## Extract Until You Can't
**When to use**: any unit longer than a few lines, with any section comment in it, or whose name
needs an "and".
**How**: extract until the next extraction's name would only restate its body (`addOneToCounter`
around `counter += 1`). The body of an `if` or a loop becomes one line, and that line is usually a
call. Keep nesting depth ≤ 2 **wherever the language branches** — that row is Tier 2 and a bare
manifest supplies no branching construct, so its indent depth is the schema's, not a finding
(ch01, ch03). The terminating condition is that name test — "it feels small enough" is not one.
**Trade-offs**: more units and more total lines; you buy a name for every step and a body you can
read without opening any of them. (ch03, ch04, `clean-code-java` ch17 `G30`)

## The TO-Paragraph Test
**When to use**: to decide whether a unit does one thing, in any language or format — it mentions no
construct, so it runs verbatim on a Terraform module and a pipeline stage.
**How**: say *"TO `do-what-the-name-says`, we do X, then Y, then Z"*, where each of X, Y and Z is one
named thing at the next level down. *"TO provision the audit log bucket, we create the bucket, apply
the retention policy, and grant the reader role"*. If the paragraph needs *"…and then, separately,
we also…"*, you have found the split point.
**Trade-offs**: none; it is a reading exercise, and it is the cheapest of the three do-one-thing
tests. (ch03)

## Argument Reduction and the Parameter Object
**When to use**: any unit over the arity budget — 0 ideal · 1 good · 2 costly · 3 avoid · 4+ never —
wherever a parameter list exists (Tier 2).
**How**: bundle the inputs that always travel together into one named object whose fields are the
arguments, and where an input is a collaborator make it **state** rather than an input (ch05). The
real prize is that computation then moves onto that object. The three legitimate single-input forms
are: ask a question about the input, transform it and **return** the result, or take an event in and
return nothing.
**Trade-offs**: one more named type or shape to maintain, and verification gets dramatically
cheaper: each input multiplies the case matrix combinatorially, so the arity budget is a
*verification* budget whether the verification is a runner or a plan. (ch03, ch08, `F1`)

## Split on the Flag
**When to use**: any boolean or selector input. *"Boolean arguments loudly declare that the function
does more than one thing"* — and they declare it in the caller's own source, as a bare `true` in
argument position.
**How**: `render(true)` / `render(false)` → `renderForSuite()` / `renderForSingleTest()`. The `if` in
the body is the seam; each branch becomes an entry point with a name.
**Trade-offs**: more entry points, each doing one thing and reading correctly at the call site.
(ch03, `F3`, `G15`)

## Replace Type Dispatch with Polymorphism
**When to use**: an `if`/`switch` chain keyed on a variant's identity, especially where the same
shape appears elsewhere — **and only where a substitutability mechanism exists** (Tier 2).
**How**: declare the operation on the contract, let each variant implement it, and keep **one**
switch, whose cases create the variants that replace every other such switch. The consumer then
calls the contract and the third variant touches zero existing code.
**Trade-offs**: adding an *operation* now touches every variant, so this is right when new **types**
are likelier than new operations. Where nothing can be dispatched to — HCL, SQL, a bare manifest —
the rule **does not apply**, and a `lookup` on a `type` attribute or a `CASE` over a `type` column is
not a type switch awaiting polymorphism. (ch05, `G23`)

## Extract the Failure Handler
**When to use**: any unit that contains a `try`, or a shell function mixing its own failure handling
into its algorithm.
**How**: error handling is one thing, so it gets its own unit — `try` is the first word and nothing
follows the handler; the body becomes its own unit. Write the failure scope first, then narrow the
caught type to what is actually raised.
**Trade-offs**: one extra unit per handled scope; the algorithm then reads unadorned, and the
transaction scope is fixed before the logic hides it. (ch06)

## Special Case Object
**When to use**: a "missing" case that has a defined business answer — no meals expensed, no
override configured — and anywhere you would return an absent-value sentinel.
**How**: return an object that answers the default, or an empty collection so the caller just
iterates. In HCL the analogue is a `variable` with a real default, or `optional(type, default)`
inside an object type (**Terraform 1.3+**).
**Trade-offs**: one small type; it deletes a branch from every caller. Watch the one place the
analogue inverts: in a Kubernetes strategic-merge patch a `null` **deletes** the field rather than
leaving it unset, so an absent key and a `null` key are not interchangeable and writing one for the
other removes live configuration. (ch06)

## Wrap the Third-Party Vocabulary
**When to use**: any foreign library, provider, chart or base image — and any API returning
sentinels or throwing many failure types.
**How**: a thin unit of yours that **translates and does nothing else**. Keep the foreign type
inside the module that uses it and never accept or return it across your own surface. In
configuration the wrapper is a thin internal module exposing your own variable names over the
upstream one, so an upstream rename is one file's change rather than every root's.
**Trade-offs**: one indirection to maintain; you gain swappability, a test seam, and one failure
vocabulary instead of three. Pinning is the adjacent discipline and translates nothing — commit
`.terraform.lock.hcl`, have child modules state a floor and the root pin the version. (ch05, ch06)

## The Extraction Loop
**When to use**: a module you suspect has more than one reason to change — the name is vague, or the
25-word description needs an "and".
**How**: extract a unit out of a long one → it wants several locals, so promote them to module state
→ cohesion drops, because only a subset of the units touches that state → **split** → repeat. The
state/unit grid reads the same on a struct and on a Terraform module's `locals`.
**Trade-offs**: more modules, none of which is more to learn — the system has the same moving parts
either way, and now you can understand one at a time. A real split leaves a reusable part; one that
leaves nothing reusable was a split by size. **In configuration the split is a state operation**:
moving a resource into a new child module renames its address, so it carries a `moved` block
(**Terraform 1.1+**) or a `terraform state mv` and you read the plan, or the plan proposes
destroy-and-create. (ch05, ch09)

## Explanatory Variable
**When to use**: a calculation, condition or expression whose meaning is not on its face.
**How**: give the intermediate value a name at the point of use. In HCL this is the cheap one: a
`locals` entry is **not** part of the module's interface, so introducing one is invisible to the
plan — still `0 to add, 0 to change, 0 to destroy` — which makes it the cheapest Boy-Scout step the
language has.
**Trade-offs**: one more name, essentially always worth it; it is the comment you did not have to
write. (ch02, ch07, ch10, `G19`)

## Encapsulate the Condition into a Named Predicate
**When to use**: a compound boolean, a negative, or a condition you had to read twice.
**How**: `if (shouldBeDeleted(timer))` rather than `if (timer.hasExpired() && !timer.isRecurrent())`.
Name the question positively and with a yes/no answer — `isPosted`, `hasQuorum`, `is_enabled`; never
`flag`, `status` or `!isNotPresent`.
**Trade-offs**: one named unit or variable; the condition becomes greppable, which in a format with
no compiler is the only find-all-callers you have. (ch02, ch05 `G28`)

## Named Constant for a Magic Value
**When to use**: any token whose value is not self-describing — strings included, so a `"PENDING"`
across nine files is as magic as `86400000` [`G25`].
**How**: name the meaning **and** the unit, keeping the derivation where there is one
(`SECONDS_PER_DAY = 60 * 60 * 24`). The mechanism differs per language and the rule never mentions
one: a `const`, a module attribute, a `locals` entry, a `variable` where the value is meant to be
tunable per environment. **SQL mostly has no constant construct**, so the honest fixes are a lookup
table joined by name, a generated constants file on the calling side, or an enumerated domain type.
**Trade-offs**: a lookup for the reader, paid back the first time the value changes — except where
the formula already carries it (`hourlyRate * 8`), and π is the counter-case, since nobody
proofreads a literal they recognize. (ch02, ch09)

## The Harmless Skeleton Migration
**When to use**: any structural change to code that is already running — this is the refactoring
protocol's step 2, and the protocol is Tier 1, so it reaches every format.
**How**: get the verification green first; add the new abstraction **alongside** the old code so it
changes nothing; migrate **one** use; re-run the rung; fix any break before anything else; expect to
undo earlier steps.
**Trade-offs**: slower than a rewrite and the only approach that reliably lands. In configuration
"harmless" is narrower than it looks: a new **module directory** nothing calls is genuinely inert,
while a new `module` **block** creates every resource inside it on the next apply. Migration renames
addresses, so each step carries its `moved` block (**Terraform 1.1+**) or a `terraform state mv`,
deletes the old block in the **same** commit, and gates on `Plan: 0 to add, 0 to change,
0 to destroy` — and **reversibility ends at the apply**: reverting the commit restores the text, not
a destroyed object. (ch10, ch09)

## Build-Operate-Check
**When to use**: writing any check, on any rung.
**How**: three visible parts — build the fixture, operate on it, check the result. A `.tftest.hcl`
`run` block is `variables` / `command` / `assert`; a Rego policy is the input document / the
expression reading it / the `deny` it produces; a `bats` case is `setup` / the invocation / the
assertion on `$status`.
**Trade-offs**: none; it is a formatting rule for a check, and it is what makes an unfamiliar one
readable in a single pass. Name the check after the behaviour rather than the data, because the name
is the first thing you read when it fails at 2am. (ch08)

## Policy-as-Code as the Missing Test
**Derives from**: ch08's ladder — policy is the highest rung most declarative ecosystems supply, and
the one check in them that somebody actually authors, so it is the only *Timely* artifact a
plan-only repo can have.
**When to use**: an invariant that must hold across every artifact, not just the one you wrote — a
retention floor, no public buckets, required labels.
**How**: write the `deny` first, run it against today's rendered artifact or plan, watch it fail,
then change the configuration until it passes — a real red-green step where no test runner exists.
Rego v1 needs **OPA 1.0+** or **conftest 0.57+**.
**Trade-offs**: it proves an estate-wide invariant and not the wiring a unit check proves; neither
substitutes for the other. Two traps, both silent: `conftest test` evaluates the `main` namespace by
default, so a policy in another package with no `--namespace` (or `--all-namespaces`) matches
nothing and **exits 0**; moving the policy to `package main` is the other fix, and either way make
the suite fail once on purpose. And pick the plan input deliberately: `planned_values` is the state
as it will look after the apply, so it **cannot see a deletion**, while `resource_changes` carries
every resource including `no-op` entries and must be filtered on `actions`. (ch08, ch09)

## Extract a Module from Copy-Pasted Blocks
**Derives from**: ch04's same-reason-to-change test, with ch03's unit as what you extract into and
ch10's protocol as how you land it.
**When to use**: near-identical resource blocks, jobs or templates that a named change hits for one
reason. Run the test first: two that merely resemble each other across domains stay two.
**How**: the smallest tool that does it — `locals` and `for_each` before a module; a module before a
library chart. Then the ch10 steps: green plan, inert skeleton, one use at a time.
**Trade-offs**: the extraction couples the call sites, which is what you wanted, and it **changes
every address it moves**. Converting unkeyed resources — or a `count` — into a keyed `for_each`
changes the instance keys, so it needs **one `moved` block per instance** (**Terraform 1.1+**), not
one per resource, and the old blocks are deleted in the same commit (a `moved` whose `from` address
is still declared fails the plan with `Moved object still exists`). An unkeyed `count` is
index-addressed, so removing a middle element re-indexes every later one and plans
destroy-and-create for each. Gate on `0 to destroy`; `must be replaced` on a stateful object is a
stop, not a warning. (ch04, ch09, ch10)

## Values File as Parameter Object
**Derives from**: ch03's arity budget over a chart's `values.yaml` surface — the parameter list
Helm supplies — plus ch05's ISP, because that surface is also a declared interface.
**When to use**: a chart whose values list has grown past what a consumer can hold in their head, or
whose keys are a flat pile of scalars.
**How**: group related scalars under one named nested object; publish nothing no consumer sets; give
every key with no sane default a `required`. Each value multiplies the case matrix your checks must
cover, so the surface is a verification budget.
**Trade-offs**: consumers' existing files must move with the shape. Helm merges a user's **unknown**
keys without complaint, so a renamed key fails **silently** and the default applies — add a
`values.schema.json` (**Helm 3.0+**) to make the miss loud, and treat removing a key as a breaking
change. (ch03, ch05, ch09)

## CTE as Extracted Unit
**Derives from**: ch03's do-one-thing and the TO-paragraph test, with the CTE as SQL's unit of work.
**When to use**: a query nested more than about two subqueries deep, or one whose steps you can
name but the text cannot.
**How**: one named CTE per level of abstraction, reading top to bottom. A 200-line query with five
well-named CTEs passes the TO-paragraph test where the same query nested four deep does not.
**Trade-offs**: dialect-specific and worth knowing before you claim the rewrite is free. In
**PostgreSQL before 12** a CTE was an optimization fence and always materialized, so an extraction
could change the plan; from 12 a single-use, side-effect-free CTE may be inlined, with
`MATERIALIZED` / `NOT MATERIALIZED` to say which (executed on **18.6**: the plain form inlines, the
`MATERIALIZED` form keeps a `CTE Scan`). Extract for readability, then read `EXPLAIN` — and note
`EXPLAIN ANALYZE` **executes** the statement, so on a write wrap it in a transaction you roll back.
(ch03, ch08, ch09)

## Fail-Fast Preamble (`set -euo pipefail`)
**Derives from**: ch06's *fail loudly* — in Bash its absence makes every other failure rule
unenforceable.
**When to use**: every script, and every `run:` block you can set a shell for. GitHub Actions runs a
`run:` step under `bash -e {0}` by default on Linux and macOS runners, which is **not** `pipefail`;
declare `shell: bash` (`bash --noprofile --norc -eo pipefail {0}`) or set `defaults.run.shell` once.
**How**: `set -euo pipefail` at the top, then quote every expansion (`"$var"`, `"$@"`) and let
`shellcheck` find the rest (SC2086) — an unquoted variable is a silent wrong-value failure, which is
why quoting is a ch06 rule rather than a ch07 one.
**Trade-offs**: `set -e` has holes that are not bugs — it does not fire for a command whose status is
consumed by `if`, `&&`, `||` or `!`, and `local x=$(cmd)` hides `cmd`'s status behind `local`'s own
(executed: under `set -e` the `local` form continues, a bare `x=$(cmd)` exits), so declare and assign
on separate lines. And **turning it on in an existing script changes behaviour at every step that
used to fail quietly**, so read what currently fails first and land it as its own commit. (ch06,
ch09, ch10)
