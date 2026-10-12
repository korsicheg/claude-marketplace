# Chapter 13: Error Handling

## Core Idea
"Thrown errors are a good thing!" In C#, keep them useful: **rethrow with `throw;`, never `throw ex;`**, so the stack trace survives; **never swallow** a caught exception; **catch by type** with multiple `catch` blocks rather than `if (ex is …)` inside one; and when you add context, **wrap** the original as the new exception's inner exception.

## Frameworks Introduced
- **Basic concept of error handling** — "Thrown errors are a good thing! They mean the runtime has successfully identified when something in your program has gone wrong and it's letting you know by stopping function execution on the current stack, killing the process (in .NET/.NET Core), and notifying you in the console with a stack trace." (The process dies only if nothing catches the exception.)
- **Don't use `throw ex` in a catch block** — "If you need to re-throw an exception after catching it, use just 'throw'. By using this, you will save the stack trace. But in the bad option below, you will lost the stack trace."
- **Don't ignore caught errors** — "Doing nothing with a caught error doesn't give you the ability to ever fix or react to said error … If you wrap any bit of code in a `try/catch` it means you think an error may occur there and therefore you should have a plan, or create a code path, for when it occurs."
  - How: `catch (Exception ex) { // silent exception }` → `NotifyUserOfError(error);` and/or `ReportErrorToService(error);`.
  - The source adds that merely printing it "isn't much better as often times it can get lost in a sea of things printed to the console" (its text says "Throwing the error", a slip carried over from the JavaScript original's console logging).
- **Use multiple catch blocks instead of if conditions** — "If you need to take action according to type of the exception, you better use multiple catch block for exception handling."
  - How: `catch (Exception ex) { if (ex is TaskCanceledException) … else if (ex is TaskSchedulerException) … }` → `catch (TaskCanceledException ex) { … } catch (TaskSchedulerException ex) { … }`.
- **Keep exception stack trace when rethrowing exceptions** — "It is a bad practice to throw a caught exception using `throw e;`. This statement resets the stack trace. Instead use `throw;`."
  - The second option: "use a custom exception. Simply instantiate a new exception and set its inner exception property to the caught exception with `throw new CustomException("some info", e);`. Adding information to an exception is a good practice as it will help with debugging."
  - The deciding line: "However, if the objective is to log an exception then use `throw;` to pass the buck to the caller."

## Key Concepts
- **Stack trace** — the call path to the point an exception was thrown; what `throw ex;` resets and `throw;` preserves.
- **`throw;`** — rethrows the current exception unchanged, inside a `catch` block.
- **`throw ex;`** — throws the caught object as if new; the trace restarts at this line.
- **Swallowed exception** — caught and ignored; the failure disappears.
- **Typed catch block** — `catch (TaskCanceledException ex)`; the runtime picks the handler by type.
- **Inner exception** — the original exception carried inside a new, more descriptive one (`InnerException`).
- **Custom exception** — your own `Exception` subclass that adds domain context.

## Mental Models
- **A `try/catch` is a claim that something may fail — so make a plan.** An empty `catch` contradicts itself.
- **The stack trace is the evidence; don't tamper with it.** `throw ex;` throws away the frames below the catch — exactly where the bug was.
- **Let the runtime dispatch on type.** Multiple `catch` blocks are the exception-handling version of "avoid type-checking" (Ch 5): the language already does the `if (ex is …)`.
- **Wrap to add meaning, rethrow to add nothing.** If you have context the caller lacks, wrap with the original as inner exception; if you only logged, `throw;`.

## Anti-patterns
- **`throw ex;`** — the stack trace now starts in your catch block.
- **Empty `catch`** or `// silent exception`.
- **Type tests inside one `catch (Exception)`** — `if (ex is TaskCanceledException)`.
- **Wrapping without the inner exception** — `throw new CustomException("failed");` loses the cause.

## Code Examples
Catch by type, not by `if`:

```csharp
// Bad
try
{
    // Do something..
}
catch (Exception ex)
{
    if (ex is TaskCanceledException)
    {
        // Take action for TaskCanceledException
    }
    else if (ex is TaskSchedulerException)
    {
        // Take action for TaskSchedulerException
    }
}

// Good
try
{
    // Do something..
}
catch (TaskCanceledException ex)
{
    // Take action for TaskCanceledException
}
catch (TaskSchedulerException ex)
{
    // Take action for TaskSchedulerException
}
```
- **A C# detail the source doesn't mention**: order `catch` blocks from most specific to most general. A `catch (Exception)` placed before a more specific one makes the later block unreachable, which the compiler rejects (error CS0160).
- The Bad version also has a silent failure: an exception that is neither type is caught and dropped.

Don't swallow:

```csharp
// Bad
try
{
    FunctionThatMightThrow();
}
catch (Exception ex)
{
    // silent exception
}

// Good
try
{
    FunctionThatMightThrow();
}
catch (Exception error)
{
    NotifyUserOfError(error);

    // Another option
    ReportErrorToService(error);
}
```

## Worked Example
**Logging and rethrowing, three ways.** The source's last rule walks the full decision.

**Bad** — log, then `throw ex;`:

```csharp
try
{
    FunctionThatMightThrow();
}
catch (Exception ex)
{
    logger.LogInfo(ex);
    throw ex;
}
```

The log line has the full trace; every handler above this one sees a trace that starts *here*. Whoever investigates upstream is told the failure happened in the catch block.

**Good — pass the buck** (when all you did was log):

```csharp
try
{
    FunctionThatMightThrow();
}
catch (Exception error)
{
    logger.LogInfo(error);
    throw;
}
```

**Good — wrap with context** (when you know something the caller doesn't):

```csharp
try
{
    FunctionThatMightThrow();
}
catch (Exception error)
{
    logger.LogInfo(error);
    throw new CustomException("some info", error);
}
```
- *The source's code writes `new CustomException(error)`; its prose gives the `("some info", e)` form shown here, which is the one that actually adds information.*

**The decision**: added no information → `throw;`. Added information → new exception with the original as `InnerException`. Never `throw ex;`. (`logger.LogInfo` is the source's placeholder; with `Microsoft.Extensions.Logging` it would be `LogError(error, "…")`.)

## Key Takeaways
1. **`throw;`, never `throw ex;`** — keep the stack trace.
2. **Never swallow**: a `catch` needs a code path — notify, report, recover, or rethrow.
3. **One `catch` per exception type**, most specific first; no `if (ex is …)`.
4. **Wrap to add context**, always passing the original as the inner exception.
5. If you only logged, **`throw;`** and let the caller decide.

## Connects To
- **Ch 5**: typed `catch` blocks are "avoid type-checking" applied to exceptions.
- **Ch 12**: exceptions from `async void` can't be caught by a caller; await tasks so these rules apply.
- **Ch 4**: "do one thing" applies to handlers too; the book (clean-code-java ch03, "Error Handling Is One Thing") says a function that handles errors should do nothing else.
- **clean-code-java** ch07 (Error Handling): use unchecked exceptions, provide context, define exception classes by the caller's needs, don't return or pass `null` — the parts this source omits.
- **clean-code-typescript** ch09: the same "never swallow" rule, plus a `Failable<R, E>` result type as an alternative to throwing.
