# Chapter 6: Return Values and Errors

## Core Idea
Errors in Go are values, so return ones a caller can **compare against**: exported sentinel variables (`ErrItemNotFound`), checked with `errors.Is`, never error strings matched by hand. Return **defined values** (`NullItem`) rather than fresh zero values. When an error must carry dynamic detail, keep a comparable sentinel inside it.

## Frameworks Introduced
- **No magic strings in errors** — a caller writing `if err.Error() == "item could not be found in the store"` has hard-coded a **magic string**. "Our code is tightly coupled — it relies on that specific magic string and the assumption that it will never change." Change the message and every such check "will break (softly)"; if the package is a library, the *client's* software breaks.
- **Defined errors** — "the fix is very simple": declare the error once as an exported package variable and return it.
  - How: `var ErrItemNotFound = errors.New("item could not be found in the store")`; callers write `errors.Is(err, clean.ErrItemNotFound)`.
  - Why it works: the technique "will achieve all three of those goals" (readability, testability, maintainability) "with very little effort" — and `ErrItemNotFound` reads better than "a novel on why a certain error has been returned."
- **Defined return values** — "This approach is not limited to errors." Return a package-level `NullItem` instead of building `Item{}` at each `return`.
  - Why: a caller that forgets the error check gets a value whose maps, slices, channels and interface fields you have already initialised, instead of `nil`s that panic later — and if you need that safety, "we now only have to change our code in a single place."
  - Caveat, in the article's own words: "In many scenarios, invoking a panic will actually be preferable to indicate that there is an error check missing."
- **Dynamic errors that stay comparable** — `fmt.Errorf("Could not find item with ID: %s", id)` carries detail but can no longer be compared. "There is no well-defined or standard method" (as the article puts it); the author's "personal preference is to return a new interface" — `ErrorDetails`, which formats as an ordinary error but also exposes the sentinel through a `Type()` method.

## Key Concepts
- **Error value** — an `error` is "simply an `interface` that implements a function (`Error()`) returning a string."
- **Magic string** — a hard-coded literal (here an error message) that other code depends on matching exactly.
- **Sentinel error** — an exported package-level error variable (`ErrItemNotFound`) that callers compare against.
- **`errors.Is`** — the standard-library comparison the article's handlers use (Go 1.13+).
- **Defined (null) value** — a package-level value such as `NullItem` returned instead of an ad-hoc zero value.
- **Nil-able field kinds** — interface, channel, map, slice and pointer fields default to `nil` in a zero-valued struct.
- **Dynamic error** — an error whose message embeds runtime data (an ID, a path).
- **`ErrorDetails`** — the author's interface pairing `Error()` with `Type()`, so details travel with a comparable sentinel.

## Mental Models
- **Think of an exported error variable as API, and its message as prose.** Callers depend on the variable; the text can change freely.
- **Use "would a client break if I reworded this?"** as the test for whether an error should be a sentinel.
- **Think of `NullItem` as a contract**: "here is a safe value even if you ignored my error" — and decide case by case whether you'd rather the caller panic.

## Anti-patterns
- **Comparing `err.Error()` to a literal** — couples every caller to your wording.
- **`errors.New(...)` inline at the return site** for an error callers need to recognise.
- **Formatting dynamic data into the only copy of an error** — the detail is gained, comparability lost.
- **Returning struct literals with `nil` map/slice/interface fields** to callers who may not check the error (unless a panic is the signal you want).

## Code Examples
*Lightly corrected: the article's handlers misspell `http.ResponseWriter`, take `http.Request` by value, and call `err.Type()` directly on an `error`, which does not compile. Its interface also declares `Type() string` while the method returns `error`.*

The smelly and the clean store:

```go
package smelly

func (store *Store) GetItem(id string) (Item, error) {
    store.mtx.Lock()
    defer store.mtx.Unlock()

    item, ok := store.items[id]
    if !ok {
        return Item{}, errors.New("item could not be found in the store")
    }
    return item, nil
}
```

```go
package clean

var (
    NullItem = Item{}

    ErrItemNotFound = errors.New("item could not be found in the store")
)

func (store *Store) GetItem(id string) (Item, error) {
    store.mtx.Lock()
    defer store.mtx.Unlock()

    item, ok := store.items[id]
    if !ok {
        return NullItem, ErrItemNotFound
    }
    return item, nil
}
```

The author's dynamic-error type:

```go
type ErrorDetails interface {
    Error() string
    Type() error
}

type errDetails struct {
    errtype error
    details interface{}
}

func NewErrorDetails(err error, details ...interface{}) ErrorDetails {
    return &errDetails{
        errtype: err,
        details: details,
    }
}

func (err *errDetails) Error() string {
    return fmt.Sprintf("%v: %v", err.errtype, err.details)
}

func (err *errDetails) Type() error {
    return err.errtype
}
```

returned as `NewErrorDetails(ErrItemNotFound, fmt.Sprintf("could not find item with id: %s", id))`, and checked by asserting to the interface first:

```go
if details, ok := err.(clean.ErrorDetails); ok && errors.Is(details.Type(), clean.ErrItemNotFound) {
    http.Error(w, err.Error(), http.StatusNotFound)
    return
}
```
- **What it demonstrates**: the error "still works as our standard error" — comparable to `nil`, printable with `.Error()` — while carrying dynamic detail and a sentinel callers can test.
- ⚠ **Dated**: `errors.Is(err, ErrItemNotFound)` will *not* see the sentinel inside `errDetails`, because the type has no `Unwrap()` method. Since Go 1.13 the standard library covers this case directly (`fmt.Errorf` with `%w`, `errors.Is`/`errors.As`); the article mentions neither `%w` nor `errors.As`. See SKILL.md, Scope & Limits.

## Reference Tables

| Caller needs to… | Return | Caller checks with |
|---|---|---|
| know *that* it failed | any `error` | `err != nil` |
| branch on *which* failure | an exported sentinel `ErrX` | `errors.Is(err, pkg.ErrX)` |
| branch *and* see runtime detail | `ErrorDetails` wrapping the sentinel (author's design) | assert to `ErrorDetails`, then compare `Type()` |
| keep working after ignoring the error | a defined `NullX` value | — (or prefer a panic that exposes the missing check) |

## Worked Example
An HTTP handler consuming the store, before and after.

**Before** — the handler matches the message text:

```go
func GetItemHandler(w http.ResponseWriter, r *http.Request) {
    item, err := smelly.GetItem("123")
    if err != nil {
        if err.Error() == "item could not be found in the store" {
            http.Error(w, err.Error(), http.StatusNotFound)
            return
        }
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    json.NewEncoder(w).Encode(item)
}
```

"This is actually not too bad. However, there is one glaring problem": the 404 path depends on a string in another package. Reword the message and this handler quietly starts returning 500s.

**After** — the handler compares against the exported variable:

```go
func GetItemHandler(w http.ResponseWriter, r *http.Request) {
    item, err := clean.GetItem("123")
    if err != nil {
        if errors.Is(err, clean.ErrItemNotFound) {
            http.Error(w, err.Error(), http.StatusNotFound)
            return
        }
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    json.NewEncoder(w).Encode(item)
}
```

The message is now free to change. And because `GetItem` returns `NullItem`, the one place to make that value safer is its declaration:

```go
var NullItem = Item{
    itemMap: map[string]Item{},
}
```

## Key Takeaways
1. **Never make callers match error strings.** Export a sentinel and compare with `errors.Is`.
2. **Declare errors once, at package level**, named `ErrSomething`.
3. **Return defined values** (`NullItem`) so safety can be added in one place — but consider whether a panic would better expose a missing error check.
4. Remember which field kinds default to `nil`: interfaces, channels, maps, slices, pointers.
5. When an error needs dynamic detail, **keep a comparable sentinel inside it** — the article's `ErrorDetails`, or today's `%w` wrapping.

## Connects To
- **Ch 4**: the article's note that helpers should return errors, not `bool`s, is cashed in here.
- **Ch 7**: the `nil` fields that `NullItem` pre-initialises, and why accessing them panics.
- **Ch 9**: `error` is itself an interface — any type with an `Error() string` method satisfies it.
- **clean-code-java ch07**: the book's error-handling chapter — don't return null, Special Case objects (the idea behind `NullItem`), and wrapping third-party errors.
- **clean-code-typescript**: the `Failable<R, E>` result type, a different answer to the same "make failure checkable" problem.
