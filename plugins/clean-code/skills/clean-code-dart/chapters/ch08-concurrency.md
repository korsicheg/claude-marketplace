# Chapter 8: Concurrency

## Core Idea
**Use `async`/`await` instead of `then`.** "Using async/await makes your code simpler and easier to understand." Wrap asynchronous work in an `async` function that returns a typed `Future<T>`, and write its steps top to bottom.

*(The thinnest chapter in the source: one rule. The guide's "Concurrency" is Dart's single-threaded asynchrony — `Future`s on the event loop. It says nothing about `Stream`s, isolates, `Future.wait`, or shared state; for concurrency proper, see `clean-code-java`, ch. 13 and Appendix A.)*

## Frameworks Introduced
- **Use async/await instead of then**:
  - When to use: any code that consumes a `Future`.
  - How: put the work in a function marked `async`, give it a `Future<T>` return type, `await` each step, and `return` the result as a plain value.
  - Why it works: the steps read in order, the result is an ordinary variable (`response`), and errors can be handled with the same `try`/`catch` as synchronous code (Ch 9).

## Key Concepts
- **`Future<T>`** — a value of type `T` that will be available later; Dart's equivalent of a JavaScript Promise.
- **`async`** — marks a function whose body may `await`; the function returns a `Future`.
- **`await`** — suspends the `async` function until a `Future` completes and yields its value.
- **`.then(callback)`** — registers a callback for a `Future`'s value; the style this rule replaces.
- **Event loop** — the loop on which each isolate runs its asynchronous callbacks, one at a time; why `Future` code is "concurrent" without being parallel. *(Background; the guide doesn't discuss it.)*

## Mental Models
- **Think of `.then` as a nested function you didn't need.** Each `.then((response) { … })` moves the next step into a callback; `await` keeps it in the function body.
- **Don't mix the two styles in one expression.** The guide's Bad example already `await`s — the result of a `.then` chain. Pick `await` and use it for every step.
- **Name the async unit.** The Good version is a function, `getAlbumTitle()`, with a typed result; the Bad version is an anonymous expression assigned to a variable. Extracting the function is half the improvement.

## Anti-patterns
- **`await` on a `.then` chain** — two styles in one statement.
- **Untyped async results** — the Good version declares `Future<String>`, so callers know what they'll get.
- **Leaving `.then` chains in place when `await` is available** — the guide treats `.then` as the worse option; where you keep one, Ch 9's rule about handling its errors applies.

## Code Examples

```dart
// Bad
final albumTitle = await client
    .get(Uri.parse('https://jsonplaceholder.typicode.com/albums/1'))
    .then((response) {
  // ...
  return title;
});

// Good
Future<String> getAlbumTitle() async {
  final response = await client
      .get(Uri.parse('https://jsonplaceholder.typicode.com/albums/1'));

  // ...

  return title;
}
```
- **What it demonstrates**: the request, the processing and the return each become a statement in an `async` function with a declared `Future<String>` result. (`client.get(Uri)` is `package:http`'s API; the guide doesn't show the import.)

## Reference Tables

| Aspect | `.then` chain | `async`/`await` |
|---|---|---|
| Next step lives in | a callback | the function body |
| Intermediate values | callback parameters | `final` locals |
| Errors handled with | `.onError` / `.catchError` | `try` / `on … catch` |
| Guide's verdict | Bad | Good |

**What the Dart port dropped**: the JavaScript parent's first concurrency rule, "Use Promises, not callbacks". Dart's asynchronous APIs return `Future`s rather than taking completion callbacks, which is presumably why the port starts one rung up the ladder.

## Key Takeaways
1. **`async`/`await` over `.then`** for any `Future`.
2. **Wrap async work in a named function** with a typed `Future<T>` return.
3. **Don't mix `await` and `.then`** in the same expression.
4. Once you `await`, **ordinary `try`/`catch` handles errors** — see Ch 9.
5. The guide covers **`Future`s only**; streams, isolates and parallelism are outside it.

## Connects To
- **Ch 9**: "Don't ignore Future errors" — the error-handling half of this rule, including the case where you keep `.then`.
- **Ch 3**: the dead-code example's `Future<void> newRequest(url)` is the same typed-`Future` habit.
- **`clean-code-java`** ch. 13 (Concurrency) and Appendix A: threads, shared state and the concurrency rules this guide never reaches.
- **`clean-code-javascript` Ch 8**: the two-rule parent chapter (callbacks → Promises → async/await).
