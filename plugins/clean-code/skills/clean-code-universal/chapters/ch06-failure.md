# Chapter 6: Failure

## Core Idea

Both rows ch01 assigns this chapter are **Tier 2**, and each names a construct a language may not
have: **an exception**, and **an absent-value sentinel**. The rules underneath them, though, are
about the *shape* of failure rather than its mechanism — and every language has a failure
mechanism even when it has neither of those. Three shape rules, holding wherever failure can
happen at all:

1. **Fail loudly.** A failure that stops nothing is a failure nobody will see.
2. **Carry enough context to act on** — the operation that failed and the failure type.
3. **Never let a failure path be a silent one.** An empty handler, a `try()` that swallows a
   lookup error, an unread exit status: each is a path with no code on it.

What changes between languages is only *what plays the part* — a raised exception, a second
return value, a `Result`, a non-zero exit status, a schema rejection at plan time. Name the
mechanism first, with ch01's construct question, then apply the three rules to it. Where the
**mechanics** genuinely need an exception — a `try` block's transaction scope, the
checked-versus-unchecked argument — this chapter says so rather than inventing an equivalent.

And in configuration, failure handling is mostly failure **placement**: the real choice is which
stage rejects — schema, plan, admission, or production — and moving the rejection earlier is
most of the design.

## Frameworks Introduced

- **Raise the failure; do not return an error code** *(Tier 2 — an exception)*. An error code
  clutters the caller, who must check immediately after the call and can simply forget. Raising
  separates two tangled concerns — the algorithm and the failure handling — so each can be read
  alone — *"This isn't just a matter of aesthetics."* There is a second argument that is pure
  OCP: a new error code changes the enumeration every caller switches on, while a new exception
  type is a derivative added without touching anyone. Three sub-rules of the same row:
  - **Write the failure scope first.** A `try` block is a **transaction scope**: execution may
    abort anywhere inside it and resume at the handler, which must leave a consistent state
    whatever happened. Define the scope before the happy path, then narrow the caught type to
    what is actually raised.
  - **Every failure carries the operation that failed and the failure type.** A stack trace says
    *where*; it never says what the code was trying to do. `new Error('Not implemented.')`
    satisfies the adaptations' rule and fails this one.
  - **Classify by how it will be caught, not by where it came from** — *"our most important
    concern should be how they are caught."* Use distinct failure types only where you genuinely
    want to catch one and let the other pass; otherwise distinguish by what the failure carries.
- **Wrap a foreign failure vocabulary into one of yours** — ch05's boundary technique applied
  here, and **not a ch01 row of its own**. *"wrapping third-party APIs is a best practice"*:
  three handlers doing identical work collapse into one, the library becomes swappable, and the
  call becomes easy to fake in a test. The wrapper translates and does nothing else.
- **The Special Case object, and the absent-value rules** *(Tier 2 — an absent-value sentinel)*.
  When the "exceptional" case is a business rule with a default — no meals expensed, no override
  configured — it is not a failure at all. Return an object that answers the default and the
  client's branch disappears with the handler. The collection form is the empty collection, so
  the caller just iterates. **Never return an absent-value sentinel and never pass one.**
  Returning it foists the problem onto every caller, and *"All it takes is one missing null check
  to send an application spinning out of control."* Passing it is worse, because no remedy works:
  raising an argument error only relocates the question, and an assertion documents the rule
  while still failing at run time. Where a language has a **declared** optional or nullable type,
  an absence stated in the signature is a different thing from a sentinel smuggled through one,
  and only the second is what this rule forbids.
  - **In configuration this is the row that binds** — ch01 records a bare YAML manifest as
    supplying the absent-value sentinel and **none** of the other ten constructs, and HCL as
    supplying `null`. So this is the one rule in the chapter a reader holding a manifest can act
    on. In HCL an argument set to `null` is the same as omitting it, which makes a `null`
    travelling through a module `variable` into a resource argument exactly "never pass a
    sentinel" in HCL; the Special Case analogue is a `variable` with a real default, or
    `optional(type, default)` inside an object type (**Terraform 1.3+**). **The consequence
    differs in Kubernetes**: in a strategic-merge patch a `null` **deletes** the field rather than
    leaving it unset, so an absent key and a `null` key are not interchangeable there, and writing
    one where you meant the other removes live configuration.
- **Put failure in the signature where the language supports it** — the same propagation row in a
  language whose failure mechanism is a return value. `clean-code-typescript` offers it as a
  genuine alternative: *"not to use the `throw` syntax and instead always return custom error
  objects. TypeScript makes this even easier."* A discriminated union (`Failable<R, E>`), Rust's
  `Result`, Go's second return — the caller cannot reach the value without discriminating, so the
  compiler is the reviewer and the failure is documented where nobody can miss it. **The cost is
  stated rather than hidden: a returned failure does not propagate.** An exception travels up the
  stack on its own until something catches it; a result type is unwrapped and rewrapped at every
  layer it crosses, each layer's error type has to compose with the next, and there is no stack
  trace at all unless the error value carries one.

## Key Concepts

- **A failure handler is a claim.** Writing one asserts that a failure may occur there, so *"If
  you wrap any bit of code in a `try/catch` it means you think an error may occur there and
  therefore you should have a plan, or create a code path, for when it occurs."* An empty handler
  retracts the claim while keeping the syntax.
- **Logging is not handling.** A logged-and-swallowed failure *"can get lost in a sea of things
  printed to the console"*: it reads as handling and is discarding with a receipt nobody opens.
  Handling means a code path — retry, fall back, tell the user, report to a service, or re-raise.
  Log *and* do one of those.
- **Never leave a failure signal unchecked**: a rejected promise with no handler, a Go `err`
  assigned to `_`, a shell command whose exit status nothing reads. One defect, three spellings.
- **Code drowning in absence checks has too many, not too few.** The fix is upstream — stop
  producing the sentinel. Where a third-party call returns one, wrap it in something that raises
  or answers with a special case, and the checks downstream delete themselves.
- **Checked versus unchecked exceptions, and a disagreement the adaptations never join.** The
  book argues against checked exceptions in general application code, and states the price as an
  **OCP violation**: a checked exception raised three levels below its handler must be declared
  by every unit in between, so a low-level change cascades signature changes upward and forces
  rebuilds of modules that care about nothing that changed. Encapsulation breaks with it, because
  every unit on the path must now know a low-level failure detail. The book's evidence is that
  C#, C++, Python and Ruby have no checked exceptions and robust software is written in all of
  them; its stated exception is a **critical library** whose caller must be forced to catch.
  **The adaptations do not disagree — they never face the question**: TypeScript and JavaScript
  have no checked exceptions, and neither does Python, so their silence is a missing construct
  rather than assent. `clean-code-java` is canonical and the rule stands as it states it. **What
  generalizes is the mechanism rather than the keyword: a failure declared in a signature couples
  every caller up the stack to that declaration.** Go's `error` return and Rust's `Result` make
  exactly that trade deliberately — a compiler-checked caller, bought with the cascade — so the
  portable form of the rule is *declare failure in a signature where you want that coupling, at a
  boundary, and not by default all the way down*.

## Mental Models

- **Error handling is one thing**, so a unit that handles failure does only that. The concrete
  form in the book: if `try` appears in a unit it is the very first word, and nothing follows the
  handler. The mechanics move into their own unit and the algorithm reads without them.
- **Push failure detection to the edges.** Wrap what is foreign at the boundary so that what
  propagates inward is your own vocabulary, and put one handler above your code for aborted work.
  The middle then reads as an unadorned algorithm.
- **Not everything abnormal is a failure.** Ask whether the case has a defined business answer.
  If it does, it is a special case, and a handler encoding a business rule is a design smell.

## Reference Table: failure mechanism by language class

| Mechanism | Where | Propagates by itself | "Carry context" means | "Never swallow" means |
|---|---|---|---|---|
| **Exceptions** | Java, Python, Ruby, C#, JS/TS `throw` | yes — up the stack until something catches | raise your own type; the message names the operation and the subject; chain the cause | no empty handler, no log-and-continue; narrow the caught type to what is actually raised |
| **Multi-return error values** | Go | **no** — every layer returns it again | wrap with the operation at each layer (`fmt.Errorf("loading %s: %w", id, err)`) so the chain reads as a path | never `_ = err`; check it or hand it up, at every layer |
| **Result types** | Rust `Result`, TS `Failable<R, E>` | no — unwrap and rewrap per layer | a typed error arm the caller must discriminate; attach a trace if you need one | the compiler blocks the value until you branch, so the swallow is `let _ =`, `.ok()` or `unwrap_or_default()`; `unwrap()` is the other defect — loud, but with the operation thrown away |
| **Exit codes** | Bash, Make, any process | in a shell, only under `set -e` and not everywhere; make aborts the target on a failed recipe line by default | a stderr line naming the command and its input; a distinct non-zero code per case | `set -euo pipefail`; never `\|\| true` to quiet a step you have not handled |
| **Schema / plan-time validation** | YAML, Kubernetes, Terraform | n/a — the run aborts | a `validation` message naming the variable and the rule; a `precondition` naming the assumption | never `try()` a lookup to quiet a plan; never `-target` past a failed precondition |

**Four consequences worth stating exactly.** *Terraform has no exception*: `validation`,
`precondition` and `postcondition` abort rather than propagate, and `try()`/`can()` **suppress**
rather than catch — so wrapping a lookup in `try()` to stop a plan failing converts a missing
value into a silent default, which is the empty handler in HCL, and moves the error from plan
time, where it is a message, to apply time, where it is a wrong resource. *A Kubernetes manifest
has no failure mechanism of its own*: its failure design is `readinessProbe`, `restartPolicy` and
admission, and the command that actually runs admission and schema validation is `kubectl apply
--dry-run=server` — `--dry-run=client` **does not reach admission or server-side validation**, so
it is not the check it looks like. *In Bash*, `set -e` does not fire for a command whose status is
consumed by `if`, `&&`, `||` or `!`, and `local x=$(cmd)` hides `cmd`'s status behind `local`'s
own — a bare `x=$(cmd)` does not, so declare and assign on separate lines; and turning
`set -euo pipefail` on in an existing script changes behaviour at every step that used to fail
quietly, so read what currently fails before landing it. *In Make*, the abort is per recipe line,
so `cmd1; cmd2` on one line hides `cmd1`'s failure entirely — split the lines, or set
`.SHELLFLAGS = -ec` so the recipe shell exits on the first failure.

## Anti-patterns

- **The empty handler.** It contradicts the `try` that created it. If nothing is to be done here,
  the handler belongs further up, not here doing nothing.
- **Logging as handling.** `console.log(error)` and its equivalents. Log *and* take a code path.
- **A bare sentinel return.** Returning the absent value moves the problem to every caller, and
  the caller who forgets one check is the one who finds out in production.
- **One handler per third-party failure type.** Three handlers whose bodies are identical are
  duplication (ch04) wearing a boundary's clothes; collapse them behind a wrapper of yours.
- **A failure message with no operation in it.** `Not implemented.`, `invalid input`, `error: 1`.
  The reader gets *where* from the trace and never gets *what was being attempted*.
- **Silencing a step to make a pipeline green** — `|| true`, a `continue-on-error: true` with no
  following check, `try()` around a lookup, an `ignore_changes` covering a field that keeps
  drifting. Each converts a loud failure into a quiet wrong state, which is the one trade this
  chapter never makes.

## Worked Example: one failure path, two mechanisms, the same shape

Reading a bucket's retention policy. Two decisions: a **missing row** is a business case with a
default, and an **unreachable store** is a failure. First in a language with exceptions.

```python
class ConfigStoreUnavailable(Exception):
    """Raised for every driver failure reading the config store."""

class RetentionPolicyStore:
    def for_bucket(self, bucket: str) -> RetentionPolicy:
        try:
            row = self._db.fetch_one(BUCKET_POLICY_SQL, bucket)
        except (OperationalError, InterfaceError, DriverTimeout) as cause:
            raise ConfigStoreUnavailable(
                f"reading the retention policy for bucket {bucket}") from cause
        return RetentionPolicy(row["days"]) if row else DefaultRetention()
```

Then in a language whose failure mechanism is a return value.

```go
// Two %w verbs in one fmt.Errorf need Go 1.20+; before 1.20, wrap one and use %v for the other.
var ErrConfigStoreUnavailable = errors.New("config store unavailable")

func (s Store) RetentionFor(ctx context.Context, bucket string) (RetentionPolicy, error) {
    row, err := s.db.Row(ctx, bucketPolicySQL, bucket)
    if errors.Is(err, sql.ErrNoRows) {
        return DefaultRetention(), nil
    }
    if err != nil {
        return RetentionPolicy{}, fmt.Errorf("reading the retention policy for bucket %s: %w: %w",
            bucket, ErrConfigStoreUnavailable, err)
    }
    return RetentionPolicy{Days: row.Days}, nil
}
```

**Three things are identical, and they are the chapter.** Absence is not a failure: "no row"
returns the default special case, with no failure raised or returned, so no caller branches on
it. The driver's vocabulary stops at this boundary and is translated into one type of ours, so
callers catch or match on one thing. And the message names the operation *and* its subject, which
makes the log line actionable without a stack trace — the rule the adaptations' `Error` rule does
not reach.

**One thing differs, and it is exactly the stated cost.** The Python raise reaches its handler
with no help from the layers in between. The Go value does not travel: every layer between here
and the handler must return it again, adding its own operation as it goes, and the failure is now
**in the signature** — which is the coupling the checked-exception argument is about, taken on
deliberately at a boundary. Both are right; neither is free, and the chapter's rule is to know
which you bought.

## Key Takeaways

1. **The rules are about the shape of failure, not the mechanism**: fail loudly, carry the
   operation and the failure type, and never leave a failure path without code on it. Every
   language has a failure mechanism, so the shape rules always have somewhere to land.
2. **Both of this chapter's ch01 rows are Tier 2.** The *mechanics* — a `try` block's transaction
   scope, the checked-exception argument — need an exception, and where there is none this skill
   names the local mechanism instead of improvising an equivalent.
3. **Raise rather than return an error code**, and where the language's mechanism *is* a returned
   value, say so and pay the cost knowingly: a result type does not propagate, so every layer
   unwraps and rewraps, and there is no stack unless the error value carries one.
4. **Every failure carries the operation that failed and the failure type.** `Not implemented.`
   passes the adaptations' rule and fails the book's.
5. **Wrap a foreign failure vocabulary into one of yours.** Classify by how a failure will be
   caught, not by where it came from; distinct types only where you would catch them differently.
6. **Never return an absent-value sentinel and never pass one.** Use a Special Case object or an
   empty collection; code drowning in absence checks has too many, not too few. **This is the
   chapter's one row that a bare manifest supplies the construct for**: in HCL an argument set to
   `null` is the same as omitting it, while in a Kubernetes strategic-merge patch a `null`
   **deletes** the field, so there it is not an omission at all.
7. **A handler is a claim, and logging is not handling.** An empty handler contradicts the `try`
   that wrote it, and a logged-and-dropped failure gets lost. Log *and* take a code path.
8. **Recorded disagreement — checked exceptions.** The book rejects them in application code as
   an OCP violation cascading signature changes upward, reserving them for critical library
   boundaries; the adaptations are **silent rather than agreeing**, because TypeScript,
   JavaScript and Python have no such construct. What ports is the mechanism: **a failure
   declared in a signature couples every caller up the stack to that decision** — which is
   exactly the trade Go and Rust make on purpose.
9. **Error handling is one thing**, so it gets its own unit: `try` first word, nothing after the
   handler.
10. **In configuration the design is placement.** Reject at schema or plan time rather than in
    production, and never quiet a stage to make it pass — `try()`, `|| true` and an unchecked
    `continue-on-error` trade a loud failure for a quiet wrong state.

## Connects To
- **[ch01 — what survives translation](ch01-what-survives-translation.md)**: the index of record
  for this chapter's two rows, and the construct question that names the local mechanism.
- **[ch03 — units of work](ch03-units-of-work.md)**: error handling is one thing, so it is its
  own unit; the `try`-first-word rule is do-one-thing applied to a handler.
- **[ch04 — duplication and abstraction](ch04-duplication-and-abstraction.md)**: three identical
  handlers for three foreign failure types are duplication, and the wrapper is the extraction.
- **[ch05 — structure and dependencies](ch05-structure-and-dependencies.md)**: wrapping is the
  boundary technique stated there; the checked-exception argument is OCP; a special case object
  is polymorphism replacing a branch.
- **[ch07 — comments and formatting](ch07-comments-and-formatting.md)**: a typed error channel
  documents the failure mode, which is a comment you do not have to write — and a handler
  commented as unreachable is either dead code or a missing code path.
- **[ch08 — verification](ch08-verification.md)**: a failure path nothing exercises is a path
  nobody has read; the test that forces the failure is what drives the handler's scope.
- **[ch09 — declarative and config](ch09-declarative-and-config.md)**: fail-fast in Bash, and
  schema, `validation`, `precondition` and admission in Terraform and Kubernetes, are this
  chapter's rules in those languages, per ecosystem.
- **`clean-code-java` ch07** — the chapter this one distils: try-catch-finally first, define
  exceptions by the caller's needs, provide context, the Special Case pattern, and the full
  checked-exception argument. Its **ch03** holds *"Error Handling Is One Thing"*, its **ch08**
  the boundary wrapping, and its **ch17** the catalogue this skill does not duplicate.
- **`clean-code-typescript` ch09** and **`clean-code-javascript` ch09** — the `Error`-always rule,
  the never-swallow rules for `catch` and for rejected promises, and the `Failable<R, E>` result
  type with its propagation cost. `clean-code-python` has no error-handling chapter, which is
  silence rather than disagreement.
