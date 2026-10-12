# Chapter 10: The Empty `interface{}`

## Core Idea
An interface with no methods is satisfied by every type, so `interface{}` lets you write functions that accept anything — and in doing so, use "Go, a statically typed language, as a dynamically typed language." Confine it: keep `interface{}` behind APIs that take and return **concrete types**, as `json.Decode` does for its callers and as a typed wrapper does around a generic store. Written before Go had generics; read it with that in mind.

## Frameworks Introduced
- **`interface{}` is dynamic typing** — "Go determines whether a concrete type implements a particular interface by checking whether the type implements the *methods* of that interface." With no methods, everything qualifies. That is "extremely useful for certain kinds of functions, such as print helpers" (`fmt.Println(v ...interface{})`) and string conversion.
- **Good use: hide it behind a concrete API** — `json.NewDecoder(r.Body).Decode(&item)`: "All the less elegant code is contained within the `Decode` function." Callers never handle reflection or casting; they supply a pointer to a concrete type.
  - Residual risk: valid JSON of the wrong shape decodes without error — "our `item` variable will just be left with the default values" — so you still validate what the client sent.
- **Bad use: a "generic" store** — a `HashMap` over `map[string]interface{}` accepts any value, so callers must type-assert on the way out. Store a `*Item` where callers expect `Item` and the assertion fails at runtime — "Worst of all, this might not even be caught by our tests." Verdict: *"This type of code should never reach production."*
- **The fixes, in order** — "The simplest solution is to just write the functions with concrete types instead of using `interface{}` values." When a package's functionality isn't trivial to reimplement, "create wrappers that expose the functionality we need but still ensure type safety": a typed `ItemCache` around the untyped store, with one function doing the only type assertion.
- **The summary's rule** — *"Hide any code using the empty `interface{}` as much as possible from end users to prevent it from being exposed."*

## Key Concepts
- **Empty interface** — `interface{}` (spelled `any` since Go 1.18); satisfied by every type.
- **Variadic `...interface{}`** — a slice of values of any types, as in `fmt.Println`.
- **Type assertion / cast** — `v.(Item)`; with `, ok` it reports failure instead of panicking.
- **Generic store (pre-generics)** — a container of `interface{}` values; the pattern behind `sync.Map`.
- **Typed wrapper** — a type with concrete-typed methods around an `interface{}`-based dependency.
- **Single cast point** — one function (`interfaceToItem`) holding the only type assertion.
- **Generics (dated)** — the article says "Go does not (yet) support generics" and suggests using another language if you need them; Go 1.18 added type parameters.

## Mental Models
- **Think of each `interface{}` in an exported API as a runtime type check you've pushed onto every caller.**
- **Use the `json.Decode` shape as the model**: untyped machinery inside, a concrete type at the boundary.
- **Think of a typed wrapper as a customs checkpoint**: everything entering the store is already the right type, so nothing leaving it needs inspection.

## Anti-patterns
- **`map[string]interface{}` stores in public APIs** — any type goes in, every caller pays at the way out.
- **Type assertions scattered through callers** — each a potential runtime failure, and the source of indentation hell (Ch 4).
- **Relying on tests to catch wrong-type insertions** — "this might not even be caught by our tests."
- **"Dangerous hacks" in place of real generics** — the article's phrase for leaning on `interface{}` to fake them.

## Code Examples
*Lightly corrected: the article's `Get` returns one value from a two-result function.*

The untyped store and the caller it forces:

```go
type HashMap struct {
    store map[string]interface{}
}

func (hashmap *HashMap) Insert(key string, value interface{}) {
    hashmap.store[key] = value
}

func (hashmap *HashMap) Get(key string) (interface{}, error) {
    value, ok := hashmap.store[key]
    if !ok {
        return nil, ErrKeyNotFoundInHashMap
    }
    return value, nil
}

func SomeFunction(id string) (Item, error) {
    itemIface, err := hashmap.Get(id)
    if err != nil {
        return EmptyItem, err
    }
    item, ok := itemIface.(Item)
    if !ok {
        return EmptyItem, ErrCastingItem
    }
    return item, nil
}
```
- **What it demonstrates**: "At first glance, this looks fine." Nothing stops someone inserting `*Item`; `SomeFunction` then fails at runtime.

## Worked Example
The typed wrapper — the article's fix when you need an `interface{}`-based library but not its looseness:

```go
type ItemCache struct {
    kv tinykv.KV
}

func (cache *ItemCache) Get(id string) (Item, error) {
    value, ok := cache.kv.Get(id)
    if !ok {
        return EmptyItem, ErrItemNotFound
    }
    return interfaceToItem(value)
}

func interfaceToItem(v interface{}) (Item, error) {
    item, ok := v.(Item)
    if !ok {
        return EmptyItem, ErrCouldNotCastItem
    }
    return item, nil
}

func (cache *ItemCache) Put(id string, item Item) error {
    return cache.kv.Put(id, item)
}
```

Walk what changed. `Put` accepts only `Item`, so "it is … no longer possible to accidentally populate our store with a wrong value type." `Get` returns `Item`, so callers never see `interface{}`. The one remaining assertion lives in `interfaceToItem`, and it cannot fail for values that came in through `Put` — "we have restricted our casting of types as much as possible." The article calls it "a very straightforward way of solving our issue, even if somewhat manually."

**Today** (Go 1.18+, not in the article): a type-parameterised container such as `HashMap[K comparable, V any]` gives the same guarantee without the hand-written wrapper. The wrapper remains the right tool around libraries whose APIs still take `any` — the article's own example, `sync.Map`, is one.

## Key Takeaways
1. **`interface{}` turns Go into a dynamically typed language** wherever it appears.
2. **Fine inside a concrete-typed API** (`fmt.Println`, `json.Decode`); never as your package's public contract.
3. **First choice: concrete types.** Second: a **typed wrapper** with a single cast point.
4. Tests won't reliably catch a wrong type in an untyped store; the compiler will catch it in a typed one.
5. The "no generics" framing is **dated** — on Go 1.18+ reach for type parameters before `interface{}`.

## Connects To
- **Ch 4**: indentation hell "is particularly common when working with `interface{}` and using type casting."
- **Ch 4**: the `RMQChannel` wrapper — the same "wrap what you don't control" move applied to signatures.
- **Ch 8**: closures, the article's other workaround for missing generics.
- **Ch 9**: why an interface with no methods is satisfied by everything.
- **clean-code-java ch08**: the book's boundaries chapter — keep a generic third-party container (its example is `Map`) behind your own typed interface.
