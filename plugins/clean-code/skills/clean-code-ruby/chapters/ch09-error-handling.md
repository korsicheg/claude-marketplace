# Chapter 9: Error Handling

## Core Idea
"Thrown errors are a good thing!" The sin is not raising; it is **rescuing without a plan** — and raising without saying **what** went wrong. Rescue `StandardError` only when you have a code path for the failure, and raise with a **descriptive error class and a message** so the failure can be understood and rescued by type. Two rules; the second is the Ruby port's own, replacing the JavaScript parent's rejected-promises rule.

## Frameworks Introduced
- **Errors are signals**: a raised error means "the runtime has successfully identified when something in your program has gone wrong and it's letting you know by stopping method execution on the current stack, killing the process, and notifying you in the logs with a stack trace."
- **Don't ignore caught errors**: "Doing nothing with a caught error doesn't give you the ability to ever fix or react to said error. Logging the error isn't much better as often times it can get lost in a sea of other logs."
  - The commitment: "If you wrap any bit of code in a `begin/rescue` it means you think an error may occur there and therefore you should have a plan, or create a code path, for when it occurs."
  - How — the guide's three options, "OR do all three!":
    1. Log at error level: `logger.error(err)`, with the logger's threshold raised to `Logger::ERROR` so these lines aren't drowned out.
    2. Notify the end user: `notify_user_of_error(err)`.
    3. Report to an error service: `report_error_to_service(err)` — "a third-party service like Honeybadger".
- **Provide context with exceptions**: "Use a descriptive error class name and a message when you raise an error. That way you know why the error occurred and you can rescue the specific type of error."
  - How: `fail ArgumentError, 'Missing user' unless user` instead of a bare `fail unless user`.

## Key Concepts
- **`begin` / `rescue`** — Ruby's try/catch; `rescue StandardError => err` binds the exception.
- **`StandardError`** — the base class of ordinary application errors; what the guide's examples rescue.
- **`Logger`** — Ruby's standard-library logger; `logger.level = Logger::ERROR` filters out lower-severity lines.
- **`logger.info` vs `logger.error`** — the guide's bad example logs a failure at info level, where it vanishes.
- **Error-reporting service** — a third-party collector of production exceptions; Honeybadger is the guide's example.
- **`fail`** — Kernel's alias for `raise`; the guide uses it in the context rule.
- **Descriptive error class** — e.g. `ArgumentError`; tells the reader the category and lets callers `rescue` that category specifically.
- **Error message** — the human-readable "why" (`'Missing user'`).

## Mental Models
- **A `rescue` is a promise that a plan exists.** If none of the three options applies, the honest move is to not rescue at all and let the error propagate.
- **Classes are for code; messages are for people.** The class (`ArgumentError`) lets a caller handle the failure by type; the message (`'Missing user'`) tells the human reading the log what happened.
- **Log levels are a filter, not decoration.** A failure logged at `info` is filtered out by exactly the configuration that keeps production logs readable.

## Anti-patterns
- **Rescue and log at info** (`logger.info(err)`): the guide's bad example — the error is "lost in a sea of other logs".
- **Rescue and do nothing**: removes any ability "to ever fix or react to said error."
- **`begin`/`rescue` without a planned code path**: if there's no plan, there's no reason to rescue.
- **Bare `fail` / `raise`**: with no class and no message, Ruby raises a generic `RuntimeError`; the reader learns nothing and callers can't rescue it selectively.
- **One generic error class for everything**: defeats "rescue the specific type of error".

## Code Examples
Provide context with exceptions:

```ruby
# Bad
def initialize(user)
  fail unless user
  # ...
end

# Good
def initialize(user)
  fail ArgumentError, 'Missing user' unless user
  # ...
end
```
- **What it demonstrates**: the class names the category of mistake (a bad argument), the message names the specific one, and a caller can now write `rescue ArgumentError` without catching unrelated failures.

## Reference Tables

| Option after `rescue StandardError => err` | Code in the guide | When it fits |
|---|---|---|
| Log at error level | `logger.error(err)` with `logger.level = Logger::ERROR` | always at minimum, if you rescue at all |
| Tell the user | `notify_user_of_error(err)` | user-facing flows |
| Report to a service | `report_error_to_service(err)` (e.g. Honeybadger) | production systems |
| All three | — | "OR do all three!" |
| None applies | — | don't rescue; let it propagate |

## Worked Example
**From a swallowed error to a planned code path.**

```ruby
require 'logger'

logger = Logger.new(STDOUT)

begin
  method_that_might_throw()
rescue StandardError => err
  logger.info(err)
end
```

The `begin` claims a failure is possible here. The `rescue` then logs it at `info` — the level most production configurations suppress — and carries on as if nothing happened. The guide's verdict: logging alone "isn't much better" than doing nothing.

```ruby
require 'logger'

logger = Logger.new(STDOUT)
# Change the logger level to ERROR to output only logs with ERROR level and above
logger.level = Logger::ERROR

begin
  method_that_might_throw()
rescue StandardError => err
  # Option 1: Only log errors
  logger.error(err)
  # Option 2: Notify end-user via an interface
  notify_user_of_error(err)
  # Option 3: Report error to a third-party service like Honeybadger
  report_error_to_service(err)
  # OR do all three!
end
```

Now the failure is logged where it will be seen, the user knows something went wrong, and the team has a record in an error service. **The transferable rule**: every `rescue` names its plan; if you can't name one, delete the `begin`.

## Key Takeaways
1. **Raised errors are good** — they stop execution and point at the problem.
2. **Never rescue without a plan**; logging at info is not a plan.
3. **Pick from log at error level, notify the user, report to a service** — or all three.
4. **Raise with a descriptive class and a message**: `fail ArgumentError, 'Missing user'`.
5. **Specific error classes let callers rescue specifically.**

## Connects To
- **Ch 3**: centralizing side effects — reporting is one service, not scattered `puts`.
- **Ch 4**: `combine`'s bad version does `raise 'Must be of type String or Numeric'` — a message, but no descriptive class, so it arrives as a generic `RuntimeError`.
- **Ch 7 (DIP)**: the logger and the reporting service are collaborators worth injecting.
- **clean-code-javascript**: its second error rule is "Don't ignore rejected promises"; the Ruby port replaces it with this chapter's context rule.
- **clean-code-java**: exceptions vs return codes, special-case objects, and wrapping third-party errors — not covered here.
