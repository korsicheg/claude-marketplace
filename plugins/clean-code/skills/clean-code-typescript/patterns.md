# Patterns & Techniques — clean-code-typescript

Every concrete technique in the source, with when / how / trade-offs. Chapter refs in brackets.

## Options Object [Ch 3]
**When**: a signature reaches 3+ parameters.
**How**: one object parameter, named via a `type` alias, destructured in the signature —
`function createMenu({ title, body }: MenuOptions)`.
**Trade-offs**: gains named parameters, visible property use, unused-property warnings, and
cloning of *primitive* values. Destructured **objects and arrays are NOT cloned**. Adds a type
declaration for a one-off shape.

## Default Object — three forms [Ch 3]
**When**: an options object has optional members.
**How**: `Object.assign({ title: 'Foo' }, config)` (**sets**) · `{ title: 'Foo', ...config }`
(**defines**) · `function f({ title = 'Foo' }: Config)` (default visible in signature).
**Trade-offs**: spread and `assign` differ subtly (define vs set). Pair any of them with
**`--strictNullChecks`** so callers can't pass explicit `undefined`/`null`.

## Split on Flag Argument [Ch 3]
**When**: a boolean parameter selects a code path.
**How**: `createFile(name, temp)` → `createTempFile(name)` + `createFile(name)`.
**Trade-offs**: two names to maintain; but each does one thing and the call site self-documents.

## Clone, Don't Mutate [Ch 3]
**When**: a function receives an object or array it would otherwise modify.
**How**: `return [...cart, item]` instead of `cart.push(item)`.
**Trade-offs**: cloning big objects costs performance — the source points at `immutable-js`.
Occasionally you *do* want to mutate the input; the source calls that rare.

## Centralized Side-Effect Service [Ch 3]
**When**: several functions write to the same file/store/global.
**How**: one service owns the effect — "one and only one".
**Trade-offs**: a chokepoint, but a testable and mockable one.

## Subclass Instead of Prototype Extension [Ch 3]
**When**: you want to add a method to a built-in (`Array`, etc.).
**How**: `class MyArray<T> extends Array<T> { diff(...) {} }` — never `Array.prototype.diff = ...`.
**Trade-offs**: your subclass isn't what other code already holds; but prototype writes clash
silently with other libraries and surface as production exceptions.

## Functional Pipeline [Ch 3]
**When**: a loop accumulates or transforms.
**How**: `filter` / `map` / `reduce` — `clients.filter(isActiveClient).forEach(email)`.
**Trade-offs**: names each step and enforces "do one thing"; an extremely hot loop may still
want the imperative form (but see "don't over-optimize").

## Encapsulate Conditional [Ch 3, Ch 11]
**When**: a boolean expression needs a comment to explain it.
**How**: extract to a named predicate — `canActivateService(subscription, account)`. Also the
comment-removal technique: the comment's text becomes the name.
**Trade-offs**: one more function; removes a comment that could drift out of sync.

## Polymorphic Dispatch (replace `switch`) [Ch 3, Ch 6]
**When**: a `switch`/`if` chain branches on a type field.
**How**: `abstract class Airplane` with subclasses overriding `getCruisingAltitude()`.
**Trade-offs**: this is OCP — new variants need zero edits. Costs a class per variant; overkill
for a closed two-case branch.

## Union Type Instead of `instanceof` [Ch 3, Ch 6]
**When**: an `instanceof` chain narrows a parameter.
**How**: `type Vehicle = Bicycle | Car` with one shared operation — `vehicle.move(...)`.
**Trade-offs**: requires a common method to exist; that requirement is usually the real fix.

## Generator / Lazy Stream [Ch 3]
**When**: a collection is used like a stream, or is unbounded.
**How**: `function* fibonacci(): IterableIterator<number> { ... yield a; }`, consumed by `for-of`.
**Trade-offs**: decouples callee from implementation, is lazy, and lets the *consumer* decide how
many items to take. Not indexable or reusable; `itiriri` adds array-like chaining.

## Accessor With Validation [Ch 4]
**When**: an object with behavior has a rule about a field.
**How**: `private accountBalance` + `get balance()` / `set balance(v)` that throws on invalid.
**Trade-offs**: a new rule changes one setter and **no callers**. Ceremony on a plain data bag —
skip it there.

## Parameter Property [Ch 4]
**When**: a constructor just assigns its arguments to fields.
**How**: `constructor(private readonly radius: number) {}`.
**Trade-offs**: declares, assigns, and locks down in one line; slightly less obvious to readers
new to TS.

## Immutability Ladder [Ch 4]
**When**: a value must not change — escalate by scope.
**How**: `readonly prop` (one property) → `Readonly<T>` (whole shape) → `ReadonlyArray<T>` /
`readonly T[]` (no `push`/`fill`) → `as const` (literals, **including returned ones**).
**Trade-offs**: `const array: number[]` still allows `push()`; plain `readonly` does **not**
protect a returned literal — only `as const` does. **All of it is erased at runtime.**

## Split by Field Usage [Ch 5]
**When**: a class's private fields each serve a different method group.
**How**: group methods by which field they touch; each group becomes a class
(`UserManager` → `UserService` + `UserNotifier`).
**Trade-offs**: mechanical and non-guessy. More classes to wire up; removes forced dependencies.

## Composition Over Inheritance [Ch 5]
**When**: you reach for `extends` by instinct.
**How**: hold the other type as a field. Use inheritance only if **all three**: is-a (not has-a),
real code reuse from the base, and you want base changes to propagate.
**Trade-offs**: more delegation; avoids the wrong hierarchy, which is expensive to undo.

## Method Chaining / Fluent Interface [Ch 5]
**When**: multi-step construction or configuration.
**How**: return **`this`** (not the class name) from each mutator; one terminal method (`build()`)
ends the chain.
**Trade-offs**: `this` survives subclassing where a hardcoded class name degrades the chain.
Chaining hides *when* mutation happens — don't share a fluent builder across call sites.

## Abstract Base for OCP [Ch 6]
**When**: a consumer branches on which implementation it holds.
**How**: `abstract class Adapter { abstract request<T>(url): Promise<T> }`; the consumer calls the
abstract method.
**Trade-offs**: adding a variant touches zero existing code. Fixes the hierarchy at design time.

## Abstract Sibling Parent for LSP [Ch 6]
**When**: a subclass overrides methods to keep its own invariant and breaks callers
(Square/Rectangle → 25 instead of 20).
**How**: introduce `abstract class Shape` with the shared *behavior* (`abstract getArea()`), and
make the two peers, each holding its own shape.
**Trade-offs**: you change the hierarchy, not the override. Callers must move to the abstraction.

## Role Interfaces [Ch 6]
**When**: an implementer must `throw new Error('… not supported')`.
**How**: split the fat interface — `Printer` / `Fax` / `Scanner`; classes implement several.
**Trade-offs**: more interfaces, each trivially small; no client depends on what it can't use.

## Constructor Injection (DIP) [Ch 6]
**When**: a class instantiates a concrete collaborator
(`private readonly formatter = new XmlFormatter()`).
**How**: define an `interface` shaped by what the *consumer* needs, take it in the constructor,
let the caller choose. Scale with an IoC container (**InversifyJS**).
**Trade-offs**: reduces coupling and makes the unit testable; each abstraction is indirection to
read through. Invert where the detail genuinely varies, not everywhere.

## Failable Result Type [Ch 9]
**When**: failure is an expected outcome the caller must handle.
**How**: `type Failable<R, E> = { isError: false, value: R } | { isError: true, error: E }`; the
caller must narrow on `isError` to reach `.value`.
**Trade-offs**: failure is in the signature and the compiler enforces handling; `E` is typed and
exhaustible. But it **doesn't propagate** — every layer unwraps and rewraps, and there's no
`stack` unless `E` carries one. Use `throw` for the genuinely exceptional.

## Promisify [Ch 8]
**When**: any callback-style API.
**How**: `const write = promisify(writeFile)` — `util.promisify`, `pify`, or `es6-promisify`.
**Trade-offs**: never hand-roll `new Promise(...)` wrappers; that's where error paths get dropped.

## `Promise.all` Parallelization [Ch 8]
**When**: consecutive `await`s that don't consume each other's results.
**How**: `const [a, b, c] = await Promise.all([f(), g(), h()])`.
**Trade-offs**: latency becomes max instead of sum. **Fails fast** on the first rejection, and
the other promises are **not cancelled** — their results are discarded.

## `Promise.race` Timeout [Ch 8]
**When**: an operation needs a deadline.
**How**: `await Promise.race([work, rejectingTimer])`, rejecting with `new Error(...)`.
**Trade-offs**: the losing promise keeps running; you've bounded the *wait*, not the work.

## Logger Instead of `console.log` [Ch 9]
**When**: any `catch` block or `.catch()` handler.
**How**: `import { logger } from './logging'; logger.log(error)` — **and a code path** for the
failure.
**Trade-offs**: `console.log` gets "lost in a sea of things printed to the console"; an empty
`catch` contradicts the `try` you just wrote.

## Newspaper Ordering [Ch 10]
**When**: a class or module has private helpers.
**How**: public entry point first, each helper directly below its first caller.
**Trade-offs**: no linter does this for you. Breaks down for a helper with several callers — put
it under the first and accept it. Only possible because functions are small (Ch 3).

## Import Grouping + `import type` [Ch 10]
**When**: every file.
**How**: six blank-line-separated groups (polyfills → node builtins → external → internal →
parent → sibling), alphabetized within and across named imports; `import type` for type-only
imports.
**Trade-offs**: mostly automatable by ESLint. `import type` is **erased at runtime**, which is how
it breaks dependency cycles — that's a correctness tool, not a style choice.

## Path Aliases [Ch 10]
**When**: imports contain `../../../`.
**How**: set `baseUrl` and `paths` in `tsconfig.json` → `import { UserService } from '@services/UserService'`.
**Trade-offs**: needs matching config in bundler/test runner. Hides depth — a deep chain often
also means the module is in the wrong place.
