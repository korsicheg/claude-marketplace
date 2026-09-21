# Chapter 4: Duplication and Abstraction

## Core Idea

Duplication *"may be the root of all evil in software."* It is rule 2 of Beck's four — above
expressiveness, below only verification — and `clean-code-java` ch17 opens its entry on it with
*"one of the most important rules in this book"* [`G5`]. Yet the rule as usually quoted, *don't
repeat yourself*, asks a question the artifact cannot answer. Two fragments that look alike are
either one idea written twice or two ideas that happen to share a shape this quarter, and
nothing in the text distinguishes them.

**The question is never "is this duplicated" but "do these share a reason to change?"** A copy
that must change whenever its twin changes, for the same reason, is duplication, and its cost is
the obligation to remember every copy. A copy that will change for its own reasons is a
coincidence of shape, and merging it buys a dependency nobody asked for.

Both rules ch01's table assigns this chapter are **Tier 1**: each assumes a name and nothing
more. Extraction needs somewhere to put the shared thing, and ch03's **unit of work** — function,
module, resource block, pipeline stage, query, recipe — is supplied by every language and every
configuration format. What differs is not whether you can extract but **what the extraction
costs**, and in configuration that cost is paid against live state rather than against a
compiler. This chapter says so where it arises.

## Frameworks Introduced

- **The same-reason-to-change test** *(Tier 1)*. Before merging two fragments, name a change you
  expect and say whether it lands on both. If every change you can name hits both copies for the
  same reason, they are one idea and belong in one unit. If you can name one change that hits
  only one of them, the shape is a coincidence. The test is a prediction, so it is a judgment —
  but a *checkable* one, because you had to say the change out loud and someone can disagree
  with it. "They look alike" is not an answer to it.
- **Extract until you cannot.** The terminating condition is the one ch03 states for units: stop
  when the next extraction's name would only restate its body. Before that point, extract —
  *"creating a clean system requires the will to eliminate duplication, even in just a few lines
  of code."* Three repeated lines clear the bar.
- **The bad-abstraction caveat, and the cross-domain exception** *(Tier 1)*. *"Bad abstractions
  can be worse than duplicate code, so be careful!"* — stated outright by all three adaptations.
  Extraction creates a dependency between the call sites: they now share an artifact, and
  whoever needs them to diverge pays to undo it. The caveat has a **stated scope**, narrower
  than "when in doubt, don't": two implementations in **different modules in different domains**
  that merely resemble each other stay duplicated, because the extracted code *"introduces an
  indirect dependency between the two modules."* Resemblance is not a shared reason to change.
  - **Recorded disagreement.** `clean-code-java`, which is the book, presses on eliminating every
    repeat and states no cross-domain exception. All three adaptations state the caveat
    explicitly, and `clean-code-typescript` states the cross-domain case in as many words. Java
    is canonical on the **priority** — duplication outranks expressiveness — and the adaptations
    supply the exception that stops the priority being applied blindly. Both are recorded, and
    neither is quietly folded into the other. The book is not naive about the risk either: ch12
    names over-applied deduplication as one of the two things Beck's rule 4 exists to brake.

## Key Concepts

- **Three lines is enough.** ch12's worked example extracts a three-line image-replacement
  sequence shared by two methods, and the extraction is what makes the design problem behind it
  visible. The threshold was never a line count; it is the test above. Three lines that must
  change together are duplication, and one line that must change in nine places is worse.
- **Near-miss duplication is the normal case**, because the near-miss is *why* the copy was made:
  *"two or more slightly different things, that share a lot in common, but their differences
  force you to have two or more separate functions…"* Tell a near-miss from a coincidence by
  asking what the **consumer** reads. Where the consumer never reads the difference, the
  difference need not exist in its inputs and the copies are one idea. Where the consumer
  branches on the difference — or is about to — the copies are two.
  - Make them identical before you judge: *"lines of code that are similar can often be massaged
    to look even more alike so that they can be more easily refactored."* An unaligned near-miss
    is hard to read the test against, and aligning it costs nothing if you then keep both copies.
- **The parallel-edits signal.** When each new case requires the same N edits in the same N
  places, an abstraction is trying to be born, and the count is the measurement. ch10 owns this
  as the stop rule — stop adding cases and extract first. Here it is the strongest evidence the
  same-reason-to-change test can have, because it is not a prediction: the changes already
  happened, and they already landed together.

## Mental Models

- **Duplication is a coupling question wearing a typing question's clothes.** It presents as "I
  typed this twice" and it is settled on "will these change together" — the axis ch05 decides SRP
  on, one altitude down. Which is why the fix and the mistake look identical in the diff:
  extracting couples two call sites, and the only difference between a good extraction and a bad
  one is whether the domain had already coupled them.
- **The abstraction is the thing you are designing, not what is left over.** A merge whose result
  you cannot name in one honest phrase has not found an abstraction, it has found a container.
  `utils` and `common` are the names that get used when the naming failed.
- **In configuration, extracting is a state operation.** Pulling duplicated resources behind a
  shared Terraform module or a `for_each` changes their addresses, and an address *is* the
  identity, so the plan reads as destroy-and-create unless you carry the move with you. That is
  the nerve ch02's rename rule touches, for the same reason. The extraction is still right; read
  the plan before you apply it.

## Reference Table: the duplication decision

| What you are looking at | The test's answer | Action | The trade-off you accept |
|---|---|---|---|
| **Identical, same domain** — the same lines serving one idea | one reason to change | **Extract now**, even at three lines | one more unit to name, and the call sites are now coupled — which is what you wanted |
| **Identical, different domains** — the same lines in two unrelated modules | two reasons to change | **Keep both copies** | you will fix the same bug twice; you are buying the right to diverge without a negotiation |
| **Near-miss**, and the consumer never reads the difference | one reason to change | Massage them identical, extract, and drop the distinction the consumer ignores | if the consumer later *does* read it, you are back here with a merged unit to split |
| **Near-miss**, and the consumer branches on the difference | two reasons to change | **Keep both** — or push the difference behind one named step that each copy calls | the shared step is a real abstraction; the branch would not have been |
| **Structural** — same algorithm, same shape, different types | one reason to change, for the shape | Extract the shape and leave the types alone: a generic unit, a template method, a strategy, a module taking the type as an input [`G5`] | the shape is now a thing to version; every caller reads it to understand their own code |

## Anti-patterns

- **Deduplicating across a domain boundary.** Billing and ingest both paginate an API in eleven
  identical lines. Extract a shared `pagination` helper and the next change to billing's
  pagination becomes a change to ingest's, negotiated with ingest's owners. The eleven lines were
  cheaper than the negotiation.
- **A shared `utils` module that couples unrelated consumers.** The name is the tell: ch02 lists
  `utils`, `helpers`, `common` and `misc` among file names that do not say what is inside. A
  module you cannot describe is a module whose blast radius nobody can bound — and everything
  depends on it. Extract into a unit named for the **idea**; if you cannot name the idea, you
  have not found one.
- **Parameterizing until the parameter list encodes the differences.** The merge "works", so the
  differences become arguments: a flag for the branch, a string for the label, two more inputs
  for the parts that never lined up. **This is where ch03's arity budget fires as the warning** —
  past three inputs you are over budget, and a flag input is already two units merged [`F3`].
  `clean-code-python` states the stop condition outright: if the merge needs a flag to tell its
  cases apart, abandon the merge. The flag is the variation telling you it was real.
- **Deduplicating on the first repeat.** With one example of a pattern you cannot see the axis of
  variation, so you guess it, and a guessed axis is exactly the bad abstraction the caveat warns
  about. The opposite failure is real too, and the adaptations name it: *"if you can make a good
  abstraction, do it!"* Caution that never ends is duplication with a rationale attached.
- **Treating a copied configuration block as free because copying it was.** Ninety near-identical
  lines of pipeline, one environment name apart, is the parallel-edits signal at its loudest:
  every pipeline change is now N edits and the N-th is the one that gets missed.

## Worked Example: two pairs in one Terraform root, decided by one test

**Pair one — identical, same domain.** Two buckets in the audit pipeline expire their objects
the same way:

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id
  rule {
    id     = "expire-past-retention"
    status = "Enabled"
    filter {}
    expiration { days = 2555 }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "audit_exports" {
  bucket = aws_s3_bucket.audit_exports.id
  rule {
    id     = "expire-past-retention"
    status = "Enabled"
    filter {}
    expiration { days = 2555 }
  }
}
```

Name a change: *the retention obligation is revised to eight years.* It lands on both, for one
reason — this is one compliance rule written twice, and `2555` is the magic value ch02 would have
named. Name another: *exports become customer-visible and need a shorter window.* That one does
not land on both, but it is not a change to how these expire; it moves `audit_exports` out from
under the obligation, and out of the pair. The test says extract, and the smallest tool that
does it is `for_each` rather than a module:

```hcl
locals {
  audit_buckets = {
    audit_logs    = aws_s3_bucket.audit_logs.id
    audit_exports = aws_s3_bucket.audit_exports.id
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "audit" {
  for_each = local.audit_buckets
  bucket   = each.value
  rule {
    id     = "expire-past-retention"
    status = "Enabled"
    filter {}
    expiration { days = var.audit_retention_days }
  }
}
```

**What this costs, which the equivalent extraction in code does not.** The two addresses were
`…lifecycle_configuration.audit_logs` and `…audit_exports`; they are now
`…lifecycle_configuration.audit["audit_logs"]` and `…audit["audit_exports"]`. The address is the
identity, so `terraform plan` proposes **destroy-and-create** for both unless you record the move
— one `moved` block per instance (Terraform 1.1+), or `terraform state mv`. Here the blast radius
is small, because the object being replaced is a lifecycle configuration attached to a bucket.
Do the same `for_each` extraction to the `aws_s3_bucket` resources themselves without the `moved`
blocks and the plan proposes destroying the buckets, which is the difference between a refactor
and an incident. Read the plan; that is what ch01 means by the verification you have.

**Pair two — near-miss, different domains.** The build cache bucket has the same shape:

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "build_cache" {
  bucket = aws_s3_bucket.build_cache.id
  rule {
    id     = "expire-stale-cache"
    status = "Enabled"
    filter {}
    expiration { days = 7 }
  }
}
```

Name changes again: *the retention obligation moves to eight years* — does not touch the cache.
*CI drops to a three-day cache to cut spend* — does not touch audit. No change anyone can name
lands on both. Same shape, two domains, so they stay separate, and adding `build_cache` to
`local.audit_buckets` would be a bad abstraction with a plausible diff. A shared
`bucket_with_lifecycle` module is the same mistake one level up: it needs inputs for the window,
the rule id, the storage-class transitions, whether object lock applies and which key encrypts —
five inputs whose only job is to re-encode the differences the module erased. That input list is
the merge confessing.

**What plays the part of the DRY tool, per ecosystem.** HCL has `locals`, `for_each` and modules.
YAML has anchors and aliases (`&`/`*`), plus the merge key `<<:` where the parser implements it —
it is a YAML 1.1 type, not part of the 1.2 core schema. GitLab CI adds `extends`; GitHub Actions
supports neither anchors nor merge keys, and its units are composite actions and reusable
workflows. **The caveat binds to all of them equally** — a wrong anchor couples two jobs exactly
as a wrong module couples two stacks. Two properties are worth knowing before reaching for an
anchor: it is resolved by the **parser**, so the object that gets applied is the expanded copy and
`kubectl get -o yaml` shows you the duplication you thought you had removed; and an anchor is
scoped to the **document** that defines it, so it reaches across neither a `---` nor a file
boundary. What it removes is duplication in the source — which is where duplication costs you.
Say that, rather than believing the live state got simpler.

## Key Takeaways

1. **The test is "do these share a reason to change?", not "is this duplicated."** Name a change
   and say whether it lands on both copies. Looking alike is not evidence.
2. **Duplication is rule 2 of four** — above expressiveness, below only verification — and three
   repeated lines already clear the bar.
3. **Bad abstractions can be worse than duplicate code**, and the exception is stated, not vibes:
   different modules in different domains, resembling each other, stay duplicated, because
   extraction would introduce an indirect dependency between them.
4. **Recorded disagreement**: the book presses to eliminate every repeat and states no
   cross-domain exception; all three adaptations state the caveat. Java is canonical on the
   priority, the adaptations supply the exception, and both are kept.
5. **Near-miss is the normal case.** Ask what the consumer reads. A difference the consumer never
   reads does not need to exist; a difference it branches on is two ideas.
6. **Parallel edits are the signal that does not require a prediction.** The same N edits in the
   same N places for every new case means extract before the next case, not after.
7. **If the merge needs a flag, or pushes you past the arity budget, abandon the merge.** The
   parameter list is where a wrong abstraction confesses.
8. **In configuration, extraction is a state operation.** Addresses change, so carry the move —
   `moved` blocks or `terraform state mv` — and read the plan before applying it. The DRY tools
   differ per ecosystem; the decision does not.

## Connects To
- **[ch01 — what survives translation](ch01-what-survives-translation.md)**: the index of record
  for both rules above, and Beck's four rules in priority order, where duplication is rule 2 and
  rule 4 is the brake on over-applying it.
- **[ch02 — names and magic values](ch02-names-and-magic-values.md)**: synonym drift is how
  duplicate implementations get created in the first place, because the next author greps for the
  word you did not use — and a `utils` module is a naming failure before it is a coupling one.
- **[ch03 — units of work](ch03-units-of-work.md)**: the unit is what you extract *into*, the
  extract-until-you-cannot condition is stated there, and the arity budget is the alarm that
  fires when a merge starts encoding its differences as inputs.
- **[ch05 — structure and dependencies](ch05-structure-and-dependencies.md)**: SRP is the same
  axis one altitude up — a bad abstraction is precisely a unit with two reasons to change, so SRP
  is how you check a merge after the fact.
- **[ch09 — declarative and config](ch09-declarative-and-config.md)**: YAML anchors, Helm named
  templates, `extends`, composite actions and Terraform modules applied per ecosystem — DRY tools
  the caveat binds just as hard, plus the state cost of every extraction.
- **[ch10 — improving existing code](ch10-improving-existing-code.md)**: the stop rule is the
  parallel-edits signal as a habit, and tiny steps under green verification is how an extraction
  gets landed without a big-bang restructure.
- **`clean-code-java` ch12 and ch17** — ch12 is Beck's four rules, reuse in the small, and the
  three-line extraction; ch17 is the 66-item catalogue, not duplicated here, where `G5`
  **Duplication** names the three forms and their three cures. Ask that skill for a tag.
