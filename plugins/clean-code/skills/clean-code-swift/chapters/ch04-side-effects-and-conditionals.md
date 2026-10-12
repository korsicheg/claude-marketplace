# Chapter 4: Side Effects, Shared Types and Conditionals

## Core Idea
The second half of the guide's Functions section: **take values in and return values out**, centralize the side effects you can't avoid, don't bolt generically named members onto types other code shares, prefer `map`/`filter`/`reduce` to accumulator loops, and replace conditionals and runtime type checks with names, polymorphism and protocol-typed parameters. Then delete what nobody calls.

## Frameworks Introduced
- **Avoid side effects (part 1)**: "A function produces a side effect if it does something other than taking an input value and returning another value(s)… writing to a file, modifying a global variable, or accidentally transferring all your money to a stranger."
  - How: return a value instead of writing a global. When an effect is genuinely needed, centralize it: "Don't have multiple functions and classes that write to a particular file. Have one service that does it. One and only one."
  - The pitfalls it names: "sharing state between objects with no structure, using mutable data types that can be written to by anything, and not centralizing where your side effects occur."
- **Avoid side effects (part 2) — return a new collection, don't mutate a shared one**: the shopping-cart story (Worked Example). "A great solution would be for the `addItemToCart` function to always clone the `cart` array, edit it, and then return its clone."
  - Two caveats the guide grants: mutating an input is sometimes right, "but… these cases are quite rare"; and copying large structures can be expensive, mitigated by libraries such as apple/swift-collections.
- **Do not write to global functions** (don't extend shared types carelessly): adding `diff` to `Array` "could collide with another library that tried to do the same thing", and the user of your API "would have no idea until they got an exception thrown in production."
- **Favor functional programming over imperative programming**: "Swift is not a functional language in the same way Haskell is, but it has a touch of functional in it… Favor this type of programming when you can."
  - How: `var total = 0; for … { total += … }` → `let totalOutput = programmerOutput.map { $0.linesOfCode }.reduce(0, +)`.
- **Encapsulate conditionals**: `if fsm.state == "fetching" && isEmpty(listNode)` → `if shouldShowSpinner(fsm:listNode:)`.
- **Avoid negations in conditionals**: `if !isViewNotPresent(view:)` → `if isViewPresent(view:)`.
- **Avoid conditionals**: "When you have classes and functions that have `if` statements, you're telling your user that your function does more than one thing." Use polymorphism: one subclass per case (`Boeing777`, `AirForceOne`, `Cessna`), each with its own `getCruisingAltitude()`.
- **Avoid type checking (part 1)**: `func travelToTexas(vehicle: Any)` with `as? Bicycle` / `as? Car` branches → `func travelToTexas(vehicle: Vehicle)` calling one method, `move(currentLocation:newLocation:)`. "The first thing to consider is consistent APIs."
- **Avoid type checking (part 2)**: "the false 'type safety' you get doesn't compensate for the loss of readability. Keep your Swift clean, write good tests, and have good code reviews."
- **Remove dead code**: "Dead code is as bad as duplicate code… If it's not being called, get rid of it. It will still be safe in your version history if you ever need it."

## Key Concepts
- **Side effect** — anything besides returning a value: a file write, a global mutation, a network call.
- **Single effect owner** — the "one and only one" service allowed to perform a given effect.
- **Value semantics** — every Swift `struct` and `enum`, including `Array`, `Dictionary` and `String`, is copied on assignment (the standard collections lazily, via copy-on-write); a class instance is shared by reference.
- **Labelled tuple return** — `-> (firstName: String, lastName: String)`; the guide's way to return several values without a global.
- **`guard`** — early exit when a precondition fails (`guard components.count >= 2 else { return … }`).
- **Extension** — adds members to an existing type, including types you don't own (`extension Array`).
- **Predicate function** — a named `Bool` function standing in for a compound condition (`shouldShowSpinner`).
- **Polymorphism** — each type supplies its own implementation of one method, so callers needn't branch.
- **`Any` / `as?`** — the escape hatch from static typing and the conditional downcast that follows it; the guide's Bad type-checking examples.
- **Dead code** — a declaration nothing calls (`oldRequestModule`).

## Mental Models
- **Ask "what else changed?"** after any call. If the answer isn't "nothing; I got a value back", the function has a side effect — make it explicit or move it to the one service that owns it.
- **`let` is the default; `var` is a decision.** The functional rewrite turns `var totalOutput` into `let totalOutput`; the pure-cart rewrite keeps its only `var` local.
- **Extending a type you don't own puts a name in a namespace you share.** Every module that imports yours sees your `Array.diff`.
- **A string-typed `switch` with a `default` is the conditional this chapter removes; an exhaustive `switch` inside an enum is the one the guide keeps.** Compare `Airplane.getCruisingAltitude()` (switch on `self.type` strings, `default: return 0`) with `Role.description` in Ch 3 (switch on `self`, no default). The first fails silently for an unknown string; the second won't compile until every case is handled.
- **Accept the protocol, not `Any`.** Part 1's Good example is the Swift answer to both type-checking rules.

## Code Examples
Side effects, part 1 — return values instead of rewriting a global:

```swift
func splitIntoFirstAndLastName(name: String) -> (firstName: String, lastName: String) {
  let components = name.split(separator: " ").map { String($0) }
  guard components.count >= 2 else {
    return (firstName: name, lastName: "")
  }
  let firstName = components[0]
  let lastName = components[1..<components.count].joined(separator: " ")
  return (firstName: firstName, lastName: lastName)
}

let fullName = "Matheus Gois"
let nameComponents = splitIntoFirstAndLastName(name: fullName)
```

- **What it demonstrates**: the input is untouched, the two results come back as a labelled tuple, and `guard` handles the one-word edge case up front.

Functional over imperative:

```swift
let totalOutput = programmerOutput
  .map { $0.linesOfCode }
  .reduce(0, +)
```

Avoid type checking, part 1:

```swift
func travelToTexas(vehicle: Vehicle) {
  vehicle.move(currentLocation: self.currentLocation, newLocation: Location("texas"))
}
```

## Reference Tables

| Smell | Swift signal | Fix the guide gives |
|---|---|---|
| Hidden effect | function mutates a top-level `var` | take a value, return a value |
| Shared mutable collection | `func addItemToCart(item:)` appends to a global `cart` | `addItemToCart(cart:item:) -> [CartItem]` |
| Collision-prone extension | `extension Array { func diff… }` | keep generic names off shared types |
| Accumulator loop | `var total = 0; for … { total += … }` | `map` + `reduce(0, +)` |
| Opaque condition | `fsm.state == "fetching" && isEmpty(listNode)` | `shouldShowSpinner(fsm:listNode:)` |
| Double negative | `!isViewNotPresent(view:)` | `isViewPresent(view:)` |
| Type switch | `switch self.type { case "777": … }` | a subclass per case |
| Runtime downcasts | `vehicle: Any` + `as? Bicycle` | `vehicle: Vehicle` |
| Unused code | `oldRequestModule` beside `newRequestModule` | delete it; git keeps it |

## Worked Example
The shopping-cart bug from "Avoid side effects (part 2)", reconstructed.

The user taps **Buy**; `purchase` sends the `cart` to the server. The connection is poor, so `purchase` retries. Meanwhile the user accidentally taps **Add to Cart** on something they didn't want. The retry goes out with the unwanted item, because `addItemToCart` changed the very `cart` the retry reads.

**Bad**:

```swift
var cart = [
  CartItem(item: "Widget", date: Date()),
  CartItem(item: "Gadget", date: Date())
]

func addItemToCart(item: CartItem) {
  cart.append(item)
}
```

**Good** — take the cart in, give a new cart back:

```swift
func addItemToCart(cart: [CartItem], item: CartItem) -> [CartItem] {
  var updatedCart = cart
  updatedCart.append(item)
  return updatedCart
}
```

**The Swift reading.** The guide explains the bug with "objects/arrays are passed by reference", which is JavaScript's model, not Swift's. A Swift `Array` is a **value**: `var updatedCart = cart` is already the clone, and copy-on-write makes it cheap until the `append`. What actually causes the bug in the Bad version is that `cart` is a **global `var`** any function can mutate — and in real Swift code the same bug appears when the cart is a **class instance** shared between the purchase flow and the UI. The Good version fixes both: no global, and the caller decides which cart value the retry sends. The guide's caveat about copying cost matters less for `Array` than it suggests, and more for large class-based models.

## Source Caveats
- **Side effects part 1**: the Bad example's body (`split(…).joined(separator: " ")`) leaves the string unchanged, so it shows the *shape* of a global mutation, not a visible bug; and the Good example's comments `// 'Ryan'`, `// 'McDermott'` are leftovers from the JavaScript original — the output is "Matheus" and "Gois".
- **Global functions**: the Good example, `class ExtendedArray<Element>: Array<Element>`, does not compile — `Array` is a struct and can't be subclassed — and both versions' `Set(comparisonArray)` needs `Element: Hashable`. The prose mentions `Array.prototype`, a JavaScript construct. The concern itself is real in Swift: two imported modules that both add `diff` to `Array` make the call ambiguous.
- **Avoid conditionals**: `Airplane` declares no `getCruisingAltitude()`, so code holding an `Airplane` can't call it, and the subclasses would need `override` if it did. The pattern needs the method declared on the base (or a protocol requirement).
- **Type checking part 2** is carried over almost verbatim: "Swift does not have types" (part 1) and "consider using TypeScript… an excellent alternative to regular Swift" (part 2) describe JavaScript. Its Good example, `String(describing: val1) + String(describing: val2)`, also changes behaviour: `combine(val1: 2, val2: 3)` returns `"23"`, not `"5"`. Apply part 1's lesson instead.

## Anti-patterns
- **Mutating a top-level `var` from a function**: invisible coupling between every caller.
- **Several writers for one file or resource**: there should be "one and only one".
- **Unstructured shared state**: "mutable data types that can be written to by anything."
- **Generic names on shared types** (`Array.diff`): collisions show up in someone else's build.
- **Accumulator loops** where `map`/`filter`/`reduce` say it directly.
- **Negative predicates** (`isViewNotPresent`): every caller writes `!isViewNotPresent`.
- **Stringly-typed `switch` with `default`**: unknown values fall through silently.
- **`Any` parameters with `as?` ladders**: the compiler can no longer help.
- **Keeping old code "just in case"**: version history already does.

## Key Takeaways
1. **Take values, return values.** Return a labelled tuple rather than writing a global.
2. **Centralize effects** — one owner per file, resource or service.
3. **Return a new collection** instead of mutating a shared one; in Swift the copy is cheap until it's modified.
4. **Keep generically named members off shared types** like `Array`.
5. **Prefer `map`/`filter`/`reduce`** and `let` over loops and `var`.
6. **Name compound conditions; state them positively.**
7. **Replace type switches with polymorphism, and `Any` with a protocol-typed parameter.**
8. **Delete dead code.**

## Connects To
- **Ch 3**: the first half of the Functions section; "do one thing" is the reason behind "avoid conditionals".
- **Ch 5**: "Use pure objects" applies "return a new value" to types (`refuel(amount:) -> Spaceship`), and enums replace the string comparisons left in `shouldShowSpinner`.
- **Ch 7 (OCP)**: the `HttpRequester` refactor is "avoid conditionals" applied to string-dispatched adapters.
- **Ch 8 (ISP/DIP)**: protocols are the abstraction behind `vehicle: Vehicle`.
- **`clean-code-javascript`**: the original "avoid side effects (part 2)", "don't write to global functions" and "avoid type-checking (part 2)", which explain the carryovers flagged above.
