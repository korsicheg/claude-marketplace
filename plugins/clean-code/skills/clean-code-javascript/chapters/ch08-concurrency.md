# Chapter 8: Concurrency

## Core Idea
Callbacks nest and obscure; **Promises** (ES2015/ES6) flatten them, and **async/await** (ES2017/ES8) flattens them further — write asynchronous logic imperatively instead of as a chain of functions.

## Frameworks Introduced
- **Use Promises, not callbacks**: "Callbacks aren't clean, and they cause excessive amounts of nesting."
  - When to use: any async API that offers, or can be wrapped into, a promise.
  - How: swap the callback-style module for its promise-returning counterpart (`request` → `request-promise`, `fs` → `fs-extra`), then chain `.then()` and terminate with a single `.catch()`.
  - Why it works: error handling collapses from one `if (err)` per level into one `.catch()` for the whole chain.
- **Async/Await are even cleaner than Promises**: "Promises are a very clean alternative to callbacks, but ES2017/ES8 brings async and await which offer an even cleaner solution."
  - When to use: whenever you can use ES2017/ES8 features — "Use this if you can take advantage of ES2017/ES8 features today!"
  - How: prefix the function with `async`, `await` each promise, and wrap in `try/catch`. "All you need is a function that is prefixed in an `async` keyword, and then you can write your logic imperatively without a `then` chain of functions."
  - Note the progression: the async/await rule's **"Bad"** example is the promise chain that was the previous rule's **"Good"** — this is a ladder, not a pair of alternatives.

## Key Concepts
- **Callback hell / pyramid of doom** — the rightward drift produced by nesting callbacks, each with its own error branch.
- **Promise** — a built-in global type since ES2015/ES6 representing a future value.
- **`.then()` chain** — sequential composition of promises; flat, but still function-per-step.
- **`.catch()`** — one terminal error handler for an entire chain.
- **`async` function** — a function that returns a promise and may `await` inside.
- **`await`** — suspends until a promise settles, yielding its value to a normal variable.
- **Imperative async** — the async/await payoff: async code that reads top-to-bottom like sync code.
- **Promise-returning module** — `request-promise`, `fs-extra`: drop-in replacements that make the migration mechanical.

## Mental Models
- **Think of nesting depth as the metric.** Each callback level adds indentation *and* a duplicate error branch; promises remove the indentation, async/await removes the ceremony.
- **Use "can I read this top to bottom?" as the test.** The async/await version reads as three sequential statements; the callback version reads inside-out.
- **Think of `try/catch` as reclaiming the language.** Once you `await`, ordinary JavaScript error handling works again — no special-case `(err, result)` convention.
- **Think of the three styles as a one-way ladder.** Callbacks → promises → async/await. The guide never suggests climbing back down.

## Anti-patterns
- **Nested callbacks with per-level error branches**: `get(url, (requestErr, response, body) => { if (requestErr) {...} else { writeFile(..., writeErr => { if (writeErr) {...} else {...} }) } })` — two operations, two error branches, three indentation levels.
- **Staying on `.then()` chains when async/await is available**: the guide marks the promise chain explicitly **Bad** relative to async/await.
- **Omitting `.catch()`** on a promise chain: see Ch 9 — an unhandled rejection is as bad as an ignored `catch`.
- **`async` without `try/catch`**: `await` throws on rejection; with no `try/catch` the rejection escapes silently.
- **Forgetting to call the async function**: `getCleanCodeArticle()` must actually be invoked — declaring it does nothing.

## Code Examples
Callbacks → Promises:

```javascript
// Bad
import { get } from "request";
import { writeFile } from "fs";

get(
  "https://en.wikipedia.org/wiki/Robert_Cecil_Martin",
  (requestErr, response, body) => {
    if (requestErr) {
      console.error(requestErr);
    } else {
      writeFile("article.html", body, writeErr => {
        if (writeErr) {
          console.error(writeErr);
        } else {
          console.log("File written");
        }
      });
    }
  }
);

// Good
import { get } from "request-promise";
import { writeFile } from "fs-extra";

get("https://en.wikipedia.org/wiki/Robert_Cecil_Martin")
  .then(body => {
    return writeFile("article.html", body);
  })
  .then(() => {
    console.log("File written");
  })
  .catch(err => {
    console.error(err);
  });
```
- **What it demonstrates**: two nested error branches collapse into one `.catch()`, and the imports change to the promise-returning variants — the migration is largely a dependency swap.

Promises → async/await:

```javascript
import { get } from "request-promise";
import { writeFile } from "fs-extra";

async function getCleanCodeArticle() {
  try {
    const body = await get(
      "https://en.wikipedia.org/wiki/Robert_Cecil_Martin"
    );
    await writeFile("article.html", body);
    console.log("File written");
  } catch (err) {
    console.error(err);
  }
}

getCleanCodeArticle()
```
- **What it demonstrates**: `body` is an ordinary local variable, the two steps are two statements, and error handling is the language's own `try/catch`.

## Reference Tables

The ladder:

| Style | Era | Nesting | Error handling | Verdict |
|---|---|---|---|---|
| Callbacks | pre-ES6 | Grows per operation | One `if (err)` per level | Bad |
| Promises | ES2015/ES6 | Flat chain | One `.catch()` | Good vs callbacks, **Bad** vs async/await |
| async/await | ES2017/ES8 | None — sequential statements | `try/catch` | Best |

Migration map:

| Callback module | Promise-returning replacement |
|---|---|
| `request` | `request-promise` |
| `fs` (`writeFile`) | `fs-extra` |

## Worked Example
The same task — fetch a Wikipedia article and write it to disk — at all three rungs, counting what each one costs.

**Rung 1, callbacks.** Two operations produce: 3 levels of indentation, 2 `if (err)` branches, 2 differently-named error parameters (`requestErr`, `writeErr`), and the success path (`console.log("File written")`) buried at maximum depth. Add a third operation and every number grows again.

**Rung 2, promises.** Indentation is flat. The two error branches merge into one `.catch(err => ...)`. The success path is visible at the same level as everything else. But each step is still a function expression handed to `.then()`, and `body` only exists inside a callback parameter — you cannot use it two steps later without threading it through.

**Rung 3, async/await.** Three statements in a row:

```javascript
const body = await get("https://en.wikipedia.org/wiki/Robert_Cecil_Martin");
await writeFile("article.html", body);
console.log("File written");
```

`body` is a normal `const` in normal scope. Adding a step means adding a line. Error handling is `try/catch`, the same construct used everywhere else in the language.

**The measurable difference across the rungs:**

| | Callbacks | Promises | async/await |
|---|---|---|---|
| Indentation levels | 3 | 1 | 1 |
| Error handlers | 2 | 1 | 1 |
| Cost of a 3rd operation | +1 level, +1 branch | +1 `.then()` | +1 line |
| Is `body` a normal variable? | No | No | Yes |

**The one thing not to skip:** the trailing `getCleanCodeArticle()`. The `async` function declaration does nothing on its own — and because the call is not `await`ed and has no `.catch()`, any error escaping the internal `try/catch` would go unhandled (Ch 9).

## Key Takeaways
1. Callbacks cause excessive nesting — replace them with Promises, a built-in global since ES2015/ES6.
2. Swapping to promise-returning modules (`request-promise`, `fs-extra`) makes most of the migration mechanical.
3. A promise chain replaces N error branches with one `.catch()`.
4. **async/await is cleaner still** — the guide marks the promise chain as the "Bad" side of that comparison.
5. `async` + `await` + `try/catch` lets you write async logic imperatively, with awaited values as ordinary variables.
6. Use async/await if your runtime supports ES2017/ES8 — which today it does.
7. Always attach error handling, and remember to actually invoke the async function.

## Connects To
- **Ch 9 (Error Handling)**: "Don't ignore rejected promises" governs the `.catch()` these chains depend on; logging with `console.log` there is the named anti-pattern.
- **Ch 3 (Functions)**: "Favor functional programming over imperative programming" — note the deliberate tension, since async/await is praised precisely for letting you "write your logic imperatively". The distinction is data transformation (functional) vs control flow (imperative).
- **Ch 7 (Testing)**: flat async code is dramatically easier to test than nested callbacks.
