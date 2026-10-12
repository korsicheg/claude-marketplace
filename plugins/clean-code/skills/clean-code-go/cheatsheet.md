# Cheatsheet — clean-code-go

## Thresholds & defaults
| Thing | Rule |
|---|---|
| Function length | **5–8 lines** "typically" in Go — "Smaller than that!" |
| Parameters | **1–2**; 3 only "in certain exceptional cases" (summary: "2–3") |
| `value, err :=` per function | **1** — repeated → split |
| Nesting | **push left**: return the error early, happy path on the margin |
| Mutable package-level variables | **0** |
| Non-doc comments | only **why**, never how |
| Error strings compared by callers | **0** — export `ErrX`, compare with `errors.Is` |
| `nil` returned to callers | avoid "when possible" |
| Interface methods | "as few … as possible" |
| `interface{}` in an exported API | **0** — hide it |
| Formatting | whatever `gofmt` says |

## Decision rules
- **Naming a function?** Higher in the call tree → shorter and broader (`Parse`). Deeper → more specific (`parseJSON`, `fileExtension`). Keep the verb.
- **Naming a variable?** Wider scope → more specific (`beerBrands`). A few lines of scope → short (`b`, `s`). Never its type.
- **Writing a comment?** Exported identifier → doc comment, high level. Otherwise: does it explain *why*? No → delete. Yes → could a name say it? Yes → rename and delete.
- **Third parameter?** Options struct; let zero values be the defaults. Can't change the signature (third-party)? Wrap it.
- **Variable assigned in a branch with `:=`?** Shadowing risk → extract a function that returns the value.
- **Caller must branch on a failure?** Exported sentinel `ErrX`. Needs runtime detail too? Keep the sentinel inside (author: `ErrorDetails`; modern Go: `%w`).
- **Returning an "empty" value?** A defined `NullX` with nil-able fields initialised — unless a panic better exposes a missing error check.
- **Struct field that can be `nil`?** Unexported field + getter that initialises it.
- **Pointer parameter?** Will the callee keep it, or will anyone else hold it after the call? → take a value (store `&copy`). Caller stays sole owner → pointer is fine.
- **Getter on a store?** Return a value, not the stored pointer.
- **Caller supplies the operation?** Simple → closure (factory if arities differ). Complex → interface.
- **Proving `T` implements `I`?** `var _ I = &T{}`. Never by embedding `I` in `T`.
- **Sharing fields across types?** Embed a struct, built by one constructor.
- **Function inputs and outputs?** Accept interfaces, return concrete types.
- **Need "any type"?** Concrete types first → typed wrapper with one cast point → (Go 1.18+, not in the article) type parameters.

## Escalation ladders (best last)
- **Nesting**: nested `if … ok` → early returns → one helper per step ("onion" layers)
- **Signature**: 6 positional args + label comments → Options struct → Options struct with zero-value defaults → wrapper type for code you don't own
- **Comment**: tutorial comment → why-comment → expressive names, no comment
- **Declaration**: top-of-function `var` → declare at use → immediately invoked literal → named constructor → unexported field behind methods
- **Errors**: `err.Error() == "…"` → sentinel + `errors.Is` → sentinel inside a detail-carrying error
- **Operations**: operation `switch` → function-typed parameter → closure factory → interface when complex
- **"Generic" store**: `interface{}` in the API → typed wrapper, single cast point

## Tells & smells
| If you see… | You're probably… | Go to |
|---|---|---|
| a comment explaining a `for` loop | writing a tutorial comment | Ch 2 |
| `DetermineFileExtensionAndParseConfigurationFile` | naming "too specific too soon" | Ch 3 |
| `b`, `bl` at function scope, `beerBrandBeerName` in the inner loop | inverting the variable gradient | Ch 3 |
| `if x, ok := …; ok {` nested four deep | in indentation hell | Ch 4 |
| `value, err :=` twice in one function | doing more than one thing | Ch 4 |
| `false, // durable` at a call site | needing an Options struct | Ch 4 |
| `var val string` then `val, err :=` in a `case` | shadowing a wide variable | Ch 5 |
| a block of `var` declarations at the top | declaring far from use | Ch 5 |
| `err.Error() == "…"` | coupled to a magic string | Ch 6 |
| `fmt.Errorf("… %s", id)` the caller must branch on | losing comparability | Ch 6 |
| an exported pointer field (`Cache *KVCache`) | one `App{}` away from a nil panic | Ch 7 |
| a store keeping a caller's pointer, or returning its own | leaking scope — aliasing, data races | Ch 7 |
| an operation `switch` that keeps growing | needing a function parameter | Ch 8 |
| `type T struct { io.Writer }` | claiming an interface with a nil method | Ch 9 |
| a method overriding one method of an embedded interface | expecting inheritance Go doesn't have | Ch 9 |
| `map[string]interface{}` in a public type | using Go as a dynamically typed language | Ch 10 |

## Judgment calls the article leaves open
- **Helpful comments** on genuinely complex logic are acceptable — "one might argue that the comment is *helpful* and therefore necessary."
- **Panic vs `NullItem`**: "In many scenarios, invoking a panic will actually be preferable."
- **Closure vs interface**: "the right choice is whichever one solves the problem at hand."
- **Breaking the rules**: "There's certainly room for you to step outside the rules" — just never by accident.
