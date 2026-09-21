# Chapter 10: Improving Existing Code

## Core Idea

**Write it dirty, then clean it.** Nobody produces the final form in one pass, and the book says
so about its own examples: *"I don't write them that way to start. I don't think anyone could."*
ch14 opens the same way — *"I did not simply write this program from beginning to end in its
current form. More importantly, I am not expecting you to be able to write clean and elegant
programs in one pass."* The first draft is expected, and shipping it unchanged is the failure:
*"It is not enough for code to work."*

**So the discipline is entirely in how the cleaning is sequenced**, which is why ch01 gives this
chapter **five rows and all five are Tier 1**: write it dirty then clean it, tiny steps under
green verification, the stop rule, the Boy Scout Rule, and LeBlanc's Law. Four of them assume
nothing but *some verification you can run*; the stop rule assumes only *a name*. No test runner,
no type system, no class — which is what makes this chapter the one that reaches a Helm chart
and a stored procedure unchanged.

**And it is where the Tier 1 promise costs the most.** In a general-purpose language a bad step
is undone by `git checkout`. In configuration every step below is a **state operation** — a
`moved` block, a `terraform state mv`, an apply-new-then-delete-old, a `metadata.name` rename —
each with a failure mode, each reached mid-refactor, and a reverted commit does not restore a
destroyed object. So every step states its own consequence, in the format it bites in.

## Frameworks Introduced

- **Write it dirty, then clean it** *(Tier 1 — some verification)*. Plan for a rough draft, a
  second and a third. The corollary is the one people drop: **build the verification while you
  are building the mess.** ch14's `Args` had JUnit tests *and* FitNesse acceptance tests
  *"created while I was building the festering pile."* The tests came first, during the mess, not
  after it — which is what makes every later step affordable.

- **The refactoring protocol** *(Tier 1 — some verification)* — ch01's *tiny steps under green
  verification* row, stated as the family cheatsheet's numbered steps, each with what it costs in
  configuration.
  1. **Get verification green and covering the behaviour, first.** Whatever rung you have
     (ch08), not necessarily a test suite. **In config, "green" means an empty diff**:
     `No changes. Your infrastructure matches the configuration.`, a `kubectl diff` that prints
     nothing, a rendered template matching its committed golden file. *Consequence*: a plan that
     already proposes changes means you are refactoring on top of somebody's undeployed change,
     and you will not be able to tell your diff from theirs. Land theirs first.
  2. **Add the new abstraction as a harmless skeleton alongside the old code.** ch14 appended the
     `ArgumentMarshaler` classes to the end of the mess — *"Clearly, this wasn't going to break
     anything."* *Consequence*: in configuration, what is harmless is narrower than it looks. A
     new **module directory** that nothing calls instantiates nothing and is genuinely inert; a
     new `module` **block** is not a skeleton at all, because it creates every resource inside it
     on the next apply, and it bills. The declarative equivalent of an unused class is an
     uncalled *definition*, never an added *instance*.
  3. **Migrate one use; run the verification.** One, then the rung, then the next.
     *Consequence*: in Terraform the migration of one use **renames an address**, and the address
     is the identity — so it carries a `moved` block (**Terraform 1.1+**) or a
     `terraform state mv`, or the plan proposes destroy-and-create. A `moved` block written at
     resource level carries every instance of that resource with its key intact; it is when the
     **keys** change — `count` to `for_each`, or separate resources folded into one keyed
     resource (ch04) — that you need one block per instance.
  4. **A break gets fixed before anything else.** *"Incrementalism demanded that I get this
     working quickly before making any other changes."* Failing *"in exactly the same way"* as
     before is the proof that no new error was introduced. *Consequence*: "the same way" is not
     eyeballable in a plan. Capture both runs — `terraform plan -out=tfplan && terraform show
     -json tfplan` — and diff the JSON, so the comparison is mechanical rather than visual.
  5. **Expect to undo earlier steps.** *"Often one refactoring leads to another that leads to the
     undoing of the first."* That is convergence, not failure: *"Refactoring is an iterative
     process full of trial and error, inevitably converging on something that we feel is worthy
     of a professional."* *Consequence*: **reversibility ends at the apply.** Reverting the
     commit restores the text and does not restore a deleted bucket, a dropped view or a
     destroyed disk. So the steps you have not applied are free to undo, and the steps you have
     applied are undone only by a new forward change — which is why step 3's gate is
     `0 to destroy`.

- **The same steps, priced outside Terraform.** The protocol is Tier 1 and reaches every format;
  only the **cost** is per ecosystem, and Terraform is not the expensive one.
  - **Kubernetes** — a `metadata.name` rename under `kubectl apply` is a **create**, not a rename:
    the old object stays live, so a Deployment doubles its pods and a StatefulSet's PVCs stay bound
    to the old name. Delete the old object by name. `--prune` is not the remedy — alpha by its own
    help text, scoped by `-l`/`--all`, and limited to what `apply` or `create --save-config` made,
    so it skips controller- and Helm-owned objects and still deletes what your split left out.
  - **Helm** — adoption needs `app.kubernetes.io/managed-by: Helm` plus **both** annotations,
    `meta.helm.sh/release-name` and `meta.helm.sh/release-namespace`; two of the three gets you
    `invalid ownership metadata`. Until adopted, uninstalling the old release **deletes the live
    object**: adopt first, uninstall second. Between subcharts of one release, no adoption needed.
  - **SQL, per dialect** — **PostgreSQL**'s `CREATE OR REPLACE VIEW` cannot rename, reorder or drop
    columns and its `DROP VIEW` defaults to `RESTRICT`, so enumerate dependents before `CASCADE`
    takes them; MySQL, Oracle and SQL Server replace wholesale and invalidate: silent, not loud.

- **The stop rule** *(Tier 1 — a name)*. **Stop adding features the moment each new case requires
  parallel edits in the same N places.** ch14's trigger was exactly that: each new argument type
  needed new code in three separate places, and the conclusion was *"Many different types, all
  with similar methods — that sounds like a class to me."* The decision it produced:
  > *"If I bulldozed my way forward, I could probably get them to work, but I'd leave behind a
  > mess that was too large to fix. If the structure of this code was ever going to be
  > maintainable, now was the time to fix it. So I stopped adding features and started
  > refactoring."*
  - **N is the measurement**; "it feels messy" is not. Count the places the *last* case touched
    and the places the *next* one will. When the count stops changing and only the values do,
    the module already exists and has not been written down yet.
  - **In configuration N is usually visible in the file list.** A new environment that means
    editing the module, the root, the tfvars and the pipeline matrix is N = 4. A new service that
    means a Deployment, a Service, an Ingress and a CI job is N = 4. That is a chart or a module
    trying to be born, and ch04 states the same signal from the duplication side.

## Key Concepts

- **The Boy Scout Rule** *(Tier 1 — some verification)*: *Leave the campground cleaner than you
  found it.* Every check-in leaves the code strictly better than you found it, never merely
  not worse. One renamed variable, one extracted unit, one deleted duplicate. ch15 applies it to
  code that was already good, because *"each of us has the responsibility to leave the code a
  little better than we found it."* **Consequence in configuration**: an opportunistic rename is
  not free — a Terraform label *is* the resource's address (ch02), so a Boy-Scout rename carries
  its `moved` block or it waits for a commit of its own. Keep the cleanup out of the behaviour
  commit either way, so that when the apply goes wrong you can revert exactly one thing.
- **LeBlanc's Law** *(Tier 1 — some verification)*: *later equals never.* The cleanup that is not
  in this change is not going to happen. If it genuinely cannot be in this change, it is a
  tracked work item, not a mental note. The cost argument behind it is ch14's: *"If you made a
  mess in a module in the morning, it is easy to clean it up in the afternoon. Better yet, if you
  made a mess five minutes ago, it's very easy to clean it up right now."* Cleanup cost grows
  superlinearly, because modules *"insinuate themselves into each other, creating lots of hidden
  and tangled dependencies."*
- **First make it work, then make it right** — ch16's two phases, sequential and neither
  optional. Phase one raises the verification until it finds real defects; phase two walks the
  artifact top to bottom: *"I will be running all of the JCommon unit tests… after every change I
  make."* Doing both at once is how a structural and a behaviour change share one commit.
- **Prefer structure that communicates a constraint over a parameter that merely enforces it** —
  **not a ch01 row**; it is step 6 of the family cheatsheet and ch15's most instructive pair. A
  correct fix for a hidden ordering was **rejected and undone** because *"It works to establish
  the ordering but does nothing to explain the need for that ordering. Another programmer might
  undo what we have done"* [`G31`, `G32`]. The configuration instance is exact: `depends_on`
  enforces an ordering and explains nothing, so the next person deletes it; passing the other
  module's `output` in as an input enforces the same ordering **and** shows why, because the
  dependency is now in the data flow.
- **Most of a refactor is deletion.** *"The majority of the changes were deletions."* A refactor
  that only adds has built the skeleton and migrated nothing — see the anti-pattern below.

## Mental Models

- **A big-bang restructure is a bet that you understood the system before you changed it.**
  *"One of the best ways to ruin a program is to make massive changes to its structure in the
  name of improvement. Some programs never recover from such 'improvements.' The problem is that
  it's very hard to get the program working the same way it worked before."* Many tiny changes
  under green verification is the same work without the bet, and the rule that enforces it is
  *"I am not allowed to make a change to the system that breaks that system."*
- **A refactor you cannot verify is a rewrite with a nicer name.** The word "refactoring" claims
  behaviour did not change. Without a rung, that is an assertion, not a finding.
- **The plan is the diff, so read it as one.** In code the compiler tells you the shape changed
  and the tests tell you the behaviour did not. In configuration one artifact does both jobs, and
  it only works if you actually read it — `0 to add, 0 to change, 0 to destroy` is a pure
  structural refactor; anything else is a behaviour change you did not intend.
- **Bad code is uniquely unrecoverable among a project's problems.** *"Bad schedules can be
  redone, bad requirements can be redefined. Bad team dynamics can be repaired. But bad code rots
  and ferments, becoming an inexorable weight that drags the team down."*

## Reference Table: refactoring under each verification rung

| Highest rung you have | "Green before you start" means | The smallest safe step | The break signal |
|---|---|---|---|
| **A test runner** | the suite passes **and covers the behaviour you are about to move** — coverage of the moved behaviour is the precondition, not the suite's total | one extraction or one rename, suite re-run | a red test; fix it before anything else, and "fails in exactly the same way" means no new error |
| **A plan or live diff** (`terraform test`, `terraform plan`, `kubectl diff`) | `No changes. Your infrastructure matches the configuration.`, or an empty `kubectl diff`, on every root or cluster you will touch | one address moved, with its `moved` block, in one commit | anything but `0 to add, 0 to change, 0 to destroy`; a `must be replaced` on a stateful object is a stop, not a warning |
| **Policy-as-code** | the suite passes against today's rendered artifact or plan | one file's change, re-render, re-run | a new `deny` — **and also** a rule that stopped matching anything, which means your refactor moved the thing out from under the policy |
| **A rendered diff** (`helm template`, `kustomize build`) | the committed golden render matches current output byte for byte | one template extracted or one file split | **any** diff at all; a pure structural refactor renders identically, so a one-line diff is a real finding |
| **Schema validation** | every artifact validates against its schema or CRD | one field moved, one file split | a validation error — but note it cannot see semantics, and a field the schema does not know about can be dropped silently |
| **Lint only** | the linter is silent at the rule set currently committed | a rename inside one file, after grepping the repo for callers | nothing: lint cannot see behaviour, so the step must shrink to what a reviewer can hold in their head |
| **None** | you do not have one, so you do not have a refactor | **build a rung — that is the first refactoring** | the cheapest rung is a golden render: commit the current output of `helm template` / `kustomize build` / `terraform show -json tfplan`, and require every structural change to leave it unchanged |

## Anti-patterns

- **Refactoring with no green rung.** Without one, "I only moved things around" is a hope. Build
  one first: a golden render is an afternoon and pays for itself on the first step.
- **Mixing a behaviour change into a structural change in one commit.** In code this makes review
  impossible; in configuration it makes the plan **unreadable**, because you can no longer tell
  which half of the diff was supposed to be empty.
- **Bulldozing past the stop rule**, and leaving behind *"a mess that was too large to fix."*
  *"Programmers who satisfy themselves with merely working code are behaving unprofessionally."*
- **Leaving the skeleton and the old path both live.** In code it is dead code (ch07, `G9`); in
  configuration **both are applied** — two sets of objects, two bills, and two writers to the same
  external thing. What a name collision does then is per service and worth checking before you
  rely on it: a second `CreateRole` fails 409 `EntityAlreadyExists` and leaves the apply
  half-done, while an S3 bucket you already own gets 200 in `us-east-1` — two addresses on one
  bucket, ACLs reset — and 409 `BucketAlreadyOwnedByYou` elsewhere.
- **`terraform state mv` on a shared backend, by hand.** It edits state immediately, appears in
  no diff and gets no review. On a backend without locking, two people running it concurrently
  leave a state that knows about one move; with locking they serialise, and the command takes and
  releases the lock itself — you do not hold one around it. Either way, back up first
  (`terraform state pull > backup.tfstate`). A `moved` block is the reviewable form: it lands in
  the commit with the change and applies atomically with it.
- **Deleting the `moved` blocks too early.** They can go once **every** state that needs them has
  applied. If the configuration serves several workspaces or environments, one that has not yet
  applied will read the resource as new and propose destroy-and-create.
- **Adding `force_destroy = true` (or its equivalent) to make a refactor's plan succeed.** The
  refusal you are suppressing is the guard that told you the step was not structural.
- **`-target` to make a step "smaller".** It applies part of the graph and leaves configuration
  and state divergent; Terraform itself warns it is for exceptional recovery, not routine use.
  Smaller steps come from smaller commits, not from partial applies.

## Worked Example: one copy-pasted block becomes a module, with `plan` as the green rung

Two near-identical bucket blocks, `audit_logs` and `audit_exports`, differing in a name and a
retention. The protocol, one use at a time.

**Step 0 — green.** `terraform plan` prints `No changes. Your infrastructure matches the
configuration.` If it does not, stop here and land whatever is pending.

**Step 1 — the harmless skeleton.** Write `modules/log_bucket/` with its `variable`s, its
resources and its `output`s, and **call it from nowhere**. Re-run the plan: still no changes,
because an uninstantiated module directory creates nothing. This is the configuration form of
*"Clearly, this wasn't going to break anything."*

**Step 2 — migrate one use, with the move recorded, in one commit.**

```hcl
module "audit_logs" {
  source         = "./modules/log_bucket"
  name           = "acme-audit-logs"
  retention_days = var.audit_retention_days
}

moved {                                        # Terraform 1.1+
  from = aws_s3_bucket.audit_logs              # the old address
  to   = module.audit_logs.aws_s3_bucket.this  # the new one
}
```

The old `aws_s3_bucket.audit_logs` block is **deleted in this same commit**. Leaving both live is
refused at plan time: its address is still declared, so the `moved` block above fails with `Moved
object still exists` and nothing is applied. Without that block the plan proposes a second bucket
under the same name, and for one you already own `CreateBucket` returns 200 in `us-east-1` — two
addresses on one bucket, and the call **resets that bucket's ACLs** — and 409
`BucketAlreadyOwnedByYou` elsewhere.

**Step 3 — run the rung and read it for the exact verdict**, with `terraform plan -out=tfplan`. A
new local `source` needs `terraform init` first, or the plan stops at *Module not installed*.

```text
  # aws_s3_bucket.audit_logs has moved to module.audit_logs.aws_s3_bucket.this

Plan: 0 to add, 0 to change, 0 to destroy.
```

**That line is the acceptance criterion, and it does not move**: a mistyped `to` address lands
in state and then plans a destroy, so `0 to destroy` catches this step's own worst failure. The
*diagnosis* of a non-zero number is less certain. `1 to change` **usually** means the module's
defaults differ from the inline block you replaced — but it can also be a provider default that
moved with a version bump, a `lifecycle { ignore_changes }` the old block carried, drift the
refresh surfaced on this run, or a `default_tags`-style injection. Find out which before you
apply. `must be replaced` means an attribute that forces replacement differs — and for a bucket,
replacement is deletion, which AWS refuses while objects remain unless `force_destroy = true`.
Adding that flag to get past the refusal converts a saved refactor into deleted audit logs.

**Step 4 — a break gets fixed before anything else.** Say the plan proposes replacement because
the module computes `bucket = "${var.name}-${var.env}"` while the old block had no suffix. Fix
the module, re-plan, and diff the two plan JSONs rather than the two terminal outputs. Nothing
has been applied yet, so this fix is free — which is the reason step 3 runs before step 2 is
repeated.

**Step 5 — apply the plan you just gated**, with `terraform apply tfplan`. A bare
`terraform apply` **re-plans**, so what lands is not the artifact that passed the gate, and under
`-auto-approve` nothing re-confirms it. Then take the second use as its own commit: never migrate
both uses in one apply, or you will not know which one caused a wrong plan.

**Step 6 — the cleanup that must wait.** Once every workspace has applied, the `moved` blocks are
dead configuration and ch07 says to delete them. Until then they are load-bearing.

**What this cost, against the same refactor in Go.** In Go, step 2 is a compile and step 5 does
not exist. Here every step is a state operation and three of them can destroy a stateful object,
so the tiny steps are not a style preference — they keep each mistake inside one reviewable plan.

## Key Takeaways

**All five of this chapter's ch01 rows are Tier 1**, tagged once each above.

1. **Write it dirty, then clean it.** Nobody writes the final form first; build the
   verification while you build the mess, so the cleaning is affordable when you get to it.
2. **Tiny steps under green verification**: green first → skeleton → migrate one use →
   re-run → fix any break before anything else → expect to undo earlier steps.
3. **"Green" is whatever rung you have** (ch08), and in configuration it means an **empty diff**.
   No rung at all means you have a rewrite, not a refactor — so build the rung first.
4. **The stop rule**: stop adding features the moment each new case needs parallel
   edits in the same N places. N is the measurement; "it feels messy" is not.
5. **The Boy Scout Rule**: every check-in leaves it strictly better, never merely not
   worse — and in configuration a rename carries its `moved` block or waits for its own commit.
6. **LeBlanc's Law**: *later equals never*. Cleanup cost grows superlinearly, so the
   cheapest moment to clean is the one five minutes after the mess.
7. **Never mix a behaviour change with a structural one** in a single commit; in config it makes
   the plan unreadable, which is the only instrument you have.
8. **Prefer structure that communicates a constraint over a parameter that enforces it** — a
   passed `output` over a `depends_on` — because the next person deletes what nothing explains.
9. **Reversibility ends at the apply.** Git restores text, not deleted objects; `0 to destroy` is
   the gate that keeps the undo cheap.
10. **Expect to reverse your own earlier steps.** That is convergence, not failure.

## Connects To
- **[ch01 — what survives translation](ch01-what-survives-translation.md)**: the index of record
  for the five Tier 1 rows above, and Beck's rule 1 generalized to the verification you have.
- **[ch02 — names and magic values](ch02-names-and-magic-values.md)**: the rename is the smallest
  Boy-Scout step, and the reason it is not free in Terraform — the label is the address.
- **[ch03 — units of work](ch03-units-of-work.md)**: extraction is what most of these steps do,
  and the extract-until-you-cannot condition tells you when to stop.
- **[ch04 — duplication and abstraction](ch04-duplication-and-abstraction.md)**: the
  parallel-edits signal is the stop rule seen from the duplication side, and the bad-abstraction
  caveat is what stops step 2's skeleton being the wrong shape.
- **[ch05 — structure and dependencies](ch05-structure-and-dependencies.md)**: an SRP split is a
  refactoring, so it runs through this protocol; the extraction loop is the design engine behind
  the steps.
- **[ch07 — comments and formatting](ch07-comments-and-formatting.md)**: deleting the old path
  and the spent `moved` blocks is the dead-code rule, and a commented-out old block is not a
  rollback plan.
- **[ch08 — verification](ch08-verification.md)**: the ladder this chapter's step 1 depends on,
  and the rule that you never claim a rung you do not run.
- **[ch09 — declarative and config](ch09-declarative-and-config.md)**: the per-ecosystem form of
  every state operation named above — `moved` and `state mv`, `metadata.name` renames, Helm
  release ownership, view dependencies.
- **`clean-code-java` ch14, ch15 and ch16** — the three long-form case studies this chapter
  compresses: `Args` refactored in hundreds of tiny test-verified steps with the stop rule in the
  middle of it; `ComparisonCompactor` refactored in ~15 named steps with one of them deliberately
  reversed; and `SerialDate` reviewed work-then-right, with coverage used to find real defects.
  **ch01** for LeBlanc's Law and the Boy Scout Rule as first stated.
- **`clean-code-java` ch17** — the 66-item catalogue, not duplicated here: `G9` dead code, `G31`
  hidden temporal couplings, `G32` an argument that enforces without explaining, `G5`
  duplication. Ask that skill for a tag.
- **`clean-code-typescript` ch01** and **`clean-code-javascript` ch01** — the wet-clay framing
  ch01 records: code is shaped in review, and the 3 Rs are the acceptance test for a step.
