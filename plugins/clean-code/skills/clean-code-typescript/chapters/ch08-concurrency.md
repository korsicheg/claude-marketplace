# Chapter 8: Concurrency

## Core Idea
A two-step ladder: **callbacks → promises → `async`/`await`**. Callbacks "aren't clean, and they
cause excessive amounts of nesting *(the callback hell)*"; promises flatten that; `async`/`await`
is *"far cleaner and more understandable than chained promises"* and restores ordinary
`try`/`catch`.

## Frameworks Introduced

- **Prefer promises over callbacks.**
  - When to use: any callback-style API, including every Node built-in written before promises.
  - How: don't hand-wrap — **promisify**. The source names the tools:
    `util.promisify` (Node.js), and for general purpose **pify** and **es6-promisify**.
  - What it buys: the error path stops being duplicated at every nesting level. In the callback
    version, `if (error) callback(error)` appears once per level; the promise version has **one**
    `.catch()`.

- **`async`/`await` over promise chains.**
  - The mechanism, as stated: within a function prefixed with `async`, `await` *"tell[s] the
    JavaScript runtime to pause the execution of code"* on a promise.
  - When to use: as the default for sequential async work.
  - How: `const response = await get(url)` in place of `.then(response => ...)`, and wrap the
    call site in `try`/`catch` instead of `.catch()`.
  - What it buys: async code reads in source order, and error handling uses the language's own
    construct rather than a method on a chain.

- **The four Promise combinators** — reproduced from the source, with its own notes on when each
  matters:
  | Pattern | Description |
  |---|---|
  | `Promise.resolve(value)` | Convert a value into a resolved promise. |
  | `Promise.reject(error)` | Convert an error into a rejected promise. |
  | `Promise.all(promises)` | Returns a new promise fulfilled with an **array of fulfillment values**, or rejected with **the reason of the first promise that rejects**. |
  | `Promise.race(promises)` | Returns a new promise fulfilled/rejected with the result/error of the **first settled** promise. |
  - **`Promise.all` is especially useful when there is a need to run tasks in parallel.**
  - **`Promise.race` makes it easier to implement things like timeouts for promises.**

## Key Concepts
- **Callback hell** — the pyramid of nesting produced by callback-style composition; the named
  reason callbacks aren't clean.
- **Promisify** — mechanically convert a callback-style function into a promise-returning one
  (`const write = promisify(writeFile)`).
- **`async` function** — a function whose body may `await`; always returns a promise.
- **`await`** — pauses execution of the enclosing async function until the promise settles.
- **`Promise.all`** — fan-out/fan-in; fails fast on the first rejection.
- **`Promise.race`** — first-settled wins; the timeout primitive.
- **Fail-fast semantics** — `Promise.all` rejects with the *first* rejection reason, not a
  collection of them.

## Mental Models
- **Read nesting depth as the cost of callbacks.** The source's `downloadPage` is two levels deep
  for two operations, with the error branch written three times. The promise version is flat and
  writes it once. That ratio is the whole argument.
- **Never hand-write a promise wrapper.** `promisify` exists; hand-rolled `new Promise((res, rej) =>
  ...)` wrappers are where the error path gets dropped.
- **Use `Promise.all` when the tasks are independent, and sequential `await` only when the second
  needs the first.** Two `await`s in a row that don't depend on each other is accidental
  serialization — the most common concurrency mistake this chapter's ladder invites.
- **Think of `Promise.race` as a general "first answer wins", of which timeout is the famous
  case.** Race the real work against a rejecting timer.
- **`async`/`await` gives you back `try`/`catch`/`finally`** — which is why ch09's error rules
  apply unchanged to async code. The same `try { } catch (error) { logger.log(error); }` works.
- **`await` is not a thread.** It pauses the enclosing async function only; the runtime is free
  to continue elsewhere.

## Code Examples

The ladder, rung 1 — callbacks to promises:

```ts
// Bad — callback hell; the error branch is written three times.
function downloadPage(url: string, saveTo: string,
                     callback: (error: Error, content?: string) => void) {
  get(url, (error, response) => {
    if (error) {
      callback(error);
    } else {
      writeFile(saveTo, response.body, (error) => {
        if (error) { callback(error); } else { callback(null, response.body); }
      });
    }
  });
}

// Good — flat, with ONE error path.
import { promisify } from 'util';
const write = promisify(writeFile);

function downloadPage(url: string, saveTo: string): Promise<string> {
  return get(url).then(response => write(saveTo, response));
}

downloadPage('https://en.wikipedia.org/wiki/Robert_Cecil_Martin', 'article.html')
  .then(content => console.log(content))
  .catch(error => console.error(error));
```

Rung 2 — promise chain to `async`/`await`:

```ts
// Bad (by this chapter's standard) — a chain.
function downloadPage(url: string, saveTo: string): Promise<string> {
  return get(url).then(response => write(saveTo, response));
}

// Good — reads in source order; ordinary try/catch.
async function downloadPage(url: string): Promise<string> {
  const response = await get(url);
  return response;
}

// somewhere in an async function
try {
  const content = await downloadPage('https://en.wikipedia.org/wiki/Robert_Cecil_Martin');
  await write('article.html', content);
  console.log(content);
} catch (error) {
  console.error(error);
}
```
- **What it demonstrates**: note that the `Good` version also *narrowed* `downloadPage` — it
  takes `url` only and no longer writes the file. Downloading and saving became two steps at
  the call site. That is ch03's "do one thing" arriving as a side effect of the rewrite, and
  it's the part worth copying.

## Reference Tables

| Need | Use |
|---|---|
| Convert a callback API | `util.promisify`, `pify`, `es6-promisify` |
| Sequential steps, each needing the last | consecutive `await` |
| **Independent** tasks, all results needed | `Promise.all([...])` |
| First answer wins | `Promise.race([...])` |
| Timeout an operation | `Promise.race([work, rejectingTimer])` |
| Lift a plain value into the chain | `Promise.resolve(value)` |
| Lift an error into the chain | `Promise.reject(new Error(...))` — see ch09: **always an `Error`** |
| Handle failure | `try`/`catch` around `await`, or one terminal `.catch()` |

| Rung | Form | Error handling | Verdict |
|---|---|---|---|
| 1 | callbacks | `if (error)` at every level | callback hell; avoid |
| 2 | promise chain | one `.catch()` | flat; acceptable |
| 3 | `async`/`await` | `try`/`catch`/`finally` | **the default** |

## Worked Example
**`Promise.all` vs sequential `await`** — the source states that `Promise.all` is "especially
useful when there is a need to run tasks in parallel," and this is where the `async`/`await`
ladder most often gets misused, so it's worth walking.

Three independent fetches:

```ts
// Accidentally serial — 3 round trips, one after another.
async function loadDashboard(userId: number) {
  const user = await getUser(userId);
  const transactions = await getTransactions(userId);   // doesn't need `user`
  const settings = await getSettings(userId);           // doesn't need either
  return { user, transactions, settings };
}
```

Each `await` pauses the function until that promise settles, so total latency is the **sum** of
the three. Nothing here required it — none of the three calls consumes a previous result.

```ts
// Parallel — 1 round trip's worth of wall clock.
async function loadDashboard(userId: number) {
  const [user, transactions, settings] = await Promise.all([
    getUser(userId),
    getTransactions(userId),
    getSettings(userId),
  ]);
  return { user, transactions, settings };
}
```

Latency is now the **max** of the three, and destructuring names the results (ch02:
destructuring is free naming).

**When the serial version is correct** — a genuine data dependency:

```ts
async function loadUserTransactions(userId: number) {
  const user = await getUser(userId);                 // needed by the next line
  return await getTransactions(user.accountId);       // depends on `user`
}
```

**Why it works**: `Promise.all` starts every promise immediately and settles when all have
fulfilled. The decision rule is mechanical — **does line N consume a value produced by line
N-1? No → they belong in one `Promise.all`.**

**Failure mode — fail-fast, stated in the source's own table**: `Promise.all` rejects with *"the
reason of the first promise that rejects."* You get one error, not three, and the other two
promises are **not cancelled** — they keep running and their results are discarded. If you need
every outcome regardless, `Promise.all` is the wrong combinator (`Promise.allSettled` is the
standard answer, though it is outside this source).

**And the timeout, via `race`:**

```ts
const timeout = (ms: number) => new Promise<never>((_, reject) =>
  setTimeout(() => reject(new Error(`Timed out after ${ms}ms`)), ms));

const content = await Promise.race([downloadPage(url), timeout(5000)]);
```

Note `new Error(...)`, not a string — ch09's rule, and it matters most here because a rejection
reason is exactly what you'll be reading in a log.

## Key Takeaways
1. **Callbacks → promises → `async`/`await`.** `async`/`await` is the default; a promise chain is
   acceptable; callbacks are not.
2. **Promisify, don't hand-wrap**: `util.promisify`, `pify`, `es6-promisify`.
3. The concrete win over callbacks is **one error path instead of one per nesting level**.
4. **`Promise.all` for independent tasks** — but it **fails fast on the first rejection** and
   doesn't cancel the rest.
5. **`Promise.race` for "first settled"**, which is how you build timeouts.
6. Consecutive `await`s that don't depend on each other are **accidental serialization** — the
   most common mistake this style invites.
7. `async`/`await` restores **`try`/`catch`/`finally`**, so ch09's rules apply unchanged.
8. Reject with **`new Error(...)`**, never a string (ch09).

## Connects To
- **Ch 9 (Error Handling)**: directly continues this chapter — always reject with an `Error`,
  never ignore a rejected promise, and the `try`/`catch` form for `await`.
- **Ch 3 (Functions)**: the `async`/`await` rewrite also split downloading from saving — "do one
  thing" showing up as a consequence. Generators there are the sync sibling of async iteration.
- **Ch 4 (Objects and Data Structures)**: `Promise<T>` and `IterableIterator<T>` are the generic
  types this chapter leans on.
- **Ch 5 (Classes)**: the `UserService`/`UserNotifier` examples there are all `async` methods —
  this is the style they're written in.
- **`clean-code-java` ch13 + ch18 (Concurrency I & II)**: far deeper — concurrency defense
  principles, **keep synchronized sections small**, execution models (producer-consumer,
  readers-writers, dining philosophers), the **four conditions for deadlock**, and why
  concurrent bugs don't reproduce. The TS chapter covers *syntax*; that one covers *hazards*.
