# Chapter 9: Error Handling

## Core Idea
"Thrown errors are a good thing!" The failure is catching one and doing nothing useful with it. In Dart that means **catching a type you can handle (`on Exception catch (e, s)`), keeping the stack trace, and choosing a real response** — log it with the trace, tell the user, or report it to a service — whether the error arrives through `try`/`catch` or through a `Future`'s `onError`.

## Frameworks Introduced
- **Thrown errors are a good thing**: they mean "the runtime has successfully identified when something in your program has gone wrong and it's letting you know by stopping function execution on the current stack, killing the process, and notifying you in the console with a stack trace."
- **Don't ignore caught errors**: "If you wrap any bit of code in a `try/catch` it means you think an error may occur there and therefore you should have a plan, or create a code path, for when it occurs."
  - How (Dart): `try { … } on Exception catch (e, s) { … }` — the `on` clause names what you expect, and the second `catch` parameter keeps the `StackTrace`. Then pick a response:
    - **Option 1**: `log('Error description...', error: e, stackTrace: s);`
    - **Option 2**: `notifyUserOfError(e, s);`
    - **Option 3**: `reportErrorToService(e, s);`
  - Why not just print: "Logging the error to the console (`log`) isn't much better as often times it can get lost in a sea of things printed to the console."
- **Don't ignore Future errors**: "Using await within try/catch is way better than future/then. But, if you want to use future/then, remember to handle the errors."
  - How: give `.onError((e, s) { … })` the same three options instead of `print(e)`.

## Key Concepts
- **`on Type catch (e, s)`** — Dart's typed catch clause: `on` filters by type, `e` is the thrown object, `s` its `StackTrace`.
- **`catch (error)` alone** — catches *any* thrown object; the guide's Bad shape.
- **`Exception` vs `Error`** — by Dart convention, `Exception`s are failures a program is expected to handle, and `Error`s (such as `StateError` or `RangeError`) signal programming mistakes. `on Exception` lets `Error`s propagate. *(Background: the guide's Good example relies on this but doesn't explain it.)*
- **`StackTrace`** — where the error came from; the reason the Good examples always pass `s` along.
- **`log(message, error:, stackTrace:)`** — `dart:developer`'s logging function (judging by its `error:` and `stackTrace:` parameters), structured rather than a bare `print`.
- **`Future.onError((e, s) { … })`** — handles a `Future`'s error in `.then`-style code; the handler's result stands in for the future's value.
- **Code path for failure** — the guide's test for a `catch` block: is there a plan, or just a print?

## Mental Models
- **A `catch` block is a promise you have a plan.** If none of the three options applies, the `try`/`catch` shouldn't be there — let the error propagate to code that can act.
- **Catch what you expect, by type.** `on Exception` (or a narrower type) says what you anticipated; a bare `catch` also swallows programming errors you'd rather see crash.
- **Never drop the stack trace.** Each Good option receives `s`; an error report without it is a guess about where things went wrong.
- **`await` first, `onError` only when you keep `.then`.** Once you `await` (Ch 8), Future errors arrive in the same `try`/`on … catch` as synchronous ones.

## Anti-patterns
- **`catch (error) { print(error); }`** — catches everything, prints without a trace, carries on.
- **`.onError((e, s) { print(e); })`** — the same mistake in `Future` form; the stack trace is in hand and thrown away.
- **Empty or comment-only catch blocks** — "Doing nothing with a caught error doesn't give you the ability to ever fix or react to said error."
- **Defensive `try`/`catch` without a plan** — if you can't say which option you'd take, you don't need the block.

## Code Examples

```dart
// Bad
try {
  functionThatMightThrow();
} catch (error) {
  print(error);
}

// Good
try {
  functionThatMightThrow();
} on Exception catch (e, s) {
  // Option 1:
  log('Error description...', error: e, stackTrace: s);
  // Option 2:
  notifyUserOfError(e, s);
  // Option 3:
  reportErrorToService(e, s);
}
```
- **What it demonstrates**: the `on` clause narrows what's caught, the second parameter keeps the trace, and each option is a real code path.

```dart
// Bad
functionThatMightThrow().then((value) {
  // ...
}).onError((e, s) {
  print(e);
});

// Good
functionThatMightThrow().then((value) {
  // ...
}).onError((e, s) {
  // Option 1:
  log('Error description...', error: e, stackTrace: s);
  // Option 2:
  notifyUserOfError(e, s);
  // Option 3:
  reportErrorToService(e, s);
});
```
- **What it demonstrates**: the `Future` version gets identical treatment. The guide prefers rewriting it with `await` inside `try` (Ch 8); this is the fallback when the chain stays.

## Reference Tables

| Catch shape | Catches | Keeps the trace? | Guide's verdict |
|---|---|---|---|
| `catch (error) { print(error); }` | anything thrown | no | Bad |
| `on Exception catch (e, s) { log(…, error: e, stackTrace: s); }` | `Exception`s only | yes | Good (Option 1) |
| `on Exception catch (e, s) { notifyUserOfError(e, s); }` | `Exception`s only | yes | Good (Option 2) |
| `on Exception catch (e, s) { reportErrorToService(e, s); }` | `Exception`s only | yes | Good (Option 3) |
| `.onError((e, s) { print(e); })` | the future's error | no | Bad |
| `.onError((e, s) { …one of the options… })` | the future's error | yes | Good, but `await` + `try` is "way better" |

## Worked Example
**Reading the guide's one inconsistency.** The explanation says logging with `log` "isn't much better" than doing nothing, yet Option 1 of the Good example *is* a `log` call. Both can't be the rule as stated, so look at what actually changes between Bad and Good:

1. **The catch is typed.** Bad catches every thrown object; Good catches `Exception`s, so a `StateError` from a bug is not quietly handled as if it were an expected failure.
2. **The trace survives.** Bad prints the error's message only; Good passes `stackTrace: s`, so the log entry says where the failure happened.
3. **The output is structured.** `print` adds a line to the console; `log` records the message with the error and trace attached, where a logging setup can filter and route it.

So the workable rule is: **printing an error and carrying on is ignoring it; logging it with its type and trace is Option 1 of a plan.** Where the failure matters to the user or to operations, Options 2 and 3 are the stronger choices. (The JavaScript parent's version ends with "OR do all three!"; the Dart port lists the options without that line.)

## Key Takeaways
1. **Thrown errors are good** — they stop execution and tell you where.
2. **Every `catch` needs a plan**: log with the trace, notify the user, or report to a service. No plan, no `catch`.
3. **Catch by type** — `on Exception catch (e, s)` — and let programming `Error`s surface.
4. **Keep the `StackTrace`** in every handler.
5. **Prefer `await` inside `try`**; if you keep `.then`, give `.onError` the same treatment.
6. **`print(error)` is not handling.**

## Connects To
- **Ch 8**: `async`/`await` is what makes `try`/`on … catch` work for asynchronous code.
- **Ch 3**: "Avoid side effects (part 1)" — reporting to a service is a side effect to centralize in one place.
- **`clean-code-java`** ch. 7 (Error Handling): exceptions vs return codes, defining exception classes by caller needs, not returning or passing null — none of which this guide covers.
- **`clean-code-javascript` Ch 9**: the parent rules with `console.error` and `.catch()`.
