# Chapter 7: Comments and Formatting

## Core Idea

*"Don't comment bad code — rewrite it."* Two rules, one move. A comment is an apology for code
that failed to express itself — *"comments are always failures"* — so the default is to delete
the comment by improving the code, and the only survivor says something the code cannot say.
Formatting is the same economy: a decision made once, encoded in a tool, and never argued about
again, because arguing about it is *"a waste of time and money for engineers."* Neither is a
matter of taste, and both are about deleting the artifact — the comment, the debate — rather
than tidying it.

All five rows ch01's table assigns this chapter are **Tier 1**, and this is the chapter that
ports most completely: nothing in either rule mentions a function, a class or a type. A
Kubernetes manifest nobody calls still has names, comments, blank lines and an order, so every
rule below reaches it unchanged — which also makes this the chapter most freely ignored in
declarative files, where "it's only config" excuses a 900-line values file with a banner every
forty lines and three commented-out blocks nobody dares touch. What does **not** port is the
consequence: deleting a block of code removes something nothing runs, deleting a block of
configuration removes something that **is running**, and reformatting a file can rebuild an
image or roll a Deployment. Where that is true below, this chapter says what the change costs.

## Frameworks Introduced

- **The rename test.** *"If a name requires a comment, the name does not reveal its intent."*
  Read every comment as a naming suggestion, because it usually contains the name you need:
  `// Check if subscription is active` is `isSubscriptionActive` with the wrong punctuation.
  Rename, extract the unit, or name an explanatory variable — then delete the comment. There is
  no third outcome: the code absorbed the comment, or the comment says something the code
  cannot, which is what the enumeration below is for. ch02 states the same test from the naming
  side, and that these are one test is the point of stating it twice.
- **The default is don't, and the legitimate kinds are enumerated** *(Tier 1)*. Comments rot,
  because nothing checks them: code moves, splits and merges, and the prose is orphaned in
  place. *"Inaccurate comments are far worse than no comments at all"* — a stale comment costs
  the next reader a debugging session, which is why the default is deletion rather than
  maintenance. The allowance, in full:
  - **Legal** — a copyright or licence header required by policy; point at the licence text
    rather than inlining it.
  - **Intent** — why this decision was made, as against what the code does. The highest-value
    kind, and the one no rename reaches.
  - **Warning of consequences** — what breaks if the next reader does the obvious thing.
  - **Amplification** — marking something that looks inconsequential and is not.
  - **TODO with a stated plan** — what is degenerate here and what its future should be. The
    marker is what makes it findable by grep and by tooling, and it is *"never an excuse to
    leave bad code in the system"*: scan the list and clear it.
  - **Where the book's table is fuller.** `clean-code-java` ch04 lists three further kinds —
    *informative*, *clarification*, and documentation for a **published** API — each with a
    caveat folding it back toward the five: informative is *"usually better fixed by renaming"*,
    clarification applies only to a signature you **cannot alter**, and published-API docs *"can
    be just as misleading, nonlocal and dishonest as any other comment."* The five stand
    unconditionally; those three where their condition holds.
  - **Recorded disagreement — whether the kinds get enumerated at all.** `clean-code-typescript`
    and `clean-code-javascript` are markedly terser. They name only *what*-comments as targets,
    endorse `// TODO` as the one form they positively allow, and hedge: *"Good code **mostly**
    documents itself"*, the emphasis on *mostly* being the source's own. Neither enumerates the
    legitimate **why**-kinds, and `clean-code-typescript` says so about itself, routing the
    reader to `clean-code-java` ch04 for the vocabulary. That is **terseness, not conflict**:
    neither says a why-comment is forbidden, and the *mostly* is the room the enumeration fills.
    `clean-code-python` omits comments altogether, which is silence rather than disagreement.
    Java is canonical, so the enumeration stands — and terser is not truer. A reader holding
    only the adaptations' rule knows what to delete and has no vocabulary for what to keep,
    which in practice deletes the warning along with the noise.
- **Delegate formatting to the formatter, and the team's style wins over yours** *(Tier 1)*.
  Every programmer has favourite rules, *"but if he works in a team, then the team rules"* —
  and *"it doesn't matter a whit where you put your braces so long as you all agree"* [`G24`].
  Martin's own team settled theirs in about ten minutes, and the result was not what he
  personally preferred. So: agree once, encode it in a formatter, commit the config, run it in
  CI, stop reviewing whitespace. Naming the tool is part of the rule, because "be consistent"
  with nothing enforcing it decays. `terraform fmt` ships with Terraform; `gofmt`, `rustfmt`,
  `black` and `shfmt` are canonical; Prettier covers YAML, JSON and Markdown; `sqlfluff format`
  and `pg_format` cover SQL. Dockerfile has a linter (`hadolint`) and no canonical formatter —
  the honest answer for Dockerfiles, not a licence to hand-align them.

## Key Concepts

- **Vertical ordering: the newspaper rule** *(Tier 1)*. Read a file top to bottom like a
  newspaper article — the name is the headline, the top holds the high-level concepts, and
  detail increases as you descend. Concretely: entry point first, each helper directly below its
  first caller, caller above callee. This is ch03's stepdown rule from the formatting side, and
  the one formatting decision no tool makes for you. Its stated failure mode is a helper with
  several callers: put it below the *first* one and accept that, because the rule is "keep
  related things vertically close", not a total order. A declarative file reads the same — the
  object a reader came for at the top and what it depends on below, a pipeline's stages in
  execution order rather than alphabetical, a Terraform `output` beside the resource behind it.
- **Vertical openness, density and distance.** A blank line separates two complete thoughts and
  the eye is drawn to the first line *after* it; **no** blank line inside a tightly related
  group, because adjacency is how a reader knows those lines belong together. Then [`G10`]: the
  stronger the relationship between two pieces of code, the less vertical distance between them
  — affinity comes from direct dependence *and* from similarity. The skipped corollary: **do not
  split closely related concepts into different files without a very good reason**, which in
  configuration is what decides whether a values file is one file or six.
- **File and line size — the figures, and the part of them that ports.** Files around **200
  lines** with **500** as the upper limit, and lines **≤ 120**. These are the most Java-bound
  numbers in the book, measured on 2008-era Java projects — FitNesse at ~50,000 lines, average
  file near 65, maximum near 400; JUnit and Time and Money none over 500 — and 120 columns is
  stated as Martin's own personal setting. The **signal** transfers: a file too big to hold in
  your head is too big in any language. The **numbers** do not — 200 lines of Helm values is
  unremarkable and 200 lines of Terraform is six or seven resources, because structure rather
  than statements fills the lines. ch03's table marks both rows Java-era for this reason; set
  them per ecosystem in the formatter config.
- **Never collapse a scope to one line, and don't column-align.** Martin undid every one-line
  scope he wrote, and changed his mind on alignment the same way: it emphasises the wrong thing
  — the eye runs down the names without the types, or the values without the assignments — and
  **if a list is long enough to want alignment, the problem is the length of the list.** The
  honest nuance is that `terraform fmt` aligns consecutive `=` in a block as a rule, and the
  team's style wins, so what is prohibited is aligning **by hand as a judgment call**. The
  signal survives either way: a block whose alignment is doing real work is a block to split.
  The one-line-scope rule has a configuration exception: a block with one argument or none, such
  as HCL's `expiration { days = 30 }` or a bare `filter {}`, is the idiom and `terraform fmt`
  will not expand it, because collapsing hides nothing when the structure is that small.
- **Reformatting is free in code and sometimes is not in configuration.** A compiler sees a
  token stream, so whitespace costs nothing. Several configuration tools hash the text instead.
  A Dockerfile's `RUN` instruction text is part of that layer's build-cache key, so re-wrapping
  the command rebuilds that layer and every layer below it. The common Helm `checksum/config`
  annotation is a hash of the **rendered** ConfigMap, so any reformat of the template that
  changes the rendered text changes the pod template and **rolls the Deployment** — one that
  renders identically does not. And in YAML quoting is semantic, not cosmetic: under the YAML
  1.1 resolver PyYAML and other widely used loaders still implement, an unquoted `no`, `on` and
  `22:30` resolve to `false`, `true` and the integer 1350. Format anyway — but land it as its
  own commit, expect the rebuild or the rollout, and never strip quotes by hand to tidy a
  column.

## Mental Models

- **A section comment inside a unit is a unit waiting to be extracted.** The author already
  named the sub-unit; the only missing step is the extraction. The book's capstone takes a
  heavily "documented" prime generator whose body is divided by six markers such as
  `// declarations`, `// sieve` and `// return the primes`, turns each into a named method,
  and ends with two comments surviving out of a dozen.
- **A closing-brace or end-of-block comment means shorten the unit.** `} // while`,
  `# end of ingress` at the bottom of a long resource block: you needed the marker because you
  had lost sight of the opening. Shorten the unit and the marker deletes itself.
- **Both are structural signals, not text problems** — which is why "delete the noise comments"
  is bad advice on its own. Deleting the marker leaves the over-long unit in place and destroys
  the evidence that found it. Fix the structure; the comment then has nothing to mark.

## Reference Table: comment triage

Read it as a ladder: the first five rows are deletions, each naming the move that makes the
deletion safe, and the last four are the kinds that survive. A legal header is policy, not triage.

| What you are looking at | Verdict | The move, and what replaces it | Tag |
|---|---|---|---|
| **Redundant restatement** — `# set the port to 8080` above `port: 8080` | **Delete** | nothing; the line already said it — and if it did not, the fix is the name, not the prose | `C3` |
| **Section marker inside a unit** — `# --- validation ---` | **Delete, after extracting** | extract that section as a named unit; the marker is already its name | `G30` |
| **Closing-brace / end-of-block marker** — `} // for`, `# end networking` | **Delete, after shortening** | shorten the unit until its end is visible from its start | — |
| **Change log, dated entry, or byline** — `# 2024-02-11 pk: added the retry` | **Delete** | `git log` and `git blame`, which are accurate, automatic and cannot rot | `C1` |
| **Commented-out code or configuration** | **Delete on sight** | nothing — source control remembers, *"promise"* | `C5` |
| **Why / intent** — the reason for a decision the code cannot carry | **Keep**, and write it well | — the highest-value kind; *"a comment worth writing is worth writing well"* | `C4` |
| **Warning of consequences** — what breaks if the next reader does the obvious thing | **Keep** | — | — |
| **Amplification** — something that looks inconsequential and is not | **Keep** | — | — |
| **TODO with a stated plan** | **Keep**, with the marker | the marker is what makes it findable; scan and clear the list, and never treat it as licence | — |

## Anti-patterns

- **Commented-out code** *(Tier 1)* [`C5`] — one member of a four-member ch01 row that also
  covers journal comments, bylines and banners, each bulleted separately below.
  *"An abomination."* Nobody deletes it, because everybody assumes someone else needs it; it
  calls things that no longer exist and follows conventions the codebase abandoned. Delete it.
  In configuration it is worse, because no reader can tell whether the block was ever applied —
  and in Terraform commenting a resource out is not a pause but a **deletion**: gone from the
  configuration, still in state, so the next plan proposes to destroy the live object. The `#`
  looked like a comment and behaved like a `terraform destroy` target.
- **Dead code** *(Tier 1)* [`G9`]. An unreachable branch, a `catch` for an exception never
  thrown, an uncalled utility, a `switch` case nothing can select: the same defect as
  commented-out code without the comment markers, which is why it lives in this chapter.
  *"Give it a decent burial."*
  - **Dead configuration is not deleted, it is decommissioned**, and the two big platforms fail
    in opposite directions. Remove a Terraform block and the next plan **destroys** the live
    object — usually what you want, still a destroy, so read the plan; where the object must
    outlive the configuration, say so with a `removed` block carrying `lifecycle { destroy =
    false }` (Terraform 1.7+) or `terraform state rm`, which stop managing it without deleting
    it. Remove a Kubernetes manifest from the repo and **nothing happens to the cluster** unless
    something prunes — `kubectl apply --prune`, or Argo CD or Flux with pruning on — so the object
    stays live, unowned and unreviewed. **Delete it by name.** Pruning is the far larger change:
    `kubectl apply --prune` is **alpha** by its own help text, needs `-l`/`--all`, and deletes what
    that scope holds and the repo omits **only where `apply` or `create --save-config` made it** —
    Argo CD and Flux prune by their own inventory and reach more. Scope it before you enable it.
  - **Prove it is dead first**, and the proof differs: in code "nothing calls it", in config
    "nothing routes to it, nothing selects it, nothing reads its output" — a `Service` selects
    Pods by **label**, so a manifest no other file mentions can still be serving production.
- **Journal comments and bylines** [`C1`]. A dated changelog at the top of a module, or
  `# Added by Rick`. Source control holds both accurately, and goes on holding them.
- **Banner comments.** `////////`, `##### NETWORKING #####`. A banner works only because it is
  rare; overuse makes it noise. A file needing signposts is too big — ch05's problem.
- **Mandated per-unit doc comments.** A rule that every unit carries a doc block manufactures
  lies at scale. Mandate the rename test instead.
- **Noise comments.** `# the name` above `name:` — worse, one with a cut-paste error in it,
  since an author not paying attention while writing it leaves the reader nothing to gain. The
  nonlocal variant is the same defect at distance: a Helm template commenting a default that
  lives in `values.yaml`, with nothing keeping the two in step.

## Worked Example: a commented block becomes a named step, in a pipeline

A GitHub Actions job carrying four rows of the table above at once, plus a banner.

```yaml
# ======================== DEPLOY ========================
# 2024-02-11 pk: added the mirror wait
# 2023-11-02 as: initial version
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: |
          # wait for the image
          until crane manifest "$MIRROR_IMAGE" >/dev/null 2>&1; do sleep 5; done

      # - name: Smoke test
      #   run: ./scripts/smoke.sh staging

      - run: kubectl apply -f k8s/   # apply the manifests
```

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      # The mirror replicates asynchronously and emits no completion event, so
      # polling is the only signal available. Five seconds keeps the worst case
      # inside the job timeout at the observed p99 replication of four minutes.
      # INC-2214.
      - name: Wait for the image to reach the mirror registry
        run: until crane manifest "$MIRROR_IMAGE" >/dev/null 2>&1; do sleep 5; done

      - name: Apply the Kubernetes manifests
        run: kubectl apply -f k8s/
```

**What each deletion cost.** The banner names the file's one job, which the file name already
does; the two dated lines are a journal [`C1`] that `git log` holds better. The commented-out
smoke test goes on sight [`C5`], and in a pipeline it is the worst case in the table: nothing
records whether it ever passed, so it reads as either a plan or a scar and no reader can tell
which.

**Two deletions were promotions.** `# apply the manifests` and `# wait for the image` are
restatements [`C3`] — but neither step had a `name`, so **each comment was the name waiting to
be written**. A YAML comment is invisible to every consumer of the file; `name:` is rendered in
the run log, where an on-call engineer actually reads it. That is the rename test in a
declarative file: the text moved into the schema rather than being thrown away.

**What survives is the why.** No name captures "there is no completion event to wait on", or
why five seconds: that is intent, plus an amplification of a number that looks arbitrary,
plus a ticket. **This is the general rule for a legitimate comment in a declarative file — the
schema expresses the what and has nowhere to put the why.** The ordering here was free, too: a
`steps:` list is sequenced by the schema. In a `values.yaml` or a Terraform root nothing
enforces an order, which is where the ordering rule has work to do.

## Key Takeaways

1. **The default is don't**, and **the rename test is the whole test**: if a name requires a
   comment, the name does not reveal its intent. Rename and the comment goes — or it was a
   *why*, and it stays.
2. **The legitimate kinds are enumerated**: legal, intent, warning of consequences,
   amplification, TODO with a stated plan. The book's table adds three more, each conditional.
3. **Recorded difference on the enumeration itself.** The TypeScript and JavaScript adaptations
   name only *what*-comments, endorse `// TODO` alone, and hedge with *"good code **mostly**
   documents itself."* They never enumerate the why-kinds — TypeScript says so and routes to
   `clean-code-java` ch04. Terseness, not conflict; the book is canonical, and terser is not truer.
4. **Delete commented-out code, journals, bylines and banners on sight.** Version control
   remembers, and it does not rot.
5. **Delete dead code — and decommission dead configuration.** Removing a Terraform block
   destroys the live object; removing a Kubernetes manifest orphans it. Prove it is dead by what
   selects it, not by what mentions it, and never reach for pruning to delete one object.
6. **A section comment means extract; a closing-brace comment means shorten.** Both are
   structural signals, so fixing the text alone destroys the evidence.
7. **Formatting goes in a formatter, and the team's style wins** — name the tool, commit the
   config, stop reviewing whitespace. Reformatting config can rebuild an image or roll a
   Deployment, so land it alone.
8. **The file and line figures are Java-era** — the signal transfers, the numbers do not.
9. **The newspaper rule is the one formatting decision no tool makes for you** — entry point
   first, caller above callee, related things vertically close.

## Connects To
- **[ch01 — what survives translation](ch01-what-survives-translation.md)**: the index of
  record for the five rows above, and the claim that a Tier 1 rule reaches a manifest unchanged.
- **[ch02 — names and magic values](ch02-names-and-magic-values.md)**: the rename test *is* the
  naming test, stated from the other side; a named constant is the comment you did not write.
- **[ch03 — units of work](ch03-units-of-work.md)**: the section comment as a size signal, the
  stepdown rule the newspaper rule implements, and the threshold table already marking the
  file-length and line-width figures Java-era.
- **[ch04 — duplication and abstraction](ch04-duplication-and-abstraction.md)**: the same move,
  delete the artifact by improving the code; a comment distinguishing two near-identical blocks
  is duplication waiting to be decided.
- **[ch05 — structure and dependencies](ch05-structure-and-dependencies.md)**: a file needing
  banners to be navigable is too big, which is SRP's problem, and the over-long aligned list is
  the same finding from the formatting side.
- **[ch09 — declarative and config](ch09-declarative-and-config.md)**: when a YAML comment is
  legitimate — the schema expresses the what and has no field for the why — plus per-ecosystem
  formatters, pruning, and the cost of reformatting a file a pipeline hashes.
- **[ch10 — improving existing code](ch10-improving-existing-code.md)**: deleting one stale
  comment or one dead block is the Boy Scout Rule's canonical small improvement, and LeBlanc's
  Law is why the commented-out block is still there.
- **`clean-code-java` ch04, ch05 and ch17** — ch04 is the full good/bad comment catalogue and
  ch05 the formatting chapter these rules are distilled from; ch17 is the 66-item catalogue, not
  duplicated here, where `C1`–`C5` are the comment smells, `G9` dead code, `G10` vertical
  separation and `G24` follow standard conventions. Ask that skill for a tag.
