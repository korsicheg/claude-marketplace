# Chapter 3: Units of Work

## Core Idea

A **unit of work** is the named thing a language lets you define once and refer to again: a
function, method or procedure; a module or package; a shell function; a Make target; a Terraform
module or resource block; a CI pipeline stage or job; a SQL view or stored procedure; an Ansible
task; a Helm template; a Dockerfile stage. Every language and every configuration format has
one, because having one is what it means to be able to define something and name it. This skill
uses *unit of work* wherever the book says *function*.

The rule, stated over that: **a unit does one thing when every statement in it sits exactly one
level of abstraction below the unit's own name.** The name is the specification; the body is
that specification carried out, and nothing else.

**The name is also the whole assumption**, which is why ch01 puts do-one-thing and the size
signal at **Tier 1**. Both are read off the unit itself: what it does is measured against its
name, and its lines are counted in the artifact in front of you. Neither needs a
call site — a Kubernetes manifest is applied and never invoked, and a manifest file bundling a
Deployment, a Service and a ConfigMap still does three things.

**Nesting depth used to sit beside size here, and the Tier-1 audit moved it.** It is now
**Tier 2 — a branching construct**, because indent depth in a declarative file is not the
author's judgment being measured, it is the schema's shape. A minimal, entirely clean Deployment
— the one `kubectl kustomize` emits from a four-field input — nests **seven** levels
(`spec` → `template` → `spec` → `containers` → `resources` → `limits` → `memory`), every one of
them schema-imposed, with no refactor available at any of them. Against a threshold of ≤ 2 the
signal fires on every Kubernetes object that exists, including the clean ones, and a signal that
always fires carries no information. The book was measuring **control flow** all along — its own
gloss is *an `if` or loop body is one line, usually a call* — so the honest precondition is
something that branches, and where nothing does, the row does not apply.

The four rules over a unit's
**inputs and its return** are different. They need something that invokes the unit and hands it
arguments; that narrower case — a unit you can name *and* invoke — is their precondition, and
ch01 tags those four rules **Tier 2**. Where nothing plays the part of a parameter list, they
do not apply — and that is the answer, not an invitation to approximate one.

## Frameworks Introduced

- **Do One Thing** *(Tier 1)* — *"FUNCTIONS SHOULD DO ONE THING. THEY SHOULD DO IT WELL. THEY
  SHOULD DO IT ONLY."* Three tests, cheapest first: (1) **operational** — the unit does only
  those steps one level of abstraction below its stated name; (2) **extraction** — you can no
  longer pull out a unit whose name would be more than a restatement of its body; (3)
  **sections** — a unit you can divide into labelled sections is doing more than one thing, and
  units that do one thing cannot be reasonably divided into sections.
- **The TO-paragraph test, for any unit** *(Tier 1)*. You must be able to say *"TO
  `do-what-the-name-says`, we do X, then Y, then Z"*, where each of X, Y and Z is one named
  thing at the next level down. If the paragraph needs *"…and then, separately, we also…"*, you
  have found the split point. It mentions no construct, so it runs verbatim on a Terraform
  module — *"TO provision the audit log bucket, we create the bucket, apply the retention
  policy, and grant the reader role"* — and on a pipeline stage.
- **Size as a smell signal, not as the rule** *(Tier 1 — a name)*. A unit hardly ever over
  **20 lines**, **2–4** the target. Counted on the artifact, so it needs no call site. Treat the
  number as the point where you stop and look; the one-thing test is what decides. Thresholds and
  their provenance are tabled below.
- **Nesting depth as a smell signal** *(Tier 2 — a branching construct)*. **Depth ≤ 2** — the
  body of an `if` or a loop is one line, and that line is usually a call. That gloss is the
  precondition: what the number measures is **control flow the author chose**, not indentation as
  such. So ask ch01's construct question first. A Helm or Jinja template branches
  (`{{ if }}`, `{{ range }}`), HCL branches (`dynamic`, a conditional expression, a `for`
  expression), Bash and SQL `CASE` branch — the row binds on all of them. **A bare manifest does
  not branch**, so its indent depth is the schema's and the row does not apply there; say so
  rather than reporting a depth of seven as a finding.
- **The arity budget** *(Tier 2 — a parameter list)*: **0 ideal · 1 good · 2 costly · 3 avoid ·
  4+ never**. Over budget, bundle the inputs into one named object whose fields are the
  arguments — and the real prize is that computation then moves onto that object. The three
  legitimate single-input forms are: ask a question about the input, transform it and **return**
  the result, or take an event in and return nothing.
  - **Recorded disagreement.** `clean-code-java`, which is the book, gives the five-rung ladder
    above and calls 4+ *"requires very special justification — and then shouldn't be used
    anyway"*. All three adaptations flatten it to **≤2** — TypeScript and JavaScript avoiding
    three and consolidating at 4+, `clean-code-python` bundling already **at** three. Java is
    canonical, so the ladder is what this skill states; the adaptations are not contradicting
    it, they draw the line at least one rung earlier and nothing is lost by treating 3 as
    already over budget. What all four agree on is the **reason**, and the
    reason is the part that ports: each input multiplies the case matrix combinatorially, so the
    arity budget is a **verification** budget. Where the verification is `terraform plan` rather
    than a test runner, the combinatorics are identical and so is the budget.
- **Split on the flag** *(Tier 2 — a parameter list)*. A boolean input is two units that got
  merged, and the `if` in the body is the seam: `render(true)` → `renderForSuite()` and
  `renderForSingleTest()`. *"Boolean arguments loudly declare that the function does more than
  one thing"* [`F3`] — and they declare it in the caller's own source, where it reads as a bare
  `true` in argument position.
- **Command/query separation** *(Tier 2 — a return value)*. A unit either **does** something or
  **answers** something, never both. `if (set("username", "bob"))` is unreadable because `set`
  could be a verb or an adjective; the fix is
  `if (attributeExists("username")) { setAttribute("username", "bob"); }`. Where a unit has no
  return value the rule has no purchase: applying a manifest cannot violate it, and ch09 says so
  rather than inventing a manifest-shaped version.

## Key Concepts

- **One level of abstraction.** Orchestration (`tokenize`, then `parse`) and mechanics (the
  character loop inside the tokenizer) are two altitudes, and a body holding both makes the
  reader guess which statements are the essential concept and which are detail. *"Humans are
  just far too good at seamlessly mixing levels of abstraction"* [`G34`] — and splitting one
  unit along its abstraction lines routinely uncovers further lines the old structure hid.
- **Extract until you cannot.** Stop when the next extraction's name would merely restate its
  body — `addOneToCounter` wrapped around `counter += 1`. That is the terminating condition;
  "it feels small enough now" is not.
- **A section comment inside a unit marks a unit waiting to be extracted.** `# --- validation
  ---` in a shell function, a `# Networking` banner halfway down a Terraform file: the author
  has already named the sub-unit, and the only thing missing is the extraction. ch07 owns the
  comment rule; here it is a size signal you can grep for.
- **Side effects belong in the name — or the effect goes.** ch02 owns the naming half. The
  reason it is usually the effect that goes is **temporal coupling** [`G31`]: a `checkPassword`
  that also initializes the session can only be called when wiping the session is safe. Renaming
  it `checkPasswordAndInitializeSession` makes the coupling honest and breaks do-one-thing at
  the same moment, which is how you know the rename was not the fix.
- **Output arguments** *(Tier 2 — a parameter list)*. An input the unit writes through is the
  hardest side effect to see, because the call site shows an argument and nothing else.
  `appendFooter(report)` — is `report` the footer, or the thing being appended to? A unit changes
  its own state or returns a value.

## Mental Models

- **The stepdown rule is a reading order, not a style preference.** Each unit is followed by the
  units one level below it, so the file descends one level at a time and a reader can stop at
  the altitude they came for. ch07 owns vertical ordering; this is why it exists.
- **"Does it do one thing" is answered by naming it, not by counting its lines.** A 30-line unit
  with an honest name that needs no "and" beats three 10-line units carved at the wrong joints.
  Hunting for the good name is what produces the split — *long descriptive name > short
  enigmatic name > long descriptive comment*.
- **Count the inputs and you have counted the cases someone must cover.** Testing every
  combination of two inputs is challenging, of three daunting, of zero trivial. That is the
  arity budget's whole argument, and it survives in ecosystems with no test runner.

## Reference Table: thresholds

| Signal | The number | Committed to by | Status |
|---|---|---|---|
| Unit length | *"hardly ever 20 lines"*; **2–4 lines** the target | `clean-code-java` (the book); no adaptation names a number | **Tier 1 signal**; the number is Java-calibrated |
| Nesting / indent depth | **≤ 2**; an `if` or loop body is one line, usually a call | `clean-code-java` | **Tier 2** — a branching construct. It measures chosen control flow, not indentation: a clean Deployment nests 7 on schema alone |
| Arity | **0 · 1 · 2 · 3 avoid · 4+ never** | `clean-code-java`; the three adaptations say ≤2, 4+ → parameter object | **Tier 2** — needs a parameter list |
| File length | ~**200 lines** typical, **500** upper limit, *"desirable, not a hard rule"* | `clean-code-java` ch05 (formatting) | **Java-era specific**; a formatter default, and ch07 owns it |
| Line width | ≤ **120** | `clean-code-java` ch05 (formatting) | **Java-era specific**; a formatter default, and ch07 owns it |

**Reading the last column.** A Tier 1 signal transfers because you measure it on the artifact
itself: a 300-line Helm template is a smell in exactly the sense the book means. The numbers
transfer less well — 20 lines of Java is not 20 lines of YAML, where structure rather than
statements fills the lines. Use the Tier 1 rows as the prompt to stop and look, and the Java-era
rows as defaults for the formatter config ch07 owns. **The nesting row is the one the Tier-1
audit moved**, and the reason is worth carrying: measured as raw indentation it fires on every
manifest ever written, so it was reporting the schema rather than the author. Bound to a
branching construct it fires on a four-deep `{{ if }}`/`{{ range }}` chain in a template, which
is a real finding with a real fix.

## Anti-patterns

- **Flag inputs** [`F3`]. `createFile(name, temp)` is `createFile` and `createTempFile` under one
  name. In configuration the same shape appears as a module variable that switches which
  resources get created; the two entry points are two modules.
- **Output arguments** [`F2`]. Readers expect inputs. If a unit must change state, have it change
  the state of the thing it belongs to, or return the new value — a transformation returns its
  result even when the body would happily have mutated in place.
- **Units that must be called in a fixed order** [`G31`]. Temporal coupling is often necessary;
  **hiding it is not.** The fix is a bucket brigade — each unit produces what the next one needs,
  so the order cannot be got wrong silently. *"That extra syntactic complexity exposes the true
  temporal complexity of the situation."*
- **A unit whose name contains "and"** — the cheapest detector in the chapter, and the unit
  telling you where to split. A vague verb (`handle`, `process`, `manage`, `do`) is the same
  defect hiding the "and" instead of admitting it.
- **Dead code left in place** [`F4`]. A unit nothing calls is a unit nobody maintains and
  everybody still reads. **ch07 owns the delete-dead-code rule**; it belongs in this list because
  the unit is the thing being deleted, and version control remembers it.

## Worked Example: an over-long unit, in a language with no classes

A deploy function in Bash. It has four positional inputs, two of them flags; three section
comments; orchestration and mechanics in the same body; and a name that stopped covering what
it does.

```bash
# Before
deploy() {
  local env=$1 tag=$2 dry=$3 notify=$4
  # --- build ---
  docker build -t "myapp:$tag" .
  docker push "myapp:$tag"
  # --- deploy ---
  if [ "$dry" = "true" ]; then
    kubectl apply -f k8s/ --dry-run=server
  else
    kubectl apply -f k8s/
    kubectl rollout status "deployment/myapp-$env" --timeout=300s
  fi
  # --- notify ---
  if [ "$notify" = "true" ]; then
    curl -sS -X POST "$SLACK_URL" -d "{\"text\":\"deployed $tag to $env\"}"
  fi
}
```

The three section comments are the extraction, already named by the author. The two flags are
four call paths collapsed under one name. And `300s` is a magic value (ch02).

```bash
# After
readonly ROLLOUT_TIMEOUT=300s

publish_image() { local tag=$1; docker build -t "myapp:$tag" . && docker push "myapp:$tag"; }
apply_manifests() { kubectl apply -f k8s/; }
preview_manifests() { kubectl apply -f k8s/ --dry-run=server; }
announce_release() { local env=$1 tag=$2; curl -sS -X POST "$SLACK_URL" \
  -d "{\"text\":\"deployed $tag to $env\"}"; }

await_rollout() {
  local env=$1
  kubectl rollout status "deployment/myapp-$env" --timeout="$ROLLOUT_TIMEOUT"
}

release() {
  local env=$1 tag=$2
  publish_image "$tag"
  apply_manifests
  await_rollout "$env"
  announce_release "$env" "$tag"
}

preview_release() {
  local tag=$1
  publish_image "$tag"
  preview_manifests
}
```

The TO paragraph now reads: *"TO release, we publish the image, apply the manifests, await the
rollout, and announce the release."* Each step is one named thing one level down, so `release`
can be read without opening any of them. Arity fell from four to two, and it fell because the
**flags became entry points** rather than because anything was bundled — `preview_release` is the
`dry=true` branch with a name, and a composition that does not want the announcement simply
omits that step. Note what Bash supplied and what it did not: its parameter list is implicit
(`$1`, `$2`), which changes nothing — ask ch01's construct question and the answer is yes, so the
Tier 2 rules bind. What Bash does not supply is a class, and the decomposition never needed one.

## Key Takeaways

1. **A unit of work is anything you can name and reuse.** The rules over its **name** are Tier 1
   and reach every language and every configuration format; the rules over its **parameter list
   and its return** are Tier 2 and need something that invokes it.
2. **Do one thing = every statement one level of abstraction below the name.** Answer it by
   naming the unit, not by counting its lines.
3. **The TO paragraph is the portable form of that test** — *"TO X, we do A, then B, then C."* An
   *"and then, separately"* is the split point, and the test never mentions a function.
4. **Size is where you stop and look, never the verdict**: hardly ever 20 lines, 2–4 the target,
   counted on the artifact and so Tier 1. **Nesting depth (≤ 2) is Tier 2 — a branching
   construct**, since raw indent depth in a schema-shaped file is the schema's and not the
   author's; the audit demoted it, and ch01 carries the row.
5. **Extract until the next extraction would only restate its body.** A section comment inside a
   unit is an extraction someone already named and did not perform.
6. **The arity budget, and the recorded disagreement.** The book's ladder — 0 · 1 · 2 · 3 avoid ·
   4+ never — is canonical here; all three adaptations converge stricter at ≤2 with 4+ forcing a
   parameter object. They agree on the **reason**, and the reason is what ports: combinatorial
   test explosion makes arity a verification budget.
7. **A flag input is two units merged.** Split it and both get a name.
8. **No output arguments**: a unit changes its own state or returns a value.
9. **Command or query, never both** — and where the unit returns nothing, the rule does not apply
   rather than applying vacuously.

## Connects To
- **[ch02 — names and magic values](ch02-names-and-magic-values.md)**: the unit's name is the
  specification its body is measured against, so extraction is mostly naming; ch02 also owns the
  rule that the name must carry the side effects, and the magic value (`300s`) in the example.
- **[ch04 — duplication and abstraction](ch04-duplication-and-abstraction.md)**: extraction is
  how duplication dies, and the unit is what you extract *into*; the bad-abstraction caveat is
  what stops you extracting at the wrong joint.
- **[ch05 — structure and dependencies](ch05-structure-and-dependencies.md)**: SRP is this
  chapter one altitude up. A unit is measured against its name; a module is measured against its
  name **and also** against its reasons to change.
- **[ch07 — comments and formatting](ch07-comments-and-formatting.md)**: section comments, the
  newspaper rule that the stepdown rule implies, and the file-length and line-width numbers
  tabled above.
- **[ch09 — declarative and config](ch09-declarative-and-config.md)**: the Terraform module as
  the unit and its `variable` blocks as its arity, plus pipeline stages, SQL views and Dockerfile
  stages.
- **`clean-code-java` ch03 and ch17** — the 66-item catalogue, not duplicated here: `F1` too many
  arguments, `F2` output arguments, `F3` flag arguments, `F4` dead function, `G30` do one thing,
  `G34` descend only one level, `G31` hidden temporal couplings. Ask that skill for a tag.
