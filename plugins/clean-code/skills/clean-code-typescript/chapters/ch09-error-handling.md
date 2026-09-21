# Chapter 9: Error Handling

## Core Idea
**"Thrown errors are a good thing!"** — they mean the runtime caught the problem and told you.
Two rules follow: **always throw/reject an `Error`** (never a string), and **never swallow a
caught error or a rejected promise** — if you wrote the `try`, you must have a plan for the
`catch`.

## Frameworks Introduced

- **Always use `Error` for throwing or rejecting.**
  - The situation: JavaScript *and* TypeScript let you `throw` any object, and a promise can be
    rejected with **any** reason object.
  - The stated reasons to use `Error` anyway:
    1. Your error **might be caught in higher level code with a `catch`** — and it "would be
       very confusing to catch a string message there," making **debugging more painful**.
    2. `Error` is **supported by the `try/catch/finally` syntax**.
    3. **Implicitly all errors have the `stack` property**, "which is very powerful for
       debugging."
  - **The same reason applies to promise rejections**: reject with `Error` types.
  - How: `throw new Error('Not implemented.')`, `Promise.reject(new Error('Not implemented.'))`,
    or — equivalently — `throw` inside an `async function`.

- **The `Failable<R, E>` alternative — errors as return values.** The source offers this as a
  genuine alternative to `throw`: *"not to use the `throw` syntax and instead always return
  custom error objects. TypeScript makes this even easier."*
  - When to use: when failure is an expected outcome the caller must handle, and you want the
    compiler to force them to.
  - How: a **discriminated union** on an `isError` boolean:
    ```ts
    type Result<R>       = { isError: false, value: R };
    type Failure<E>      = { isError: true,  error: E };
    type Failable<R, E>  = Result<R> | Failure<E>;
    ```
  - What it buys: the failure is **in the signature**, so the caller cannot ignore it —
    narrowing on `isError` is the only way to reach `.value`.

- **Don't ignore caught errors.** Doing nothing with a caught error *"doesn't give you the
  ability to ever fix or react to said error."*
  - And `console.log(error)` **isn't much better** — *"often it can get lost in a sea of things
    printed to the console."*
  - **The rule that follows**: *"If you wrap any bit of code in a `try/catch` it means you think
    an error may occur there and therefore you should have a plan, or create a code path, for
    when it occurs."*
  - How: route it to a real logger (`import { logger } from './logging'`), not the console.

- **Don't ignore rejected promises** — *"for the same reason you shouldn't ignore caught errors
  from `try/catch`."* Applies to both `.catch()` handlers and `await` in a `try` block.

## Key Concepts
- **`Error`** — the built-in type that carries `message` and, crucially, **`stack`**.
- **Rejection reason** — whatever a promise rejects with; should be an `Error`.
- **Swallowed error** — a `catch` block that does nothing, or only `console.log`s.
- **`Failable<R, E>`** — the discriminated-union result type; failure as a value, not a throw.
- **Discriminated union** — a union whose members are distinguished by a literal field
  (`isError: false` vs `isError: true`), which TypeScript uses to narrow.
- **Logger** — a real logging facility, as opposed to `console.log`; the source's fix in every
  Good example.

## Mental Models
- **Read a `try/catch` as a declaration of belief.** Writing one asserts "an error may occur
  here." An empty `catch` contradicts the assertion you just made by writing the `try`.
- **`console.log(error)` is not handling; it is hiding.** The stated failure mode is that the
  message gets **lost in a sea of console output** — so it passes review and fails in production.
- **The `stack` property is the reason the `Error` rule is not pedantry.** `throw 'Not
  implemented.'` gives a catcher a bare string with no origin; `throw new Error('Not
  implemented.')` gives them the call site for free.
- **Choose between `throw` and `Failable` by whether failure is exceptional or expected.**
  `throw` for the genuinely unexpected; `Failable<R, E>` when the caller must branch and you want
  the compiler to insist.
- **`Failable` is the `type`-for-unions rule from ch04 doing real work** — it cannot be expressed
  with `interface`.
- **Every rule here applies unchanged to `async`/`await`**, because `await` inside `try` behaves
  like any throwing call. The source shows both forms side by side deliberately.

## Code Examples

Always an `Error`:

```ts
// Bad — a bare string; no stack, confusing to catch upstream.
function calculateTotal(items: Item[]): number {
  throw 'Not implemented.';
}

function get(): Promise<Item[]> {
  return Promise.reject('Not implemented.');
}

// Good
function calculateTotal(items: Item[]): number {
  throw new Error('Not implemented.');
}

function get(): Promise<Item[]> {
  return Promise.reject(new Error('Not implemented.'));
}

// or equivalent to:
async function get(): Promise<Item[]> {
  throw new Error('Not implemented.');
}
```

Don't ignore a caught error:

```ts
// Bad
try { functionThatMightThrow(); } catch (error) { console.log(error); }

// or even worse
try { functionThatMightThrow(); } catch (error) { /* ignore error */ }

// Good
import { logger } from './logging';
try { functionThatMightThrow(); } catch (error) { logger.log(error); }
```

Don't ignore a rejected promise — both forms:

```ts
import { logger } from './logging';

// chain form
getUser()
  .then((user: User) => sendEmail(user.email, 'Welcome!'))
  .catch((error) => { logger.log(error); });

// async/await form
try {
  const user = await getUser();
  await sendEmail(user.email, 'Welcome!');
} catch (error) {
  logger.log(error);
}
```

## Reference Tables

| Situation | Don't | Do |
|---|---|---|
| Signalling a bug / unimplemented path | `throw 'Not implemented.'` | `throw new Error('Not implemented.')` |
| Rejecting a promise | `Promise.reject('...')` | `Promise.reject(new Error('...'))` |
| Rejecting from an async fn | — | `throw new Error('...')` (equivalent) |
| Caught an error | `{}` or `console.log(error)` | `logger.log(error)` + a code path |
| Rejected promise | no `.catch()` | `.catch()` or `try`/`catch` around `await` |
| Failure is an **expected** outcome | `throw` and hope | `Failable<R, E>` in the return type |

**`throw` vs `Failable<R, E>`:**

| | `throw new Error(...)` | `Failable<R, E>` |
|---|---|---|
| Visible in the signature | ✗ | ✓ |
| Caller can ignore it | ✓ (silently) | ✗ (compiler blocks `.value`) |
| Carries a stack trace | ✓ | only if `E` is an `Error` |
| Fits `try/catch/finally` | ✓ | ✗ (it's branching, not catching) |
| Best for | unexpected failure | expected, handleable failure |

## Worked Example
**`Failable<R, E>` end to end** — the source gives the type and the producer; the payoff is at
the consumer, which is where it's worth seeing.

The type and a function that uses it (from the source):

```ts
type Result<R>      = { isError: false, value: R };
type Failure<E>     = { isError: true,  error: E };
type Failable<R, E> = Result<R> | Failure<E>;

function calculateTotal(items: Item[]): Failable<number, 'empty'> {
  if (items.length === 0) {
    return { isError: true, error: 'empty' };
  }

  // ...
  return { isError: false, value: 42 };
}
```

**What the consumer is forced to do.** This does not compile:

```ts
const total = calculateTotal(items);
console.log(total.value * 2);
//                ^^^^^ Property 'value' does not exist on type 'Failable<number, "empty">'.
```

`value` only exists on the `Result<R>` arm, so TypeScript refuses until you discriminate:

```ts
const total = calculateTotal(items);

if (total.isError) {
  logger.log(new Error(`Cannot total: ${total.error}`));   // total.error: 'empty'
  return;
}

console.log(total.value * 2);                              // total.value: number — narrowed
```

**Why it works**: `isError` is a *literal* type (`false` on one arm, `true` on the other), so the
`if` narrows the union and each branch sees only its own fields. The failure isn't documented in
a comment or a JSDoc `@throws` — it's in the type, and the compiler is the reviewer.

Note the error channel is also **typed**: `Failable<number, 'empty'>` says the only failure is
`'empty'`. A caller can exhaustively handle `E`, which a `throw` never permits.

**Trade-off, and why the source calls it an alternative rather than the rule**: `Failable` does
not travel. An `Error` propagates up the stack on its own until someone catches it; a `Failable`
must be unwrapped and re-wrapped at **every** layer it crosses, and each layer's `E` has to
compose with the next. It also has no `stack` unless you put one in `E`. Use it at boundaries
where failure is part of the contract; use `throw` for the genuinely exceptional.

## Key Takeaways
1. **Thrown errors are good** — they are the runtime reporting a real problem, not a nuisance.
2. **Always `new Error(...)`** when throwing or rejecting. A string has no `stack` and confuses
   whoever catches it upstream.
3. `throw` in an `async` function ≡ `Promise.reject(new Error(...))`.
4. **A `try/catch` is a claim that an error may occur** — so an empty `catch` contradicts itself.
5. **`console.log(error)` is not error handling**; it gets lost. Use a real logger *and* a code
   path.
6. **Never leave a promise rejection unhandled** — `.catch()`, or `try`/`catch` around `await`.
7. **`Failable<R, E>`** puts failure in the signature so callers can't ignore it; the cost is
   manual propagation at every layer.
8. All of this applies identically to `async`/`await`, which is why ch08 recommends it.

## Connects To
- **Ch 8 (Concurrency)**: the direct predecessor — `async`/`await` is what makes `try`/`catch`
  available for async code, and `Promise.reject` is covered by the `Error` rule.
- **Ch 4 (Objects and Data Structures)**: `Failable<R, E>` is a union, so it *must* be a `type`,
  not an `interface` — this chapter is the clearest payoff of that rule.
- **Ch 11 (Comments)**: a typed error channel documents the failure mode, which is a comment you
  don't have to write.
- **Ch 6 (SOLID / DIP)**: `import { logger } from './logging'` is a module-level dependency; DIP
  would inject it, which is also what makes error paths testable.
- **`clean-code-java` ch07 (Error Handling)**: much more — **never return null, never pass
  null**, the **Special Case object** pattern, **prefer unchecked exceptions** (checked ones
  violate OCP), **wrap third-party APIs** to collapse their exception types into one of yours,
  *"define the normal flow"*, and the rule that every exception must carry **the operation that
  failed and the failure type**. That last one is the missing piece here: `new Error('Not
  implemented.')` satisfies this chapter but not that one.
