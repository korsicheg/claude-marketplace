# Chapter 9: Error Handling

## Core Idea
"**Thrown errors are a good thing!**" — they mean the runtime caught a failure and told you. The sin is not throwing; it is **catching without a plan**, in `try/catch` or in `.catch()`.

## Frameworks Introduced
- **Errors are a feature, not a nuisance**: a thrown error means the runtime "has successfully identified when something in your program has gone wrong" — stopping execution on the current stack, killing the process (in Node), and notifying you with a stack trace.
  - When to use: as the framing before any error-handling decision.
  - How: don't suppress the signal; decide what to do with it.
- **Don't ignore caught errors**: an empty or `console.log`-only `catch` block throws away the ability to fix or react.
  - When to use: every `try/catch` you write.
  - How: choose at least one of the three responses below — "OR do all three!"
    1. `console.error(error)` — "more noisy than `console.log`", which is the point.
    2. `notifyUserOfError(error)` — tell the person affected.
    3. `reportErrorToService(error)` — send it somewhere that persists and alerts.
  - The rule behind the rule: "If you wrap any bit of code in a `try/catch` it means you think an error may occur there and therefore you should have a plan, or create a code path, for when it occurs."
- **Don't ignore rejected promises**: the identical rule for `.catch()` — "For the same reason you shouldn't ignore caught errors from `try/catch`."
  - When to use: every promise chain.
  - How: the same three responses; `console.log(error)` in a `.catch()` is the same defect in different syntax.

## Key Concepts
- **Thrown error** — the runtime's successful detection of a fault; a signal, not a failure of design.
- **Stack trace** — the diagnostic the throw hands you for free.
- **Swallowed error** — a caught error that produces no action; the chapter's core anti-pattern.
- **`console.log` vs `console.error`** — `log` is quiet and "can get lost in a sea of things printed to the console"; `error` is deliberately noisier and goes to stderr.
- **Code path for failure** — the plan a `try/catch` implies you already have.
- **Rejected promise** — the promise-chain equivalent of a throw; ignoring it is the same mistake.
- **Error reporting service** — durable, alertable storage for production errors.

## Mental Models
- **Think of `try/catch` as a claim.** Writing one asserts "I believe this can fail." An empty catch block retracts the claim while keeping the syntax.
- **Use "who finds out?" as the test.** If the answer is "nobody, or me if I happen to be scrolling the console", the handler is inadequate.
- **Think of `console.log(error)` as the most common way to hide a bug in plain sight.** It looks like handling. It is discarding, with a receipt nobody reads.
- **The three responses are additive, not exclusive.** Log loudly, tell the user, report to the service — "OR do all three!"
- **Treat `.catch()` and `catch {}` as the same construct.** Every rule you'd apply to one applies to the other.

## Anti-patterns
- **`catch (error) { console.log(error); }`**: the guide's named bad example — quiet, ephemeral, and easily lost in console noise.
- **An empty catch block**: "Doing nothing with a caught error doesn't give you the ability to ever fix or react to said error."
- **`.catch(error => { console.log(error); })`**: the identical defect on the promise side.
- **Catching to silence a noisy log**: if you wrapped it, you expected failure — handle it rather than muting it.
- **Treating thrown errors as something to eliminate**: the throw is the runtime doing its job; the process dying in Node with a stack trace is information, not damage.
- **A promise chain with no `.catch()` at all**: strictly worse than an inadequate one.

## Code Examples
`try/catch` — give the caught error somewhere to go:

```javascript
// Bad
try {
  functionThatMightThrow();
} catch (error) {
  console.log(error);
}

// Good
try {
  functionThatMightThrow();
} catch (error) {
  // One option (more noisy than console.log):
  console.error(error);
  // Another option:
  notifyUserOfError(error);
  // Another option:
  reportErrorToService(error);
  // OR do all three!
}
```
- **What it demonstrates**: the fix is not more code around the error, it is *a decision* about who learns of it — the developer (stderr), the user (notification), or the on-call rotation (reporting service).

The same rule on the promise side:

```javascript
// Bad
getdata()
  .then(data => {
    functionThatMightThrow(data);
  })
  .catch(error => {
    console.log(error);
  });

// Good
getdata()
  .then(data => {
    functionThatMightThrow(data);
  })
  .catch(error => {
    console.error(error);
    notifyUserOfError(error);
    reportErrorToService(error);
  });
```
- **What it demonstrates**: `.catch()` is `catch` — there is no separate, laxer standard for promise chains.

## Reference Tables

The three responses:

| Response | Audience | When it's enough |
|---|---|---|
| `console.error(error)` | Developer, now | Local dev, or alongside the others. Noisier than `console.log` — deliberately |
| `notifyUserOfError(error)` | The affected user | The user can retry, correct input, or needs to stop waiting |
| `reportErrorToService(error)` | On-call / future you | Production. The only option that persists and alerts |
| All three | Everyone | The guide's explicit recommendation: "OR do all three!" |

Handler adequacy:

| Handler | Verdict |
|---|---|
| `catch (e) {}` | Worst — error erased |
| `catch (e) { console.log(e) }` | Bad — lost in console noise |
| `catch (e) { console.error(e) }` | Minimum acceptable |
| `catch (e) { console.error(e); notifyUserOfError(e); reportErrorToService(e); }` | Recommended |
| No `.catch()` on a chain | Unhandled rejection |

## Worked Example
The chapter's logic, applied as a decision you make at the moment you type `try`:

**Step 1 — Why are you wrapping this?** You typed `try` because you believe `functionThatMightThrow()` can fail. That belief is the whole justification for the construct. Write it down, at least mentally: *"the network can be down"*, *"the file may not exist"*, *"the payload may be malformed."*

**Step 2 — Given that failure, what must happen?** This is the "plan, or code path" the guide demands. Work through the three audiences:

| Question | If yes, add |
|---|---|
| Does a developer need to see this while working? | `console.error(error)` |
| Is a human waiting on this operation right now? | `notifyUserOfError(error)` |
| Would I want to know this happened in production at 3am? | `reportErrorToService(error)` |

**Step 3 — If every answer is "no", delete the `try/catch`.** This is the part that is easy to miss. If nobody needs to know and nothing should change, then you did not have a plan — and letting the error propagate to a caller who *does* have one is better than swallowing it here. An empty catch doesn't handle the error; it deletes it.

**Step 4 — Apply the identical process to `.catch()`.** The promise version of the bad example is character-for-character the same mistake:

```javascript
.catch(error => {
  console.log(error);   // same defect, different syntax
});
```

**Why `console.log` specifically fails the test:** it isn't that logging is wrong — it's that `console.log` output "can get lost in a sea of things printed to the console." `console.error` writes to stderr, is visually distinguished in most terminals and browsers, and can be routed separately in production. The upgrade costs four characters.

## Key Takeaways
1. Thrown errors are **good** — the runtime detected a fault and handed you a stack trace.
2. Writing `try/catch` is a claim that failure is possible; back it with a plan or don't write it.
3. **Never** leave a catch block empty, and never let `console.log` be the whole handler.
4. Choose from three responses — `console.error`, notify the user, report to a service — and prefer doing all three.
5. `console.error` over `console.log`: noisier on purpose, and it survives in a busy console.
6. Rejected promises get exactly the same treatment as caught exceptions — `.catch()` is not a weaker construct.

## Connects To
- **Ch 8 (Concurrency)**: promise chains and `async`/`await` `try/catch` blocks are where these rules get applied; the worked async example's trailing uncaught call is the gap this chapter closes.
- **Ch 3 (Functions)**: "Avoid Side Effects (part 1)" — centralizing side effects into one service gives you one place to report failures from; `reportErrorToService` is that pattern.
- **Ch 11 (Comments)**: a swallowed error with `// shouldn't happen` next to it is two anti-patterns at once.
- **Ch 7 (Testing)**: the error path is a branch — branch coverage means testing that your handler actually runs.
