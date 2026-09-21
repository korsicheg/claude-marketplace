# Chapter 2: Names and Magic Values

## Core Idea
**If a name needs a comment to be understood, the name has failed.** That is the whole test, and
it is the test with no construct assumptions at all: it asks only that something be named. A
Terraform resource label, a YAML key, a Bash variable, a SQL column alias and a Java class are
judged by it identically — it never asks *what kind of thing* you named, only whether the name
answers the questions the next reader will have. All seven naming rules ch01's table assigns this
chapter are **Tier 1** for that reason, and they are the rules that reach the artifacts no other
chapter reaches. Each is tagged where it is stated below; the supporting rules alongside them
assume no more than a name either.

## Frameworks Introduced

- **Intention-revealing names — the four questions** *(Tier 1)*. A name states why the thing
  exists, what it does, and how it is used. Ask what the artifact leaves implicit — *what is in
  this collection? what does this index or key mean? what does this literal mean? how is the
  result used?* — and push each answer into a name. The failure mode it fixes is **implicity**:
  context that exists in the author's head and nowhere in the artifact.
- **The scope-length rule** *(Tier 1)*. *"The length of a name should correspond to the size of its
  scope"* (`clean-code-java` ch02; `N5` in the catalogue) — long scope, long name. Single letters
  belong only in the tiniest local scope, where `i` in a two-line loop is clear and `rollCount`
  would obfuscate it; anything read far from its declaration earns a longer, searchable name. Do
  not flinch at the resulting length: `renamePageAndOptionallyAllReferences` is long, *"but it's
  only called from one place… its explanatory value outweighs the length"* [`N4`].
- **One word per concept, and never a pun** *(Tier 1)*. One word per abstract concept, used
  everywhere: `get`/`fetch`/`retrieve` for one operation breeds three implementations of it, because
  the next person greps for the word you did not pick (`getUserInfo`/`getUserData`/`getUserDetails`
  → `getUser`). The converse is the more dangerous half — never one word for two meanings. If `add`
  everywhere means "combine two values into a new one", then putting an item into a collection is
  `insert` or `append`, even though `add` would feel consistent.
- **Add context by enclosure, not by prefix.** In order of preference: (1) put the names inside
  a well-named container — a class, a module, a Terraform module, a YAML mapping, a SQL schema;
  (2) inside a well-named unit or namespace; (3) **only as a last resort**, prefix them
  (`addrState`). Gratuitous context is the same mistake inverted: prefixing every type in "Gas
  Station Deluxe" with `GSD` defeats completion and buys nothing.
- **Magic values become named constants** *(Tier 1)*. The rule reaches any non-self-describing
  token [`G25`], strings included, so a `"PENDING"` repeated across nine files is as magic as
  `86400000`. Keep the derivation where there is one: `SECONDS_PER_DAY =
  60 * 60 * 24` documents itself in a way `86400` cannot. The exceptions the book grants are in
  **Anti-patterns** below, and they are narrower than they look.

## Key Concepts

- **Searchable names** *(Tier 1)*. Searchability is a design property. You can grep
  `MAX_CLASSES_PER_STUDENT`; you cannot usefully grep `7`, or `e`, or an `86400000` that one call
  site spells `24 * 60 * 60 * 1000`. A name you cannot find is a name you cannot change safely —
  the second reason to confine single letters to tiny scopes.
- **Pronounceability.** *"If you can't pronounce it, you can't discuss it"*, and programming is a
  social activity. `genymdhms` forces a team to invent a spoken word for a real concept, and the
  invented word never makes it back into the code.
- **No noise words** *(Tier 1)*. A noise word is a symptom, not a style problem. `Manager`,
  `Processor`, `Data`, `Info`, `Object`: `ProductData` and `ProductInfo` are the same name twice.
  Usually the noise word is there because the thing has **aggregated responsibilities** and no
  single word fits it any more — ch05's rule showing up as ch02's evidence. Drop the noise, or
  find the real distinction and split on it.
- **The name must include the side effects** *(Tier 1)* [`N7`]. A `getX` that also creates X is
  `createOrReturnX`; a `check_config` script that also rewrites the config is not a check. A name
  that omits an effect is a lie no reader can detect from the use site — and the fix is usually
  to remove the effect rather than to lengthen the name (ch03).
- **Don't repeat the container's name inside its members.** If the type is `Car`, the field is
  `make`, not `carMake`, because the reader meets it as `car.make`. **ch09 applies this exact
  rule to Terraform resource labels**, where the address already carries the type:
  `resource "aws_s3_bucket" "audit_logs"` is referred to as `aws_s3_bucket.audit_logs`, so a
  label of `s3_bucket` or `audit_logs_bucket` stutters at every use.

## Mental Models

- **Test the name at the use site, not at the declaration.** `carMake` looks reasonable in the
  type declaration and reads as *car car-make* where it is used. That test is also what makes the
  Terraform label rule obvious — and it cuts both ways: strip context the use site does *not*
  supply and the name goes vague, so a free-floating `make` is worse than `carMake`.
- **A name is the comment you did not have to write.** `MILLISECONDS_PER_DAY` retires
  `// what is 86400000 for?`. When you catch yourself writing that comment, you have already
  written the name; move it into the code.
- **Renaming is cheap — once you do the state move with it.** In code, tooling makes it
  mechanical. In config, a name is often an **identity**, so the search-and-replace is only half
  the rename: a Terraform resource label *is* its address, so changing it makes `terraform plan`
  propose **destroy-and-create** unless you record the move (a `moved` block, Terraform 1.1+, or
  `terraform state mv`); changing `metadata.name` makes `kubectl apply` create a second object
  and orphan the first, which is a duplicate rather than a rename. The plan shows you that — it
  does not stop it. Rename anyway, with the move attached: in Terraform the `moved` block or
  `terraform state mv`; in Kubernetes, which has no state move, apply the renamed object and
  then delete the old one by its old name.

## Reference Table: naming rules by construct

| Construct | What the name must convey | Universal form | The tell it is wrong |
|---|---|---|---|
| **Callable** — function, method, job, task, target, recipe | the action, and every effect it has | verb phrase, effects included | `handle`, `process`, `doIt`; a `get` that also creates |
| **Type / container** — class, struct, record, module, resource block, table | the thing it *is*, never the job it does | noun phrase, no noise word | `Manager`, `Processor`, `ProductInfo` beside `ProductData` |
| **Constant** — named literal, variable default, `locals` entry | the meaning *and* the unit, plus the derivation where there is one | `SECONDS_PER_DAY = 60 * 60 * 24` | the bare literal, repeated at each call site |
| **Collection** — list, set, map, array key | the element pluralized, and what makes something a member | `flaggedCells`, `activeUsers` | `list1`, `theList`, `data`, a plural with no predicate |
| **Boolean / predicate** — flag field, condition, guard | a question with a yes/no answer, asked **positively** | `isPosted`, `hasQuorum`, `is_enabled` | `!isNotPresent`, `flag`, `status`, `check` |
| **File / module** — source file, manifest, chart, stage | what is inside, at the altitude the importer reads it | `retention_policy.tf`, `billing/invoice.py` | `utils`, `helpers`, `common`, `misc`, `main2` |
| **Index in a tiny scope** — loop counter, accumulator | nothing; the two lines around it carry the meaning | `i`, `j`, `k` | `l` and `O`, unreadable against `1` and `0`; `a1`, `a2` |

## Anti-patterns

- **Encodings and type prefixes** [`N6`]. Hungarian notation, `m_`, `str_name`, `ymdstr`,
  `IShapeFactory`. Each duplicates something the annotation, the schema or the declaration
  already states, and the duplicate is what goes stale. The configuration-language form is the
  same instinct with different spelling: `tags_map`, `subnet_ids_list`, `enable_flag` — an HCL
  `variable` block carries a `type` argument that says it better.
- **Disinformation.** A name whose entrenched meaning differs from your use: `accountList` for
  something that is not a list, `hp`/`aix`/`sco` as variable names, a `timeout` that holds a
  retry count. Worse than a vague name, because the reader stops checking.
- **Number-series and noise-word distinctions.** `a1, a2, …aN` is not disinformative, it is
  *non*informative. `getActiveAccount()`, `getActiveAccounts()` and `getActiveAccountInfo()` in
  one API: no reader can pick correctly, and no rule tells them how.
- **Cute or culture-bound names.** `HolyHandGrenade` for `DeleteItems`, `whack()` for `kill()`,
  `eatMyShorts()` for `abort()`. The joke does not survive the reader's first language, the
  on-call engineer at 3am, or five years.
- **Over-applying the constant rule — the exceptions the book grants** [`G25`]. *"There are some
  formulae in which constants are simply better written as raw numbers"*: `hourlyRate * 8`,
  `feetWalked / 5280.0`, `radius * PI * 2`. The `8`, the `5280` and the `2` are part of a formula
  the reader already holds, and naming the `2` `TWO` adds a lookup without adding meaning. **π is
  the counter-case, and the book says why**: *"Every time someone sees 3.1415927535890793, they
  know that it is π, and so they fail to scrutinize it. (Did you catch the single-digit error?)"*
  Nobody proofreads a literal they recognize, so the familiar value is precisely the one that
  needs a name. The exception covers values the reader reconstructs from the formula in front of
  them. It is not a licence for `86400000`, a bare `0.85` tax rate, or a repeated `"PENDING"`.

## Worked Example: one rename chain, three paradigms

The same artifact — *select the audit records past their retention window* — written in a
language with objects, one without them, and one with no runtime at all. Nothing is wrong with
any "before" except that all the context is missing: the reader cannot say what is in the
collection, what `30` means, or what to do with the result.

**Object-oriented (C#):**

```csharp
// Before
List<Rec> GetThem(List<Rec> l) =>
    l.Where(x => (DateTime.UtcNow - x.d).Days > 30).ToList();

// After
private const int RetentionDays = 30;

IReadOnlyList<AuditLog> ExpiredAuditLogs(IEnumerable<AuditLog> logs) =>
    logs.Where(IsPastRetention).ToList();

private static bool IsPastRetention(AuditLog log) =>
    (DateTime.UtcNow - log.RecordedOn).Days > RetentionDays;
```

**Functional (Elixir) — no classes, same four answers:**

```elixir
# Before
def get(l), do: Enum.filter(l, &(Date.diff(Date.utc_today(), &1.d) > 30))

# After
@retention_days 30

def expired_audit_logs(logs), do: Enum.filter(logs, &past_retention?/1)

defp past_retention?(log),
  do: Date.diff(Date.utc_today(), log.recorded_on) > @retention_days
```

**Declarative (Terraform/HCL) — no callable at all, and the rule does not notice:**

```hcl
# Before
resource "aws_s3_bucket_lifecycle_configuration" "b1" {
  bucket = aws_s3_bucket.b1.id
  rule {
    id     = "r1"
    status = "Enabled"
    expiration {
      days = 30
    }
  }
}

# After
variable "audit_log_retention_days" {
  type    = number
  default = 30
}

resource "aws_s3_bucket_lifecycle_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id
  rule {
    id     = "expire-past-retention"
    status = "Enabled"
    expiration {
      days = var.audit_log_retention_days
    }
  }
}
```

**What changed, and what did not.** Every fix is the same four answers: the collection holds
audit logs; `30` is the retention window; the predicate is *past retention*; the result is the
set to expire. The **mechanism** for the named constant differs in each — a `const` field, a
module attribute, a `variable` block — and the rule never mentioned any of them, which is what
Tier 1 buys. In HCL the mechanism is itself a choice: a `variable` where the window is meant to
be tunable per environment, a `locals` entry where it is not — the `variable` buys the name at
the cost of one more module input, which ch03 counts as arity.

Note also what the Terraform label `b1` was: the number-series case, so **non**informative rather
than disinformative. It answers none of the four questions, and the address
`aws_s3_bucket_lifecycle_configuration.b1` already supplies the type — which leaves
distinguishing this resource from every other of its type as the label's one job, and the one it
did not do.

## Key Takeaways

1. **If a name needs a comment, rename it.** One test, no construct required — it reaches a
   Kubernetes manifest and a Rust crate identically.
2. **Length is proportional to scope.** Single letters only in the tiniest local scope; the
   further from its declaration a name is read, the more it has to say on its own.
3. **One word per concept, and never one word for two concepts.** Synonym drift is how a codebase
   grows three implementations of one operation.
4. **Searchable beats short.** Every meaningful literal becomes a named constant — the derivation
   included, because `60 * 60 * 24` documents itself.
5. **The name carries the side effects, or the effect goes.** A name that omits an effect cannot
   be checked against anything.
6. **Add context by enclosure; prefix only as a last resort**, and never repeat the container's
   name inside its members.
7. **The magic-value exception is narrow**: values the reader reconstructs from the formula in
   front of them. π is the counter-case — a recognized literal is the one nobody proofreads.
8. **Test every name at the use site.** It is where the stutter, the vagueness and the missing
   effect all become visible.

## Connects To
- **[ch03 — units of work](ch03-units-of-work.md)**: a unit's name is what "one thing" is
  measured against, so every extraction is mostly an act of naming — and the constants named here
  are what let a unit's body stay one level of abstraction below its name.
- **[ch04 — duplication and abstraction](ch04-duplication-and-abstraction.md)**: synonym drift
  is how duplicate implementations are created, because the next author greps for the word you
  did not use.
- **[ch05 — structure and dependencies](ch05-structure-and-dependencies.md)**: a noise word in a
  name is usually evidence of aggregated responsibility, which is SRP's problem, not naming's.
- **[ch07 — comments and formatting](ch07-comments-and-formatting.md)**: the rename test *is* the
  comment test. If a name requires a comment, the name does not reveal its intent; rename, then
  delete the comment.
- **[ch09 — declarative and config](ch09-declarative-and-config.md)**: these seven rules applied
  per ecosystem — `metadata.name`, Terraform resource labels and the container-stutter rule,
  pipeline stage names, SQL aliases.
- **`clean-code-java` ch02 and ch17** — ch17 is the 66-item catalogue, not duplicated here:
  `N1`–`N7` are the naming heuristics and `G25` the magic-number one; ask that skill for a tag.
  **One recorded gap.** `clean-code-java` ch02 adds an *inversion* of the scope-length rule for
  class and member names, cross-referenced to a "public-API rule in Ch4" that does not resolve —
  its ch04 is Comments and states no such rule, ch17 states `N5` with no inversion, and no
  adaptation mentions one. It could not be checked against the book, because this environment
  has no PDF text extractor. The claim is therefore **not carried here**.
