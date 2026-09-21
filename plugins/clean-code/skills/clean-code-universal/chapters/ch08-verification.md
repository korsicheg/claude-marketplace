# Chapter 8: Verification

## Core Idea

ch01 gives this chapter **one row** — *automated tests, TDD's three laws, F.I.R.S.T.*, **Tier 2,
assuming a test runner** — and the chapter is much bigger than its row, because it also owns the
thing that makes Tier 1 work. Tier 1 assumes two constructs: **a name**, and **some verification
you can run**; ch02–ch07 cash the first, and this chapter cashes the second, through the
**verification ladder** below — the claim that every format supplies *some* verification is only
honest if you can name that verification per ecosystem.

**Two words carry this chapter, so both are defined here.** A **check** is anything executable
that returns a pass or a fail over an artifact: a test case, a policy rule, a schema validation,
a rendered template diffed against a committed baseline. A **rung** is one class of check, named
by what a green result licenses you to claim. Every language and every configuration format
supplies at least one rung; none supplies all seven.

**The rules are properties of a verification suite, not facts about unit tests.** Read F.I.R.S.T.
as five properties and every one of them survives the loss of the runner: a check you can run
often (**Fast**), in any order (**Independent**), in any environment (**Repeatable**), whose
result is a pass or a fail rather than something a human reads and judges (**Self-Validating**),
written with the change rather than after it (**Timely** — the book's form is *"just before"*
the production code, widened here deliberately rather than absorbed). A Conftest suite, a
`kubeconform` run and a `shellcheck` invocation have four of the five outright, wanting only
*Self-Validating* where the output is prose a human interprets. **A `terraform plan` is the weak
case**: it needs credentials, network and state, so it is not *Repeatable* either, and Key
Concepts below says why nobody having authored it is the loss that matters.

**The row is Tier 2 and it stays Tier 2.** Where there is no test runner, TDD's three laws have
no red step you can run and they do not apply — this skill says so rather than approximating a
"red" out of a plan you have not written yet. What remains is the property list, the ladder, and
the rule that governs both: **you own the highest rung available, and you never claim a rung you
do not run** — because *"a system that cannot be verified should never be deployed."*

## Frameworks Introduced

- **The verification ladder** — **not a ch01 row**, and flagged in `SKILL.md` as a
  **derivation**: the book names none of these tools, and the ladder is this skill's own
  translation of Beck's generalized rule 1 into ecosystems with no runner. Seven rungs ordered by
  **the strength of the claim a green result licenses**, from an authored assertion about
  behaviour down to a style check licensing no behavioural claim at all. **"Highest" means
  nearest the top of this list**; rungs 1–3 differ in scope rather than strength, and an
  ecosystem supplying several owns all of them.

  1. **Unit** — one unit of work, in isolation, with its collaborators supplied. Proves the logic.
  2. **Integration** — the unit against a real collaborator. Proves the wiring.
  3. **Contract** — both sides of a boundary against one agreed shape. Proves the interface.
  4. **Policy-as-code** — an executable rule over a rendered artifact or plan. Proves an invariant.
  5. **Plan / diff** — the proposed change, read against what exists. Proves the delta.
  6. **Schema validation** — the artifact against its declared shape. Proves it is well-formed.
  7. **Lint / format** — the artifact against a style and a rule set. Proves nothing behavioural.

  **The rule: own the highest rung the ecosystem gives you, and never claim a rung you do not
  run.** Two separate obligations. The first: a Terraform module in a repo that has
  `terraform test` available is not verified by `tflint`. The second: a green `terraform fmt` is
  not `terraform validate`, `validate` is not a plan (it checks syntax and internal consistency
  and does not contact providers or state), a plan is not a policy suite, and a policy suite is
  not an apply. **The most common failure in configuration repos**, and a failure of *claim*
  rather than of tooling: the pipeline is green and nobody wrote down which rung it belongs to.

- **Automated tests, TDD's three laws and F.I.R.S.T.** *(Tier 2 — a test runner)*. One ch01 row,
  covering three things, tagged here once.
  - **The three laws.** (1) You may not write production code until you have written a failing
    unit test. (2) You may not write more of a unit test than is sufficient to fail — and not
    compiling is failing. (3) You may not write more production code than is sufficient to pass
    that test. The cycle is **roughly thirty seconds long**, and `clean-code-typescript`'s typed
    reading of law 2 is that a test naming a type which does not exist yet is already red.
  - **Where the construct exists in configuration, the laws come with it.** `terraform test`
    (**Terraform 1.6+**, `.tftest.hcl` files with `run` blocks) is a real runner, so red-green
    works: write the `assert` first, watch it fail, then write the resource. A policy suite is
    the other honest red step — write the `deny`, run it against today's plan, watch it fail,
    then change the configuration until it passes. Where neither exists, they do not apply.
  - **F.I.R.S.T. is a diagnostic vocabulary, not a slogan**: it turns "the checks are annoying"
    into one fixable letter. Nobody runs them → **F**. Green alone, red in a full run → **I**.
    Green locally, red in CI → **R**. Someone must read the output to judge it → **S**. Writing
    the check is harder than the change → **T**, a *design* finding. `T9` is what failing **F**
    costs: *"A slow test is a test that won't get run. When things get tight, it's the slow tests
    that will be dropped from the suite."*

- **Build-Operate-Check** — **not a ch01 row**; it is a formatting rule for a check, ch07's
  material applied to verification. Every check splits into three visible parts: build the
  fixture, operate on it, check the result — what makes an unfamiliar check readable in one pass,
  and it survives every rung. A `.tftest.hcl` `run` block is `variables` / `command` / `assert`;
  a Rego policy is the input document / the expression reading it / the `deny` it produces; a
  `bats` case is `setup` / the invocation / the assertion on `$status`.

- **One concept per check** — **not a ch01 row**. The book's own softening is the part to carry:
  one assert per test is a *guideline* Martin states and then declines to enforce, because
  forcing it costs *"too much mechanism for such a minor issue."* The final formulation is
  **minimize the number of asserts per concept, and test just one concept per check.** The tell
  is a **reassigned shared subject**: build, assert, rebuild, assert again is two concepts
  wearing one name, and the second failure hides behind the first.

## Key Concepts

- **The dual standard** — **not a ch01 row**. Checks are held to production standards of
  cleanliness, and **efficiency is the only dimension where the standard differs**: *"There are
  things that you might never do in a production environment that are perfectly fine in a test
  environment. Usually they involve issues of memory or CPU efficiency. But they never involve
  issues of cleanliness."* A `.tftest.hcl` file, a Rego policy and a `bats` script are code, so
  ch02–ch07 bind on them unchanged: a rule named `deny_1` is a test named `2/29/2020`.
- **Dirty tests are worse than no tests**, by a sequence rather than an opinion: hard to change
  → new ones cost more than the production change → old ones fail on every edit → the suite is
  judged a liability → **it is discarded** → nothing catches cross-module breakage → the team
  stops cleaning → the production code rots. *"In a way they were right. Their testing effort had
  failed them. But it was their decision to allow the tests to be messy that was the seed of that
  failure."* The config form: a suite everyone runs with `--ignore` flags until the flags are
  the policy.
- **Name a check after the behaviour, not the data.** *"When a test fails, its name is the first
  indication of what may have gone wrong."* `2/29/2020` → `should handle leap year`;
  `deny_bucket_1` → `deny_public_audit_bucket`. You read the name at 2am with no context.
- **"Hard to verify at all" is a design signal, not a verification one.** ch05 states the
  detector — *"If a system is decoupled enough to be tested in this way, it will also be more
  flexible and promote more reuse"* — and *where* it is hard names the dependency to invert. It
  survives into configuration: a Terraform module you cannot plan on its own, because it reads a
  data source or assumes a named remote state, is too coupled, and the fix is DIP's. ch03's arity
  budget argues it from the other end — each input multiplies the case matrix, so **arity is a
  verification budget** whether the verification is a runner or a plan.
- **Timeliness is what the config rungs lose first.** A plan is written by Terraform, not by
  you, so nothing about it is *Timely*; the timely artifact is the **policy or assertion you
  write alongside the change**. A plan-only repo has no check anybody authored, and so none that
  encodes an intention.

## Mental Models

- **Coverage tells you what you have *not* verified. It never tells you that what you verified is
  right.** `T2` says the same from the other side: coverage reports gaps in your *strategy*. A
  100% figure over assertion-free checks is 100% of nothing.
- **A never-executed line is an impossible condition — prove it and delete it.** ch16 found a bug
  that way: the coverage map **pointed** at a line that never executes and inspection **proved**
  the `if` above it always false [`T8`]. Without a coverage tool, ch15's move does the same job
  — comment the branch out, run the suite, delete it if it stays green.
- **A percentage can drop while quality rises.** ch16's coverage *fell* to 84.9% after the
  refactor, *"not because less functionality is being tested; rather it is because the class has
  shrunk so much that the few uncovered lines have a greater weight."* An instrument, not a score.
- **The rung you claim is a promise about blast radius.** "Validated" from `kubectl apply
  --dry-run=client` means the object was parsed and merged locally: no admission webhook, no
  server-side defaulting, nothing persisted. It is not offline either — it reads the live object
  to compute the merge and pulls the server's OpenAPI to validate, so it fails without cluster
  access. `--dry-run=server` means the object passed the real admission chain and was not
  persisted. Two claims, one word.

## Reference Table: what plays the part of the test

ch09 expands each row per ecosystem; this table is the index.

| Ecosystem | Highest rung available | Tool | What "fast and independent" means here |
|---|---|---|---|
| **General-purpose language with a runner** | Unit → integration → contract | the runner, plus a coverage tool | Milliseconds, no I/O, no shared fixture; a case passes alone and in any order |
| **Terraform / HCL** | Unit (`terraform test`, **1.6+**) → policy → plan | `terraform test`, Conftest/OPA or Sentinel over `terraform show -json`, `terraform validate`, `tflint` | `command = plan` runs in seconds and creates nothing (it still reads, so it needs credentials); `command = apply` **creates real objects and destroys them at the end of the file**, so it is neither fast nor independent, and objects are left behind when the teardown itself fails |
| **YAML / Kubernetes** | Policy → server dry-run → schema | `conftest`, `kyverno`, `kubectl apply --dry-run=server` (**kubectl 1.18+**), `kubeconform` | Schema and policy are offline and order-free; a server dry-run needs a cluster and runs admission webhooks, so it is neither offline nor free of side effects |
| **Helm** | Unit → policy → rendered diff → lint | `helm unittest`, `conftest` over `helm template`, a committed golden render, `helm lint` | `helm template` is local and deterministic, so it is the fast rung; `--validate` and `helm upgrade --dry-run` contact the API server and lose both properties |
| **CI pipeline** | Lint → provider-side validation | `actionlint`, GitLab's `/ci/lint`, a pipeline run on a branch | There is no plan rung: the only full verification is executing the pipeline, so **independence is bought by making the pipeline's effects gated**, not by the checker |
| **SQL** | Unit → integration → plan | `pgTAP`, `tSQLt`, dbt tests, `EXPLAIN` | A unit runs inside a transaction that is rolled back, which is what makes it independent; **`EXPLAIN ANALYZE` executes the statement**, so on a write it must be wrapped in a transaction you roll back |
| **Bash** | Unit → lint → parse | `bats`, `shellcheck`, `bash -n` | `bats` cases are fast and independent only if each builds its own temp directory; `bash -n` parses and does **not** execute, so it catches nothing semantic — not an unquoted variable, not a missing command |
| **Dockerfile** | Integration → lint | `container-structure-test`, a smoke `docker run`, `hadolint` | `hadolint` is instant and offline; a build executes every `RUN`, pulls from registries and mutates the layer cache, so it is the slow, environment-dependent rung |

## Anti-patterns

- **A check with no assertion.** It executes, it is green, it proves the code did not crash. In
  Rego the form is a `deny` rule whose body can never be satisfied, which reports nothing forever.
- **A reassigned shared subject across assertions** — two concepts merged, the second hidden
  behind the first failure.
- **Order-dependent checks.** One case leaving state another consumes: the first failure cascades
  and hides every defect downstream. In config the form is a test file whose later `run` blocks
  depend on an earlier `command = apply`.
- **A suite nobody runs.** Slow, flaky or unrunnable locally — `T9`'s consequence, and the first
  step of the decay sequence above.
- **Claiming a rung you do not run.** `fmt` reported as validation; `validate` reported as a
  plan; a plan reported as a policy pass; `--dry-run=client` reported as "the cluster accepted
  it". State the rung in the PR description, in the same words the tool uses.
- **A policy over the wrong plan input.** `planned_values` cannot see a deletion;
  `resource_changes` carries `no-op` entries and must be filtered on `actions` (worked example).
- **Verifying by applying.** "We'll see if it works in staging" is the apply rung, and the apply
  rung is not a check — it is the change.

## Worked Example: one behaviour, verified twice

The behaviour: **an audit log bucket's objects expire at the configured retention, and never
sooner than the 30-day floor.** Once as a unit check with the runner, once as policy-as-code over
a plan — both Build-Operate-Check, proving different things, and that difference is the point.

**Rung 1 — unit, with the runner** (`terraform test`, **Terraform 1.6+**):

```hcl
# tests/retention.tftest.hcl
variables {
  audit_retention_days = 30                      # BUILD — the fixture is the input set
}

run "expiration_follows_the_retention_variable" {
  command = plan                                 # OPERATE — no apply, so no object is created

  assert {                                       # CHECK — one concept, named for the behaviour
    condition = (aws_s3_bucket_lifecycle_configuration.audit.rule[0].expiration[0].days
                 == var.audit_retention_days)
    error_message = "audit log expiration must follow var.audit_retention_days"
  }
}
```

`command = plan` keeps this rung **Fast** and **Independent**: nothing is created, nothing is
destroyed, and it runs in any order against any account with read access. Switching to
`command = apply` to "make it more realistic" **creates the bucket for real** and relies on the
teardown at the end of the file — which Terraform warns can itself fail, leaving live objects
behind — so the rung stops being independent of every other run.

**Rung 2 — policy-as-code, over the plan.** Same shape, different claim:

```rego
package terraform.audit  # Rego v1 needs OPA 1.0+ (0.59+ with `import rego.v1`), conftest 0.57+

deny contains msg if {
  walk(input.planned_values, [_, node])                       # BUILD — root and child modules
  resource := node.resources[_]
  resource.type == "aws_s3_bucket_lifecycle_configuration"
  days := resource.values.rule[_].expiration[_].days          # OPERATE — read the planned value
  is_number(days)                                             # unknown at plan time? see below
  days < 30                                                   # CHECK — the invariant
  msg := sprintf("%s expires audit objects below the 30-day floor", [resource.address])
}
```

```bash
terraform plan -out=tfplan && terraform show -json tfplan > plan.json
conftest test --namespace terraform.audit --policy policy/ plan.json
```

**That `--namespace` is not decoration; leaving it off is this chapter's own anti-pattern.**
`conftest test` evaluates the `main` namespace by default, so a policy in `terraform.audit` with
no `--namespace` (or `--all-namespaces`) matches no rules, prints nothing and **exits 0** — a
green gate that ran zero checks. `package main` is the other fix; either way, make the suite fail
once on purpose before you trust it passing.

**What each rung proves, and what it does not.** The unit check proves the module wires the
variable through to the resource, for the one input set the fixture supplies. The policy proves
the floor holds across **every** lifecycle configuration in the plan, including ones nobody who
read the module wrote. Neither proves the other: pass the unit check with
`audit_retention_days = 7` and the module is correct and the estate still non-compliant.

**And the value may not be there**, in two ways that behave oppositely. An **absent** `days` —
`(known after apply)` — leaves the reference undefined, so the body never binds and no `deny`
fires. A **`null`** does the reverse: Rego's total ordering puts `null` below every number, so an
unguarded `null < 30` is **true** and denies a resource that set no retention. `is_number(days)`
closes both; an estate-wide claim still needs a companion rule denying an unknown retention
outright, or the check re-run against state.

**The consequence that bites in configuration.** The two plan-JSON inputs are not "whole" versus
"partial", which is the intuition to unlearn. `planned_values` is the state as it will look
**after** the apply: it omits every resource scheduled for **destruction**, so a policy over it
cannot see a deletion, and its resources nest, which is why this rule `walk`s instead of reading
`root_module.resources`. `resource_changes` is flat and carries an entry for **every** resource,
unchanged ones included and marked `"actions": ["no-op"]`, so a rule over it sees every resource
in this configuration, not the estate beyond it, but must filter on `actions` to say anything
about the delta. Both are legitimate and answer different questions; writing one while claiming
the other is the config-repo form of a green build that tests nothing.

## Key Takeaways

1. **ch08 holds one ch01 row — automated tests, TDD's three laws and F.I.R.S.T., Tier 2,
   assuming a test runner.** Where no runner exists the row does not apply; the rest still does.
2. **The verification ladder makes Tier 1's "some verification you can run" concrete**: unit →
   integration → contract → policy → plan/diff → schema → lint. A derivation, not the book's.
3. **Own the highest rung available, and never claim a rung you do not run.** `fmt` passing is
   not validation passing; a client-side dry run is not a cluster's acceptance.
4. **Read F.I.R.S.T. as five properties of any rung**, and use the letters to name what is wrong
   with a painful one. Fast · Independent · Repeatable · Self-Validating · Timely.
5. **The dual standard**: checks are held to production standards of cleanliness, and efficiency
   is the only dimension differing. Dirty checks get abandoned and what they checked rots.
6. **One concept per check, named after the behaviour.** A reassigned subject is the tell.
7. **Structure every check as Build-Operate-Check** — fixture, operation, assertion, on every
   rung.
8. **"Hard to verify" is a design finding.** Invert the dependency; a module you cannot plan
   alone is too coupled.
9. **Recorded disagreement — the coverage number.** `clean-code-typescript` and
   `clean-code-javascript` both target **100% of statements and branches** — *"how you achieve
   very high confidence and developer peace of mind"* — while conceding *"deciding on what
   constitutes an adequate amount is up to your team."* **The book sets no coverage number.** It
   argues from cleanliness and from the TDD cycle, and treats measurement as a diagnostic: `T2`
   says a coverage tool reports gaps in your *strategy*, `T1` rejects *"that seems like enough"*
   in favour of testing everything that could possibly break, and ch16 reports coverage
   **falling** while quality rose. `clean-code-java` is canonical, so **the rule here is the
   book's** — test everything that could possibly break, and read coverage as a map of what you
   have not checked. The adaptations' 100% is a stricter community convention, useful as a
   release gate, not the book's position.

## Connects To
- **[ch01 — what survives translation](ch01-what-survives-translation.md)**: the index of record
  for the one row above; the Tier 1 floor whose second construct this chapter makes concrete; and
  Beck's generalized rule 1, the ladder's charter.
- **[ch03 — units of work](ch03-units-of-work.md)**: the arity budget is a verification budget,
  because each input multiplies the case matrix combinatorially.
- **[ch04 — duplication and abstraction](ch04-duplication-and-abstraction.md)**: duplication in
  checks costs exactly what it costs in production code, and `G5` names it there too.
- **[ch05 — structure and dependencies](ch05-structure-and-dependencies.md)**: testability as the
  coupling detector, and DIP as the fix when a unit is hard to verify.
- **[ch06 — failure](ch06-failure.md)**: a check that asserts on a failure needs the failure to
  be visible and non-silent; a swallowed failure is unverifiable by construction.
- **[ch07 — comments and formatting](ch07-comments-and-formatting.md)**: a check is code, so the
  comment and formatting rules bind on it, and Build-Operate-Check is a formatting rule.
- **[ch09 — declarative and config](ch09-declarative-and-config.md)**: each table row above,
  expanded per ecosystem, with the tools named and the rung stated.
- **[ch10 — improving existing code](ch10-improving-existing-code.md)**: the refactoring protocol
  needs a **green rung** before step 1; where none exists, building one is the first refactoring.
- **`clean-code-java` ch09** — the fullest treatment in the family: the three laws in their
  original form, F.I.R.S.T., Build-Operate-Check, the domain-specific testing language, the dual
  standard, and the cautionary tale of the discarded suite. **ch12** for Beck's rule 1 and
  *"Writing tests leads to better designs."*; **ch15**/**ch16** for coverage as a diagnostic and
  for "comment it out and run the tests" as a deletion proof.
- **`clean-code-java` ch17** — the 66-item catalogue, not duplicated here; ask it for a tag. Its
  test items: `T1` insufficient tests, `T2` use a coverage tool, `T3` don't skip trivial tests,
  `T4` an ignored test is a question about an ambiguity, `T5` test boundary conditions, `T6`
  exhaustively test near bugs, `T7` patterns of failure are revealing, `T8` coverage patterns are
  revealing, `T9` tests should be fast.
- **`clean-code-typescript` ch07** and **`clean-code-javascript` ch07** — the coverage target
  recorded as a disagreement above, the F.I.R.S.T. diagnostic table, and test names as failure
  messages. **`clean-code-python` omits testing entirely**, so its silence is not evidence.
