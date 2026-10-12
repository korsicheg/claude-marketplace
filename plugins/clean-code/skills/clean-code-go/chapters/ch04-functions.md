# Chapter 4: Functions — Length and Signatures

## Core Idea
Make functions as short as possible — "typically 5–8 lines in Go" — not to avoid duplication but to improve **comprehension**. Get there by returning errors early ("push our code to the left"), splitting wherever `value, err :=` repeats, and keeping signatures to **one or two parameters**, with an Options struct (or a wrapper around code you don't own) beyond that.

## Frameworks Introduced
- **Smaller than that** — the article quotes Robert C. Martin: *"How small should a function be? Smaller than that!"*
  - When to use: every function.
  - How: write the function's job as a short list of steps first; the code should read "almost as naturally as our description."
  - Why: "It's important to understand that we don't necessarily do this to avoid code duplication. The more important reason is to improve *code comprehension*."
- **Indentation hell** — "a chain of `if` statements … carelessly nested in a function." It is "particularly common when working with `interface{}` and using type casting."
  - Costs: the flow is hard to follow; it gets "exponentially more difficult to figure out which statement returns what (and to ensure that all paths return some value)"; the reader scrolls and tracks "many logical states in their head"; and there are "so many different nested possibilities" to test.
- **Push the code to the left** — the first fix: "ensure that we are returning an error as soon as possible. Instead of nesting the `if` and `else` statements, we want to 'push our code to the left'." Each check fails fast; the success path runs down the left margin.
- **The `value, err :=` rule of thumb** — *"If the `value, err :=` pattern is repeated more than once in a function, this is an indication that we can split the logic of our code into smaller pieces."*
- **Onion layering** — the refactored code is "layered in an onion-style fashion, where we can ignore 'layers' that we aren't interested in and simply peel back the ones that we do want to examine," reading "maybe 3–5 lines at a time."
- **Lines are not the measure** — "we cannot measure the cleanliness of our code by the number of lines it uses." Cleaning code "will initially expand the existing codebase," and a short version can be "*artificially* short."
- **One or two parameters** — *"Function signatures should only contain one or two input parameters."* Three is acceptable "in certain exceptional cases, … but this is where we should start considering a refactor." (The summary loosens this to "2–3 arguments".)
- **Options struct** — replace a run of positional arguments with a struct whose field names label each value.
  - Fixes: comments standing in for argument names; mislabelled arguments; argument order ("The ordering of the properties also doesn't matter anymore").
  - Bonus: Go zero-initialises struct fields, so callers set only what differs from the default.
- **Wrap what you can't change** — "It's not always possible to change a function's signature." Wrap the third-party call in your own type and method that takes the Options struct.

## Key Concepts
- **Function length (Go)** — typically 5–8 lines in the author's practice.
- **Indentation hell** — deeply nested conditionals, especially chained `, ok` lookups and type assertions.
- **Early return / guard clause** — returning on failure immediately so nesting never builds up.
- **Onion layering** — a public function made of named helpers you can read or skip.
- **Artificially short** — fewer lines bought by cramming, not by clarity.
- **Options struct** — a parameter object (`QueueOptions`) used instead of a long positional signature.
- **Zero-value defaults** — unspecified fields default to `false`, `0`, `""` or `nil`, so the struct doubles as a default-arguments mechanism.
- **Wrapper type** — your own type (`RMQChannel`) embedding a dependency to give it a clean signature.

## Mental Models
- **Think of a function as its own one-line-per-step description.** If the body doesn't read like the list, extract until it does.
- **Use the left margin as the happy path.** Anything indented is an exception being handled and returned.
- **Treat a positional `false` as a question the reader can't answer.** "Try to remember what the fourth and fifth `false` arguments represent. It's impossible, right?"
- **Count comprehension, not lines.** A refactor that adds lines but lets a reader skip whole layers is a win.

## Anti-patterns
- **Nested `if x, ok := …; ok {` ladders**, each `else` returning a different error.
- **The two-line "clean-up"** — collapsing the ladder onto one line; same logic, unreadable.
- **Six-argument calls labelled with comments** — "the comments are actually part of the problem"; drop them and the call becomes `QueueDeclare("hello", false, false, false, false, nil)`.
- **Bool returns in production code** — the article's own note: return errors instead of `bool` so it is clear "where the error is originating from."
- **Unchecked type assertions** — the article's split helpers use `refIface.(string)` without `, ok`, which panics on a wrong type; keep the `, ok` form from the first refactor.

## Code Examples
*Snippets are lightly corrected so they compile; the article's originals contain typos (`return Item, nil`, `[]bytes`, a reversed `if ok`).*

The Options struct, and the call it allows:

```go
type QueueOptions struct {
    Name         string
    Durable      bool
    DeleteOnExit bool
    Exclusive    bool
    NoWait       bool
    Arguments    amqp.Table
}

q, err := ch.QueueDeclare(QueueOptions{
    Name: "hello",
})
```

Wrapping a signature you don't own:

```go
type RMQChannel struct {
    channel *amqp.Channel
}

func (rmqch *RMQChannel) QueueDeclare(opts QueueOptions) (amqp.Queue, error) {
    return rmqch.channel.QueueDeclare(
        opts.Name,
        opts.Durable,
        opts.DeleteOnExit,
        opts.Exclusive,
        opts.NoWait,
        opts.Arguments,
    )
}
```
- **What it demonstrates**: callers get named, order-free, defaulted parameters "without actually having to change any of the code in the RabbitMQ library."

## Reference Tables

| Threshold | Value | Source wording |
|---|---|---|
| Function length | **5–8 lines** (typical in Go) | "By writing short functions (which are typically 5–8 lines in Go)" |
| Parameters | **1–2**; 3 exceptionally | "Function signatures should only contain one or two input parameters" |
| `value, err :=` per function | **1** | "repeated more than once … split the logic" |
| Lines read at a time after layering | **3–5** | "we only have to read maybe 3–5 lines at a time" |

| Smell | Fix |
|---|---|
| Nested `if … ok` chain | Early returns; push left |
| `value, err :=` twice | Extract a helper per step |
| Comments labelling arguments | Options struct |
| Third-party long signature | Wrapper type + Options struct |

## Worked Example
`GetItem` from indentation hell to onion layers. The job, as the article first writes it:

```
fn GetItem:
    - parse json input for order id
    - get user from context
    - check user has appropriate role
    - get order from database
```

and the short version that reads like it:

```go
var (
    NullItem                  = Item{}
    ErrInsufficientPrivileges = errors.New("user does not have sufficient privileges")
)

func GetItem(ctx context.Context, json []byte) (Item, error) {
    order, err := NewItemFromJSON(json)
    if err != nil {
        return NullItem, err
    }
    if !GetUserFromContext(ctx).IsAdmin() {
        return NullItem, ErrInsufficientPrivileges
    }
    return db.GetItem(order.ItemID)
}
```

The cache-backed `GetItem` starts five levels deep: two map lookups and two type assertions, each `if … ok {` nesting the next, each `else` returning a different error. **Step 1, push left** — every check returns early, so nothing nests:

```go
func GetItem(extension string) (Item, error) {
    refIface, ok := db.ReferenceCache.Get(extension)
    if !ok {
        return EmptyItem, errors.New("reference not found in cache")
    }

    ref, ok := refIface.(string)
    if !ok {
        // return cast error on reference
    }

    itemIface, ok := db.ItemCache.Get(ref)
    if !ok {
        // return no item found in cache by reference
    }

    item, ok := itemIface.(Item)
    if !ok {
        // return cast error on item interface
    }

    if !item.Active {
        // return no item active
    }

    return item, nil
}
```

**Step 2, split on the repeated lookup pattern** — each step becomes a helper, and `GetItem` keeps "just two branching paths":

```go
func GetItem(extension string) (Item, error) {
    ref, ok := getReference(extension)
    if !ok {
        return EmptyItem, ErrReferenceNotFound
    }
    return getItemByReference(ref)
}

func getReference(extension string) (string, bool) {
    refIface, ok := db.ReferenceCache.Get(extension)
    if !ok {
        return "", false
    }
    return refIface.(string), true
}

func getItemByReference(reference string) (Item, error) {
    item, ok := getItemFromCache(reference)
    if !ok || !item.Active {
        return EmptyItem, ErrItemNotFound
    }
    return item, nil
}

func getItemFromCache(reference string) (Item, bool) {
    itemIface, ok := db.ItemCache.Get(reference)
    if !ok {
        return EmptyItem, false
    }
    return itemIface.(Item), true
}
```

The result has more lines than the original. That is the point: "cleaning the `GetItem` function resulted in more lines of code overall. However, the code itself is now much easier to read." For production, the article would go one step further and return errors rather than `bool`s from the helpers (Ch 6).

## Key Takeaways
1. **Aim for 5–8 line functions** — for comprehension, not deduplication.
2. **Return early.** Push the code to the left; the happy path never indents.
3. **`value, err :=` more than once means split.**
4. **Clean code can be longer.** Judge by what a reader can skip, not by line count.
5. **One or two parameters**; at three, reach for an **Options struct** and let zero values supply defaults.
6. **Wrap third-party signatures** you can't change rather than living with them at every call site.
7. Prefer **errors over `bool`s** from helpers in production code.

## Connects To
- **Ch 2**: argument-label comments are a symptom of the signature problem solved here.
- **Ch 5**: small functions are also what removes long-lived mutable variables.
- **Ch 6**: the sentinel errors (`ErrItemNotFound`) these helpers return.
- **Ch 10**: indentation hell's usual cause — `interface{}` values that must be type-asserted.
- **clean-code-java ch03**: the book's functions chapter (do one thing, one level of abstraction, argument counts, flag arguments, Command Query Separation), which this chapter's thresholds compress.
- **clean-code-java ch08**: the book's boundaries chapter — the general case of the `RMQChannel` wrapper.
