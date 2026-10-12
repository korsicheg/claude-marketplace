# Chapter 5: Objects and Data Structures

## Core Idea
Objects that **don't share mutable state** are easier to trust; decisions should be made on **typed values (enums), not strings**; and state should change only **through accessors that can validate it**. This is the source's own section — it replaces the JavaScript original's closure-privacy material with Swift's `enum` and `private`.

## Frameworks Introduced
- **Use pure objects**: "Objects are said to be pure when they don't share state with other objects." The guide's three-tier spaceship (Worked Example):
  1. **Impure** — `addFuel(fuel:)` mutates `fuelTank` in place.
  2. **Less pure** — a `SpaceStation` reaches into the ship to refuel it (`spaceStation.refuel(ship: self)`).
  3. **Pure** — `refuel(amount:) -> Spaceship` returns a new ship.
  - Why: "They are easier to test and understand. They cannot be changed by other systems while they are being used. Data passed to them can be trusted, and they have no side effects that can cause difficult-to-trace bugs."
- **Make decisions based on an object**: `if car.engine.type == "v8"` → `enum Engine { case v8 }` and `if car.engine == .v8`.
  - When to use: any comparison against a string or integer code that stands for a kind of thing.
  - How: model the kinds as enum cases; compare against cases. The compiler now checks the spelling.
- **Use getters and setters**: the guide's "unordered list of reasons":
  - "When you want to do more than get a property of an object, you don't have to search and change all the accessors in your code."
  - "Makes it easier to do validation when setting."
  - "Encapsulates the internal representation."
  - "Easier to add logging and error handling when getting and setting."
  - "You can use lazy loading on your object's properties, for example, fetching it from a server."
  - How, in the guide's Swift: a `private var _name` backing store plus a public computed `var name { get set }` whose setter validates.

## Key Concepts
- **Pure object** — one that shares no mutable state with other objects; its "changes" produce new instances.
- **Impure object** — one whose state other systems can change while it's in use.
- **Enum case comparison** — `car.engine == .v8`; the implicit member expression `.v8` is inferred from the property's type.
- **Stringly-typed decision** — branching on a string (`"v8"`, `"fat"`) that the compiler can't check.
- **Backing store** — a `private` stored property (`_name`) behind a public computed property.
- **Computed property with `get`/`set`** — Swift's built-in getter/setter syntax; callers still write `user.name`.
- **`private`** — Swift access control limiting a member to its enclosing declaration (and same-file extensions).
- **Encapsulation** — hiding representation so it can change without touching callers.

## Mental Models
- **Ask "who else can change this while I'm using it?"** If the answer is "anything holding a reference", the object is impure.
- **A string that stands for a kind is an enum waiting to be declared.** Engines, tires, states, roles (Ch 3) — if the set is closed, make it a type.
- **Computed properties keep the call site stable.** Because Swift's getter/setter is a property, you can add validation later without changing `user.name = …` anywhere — the guide's first reason, which Swift gives you for free.

## Code Examples
Decisions on an object:

```swift
enum Engine {
  case v8
}

enum Tire {
  case fat
}

if car.engine == .v8 {
  // ...
}

if bike.tires == .fat {
  // ...
}
```

- **What it demonstrates**: a typo in `"v8"` compiles and silently fails; a typo in `.v8` doesn't compile.

Getters and setters, the guide's Good version (setter half):

```swift
class User {
    private var _name: String
    private var _age: Int

    init(name: String, age: Int) {
        self._name = name
        self._age = age
    }

    var name: String {
        get {
            return _name
        }
        set {
            if newValue.isEmpty {
                print("Name cannot be empty.")
            } else {
                _name = newValue
            }
        }
    }
    // `age` follows the same pattern, rejecting negative values.
}
```

## Reference Tables

| Tier | Spaceship code | Who can change the fuel? |
|---|---|---|
| Impure | `func addFuel(fuel: Int) { self.fuelTank += fuel }` | the ship, from anywhere |
| Less pure | `func visitSpaceStation(spaceStation:)` → station calls `ship.addFuel(…)` | the ship *and* any station |
| Pure | `func refuel(amount: Int) -> Spaceship { Spaceship(fuelTank: fuelTank + amount) }` | nobody; you get a new ship |

## Worked Example
The spaceship, walked through the three tiers.

**Impure** — the ship mutates its own tank, and any code holding the ship can call `addFuel`:

```swift
class Spaceship {
  var fuelTank: Int

  init(fuelTank: Int) {
    self.fuelTank = fuelTank
  }

  func launch() {
    Rocket().ignite(boosters: self.fuelTank)
  }

  func addFuel(fuel: Int) {
    self.fuelTank += fuel
  }
}
```

**Less pure** — refuelling moves to another object that reaches in and changes the ship (`spaceStation.refuel(ship: self)` → `ship.addFuel(fuel: self.fuelTank)`). Now two types can change the tank, and a launch can read a value a station is in the middle of changing.

**Pure** — refuelling returns a new ship:

```swift
func refuel(amount: Int) -> Spaceship {
  return Spaceship(fuelTank: self.fuelTank + amount)
}
```

The caller decides whether the refuelled ship replaces the old one. Nothing that already holds the old ship sees its tank change mid-use.

**The Swift reading.** The guide writes all three tiers as `class`es and keeps `var fuelTank` even in the pure tier, so purity is a convention the compiler can't see. The source uses `struct` elsewhere for plain data (`MenuViewData` in Ch 3, `AppearanceConfig` in Ch 8) but never ties the two together or discusses when to choose a value type; that choice is outside its scope.

## Source Caveats
- **Pure objects**: in the less-pure tier, `Spaceship` no longer declares `addFuel(fuel:)`, which `SpaceStation.refuel(ship:)` calls, and `SpaceStation` has no initializer for `fuelTank`.
- **Getters and setters**: the Good example's usage comments still say "No validation, name can be empty", copied from the Bad one; the setter now rejects those values. And it rejects them by `print`ing and silently keeping the old value — the very handling the guide's own error-handling rule calls "not much better" than nothing (Ch 9).
- The `_name` backing-store pattern is the guide's only encapsulation technique; it doesn't cover Swift's lighter options such as `private(set)` or property observers (`didSet`).

## Anti-patterns
- **Shared mutable objects passed around and modified in place**: "difficult-to-trace bugs."
- **Other objects mutating yours** (`SpaceStation` refuelling a `Spaceship`): the less-pure tier.
- **Branching on strings that name kinds** (`engine.type == "v8"`): typos compile.
- **Public stored properties with invariants** (`user.age = -5`): *Lack of Validation*, *Uncontrolled Access*, *No Encapsulation*, *Inconsistent State Management*, *Difficult to Add Logic* — the guide's five labels.
- **Validation that only prints**: the invalid write is dropped and the caller never knows.

## Key Takeaways
1. **Prefer objects that return new values over objects others mutate.**
2. **Never let another type reach in and change your state.**
3. **Model closed sets of kinds as enums**; compare against cases, not strings.
4. **Route state changes through accessors that validate** — Swift computed properties keep the call site unchanged.
5. **Make invalid states unrepresentable or loudly rejected**, not silently printed.

## Connects To
- **Ch 3**: `enum Role` is the same enum-over-strings move, used there to remove duplication.
- **Ch 4**: "return a new value" is side-effects part 2 applied to a type; `fsm.state == "fetching"` there is the string comparison this chapter replaces.
- **Ch 6**: method chaining puts `private` state behind mutators that return `self`.
- **Ch 9**: "Don't ignore caught errors" is the standard the `print`-and-ignore setter falls short of.
- **`clean-code-java`** (ch06, Objects and Data Structures): the data/object anti-symmetry and the Law of Demeter, which this section doesn't cover.
