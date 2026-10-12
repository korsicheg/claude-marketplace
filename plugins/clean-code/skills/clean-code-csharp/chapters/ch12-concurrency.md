# Chapter 12: Concurrency

## Core Idea
**Use `async`/`await` on `Task`, all the way through, for I/O-bound work.** Never block on a task (`.Result`, `.Wait()`), never write `async void` except for event handlers, replace every blocking primitive with its awaitable twin (`Task.WhenAll`, `Task.WhenAny`, `Task.Delay`), and keep CPU-bound work off the `async` path. The whole section is one entry — a set of reference tables the source takes from a gist that cites Stephen Cleary's 2013 MSDN Magazine article *"Async/Await - Best Practices in Asynchronous Programming"* and his blog.

## Frameworks Introduced
- **The three guidelines** ("Summary of Asynchronous Programming Guidelines"), each with its stated exception:
  - **Avoid `async void`** — "Prefer async Task methods over async void methods." Exception: event handlers.
  - **Async all the way** — "Don't mix blocking and async code." Exception: the console `Main` method.
  - **Configure context** — "Use `ConfigureAwait(false)` when you can." Exception: methods that require context.
- **The async way of doing things** — four replacements: `await` instead of `Task.Wait`/`Task.Result`; `await Task.WhenAny` instead of `Task.WaitAny`; `await Task.WhenAll` instead of `Task.WaitAll`; `await Task.Delay` instead of `Thread.Sleep`.
- **I/O-bound vs compute-bound** — "The async/await is the best for IO bound tasks (networking communication, database communication, http request, etc.) but it is not good to apply on computational bound tasks (traverse on the huge list, render a huge image, etc.)" because awaiting releases the thread rather than doing the work. For heavy computation the source prescribes a task started with `TaskCreationOptions.LongRunning` (it writes `Task.Factory.CreateNew`; the API is `Task.Factory.StartNew`), which "will start a new background thread … without release it back to the thread pool until the task being completed."
- **Know your tools** — a table of the right primitive for each common async problem (below), and a pointer to Microsoft's *Task-based Asynchronous Pattern (TAP)* document: "extremely well-written, and includes guidance on API design and the proper use of async/await (including cancellation and progress reporting)."
- **"Doing It Wrong(TM)"** — "If you have any of these Old examples in your new async code, you're Doing It Wrong(TM)": the Old → New table below.

## Key Concepts
- **`Task` / `Task<T>`** — the awaitable unit of asynchronous work.
- **`async void`** — an async method nobody can await; its exceptions can't be caught by the caller. Fit only for event handlers.
- **Async all the way** — once one call is async, its callers are too; no blocking bridges.
- **Blocking on async** — `.Result` / `.Wait()`; risks deadlock where a synchronization context exists, and wastes a thread everywhere.
- **`ConfigureAwait(false)`** — resume on any thread instead of the captured context.
- **I/O-bound** — waiting on a network, disk or database; `await` frees the thread.
- **Compute-bound** — the CPU is the bottleneck; `await` doesn't make it faster.
- **`TaskCreationOptions.LongRunning`** — hints the scheduler to use a dedicated thread instead of a pool thread.
- **TAP** — the Task-based Asynchronous Pattern, .NET's convention for async APIs.

## Mental Models
- **Async is contagious, so let it spread.** Fighting it with `.Result` at some layer is where deadlocks and starved thread pools come from.
- **`await` is for waiting, not working.** It gives the thread back while something *else* (a socket, a disk) does the work. If nothing else is doing the work, there's nothing to wait for — that's compute, and it needs a thread.
- **Every blocking call has an awaitable twin.** `Wait`→`await`, `WaitAll`→`WhenAll`, `WaitAny`→`WhenAny`, `Sleep`→`Delay`. If you see the left column in async code, convert it.
- **`async void` is fire-and-forget with no catch.** Treat it as an event-handler-only signature.

## Anti-patterns
- **`task.Result` / `task.Wait()`** inside async code.
- **`Thread.Sleep`** in async code — it blocks the thread `await Task.Delay` would have released.
- **`async void` methods** other than event handlers.
- **`new Task(…)` + `Start()`** — the source: use `Task.Run` or `TaskFactory.StartNew`, "not the Task constructor or Task.Start".
- **Wrapping CPU-heavy loops in `async`** and expecting a speedup.
- **Sequential awaits that could be `WhenAll`** — the "retrieve the results of multiple tasks" row.

## Reference Tables

**Summary of Asynchronous Programming Guidelines**

| Name | Description | Exceptions |
|---|---|---|
| Avoid async void | Prefer async Task methods over async void methods | Event handlers |
| Async all the way | Don't mix blocking and async code | Console main method |
| Configure context | Use `ConfigureAwait(false)` when you can | Methods that require context |

**The Async Way of Doing Things**

| To do this … | Instead of this … | Use this |
|---|---|---|
| Retrieve the result of a background task | `Task.Wait` or `Task.Result` | `await` |
| Wait for any task to complete | `Task.WaitAny` | `await Task.WhenAny` |
| Retrieve the results of multiple tasks | `Task.WaitAll` | `await Task.WhenAll` |
| Wait a period of time | `Thread.Sleep` | `await Task.Delay` |

**Solutions to Common Async Problems**

| Problem | Solution |
|---|---|
| Create a task to execute code | `Task.Run` or `TaskFactory.StartNew` (not the `Task` constructor or `Task.Start`) |
| Create a task wrapper for an operation or event | `TaskFactory.FromAsync` or `TaskCompletionSource<T>` |
| Support cancellation | `CancellationTokenSource` and `CancellationToken` |
| Report progress | `IProgress<T>` and `Progress<T>` |
| Handle streams of data | TPL Dataflow or Reactive Extensions |
| Synchronize access to a shared resource | `SemaphoreSlim` |
| Asynchronously initialize a resource | `AsyncLazy<T>` |
| Async-ready producer/consumer structures | TPL Dataflow or `AsyncCollection<T>` |

`AsyncLazy<T>` and `AsyncCollection<T>` are not in the .NET base library; they ship in Stephen Cleary's Nito.AsyncEx package. The source doesn't say so.

**Old → New**

| Old | New | Description |
|---|---|---|
| `task.Wait` | `await task` | Wait/await for a task to complete |
| `task.Result` | `await task` | Get the result of a completed task |
| `Task.WaitAny` | `await Task.WhenAny` | Wait/await for one of a collection of tasks to complete |
| `Task.WaitAll` | `await Task.WhenAll` | Wait/await for every one of a collection of tasks to complete |
| `Thread.Sleep` | `await Task.Delay` | Wait/await for a period of time |
| `Task` constructor | `Task.Run` or `TaskFactory.StartNew` | Create a code-based task |

## Worked Example
The source gives tables, not code. Here is its Old → New table applied to one method — a reconstruction, not a source snippet.

**Old** — blocking calls in a method that already has async dependencies:

```csharp
public Report BuildReport(int customerId)
{
    var orders = _orders.GetOrdersAsync(customerId).Result;      // task.Result
    var invoices = _billing.GetInvoicesAsync(customerId).Result; // task.Result
    Thread.Sleep(500);                                            // Thread.Sleep
    return new Report(orders, invoices);
}
```

**New** — async all the way, with the awaitable twins:

```csharp
public async Task<Report> BuildReportAsync(int customerId, CancellationToken cancellationToken)
{
    var ordersTask = _orders.GetOrdersAsync(customerId, cancellationToken);
    var invoicesTask = _billing.GetInvoicesAsync(customerId, cancellationToken);
    await Task.WhenAll(ordersTask, invoicesTask);                 // Task.WaitAll → WhenAll
    await Task.Delay(500, cancellationToken);                     // Thread.Sleep → Delay
    return new Report(await ordersTask, await invoicesTask);      // .Result → await
}
```

Row by row: both `.Result` calls become `await`s; the two independent fetches start together and are awaited with `WhenAll` ("retrieve the results of multiple tasks"); `Thread.Sleep` becomes `Task.Delay`; and a `CancellationToken` flows through, per the "support cancellation" row. The return type is `Task<Report>`, not `void` — "avoid async void". Every caller of `BuildReportAsync` now awaits it too: async all the way.

## Dated advice — read with the year in mind
The tables date from the .NET Framework 4.5 era (2012–2013). Three points have moved since; none is a rule from the source:
- **"Console main method" is no longer an exception** to async-all-the-way: since C# 7.1, `static async Task Main` is allowed.
- **`ConfigureAwait(false)`** matters where a synchronization context exists (UI frameworks, classic ASP.NET) and in general-purpose libraries; ASP.NET Core has no synchronization context, so in its application code it changes little.
- **Newer tools the tables predate**: `ValueTask`, `IAsyncEnumerable<T>` with `await foreach`, `System.Threading.Channels` for producer/consumer, and `Parallel.ForEachAsync`.

## Key Takeaways
1. **`async Task`, never `async void`** (event handlers excepted).
2. **Async all the way** — no `.Result`, no `.Wait()`.
3. Swap every blocking primitive for its **awaitable twin**: `WhenAll`, `WhenAny`, `Delay`.
4. **`await` is for I/O**; give heavy computation its own thread (`LongRunning`).
5. Create tasks with **`Task.Run` / `TaskFactory.StartNew`**, never the `Task` constructor.
6. Use the **framework's primitives** for cancellation, progress and coordination: `CancellationToken`, `IProgress<T>`, `SemaphoreSlim`.

## Connects To
- **Ch 9**: the OCP adapters' `Request` methods, "return promise" in the source, are `Task<bool>` in real C#.
- **Ch 13**: an exception from `async void` can't be caught by the caller — the error-handling rules assume awaited tasks.
- **Source further reading**: the source's Cheatsheets list includes David Fowler's *AspNetCoreDiagnosticScenarios* ("Examples of broken patterns in ASP.NET Core applications") — the current companion to these tables.
- **clean-code-java** ch13 and Appendix A: the book's concurrency principles (keep concurrency code separate, limit shared data, know the execution models), which this source does not cover.
- **clean-code-typescript** ch08: the same callbacks → promises → `async`/`await` ladder, with `Promise.all` for `Task.WhenAll`.
