# Chapter 9: Declarative and Config Languages

## Core Idea

A declarative file has no callables, no types and usually no test runner, so **every Tier 2 rule
must have its construct identified before it binds** (ch01) — and **every Tier 1 rule applies to it
unchanged**. That second half is the one people skip, and it is already most of what goes wrong in
these files: an unsearchable name, a magic literal, a copy-pasted block, a commented-out resource.

**ch01 gives this chapter zero rows, and that is correct.** ch09 owns no rule. Every rule below is
*derived* — it names the ch02–ch08 rule it descends from, and a claim that cannot name one does not
belong here. The book is from 2008 and no sentence in it is about a manifest.

**The derivation is not a translation of words, it is a re-pricing of consequences.** The
generalizable form: **an editing operation in code is often a state operation in config, because a
name here is a key against live state.** Renaming a local in Go is free; renaming a Terraform
resource label changes the resource's *address*, so the plan proposes destroy-and-create; changing
a `metadata.name` makes `kubectl apply` create a second object and orphan the first. Same Tier 1
rule (ch02), three bills. So every rule below states what applying it costs.

## Frameworks Introduced

- **The three questions** — **not a ch01 row**; this chapter's instrument, answered at the head of
  each ecosystem below and tabulated in the Reference Table.
  1. **What is the unit?** (ch03) — the named, reusable thing: module, chart, object, job, stage,
     CTE, view, function, image. ch03 defines a unit as anything you can name and reuse, so **every
     format has one**; only the four rules over its **inputs and return** (ch03, Tier 2) need a caller.
  2. **What is the verification rung?** (ch08) — which of unit / integration / contract / policy /
     plan-diff / schema / lint the format supplies, and which is highest. Own the highest available,
     and **never claim a rung you do not run**.
  3. **What is the failure mechanism?** (ch06) — what makes a failure visible and non-silent here.
     Several of these formats have none of their own, and ch06's table says which.

  Answer all three before quoting a rule at a file, or the rule is the approximation ch01 calls
  worse than an absent rule: uncheckable, and it teaches the reader to discount the rules that reach.

- **The re-pricing step** — **not a ch01 row**. Once you have the rule, ask *what does applying it
  cost here?* Three prices recur. **Free**: a `locals` rename, a deleted comment, a reordered block.
  **A state operation**: a `moved` block, `terraform state mv`, apply-new-then-delete-old.
  **Destructive**: a `DROP VIEW`, a resource replacement, a prune, and a `removed` block that lacks
  `lifecycle { destroy = false }` (**Terraform 1.7+**), which destroys the real object. ch10 owns
  the protocol for the last two prices; this chapter says which is which, so a Tier 1 rule is never
  quoted as free.

## Key Concepts

- **Declarative code has the same coupling and duplication problems as imperative code, and fewer
  tools to hide them.** No compiler catches a renamed key, no type checker catches a wrong shape, no
  callers list exists. ch04's same-reason-to-change test is *more* load-bearing here, not less: the
  only thing between two copied blocks and a silent divergence is somebody's memory.
- **The absence of a compiler moves the burden onto naming and validation.** ch02's searchable rule
  is what `grep` replaces the compiler with; ch08's schema and policy rungs replace the type check.
  A schema you have not run is a type system you declined.
- **Configuration is code that runs in production**, usually with more authority than the
  application it configures — a Terraform module holds the credential that deletes the database.
  ch05's SRP, and the no-secrets rule this chapter derives from ch06, are blast radius not hygiene.
- **Most missing Tier 2 constructs are simply missing, and saying so is the answer** (ch01). HCL
  supplies a parameter list, a return value, a declared interface, an injectable abstraction, an
  absent-value sentinel, a test runner and a branching construct — and **no substitutability
  mechanism**, so OCP, LSP and polymorphism (ch05) do not reach it. A bare YAML manifest supplies
  only the sentinel.

## Mental Models

- **A config file's blast radius is usually larger than a function's, so the same smell costs more.**
  A duplicated helper in Go is a maintenance cost; a duplicated security-group rule is two places an
  open port survives a fix. Tier 1 violations in IaC are not cosmetic.
- **A name here is a key against live state, not a label on a box.** ch02's rename test still
  applies; it is the *rename* that stopped being free.
- **"It applied cleanly" is not a verdict** (ch08) — an apply is the change, not a check.
- **The formatting argument is already settled here** (ch07): `terraform fmt`, `shfmt`, `sqlfluff`,
  `yamlfmt`, `hadolint`. What no formatter gives you is the newspaper rule and vertical ordering.

## The Seven Ecosystems

### YAML, generally

**Unit**: the **document** — one `---`-separated stream entry — and each named key subtree in it.
**Rung** (ch08): **schema** at best, **lint** below it. **Failure mechanism** (ch06): **none of its
own** — the parser aborts, or, worse, succeeds with the wrong type.

- **Keys are names, so every ch02 rule binds unchanged.** `config:`, `data:`, `info:` are ch02's
  noise words; `timeoutSeconds` beats `timeout` because ch02 wants the unit in the name.
  *Consequence*: renaming a key is **not** a rename — nothing type-checks the consumer, so the old
  key stops being read, the new one is unset, the default applies, and the deploy succeeds with the
  wrong value. Make the key required where the format allows (Helm's `required`, a JSON Schema
  `required` list) so the miss is loud (ch06).
- **Anchors and aliases are YAML's only DRY tool, and ch04's caveat bites hardest here.** Extract a
  fragment with `&base` / `*base` / `<<: *base` only where it has **one reason to change** (ch04).
  *Consequence*, three of them: an alias must point at an anchor earlier in the **same document**, so
  `---` ends its reach; the merge key `<<` is a YAML 1.1 extension rather than part of YAML 1.2's
  core schema, so parser support varies; and most tools that read a YAML file and write it back emit
  the **expanded** form, so the first machine edit deletes the abstraction and leaves the
  duplication. Anchors pay in a hand-maintained file, not a generated one.
- **Comments: the one place ch07's rename test cannot be run.** ch07 holds a comment to be an apology
  for a name — but you do not own these names. You cannot rename `terminationGracePeriodSeconds`, so
  where the schema's key cannot carry the intent the comment is the **only** carrier and ch07's
  *why*, *warning* and *amplification* rows keep it. The rest of ch07's ladder still deletes: the
  restatement above `port: 8080`, the dated journal line, the byline, the banner, the commented block.
- **File size and splitting** (ch03's size signal; ch07 owns the file-length figure). A 900-line
  values file fails ch03 on the artifact itself, no call site needed. *Consequence*: splitting is
  cheap for a consumer that globs a directory, expensive for one reading a fixed path, and it
  changes nothing about what is applied.
- **No secrets inline** (ch06 — a failure mode with no failure path: nothing to raise, nothing to
  catch, no exit code). *Consequence*: deleting the line does not undo it. The value is in git
  history, in every clone and in every CI cache, so the remediation is **rotation**. And a
  Kubernetes `Secret` is base64, not encryption — on the kubectl here (**v1.33.9**), `kubectl create
  secret generic db --from-literal=password=hunter2 --dry-run=client -o yaml` prints
  `password: aHVudGVyMg==`, which is the password.

### Kubernetes and Helm

**Unit**: the **object** (`kind` + `metadata.name` + namespace) — named and applied, never invoked,
and every Tier 1 rule reaches it anyway (ch01); for Helm, the **chart** and its named templates.
**Rung** (ch08): policy → server dry-run → schema → lint; for Helm, `helm unittest` → policy over
`helm template` → a golden render → `helm lint`. **Failure mechanism** (ch06): **the object has
none** — its failure design is `readinessProbe`, `restartPolicy` and admission.

- **Two dry-runs, two claims** (ch08). `--dry-run=server` runs the real admission chain and persists
  nothing; `--dry-run=client` reaches neither admission nor server-side validation and — checked on
  the **kubectl v1.33.9** installed here — is not offline either, failing without cluster access even
  with `--validate=false`. On the same binary, `kubectl create configmap MyMap --dry-run=client -o
  yaml` prints `name: MyMap` without complaint, though the server rejects an uppercase name.
- **Labels and annotations are names** (ch02) — searchable, no noise, one word per concept, which
  `app.kubernetes.io/name`, `/instance` and `/component` already give you. *Consequence*: a label
  **value** is capped at **63 characters** (verified on v1.33.9 — `kubectl label --local` refuses a
  64th), so a value encoding a branch plus a SHA is rejected, not truncated.
- **In `apps/v1` a Deployment's `spec.selector` is immutable** (ch02, ch10): renaming a label in
  it is refused by the API server. Delete-and-recreate takes the Pods with it; `kubectl delete
  deployment X --cascade=orphan` (on v1.33.9) instead leaves the ReplicaSets and Pods serving
  while you recreate, and cutting over behind the same Service is free **only where no selector
  carries the renamed label** — the Service's, a `NetworkPolicy` `podSelector`, a
  `PodDisruptionBudget`, a `ServiceMonitor`, a second Service. Orphaning releases **every**
  ReplicaSet it owned — the retained revisions, `revisionHistoryLimit` (default 10), **plus the
  active one** — so **once the new Pods are serving**, delete them all by name: the scaled-to-zero
  revisions are dead configuration (ch07) and the one still running Pods is the cutover itself.
  Get selector labels right once; keep the churn in `metadata.labels`.
- **`metadata.name` is an identity, so ch02's rename is a state operation** (ch10). Under `kubectl
  apply` a changed name **creates a second object** and leaves the first live and unreferenced.
  Delete the old one **by name**. `--prune` is not a peer remedy: per `kubectl apply --help` on
  v1.33.9 it is **alpha** ("not yet complete. Do not use unless you are aware of what the current
  state is"), it "should be used with either `-l` or `--all`", and it deletes only objects that "do
  not appear in the configs and are created by either apply or create --save-config". So it **skips**
  controller-, operator- and Helm-owned objects, and still deletes every *applied* object in that
  selector your file set no longer declares. Argo CD and Flux prune from their own inventory or
  tracking labels — a different mechanism with a different scope.
- **`values.yaml` is the chart's parameter object, so the values surface is the arity budget** (ch03)
  **and a declared interface, so ISP binds** (ch05). Each value multiplies the case matrix, making
  arity a verification budget (ch08). Group related scalars into one named nested object (ch03),
  publish none no consumer sets (ch05), and give those with no sane default a `required`.
  *Consequence*: Helm merges a user's unknown keys without complaint, so a **renamed** value fails
  silently. A `values.schema.json` (**Helm 3.0+**) makes that loud; treat a removal as breaking.
- **Template duplication across charts is decided by the same-reason-to-change test** (ch04). Charts
  whose templates always change together are one library chart (`type: library`, **Helm 3.0+**); ones
  that merely look alike are ch04's cross-domain exception and keep both copies. *Consequence*: a
  library chart couples release cadence — each fix is a version bump in every consumer's `Chart.yaml`.
- **Requests and limits are magic values wherever they are literals** (ch02). `memory: 512Mi`
  repeated across eleven manifests is ch02's defect, and the one that pages you.

### CI pipelines

**Unit**: the **job** and the **step**; the reusable workflow and composite action are the
extractable units. **Rung** (ch08): **lint** (`actionlint`, GitLab's `/ci/lint`), then a branch run —
**there is no plan rung**, so independence is bought by gating the pipeline's effects, not by the
checker. **Failure mechanism** (ch06): **exit codes**; every `run:` block is a shell.

- **Job and step names are the documentation** (ch02, ch07). The step name is what appears beside the
  red X at 2am — ch08's *name it after the behaviour* applied to a pipeline.
  `build-and-push-and-notify` fails ch05's **naming** test: no concise name means too large. And a
  stage is a unit of work that should do one thing (ch03), so a `deploy` job that also builds cannot
  be re-run after a flaky deploy without rebuilding.
- **Duplication across workflows is resolved by reusable workflows and composite actions** (ch04),
  under the same-reason-to-change test. *Consequence*: a shared workflow referenced by a branch ref
  changes under **every** caller at once — the opposite failure from duplication, and arguably worse,
  because no consuming repository changed and no consuming reviewer saw it.
- **A floating tag is a magic value that changes underneath you** (ch02). `actions/checkout@v4` is
  not a version: a git tag is **mutable** and can be repointed by the publisher or by whoever takes
  over the account. Pin the full 40-character commit SHA with the readable version in a trailing
  comment — ch07's *amplification* row earning its keep. *Consequence to accept*: SHA pins never
  update themselves, so pair them with a bump bot and name that trade in the PR.
- **Never swallow** (ch06). `continue-on-error: true` and GitLab's `allow_failure: true` are the
  empty catch block at pipeline level; a trailing `|| true` is the same defect one layer down.
  *Consequence most people miss*: GitHub Actions runs a `run:` step under `bash -e {0}` by default on
  Linux and macOS runners, and that is **not** `pipefail` — a failure mid-pipe stays invisible.
  Declare `shell: bash`, which uses `bash --noprofile --norc -eo pipefail {0}`, or set
  `defaults.run.shell` once. And a pipeline is the highest-privilege YAML in the repository (ch06):
  scope secrets per job and never echo one into a log a fork's PR can read.

### Terraform and HCL

**Unit**: the **module** (ch03), and each named resource block in it. **Rung** (ch08): `terraform
test` (**1.6+**) → policy over `terraform show -json` (Conftest/OPA — **Rego v1 needs OPA 1.0+ or
conftest 0.57+** — Sentinel, Checkov) → `plan` → `validate`, which contacts neither providers nor
state → `fmt`/`tflint`. **Failure mechanism** (ch06): **no exception** — `validation`/`precondition`
**abort** rather than propagate, and `try()`/`can()` **suppress** rather than catch, so a `try()`
round a lookup to quiet a plan is HCL's empty handler: it moves the error from plan time, where it
is a message, to apply time, where it is a wrong resource.

- **A resource label must not repeat its type** (ch02 — do not repeat the container's name in its
  member): `aws_s3_bucket "logs"`, never `aws_s3_bucket "logs_bucket"`. *Consequence, the chapter's
  headline*: the label **is** the address. State is keyed on `aws_s3_bucket.logs`, so renaming it is
  not a search-and-replace — the plan proposes **destroy-and-create** unless the change carries a
  `moved` block (**Terraform 1.1+**) or a `terraform state mv`. Free in Go; a state operation (ch10).
- **`locals` are explanatory variables** (ch02), and they are the cheap ones — a `local` is **not**
  part of the module's interface, so introducing one is invisible to the plan, still `0 to add, 0 to
  change, 0 to destroy`. The cheapest Boy-Scout step HCL has (ch10), and where hardcoded ARNs,
  account IDs, regions and CIDRs go (ch02): a hardcoded account ID makes the module single-tenant,
  surfacing in the second environment rather than in review of the first.
- **Variable count is the arity signal** (ch03, Tier 2 — the `variable` blocks are the parameter
  list, per ch01). Fifteen variables is a module doing several things, and the parameter-object move
  exists: one `object({...})` variable with `optional()` attributes (**Terraform 1.3+**) carries a
  shaped group where twelve scalars carried a pile. *Consequence*: every variable multiplies the case
  matrix your `.tftest.hcl` files and policy suite must cover (ch08). A boolean is worse —
  `create_bucket = true` driving a `count` is ch03's flag input, two modules merged.
- **Copy-pasted resource blocks are resolved by a module or `for_each`** (ch04). *Consequence*:
  converting unkeyed resources — or a `count` — into a keyed `for_each` **changes the instance keys**,
  so it needs **one `moved` block per instance**, not one per resource (ch10). And an unkeyed `count`
  is index-addressed: removing the middle element of its list re-indexes every element after it and
  plans a destroy-and-create for each. So `count` versus `for_each` is a readability **and** a safety
  decision (ch07) — `for_each` keys by a stable string, `count` by position.
- **Outputs are the public interface, and ISP applies** (ch05): do not output what no consumer uses.
  *Consequence, asymmetric*: adding an output is free, removing one is a plan-time error in **every**
  root module referencing `module.x.y`. Mark any output carrying a credential `sensitive = true` or
  it prints in the plan and the CI log (ch06).
- **Data sources are hidden dependencies, and DIP says pass it in** (ch05). `data "aws_vpc"` matched
  by tag binds the module to whatever matches at plan time in whatever account the credentials point
  at, and it cannot be planned in isolation — which ch08 names as a **design** finding rather than a
  testing one. Taking `vpc_id` as a variable puts the dependency in the data flow: ch10's *structure
  that communicates over a parameter that merely enforces*.
- **State is the same coupling at repo scale** (ch05). `terraform_remote_state` reads the other
  root's **entire** state — the widest interface there is, breaching ISP by construction — and needs
  read access to a file that usually holds secrets in plaintext (ch06). Publish one value instead.
- **Formatting is delegated, deletion is not** (ch07). `terraform fmt` handles layout and `tflint`
  the rule set, and `fmt` never reorders or renames, so the newspaper rule stays yours. Removing a
  block plans a **destroy** — **and so does a bare `removed` block**, which by default removes the
  resource from state *and destroys the real object*. To stop managing without deleting it must
  carry `lifecycle { destroy = false }` (**Terraform 1.7+**); `terraform state rm` is the other way.

### SQL

**Unit**: the **view, function, procedure or CTE**; the **schema** is the module (ch05). **Rung**
(ch08): unit (`pgTAP`, `tSQLt`, dbt) → integration → `EXPLAIN`, which under `ANALYZE` **executes** the
statement. **Failure mechanism** (ch06): the statement aborts, and whether anything unwinds is
itself dialect-specific — **PostgreSQL** has transactional DDL (verified on 18.6: a `CREATE TABLE`
in a rolled-back `BEGIN` leaves nothing in `pg_class`), while MySQL and Oracle commit implicitly on
DDL, so a migration cannot be wrapped and a half-finished one stays that way. `NULL` is three-valued
everywhere, so `WHERE status <> 'closed'` drops rows where `status IS NULL`. **A dialect qualifier
is part of every rule here**: the same refactor is a loud refusal in one and silent in another.

- **Naming** (ch02): `tbl_customer` and `vw_active` are type prefixes, which ch02 rejects as noise; a
  column called `amount` with no unit or currency fails the same rule. *Consequence*: a column rename
  is a **contract change** with every view, report and application naming it, and SQL has no
  rename-with-forwarding — so it is add, backfill, migrate readers, drop, one per commit (ch10).
- **CTEs are extracted units, one level of abstraction each** (ch03). A 200-line query with five
  well-named CTEs passes ch03's TO-paragraph test; the same query nested four subqueries deep does
  not. *Consequence, dialect-specific*: in **PostgreSQL before 12** a CTE was an optimization fence
  and always materialized, so an extraction could change the plan; from 12 a single-use,
  side-effect-free CTE may be inlined, with `MATERIALIZED` / `NOT MATERIALIZED` to say which. Extract
  for readability, then read `EXPLAIN` (ch08).
- **`SELECT *` is unexpressed intent** (ch02) and an ISP breach (ch05): a view defined with `*`
  publishes every column of every base table as its interface, and each one a consumer touches is a
  negotiation before that column can move. *Consequence, in PostgreSQL*: the `*` is expanded **when
  the view is created**, so a column added to the base table afterwards never appears in it.
- **Magic literals in predicates** (ch02): `WHERE status = 3`. Most dialects have **no constant
  construct** to extract them into, and ch01 says to state that rather than approximate one — so the
  honest fixes are a lookup table joined by name, a generated constants file on the calling side, or
  an enumerated domain type where the dialect offers one.
- **Views are abstraction with ch04's caveat, and changing one's shape is priced by dialect** (ch10).
  A view two reports share because they genuinely ask the same question is an extraction; one they
  share because it was there is the bad abstraction. In **PostgreSQL**, `CREATE OR REPLACE VIEW`
  cannot rename, reorder or drop columns (appending is allowed) and `DROP VIEW` defaults to
  `RESTRICT`, so the refactor arrives as a loud refusal and `CASCADE` is what makes it destructive —
  enumerate the dependents first. **MySQL** and **Oracle**'s `CREATE OR REPLACE VIEW` and **SQL
  Server**'s `CREATE OR ALTER VIEW` (2016 SP1+) replace the definition wholesale and will rename or
  reorder columns without complaint, and their `DROP` does not refuse while dependents exist — Oracle
  marks them invalid, the others leave them to fail at next use. **Same edit: loud in one dialect,
  silent in the others.**
- **Formatting is delegated** (ch07): `sqlfluff`, whose `dialect` setting is part of the team's
  committed style — the linter cannot parse your SQL until you tell it whose SQL it is.

### Bash

**Unit**: the **function**, and the script. **Rung** (ch08): unit (`bats`) → lint (`shellcheck`) →
parse (`bash -n`, which does **not** execute and so catches nothing semantic). **Failure mechanism**
(ch06): **exit codes**, propagating only under `set -e`, and not everywhere even then.

- **`set -euo pipefail` is ch06's *fail loudly*, and its absence makes every other ch06 rule
  unenforceable.** Without `-e` a failed command is a log line and the script continues on half its
  state; without `-o pipefail` a failure inside a pipe is invisible; without `-u` a mistyped variable
  expands to nothing and `rm -rf "$PREFIX/"` becomes `rm -rf /`. *Consequence of adding it*: turning
  it on in an existing script **changes behaviour at every step that used to fail quietly** (ch06),
  so read what currently fails first — a behaviour change, and its own commit (ch10).
- **`set -e` has holes, and they are not bugs** (ch06). It does not fire for a command whose status is
  consumed by `if`, `&&`, `||` or `!`, and `local x=$(cmd)` hides `cmd`'s status behind `local`'s own
  success — a bare `x=$(cmd)` does not, so **declare and assign on separate lines**.
- **Quoting is a correctness rule, not a formatting one.** An unquoted `$var` is word-split and
  glob-expanded; `"$var"` and `"$@"` are the defaults. This derives from ch06 rather than ch07,
  because an unquoted variable is a silent wrong-value failure. `shellcheck` finds them at scale
  (SC2086) — not behind `eval` or an indirect expansion.
- **Functions and their arity** (ch03, Tier 2 — the positional parameters are the parameter list).
  Four positionals is over budget, and Bash makes it worse because they are **unnamed at the call
  site**: `deploy prod api true 30` is unreadable where `deploy(env=…, wait=…)` is not — and that
  `true` is ch03's flag input in the wild. Bind them to named locals on the function's first lines,
  ch02's intention-revealing rule doing work the language will not.
- **Exit codes carry the operation that failed** (ch06): a distinct non-zero code per case plus a
  stderr line naming the command and its input, because a blanket `exit 1` tells the caller nothing.
  And never swallow — `|| true` is the empty catch block, `2>/dev/null` the same with the evidence
  deleted.
- **Formatting is delegated** (ch07): `shfmt` for layout, `shellcheck` for the rule set — and
  `shellcheck` is the rare linter that finds real defects rather than style, so it is a CI gate
  rather than advice (ch08).

### Dockerfile

**Unit**: the **image**, and each **stage** of a multi-stage build. **Rung** (ch08): integration
(`container-structure-test`, a smoke `docker run`) → lint (`hadolint`) → image scan; a build is the
slow rung, since it executes every `RUN` and pulls from registries. **Failure mechanism** (ch06):
**exit codes** — a non-zero `RUN` aborts the build, and each `RUN` is its own shell.

- **One concern per image** (ch05, SRP). An image running the app, its cron jobs and a sidecar proxy
  fails the 25-word test, and ch05's reason is the operative one: three reasons to change means it is
  rebuilt and redeployed three times as often as any one of them needs.
- **A toolchain and a runtime have different reasons to change, so multi-stage builds split them**
  (ch05's SRP; ch05 lists a Dockerfile stage as a module). The builder stage holds the compiler,
  toolchain and source, the final stage the artifact. The *separate construction from use* framing
  is `clean-code-java` ch11, which this skill does not distil. *Consequence, a security one*: every
  layer of a single-stage build ships inside the image, so a credential written by one `RUN` and
  deleted by the next is **still in the image** — the deletion adds a layer, it does not remove the
  earlier one. A stage you never `COPY --from` never ships.
- **A floating base tag is a magic value that changes underneath you** (ch02). `FROM node:latest` and
  `FROM node:20` are both mutable; `FROM node:20.11.1-bookworm@sha256:…` is not. *Consequence to
  accept*, as with the CI pins: a digest pin never updates itself, so pair it with a bot or a
  scheduled rebuild or you are pinned to an unpatched base.
- **Layer ordering is vertical distance** (ch07 — the stronger the dependence, the less distance).
  Copy the dependency manifest and install before the source, because a changed layer invalidates
  every layer after it. *Consequence*: the one formatting rule in this skill with a measurable
  runtime cost — backwards, every one-character source edit reinstalls every dependency.
- **Duplication and delegation** (ch04, ch07): a shared base stage the others build `FROM` is the
  extraction and it couples their rebuild cadence, so run the same-reason-to-change test first.
  `hadolint` owns the style and runs `shellcheck` over the `RUN` lines, so the Bash rules above are
  enforced inside your Dockerfile too.

## Reference Table: the three questions, answered

| Ecosystem | The unit | Verification rung (highest first) | Failure mechanism (ch06) | Formatter / linter |
|---|---|---|---|---|
| **YAML, generally** | the document; each named key subtree | schema (`check-jsonschema`, `ajv`) → lint | **none of its own** — the parser aborts, or succeeds with the wrong type | `yamllint`, `yamlfmt`/`prettier` |
| **Kubernetes** | the object (`kind` + `metadata.name` + namespace) | policy (`conftest`, Kyverno) → `apply --dry-run=server` → `kubeconform` → lint | **none of its own** — `readinessProbe`, `restartPolicy`, admission | `kubeconform`, `kube-linter` |
| **Helm** | the chart; the named template | `helm unittest` → policy over `helm template` → golden render → `helm lint` | template `required` / `fail`, then Kubernetes' | `helm lint`, `values.schema.json` (3.0+) |
| **CI pipeline** | the job; the step; the reusable workflow | lint (`actionlint`, `/ci/lint`) → provider validation → a branch run. **No plan rung** | exit codes, per step; `continue-on-error` is the swallow | `actionlint`, `yamllint` |
| **Terraform / HCL** | the module; each resource block | `terraform test` (1.6+) → policy over `show -json` → `plan` → `validate` → `fmt` | **no exception** — `validation`/`precondition` abort; `try()` suppresses | `terraform fmt`, `tflint` |
| **SQL** | the view, function, procedure, CTE; the schema is the module | unit (`pgTAP`, `tSQLt`, dbt) → integration → `EXPLAIN` | statement aborts; what unwinds is dialect-specific — PostgreSQL has transactional DDL, MySQL and Oracle commit implicitly on DDL; `NULL` is three-valued | `sqlfluff` (dialect-configured) |
| **Bash** | the function; the script | `bats` → `shellcheck` → `bash -n` (parse only) | exit codes, under `set -e` and not everywhere | `shfmt`, `shellcheck` |
| **Dockerfile** | the image; each build stage | `container-structure-test` / smoke `docker run` → `hadolint` → image scan | exit codes — a non-zero `RUN` aborts the build | `hadolint` (wraps `shellcheck`) |

## Anti-patterns

- **A 900-line values file nobody can diff** (ch03 size signal; ch05 SRP). Nothing in it is
  reviewable, so every change is approved on trust. Split by workload — the split is free, because it
  changes what humans read and not what is rendered.
- **Anchors used so heavily the file cannot be read top to bottom** (ch04's bad-abstraction caveat;
  ch07's vertical ordering). Every alias is a jump, and a reader following four has lost the
  newspaper rule.
- **A module with a variable per attribute of the resource it wraps** (ch03, ch04). A pass-through
  module abstracts nothing: it adds indirection, an address change and a version to manage, and
  buys no decision. If its body is one resource whose every argument is `var.x`, name the decision
  it should be making — or remove it, which re-addresses every resource inside
  (`module.x.aws_s3_bucket.this` → `aws_s3_bucket.this`), so it needs a `moved` block (**1.1+**)
  or `terraform state mv`, or the plan proposes destroy-and-create.
- **`latest`, anywhere** (ch02): `image: app:latest`, `FROM node:latest`, `@main`, `version: "*"`. A
  magic value whose meaning changes without a commit, so no two applies are the same change.
- **Commented-out resource blocks** (ch07, `C5`). Worse in configuration than in code, because no
  reader can tell whether it was ever applied — and in Terraform commenting a resource out is not a
  pause but a **deletion**: gone from the configuration, still in state, so the next plan destroys it.
- **A Bash script with no `set -e` and a trailing `|| true`** (ch06). Together they mean the script
  cannot fail, so it also cannot be verified (ch08) and every claim it makes is unchecked.
- **Secrets in plain text with a comment apologizing for them** (derived from ch06; ch07). The
  comment proves the author knew — ch07's case where the fix is the code, not the prose. Rotate
  first, then remove; deleting the line changes nothing that matters.

## Worked Example: two copy-pasted blocks become one `for_each`, with `plan` as the green rung

Two near-identical queues, `aws_sqs_queue.orders` and `aws_sqs_queue.invoices`, differing only in
`name` and `visibility_timeout_seconds` and sharing a literal `message_retention_seconds = 345600`.
ch04's test says one reason to change, so they are one idea written twice. ch10 owns the protocol.

**Step 0 — green** (ch10 step 1; ch08's plan rung). `terraform plan` must print `No changes. Your
infrastructure matches the configuration.` If it does not, somebody's undeployed change is in front
of you and you cannot tell your diff from theirs. **Step 1 — the skeleton** (ch10 step 2) is a
`locals` block mapping `orders` and `invoices` to their timeouts: a `local` is not part of the
interface and creates nothing, so re-planning still gives `0 to add, 0 to change, 0 to destroy`.

**Step 2 — the keyed resource and its moves, in one commit** (ch10 step 3). The two old blocks are
**deleted in this same commit**, and the refusal is plan-time: a `moved` block whose `from`
address is still declared fails with `Moved object still exists`, so nothing applies at all. Drop
the `moved` blocks and it gets quieter and worse: SQS `CreateQueue` returns the existing queue
when name and attributes match, so two addresses bind one queue.

```hcl
resource "aws_sqs_queue" "work" {
  for_each                   = local.queues
  name                       = "acme-${each.key}"
  visibility_timeout_seconds = each.value.visibility_timeout_seconds
  message_retention_seconds  = 345600          # still a magic literal (ch02) — see step 5
}

moved {                                        # Terraform 1.1+ — one block PER INSTANCE
  from = aws_sqs_queue.orders
  to   = aws_sqs_queue.work["orders"]
}

moved {
  from = aws_sqs_queue.invoices
  to   = aws_sqs_queue.work["invoices"]
}
```

**Why two blocks and not one.** A resource-level `moved` carries every instance with its key intact,
but that is the case where the **keys do not change**. Here they do — the old addresses are unkeyed
and the new ones keyed by string (ch10) — so each instance needs its own block naming its key.
Whatever a wrong form does, the gate is the same: anything but `0 to destroy` means a move did not
land, and the address it failed to migrate is scheduled for deletion.

**Step 3 — run the rung and read it for the exact verdict** (ch10 step 3; ch08).

```text
  # aws_sqs_queue.orders has moved to aws_sqs_queue.work["orders"]
  # aws_sqs_queue.invoices has moved to aws_sqs_queue.work["invoices"]

Plan: 0 to add, 0 to change, 0 to destroy.
```

**That line is the acceptance criterion and it does not move.** ch10 lists what a non-zero number
can mean besides the obvious — a shifted provider default, refresh-surfaced drift, a `default_tags`
injection — so diagnose before applying. `must be replaced` means an attribute forcing replacement
differs, and for a queue replacement is deletion: **the messages go too.** A stop, not a warning.
Gate the step with a Conftest rule and you must pass the `--namespace` your package declares, or it
evaluates `main`, matches nothing and **exits 0** — a green gate that ran no rules (ch08).

**Step 4 — a break gets fixed before anything else** (ch10 step 4). If the plan proposes replacement
because `"acme-${each.key}"` renders one name differently from the live one, nothing has been applied
and the fix is free — which is why step 3 runs before step 5. Diff the two plan JSONs
(`terraform show -json tfplan`), never the terminal output.

**Step 5 — apply the plan you gated, then take the cleanup as its own commit.** `terraform apply
tfplan` applies the artifact that passed; a bare `terraform apply` **re-plans**, so what lands is not
what you read (ch10). `message_retention_seconds = 345600` is still the magic value ch02 names — it
becomes `local.four_days_in_seconds` in a **separate** commit, because that rename plans
`0 to change` and must not share a commit with a state operation (ch10).

**Step 6 — the `moved` blocks stay until every workspace has applied** (ch07's dead-code rule,
deferred): one that has not applied reads the resource as new and proposes destroy-and-create. In Go
step 2 would be a compile; here every step is a state operation and three of them can destroy a
queue with messages in it — which is what the tiny steps buy (ch10).

## Key Takeaways

1. **Every Tier 1 rule applies to these files unchanged** (ch01) — names, duplication, do-one-thing,
   size, SRP, comments, dead code, the refactoring protocol. No construct hunt first, and that is
   most of what is wrong in your YAML.
2. **Answer the three questions before quoting a rule**: the unit (ch03), the verification rung
   (ch08), the failure mechanism (ch06) — or you have the approximation ch01 calls worse than an
   absent rule.
3. **An editing operation in code is often a state operation in config**, because a name here is a
   key against live state. A Terraform label is the address; a `metadata.name` is an identity. State
   what a change costs, every time (ch10).
4. **Never claim a rung you do not run** (ch08). `terraform validate` is not a plan; a plan is not a
   policy pass; `kubectl apply --dry-run=client` does not reach admission — and, on the kubectl here,
   does not even run offline.
5. **The values surface, the variable list and the positional parameters are parameter lists** (ch03,
   Tier 2), so the arity budget binds on all three (ch08). **Outputs, view column lists and values
   keys are declared interfaces** (ch05), so ISP binds — and removal is the expensive direction.
6. **A floating tag or a `latest` is a magic value that changes without a commit** (ch02). Pin by
   digest or SHA — a chart dependency by an exact version — and accept the bot you now need.
7. **Say whose dialect, whose version and whose tool.** A Postgres behaviour is not SQL; a `moved`
   block needs Terraform 1.1+; `--prune` is alpha and scoped. An unqualified claim about a
   destructive operation is the most dangerous sentence this chapter can contain.
8. **The honest limit: this chapter is synthesis, not extraction.** The book predates every language
   in it and ch01 gives ch09 no rows. Each rule above names the ch02–ch08 rule it derives from, and
   an unlabelled declarative rule is a bug in this skill, not scripture.

## Connects To
- **[ch01 — what survives translation](ch01-what-survives-translation.md)**: the index of record.
  ch09 owns **zero rows** and tags nothing; it applies ch01's rows per ecosystem, and ch01 lists
  which constructs HCL and a bare manifest actually supply.
- **[ch02 — names and magic values](ch02-names-and-magic-values.md)**: keys, labels, resource labels,
  job and step names, column names; magic literals, hardcoded ARNs, floating tags.
- **[ch03 — units of work](ch03-units-of-work.md)**: the unit per ecosystem, the size signal, and the
  arity budget over `values.yaml`, `variable` blocks and positional parameters, plus flag inputs.
- **[ch04 — duplication and abstraction](ch04-duplication-and-abstraction.md)**: anchors, library
  charts, reusable workflows, `for_each`, views and shared base stages — under the
  same-reason-to-change test, with the bad-abstraction caveat and the cross-domain exception.
- **[ch05 — structure and dependencies](ch05-structure-and-dependencies.md)**: SRP over a chart and
  an image; ISP over outputs, values keys and view columns; DIP over data sources and remote state;
  and the rows that stay empty, since HCL and SQL supply no substitutability mechanism.
- **[ch06 — failure](ch06-failure.md)**: the mechanism table these sections instantiate — exit codes,
  plan-time validation, no-mechanism formats — plus never-swallow, and the **derived** no-secrets rule.
- **[ch07 — comments and formatting](ch07-comments-and-formatting.md)**: the comment triage ladder,
  the schema-key case where the rename test cannot be run, vertical ordering as layer ordering, dead
  configuration, and the formatter delegation for every ecosystem above.
- **[ch08 — verification](ch08-verification.md)**: the ladder every rung above comes from, the
  per-ecosystem table this chapter expands, and the rule against claiming a rung you do not run.
- **[ch10 — improving existing code](ch10-improving-existing-code.md)**: the protocol every state
  operation above runs under, and the reminder that reversibility ends at the apply.
- **[references/declarative-translation.md](../references/declarative-translation.md)**: the
  compressed one-row-per-rule lookup these seven sections feed.
- **No sibling skill covers these languages.** `clean-code-java`, `clean-code-python`,
  `clean-code-typescript` and `clean-code-javascript` each name their language, and none covers
  configuration — which is why this chapter exists. For the 66-item smells catalogue ask
  `clean-code-java` for a tag such as `G5`, `G9` or `C5`.
