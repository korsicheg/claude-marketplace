# Patterns & Techniques — clean-code-go

Concrete refactorings from the article, each with its trigger and cost.

## Run gofmt, Stop Debating
**When to use**: any disagreement about layout or formatting.
**How**: format with `gofmt` and accept its output, even where you'd choose otherwise.
**Trade-offs**: lose personal style; gain "homogeneous code," which the author values above "complete expressive freedom." (Ch 1)

## Test, Pass, Refactor, Repeat
**When to use**: all development, and every refactoring in this skill.
**How**: write or run a test; make it pass; refactor; repeat.
**Trade-offs**: slower first draft; refactors stop changing behaviour silently. Pushes you toward small functions. (Ch 1)

## Replace a Comment with Names
**When to use**: a comment that narrates what the next lines do.
**How**: delete tutorial comments; if a "why" comment really states an action, rename the variable and function to say it (`i` → `workerID`, `doSomething` → `instantiateThread`), then delete the comment.
**Trade-offs**: names get longer; prose-to-code mapping disappears. Keep doc comments on exported identifiers. (Ch 2)

## Name Functions by Altitude
**When to use**: naming an entry point and its helpers.
**How**: short and broad at the top (`Parse`), more specific per layer (`parseJSON`, `fileExtension`), each name readable on its own and keeping its verb.
**Trade-offs**: none; avoids names that try to cover the whole call tree. (Ch 3)

## Scale Variable Names with Scope
**When to use**: every variable.
**How**: specific names for wide scopes (`beerBrands`), short ones for tiny scopes (`b`, `s`); never name after the type.
**Trade-offs**: short names become wrong if the scope later grows — rename when it does. (Ch 3)

## Push Code to the Left
**When to use**: nested `if … ok` / `if err == nil` chains.
**How**: invert each condition and return immediately on failure; the success path runs unindented.
**Trade-offs**: more `return` statements; every path's result becomes obvious. (Ch 4)

## Split on Repeated `value, err :=`
**When to use**: the pattern appears more than once in a function.
**How**: extract one helper per step; the public function keeps only the top-level branches ("onion" layers).
**Trade-offs**: more lines and functions in total; each reads in 3–5 lines and tests in isolation. Return errors, not `bool`s, from the helpers in production. (Ch 4)

## Options Struct
**When to use**: three or more parameters, or any positional `bool`s.
**How**: define `XOptions` with named fields; callers set only what differs, relying on zero values for defaults.
**Trade-offs**: one more type; removes argument-label comments and order mistakes. (Ch 4)

## Wrap a Signature You Don't Own
**When to use**: a third-party function with a bad signature.
**How**: a type holding the dependency (`RMQChannel{channel *amqp.Channel}`) with a method taking your Options struct and forwarding the call.
**Trade-offs**: a thin layer to maintain; callers never see the long signature. (Ch 4)

## Extract to Remove Shadowing
**When to use**: a wide-scoped `var` later assigned in an inner block — especially with `:=`.
**How**: move the branch into a function that returns the value; assign once at the call site.
**Trade-offs**: one more function; the wide mutable variable — and the shadowing bug — disappear. (Ch 5)

## Return a New Value Instead of Mutating
**When to use**: a variable that goes through several modifications.
**How**: each stage becomes a function returning the next value (`getStringResult` → `getVal`).
**Trade-offs**: more function boundaries; mutable scope stays minimal. (Ch 5)

## Declare at Use, then Name the Constructor
**When to use**: C-style declaration blocks; variables whose setup logic is far away.
**How**: declare where first used; tie setup to the declaration with an immediately invoked literal; then move that literal into `NewX()`.
**Trade-offs**: none significant; each variable's role is clear where it appears. (Ch 5)

## Unexported Field Behind Methods
**When to use**: a non-primitive value that must not be changed from outside the package (Go has no `const struct`).
**How**: a struct with an unexported field, a `NewX()` constructor, and methods for the allowed operations (`Sender.Send`).
**Trade-offs**: "a little verbose"; buys public immutability and a free hand to change the implementation. (Ch 5)

## Sentinel Error Variables
**When to use**: any error a caller may branch on.
**How**: `var ErrItemNotFound = errors.New("…")` at package level; return it; callers use `errors.Is`.
**Trade-offs**: the variable becomes public API; the message can change freely. (Ch 6)

## Defined Null Value
**When to use**: returning an "empty" value alongside an error.
**How**: a package-level `NullItem` with maps, slices and other nil-able fields initialised; return it instead of `Item{}`.
**Trade-offs**: hides a missing error check that a panic would expose — the article notes a panic is often preferable. (Ch 6)

## Detail-Carrying Error with a Sentinel Inside
**When to use**: an error needs runtime detail (an ID) and must stay comparable.
**How (article)**: an `ErrorDetails` interface with `Error()` and `Type() error`; construct with `NewErrorDetails(ErrItemNotFound, details)`. Callers assert to `ErrorDetails` and compare `Type()`.
**Trade-offs**: custom, non-standard; invisible to `errors.Is` without an `Unwrap` method. Modern Go's `%w` wrapping does the same job (not in the article). (Ch 6)

## Nil-Safe Getter
**When to use**: an exported struct with a pointer field users may leave `nil` (`App{}`).
**How**: unexport the field; add a method that initialises it if `nil` and returns it.
**Trade-offs**: callers write `app.Cache()` instead of `app.Cache`; no nil panic. Not safe for concurrent first use as written. (Ch 7)

## Values In, Values Out at a Store
**When to use**: a type that stores data passed in by callers.
**How**: take the argument by value and store `&arg` (a pointer to the copy); return values, not stored pointers.
**Trade-offs**: copying cost; the store becomes the only code that can change its data. Pointer parameters remain fine when the caller stays sole owner. (Ch 7)

## Closure Factory
**When to use**: a method with an operation `switch`, or a function-typed parameter whose signature is messy.
**How**: `Do(operation func([]byte) ([]byte, error))`; each operation is built by a factory (`concat(data)`) that captures its own inputs.
**Trade-offs**: unfamiliar at first; decouples operations from `Do`. Switch to an interface when the logic grows complex. (Ch 8)

## Compile-Time Interface Assertion
**When to use**: a type meant to satisfy an interface.
**How**: `var _ io.Writer = &NullWriter{}` next to the type; one line per interface.
**Trade-offs**: none — the compiler enforces the contract; never embed the interface instead. (Ch 9)

## Shared Fields via an Embedded Struct
**When to use**: several types need the same fields and behaviour (`Metadata` in `Document` and `AudioFile`).
**How**: embed the struct; build it with one constructor (`NewMetadata`); add shared methods on it.
**Trade-offs**: composition, not inheritance — no overriding semantics. One change point for every embedding type. (Ch 9)

## Accept Interfaces, Return Concrete Types
**When to use**: every function signature with a dependency.
**How**: parameters typed as small interfaces (`io.Writer`); return the concrete type (`*Pipe`). In tests, pass a do-nothing implementation (`NullWriter`, or `io.Discard`).
**Trade-offs**: none notable; mocks become a few lines. (Ch 9)

## Typed Wrapper over `interface{}`
**When to use**: you need a library whose API takes and returns `interface{}`.
**How**: a wrapper with concrete-typed methods (`ItemCache.Get/Put`) and one cast function (`interfaceToItem`).
**Trade-offs**: manual, per-type code; wrong types can't get in. On Go 1.18+ consider type parameters for your own containers. (Ch 10)
