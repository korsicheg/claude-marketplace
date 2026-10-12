# Chapter 7: Nil Values and Pointers

## Core Idea
"Things break when you try to access methods or properties of a `nil` value" — so avoid returning `nil`, and guard any struct field that can be `nil` behind an **unexported field and a getter** that never returns it. Treat every pointer as an **expansion of a variable's scope**: take and return values when data crosses an ownership boundary, and pass pointers only when the caller stays the sole owner.

## Frameworks Introduced
- **Avoid returning `nil`** — `nil` "corresponds to the value `NULL` in C and is essentially an uninitialised pointer." "It's recommended to avoid returning a `nil` value when possible. This way, the users of our code are less likely to accidentally access `nil` values."
- **Nil-safe getter** — a struct can be "initialised incorrectly," leaving pointer fields `nil`. Make the field unexported and expose a method that initialises it on demand.
  - When to use: an exported struct with a pointer (or other nil-able) field that users may construct with a bare literal (`App{}`).
  - How: `cache *KVCache` plus `func (app *App) Cache() *KVCache` that creates the cache if it is `nil`.
  - The article's hedge: "There are other methods of achieving a similarly safe outcome. However, I believe this is the most straightforward approach."
- **Mutability only when necessary** — "Mutability is a powerful tool, but we should really only ever use it when it's necessary." The author is "by no means an advocate for writing 100% pure functional programs."
- **A pointer parameter expands scope** — *"When passing pointers as an input parameter of a function, we are expanding the scope of the variable whose data is being pointed to."* Worse, "we are expanding the scope to an undefined level. We are *almost* expanding the scope of the variable to the global level."
- **Store a copy, return a value** — a store should take its input by value and keep a pointer to *its own copy*; a getter should return a value, not the stored pointer. "Our store should be the only entity allowed to make changes to its values."
- **Ownership decides** — "there is intrinsically nothing wrong with returning pointers. However, the expanded scope of variables (and the number of owners pointing to those variables) is the most important consideration." A function like `AddName(user *User, name string)` is fine: the caller's scope "remains the same after the function returns" and the caller "remains the sole owner."

## Key Concepts
- **`nil`** — Go's zero value for pointers, interfaces, maps, slices, channels and functions; touching what it "points to" panics.
- **Nil pointer dereference** — `panic: runtime error: invalid memory address or nil pointer dereference`.
- **Incorrectly initialised struct** — a struct literal that leaves required pointer fields `nil`.
- **Nil-safe getter** — an accessor that guarantees a non-`nil` result by initialising lazily.
- **Pointer mutability** — any holder of a pointer can change the pointed-to data.
- **Owner** — a holder of a pointer to some data; more owners, more places a change can come from.
- **Pointer to a copy** — taking a value parameter and storing `&param`, so the store owns the only pointer.
- **Data race** — the article's warning that shared pointers across threads can "cause a panic from a data race," not only corrupt data.

## Mental Models
- **Think of a pointer as a variable whose scope you've handed out.** Before passing or returning one, ask who else will hold it afterwards.
- **Use "who owns this after the call returns?"** If the answer is "the caller, alone," a pointer is fine; if it is "the caller *and* the store," pass a value.
- **Think of a getter that returns a stored pointer as an unguarded setter.**
- **Remember the summary's line**: "Garbage collection only assists with memory management; it does not assist with all of the other complexities associated with pointers."

## Anti-patterns
- **Exported pointer fields** that users must remember to initialise.
- **Storing a caller's pointer** — the caller can change your stored data after the call.
- **Returning a pointer to internal state** — "giving other parts of our application the ability to change our store values."
- **Sharing one pointer across goroutines** without coordination — data corruption, or a data-race panic.

## Code Examples
*Lightly corrected: the article's `insertUser` takes `User` but passes it to `Insert(user *User)`, and its handlers pass an `error` where `http.Error` wants a string.*

The nil-safe getter:

```go
type App struct {
    cache *KVCache
}

func (app *App) Cache() *KVCache {
    if app.cache == nil {
        app.cache = NewKVCache()
    }
    return app.cache
}

func main() {
    app := App{}
    app.Cache().Add("panic", "now") // no panic: the getter initialised the cache
}
```

Before, with an exported field, `app := App{}; app.Cache.Add("panic", "now")` panicked with a nil pointer dereference, because `Cache` "has never been initialised and is therefore a `nil` pointer."

A store that owns its data:

```go
func (store *UserStore) Insert(user User) error {
    if store.userExists(user.ID) {
        return ErrItemAlreadyExists
    }
    store.users[user.ID] = &user
    return nil
}

func (store *UserStore) Get(id int64) (User, error) {
    user, ok := store.users[id]
    if !ok {
        return EmptyUser, ErrUserNotFound
    }
    return *user, nil
}
```
- **What it demonstrates**: `Insert` stores a pointer "to the copied value, whose scope is inside the function"; `Get` follows the article's stated fix — "return a value of `User` rather than returning a pointer."

## Reference Tables

| Situation | Pointer OK? | Why (article's reasoning) |
|---|---|---|
| Mutator where the caller keeps sole ownership (`AddName(user *User, …)`) | ✓ | Scope unchanged after return; one owner |
| Constructor returning a new value (`NewSender() *Sender`) | ✓ | Nothing else holds it yet |
| Store method that keeps its argument (`Insert(user *User)`) | ✗ | Caller and store now share it; scope "almost … global" |
| Getter returning stored state (`Get(id) *User`) | ✗ | Anyone can now change the store's values |
| Same pointer used from several goroutines | ✗ | Data race: corruption or panic |
| Exported pointer field on a struct users construct | ✗ | `App{}` leaves it `nil`; use a nil-safe getter |

## Worked Example
How a password reset in a handler rewrites the database. The store, as first written:

```go
func (store *UserStore) Insert(user *User) error {
    if store.userExists(user.ID) {
        return ErrItemAlreadyExists
    }
    store.users[user.ID] = user
    return nil
}
```

The handler that uses it:

```go
func CreateUser(w http.ResponseWriter, r *http.Request) {
    user, err := parseUserFromRequest(r)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    if err := insertUser(w, user); err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
}

func insertUser(w http.ResponseWriter, user *User) error {
    if err := store.Insert(user); err != nil {
        return err
    }
    user.Password = ""
    return json.NewEncoder(w).Encode(user)
}
```

Clearing the password before encoding the response is "all quite common practice" — we don't want to return the hash. But with an in-memory `map` store, "the change we made to the user's password in the HTTP handler function also affected the object in our store": `parseUserFromRequest` returned a pointer, the store kept that same pointer, and the handler then wrote through it.

**The fix** is to make `Insert` take `User` by value and store `&user` — a pointer to the copy (Code Examples above). That "fixes the immediate problem but might still cause issues further down the line": a `Get` that returns `store.users[id]` hands the stored pointer straight back out. So `Get` returns a `User` value too.

**The transferable lesson**: the bug wasn't the pointer type; it was two owners. Fix ownership at the store's boundary — values in, values out — and the store becomes the only code that can change its data.

## Key Takeaways
1. **Avoid returning `nil`**; return defined values (Ch 6) or guarantee initialisation.
2. **Hide nil-able fields** behind an unexported field and a getter that never returns `nil`.
3. **Use mutability only when it's necessary.**
4. **A pointer parameter widens a variable's scope** — potentially to everyone.
5. **Stores take values and return values**; keep pointers to your own copies.
6. A pointer is fine when the **caller remains the sole owner** and its scope is unchanged after the call.
7. Shared pointers across goroutines risk **data races**, not just bad data.

## Connects To
- **Ch 5**: the unexported-field technique used here for nil safety is the same one used there for immutability; pointers are the scope problem from Ch 5 in another form.
- **Ch 6**: `NullItem` is the return-value side of avoiding `nil`.
- **Ch 9**: embedded interfaces are nil-able and always public, so this chapter's getter cannot protect them.
- **clean-code-java ch07**: the book's rules against returning or passing null, and the Special Case pattern.
- **clean-code-java ch13**: the book's concurrency chapter, for the shared-data hazards this chapter only flags.
