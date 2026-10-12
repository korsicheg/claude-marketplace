# Patterns & Techniques — clean-code-swift

Concrete refactorings from the guide, each with its trigger and cost.

## Drop the Type Tag
**When to use**: a name encodes its type (`currentDateStr`).
**How**: name the meaning (`currentDate`); the declaration and the compiler hold the type.
**Trade-offs**: none, but pick a noun that can't be mistaken for another type. (Ch 2)

## Bind a Literal to a Named Constant
**When to use**: any literal whose meaning isn't obvious (`86400000`).
**How**: `let millisecondsPerDay = 86400000`, lowerCamelCase as the snippet writes it.
**Trade-offs**: none; searchable and changed in one place. (Ch 2)

## Bind, Then Name the Parts
**When to use**: an optional result read by index or force-unwrapped (`match(regex)![1]`).
**How**: `if let match = …` then `let city = …`, `let zipCode = …`.
**Trade-offs**: a few more lines; removes a crash path and names every part. (Ch 2)

## Bundle Arguments into a Struct
**When to use**: three or more parameters.
**How**: a `struct` of `let`s (`MenuViewData`) passed as one argument; use the free memberwise initializer at the call site.
**Trade-offs**: one more type to name; immutable and reusable. (Ch 3)

## Non-Optional Parameter with a Default
**When to use**: `name: String?` followed by `name ?? "fallback"`.
**How**: `breweryName: String = "Hipster Brew Co."`.
**Trade-offs**: callers can no longer pass `nil` deliberately; usually that's the point. (Ch 3)

## Extract the Predicate, Then Pipe
**When to use**: a loop that looks up, filters and acts.
**How**: name the test (`isActiveClient(client:)`); write `clients.filter { … }.forEach { … }`.
**Trade-offs**: more functions; each testable alone. (Ch 3)

## Split a Flag into Two Functions
**When to use**: a `Bool` parameter selecting a path.
**How**: `createFile(name:temporary:)` → `createTemporaryFile(name:)` + `createPermanentFile(name:)`.
**Trade-offs**: two names to maintain; each reads correctly at the call site. (Ch 3)

## Deduplicate with an Enum
**When to use**: near-identical functions differing per kind (`showDeveloper`/`showManager`).
**How**: one function taking an `enum`; per-case data in a computed property with an exhaustive `switch`.
**Trade-offs**: check that output doesn't change (`developer` vs `Developer`); adding a case is a compile error until handled — a feature. (Ch 3)

## Return a Value Instead of Writing a Global
**When to use**: a function mutates a top-level `var`.
**How**: take the input as a parameter; return the result, as a labelled tuple if there are several (`-> (firstName: String, lastName: String)`); handle edge cases with `guard`.
**Trade-offs**: the caller holds the result. (Ch 4)

## Return a New Collection
**When to use**: a function appends to a shared collection.
**How**: `func addItemToCart(cart: [CartItem], item: CartItem) -> [CartItem]` — copy, modify, return.
**Trade-offs**: Swift arrays are values with copy-on-write, so the copy is cheap until modified; large class-based models cost more (the guide points to apple/swift-collections). (Ch 4)

## Centralize a Side Effect
**When to use**: several functions or types write the same file or resource.
**How**: "Have one service that does it. One and only one."
**Trade-offs**: one indirection; one place to audit and change. (Ch 4)

## Keep Generic Names Off Shared Types
**When to use**: tempted to add `diff` (or similar) to `Array`.
**How**: don't extend a widely shared type with a generically named member another library may also add.
**Trade-offs**: the guide's own alternative (subclassing `Array`) doesn't compile; see Ch 4's caveats. (Ch 4)

## Map and Reduce Instead of Accumulating
**When to use**: `var total = 0; for x in xs { total += … }`.
**How**: `let total = xs.map { $0.value }.reduce(0, +)`.
**Trade-offs**: none for simple folds; `let` replaces `var`. (Ch 4)

## Name the Condition, Positively
**When to use**: a compound or negated `if`.
**How**: `shouldShowSpinner(fsm:listNode:)`; `isViewPresent` instead of `!isViewNotPresent`.
**Trade-offs**: one more function; the call site reads as intent. (Ch 4)

## Replace a Type Switch with Polymorphism
**When to use**: `switch self.type { case "777": … }` inside a class.
**How**: one subclass per case, each implementing the method (`Boeing777.getCruisingAltitude()`); declare the method on the base type so callers can use it.
**Trade-offs**: more types; no silent `default` for unknown kinds. (Ch 4)

## Accept a Protocol, Not `Any`
**When to use**: a parameter typed `Any` followed by `as?` branches.
**How**: `travelToTexas(vehicle: Vehicle)` calling one method every conformer provides.
**Trade-offs**: conformers must share one API ("consistent APIs"). (Ch 4)

## Return a New Instance (Pure Object)
**When to use**: other code mutates your object's state (`SpaceStation` refuelling a `Spaceship`).
**How**: `func refuel(amount: Int) -> Spaceship`.
**Trade-offs**: callers must use the returned value; nothing mid-use changes underneath them. (Ch 5)

## Replace String Codes with Enum Cases
**When to use**: `engine.type == "v8"`, `fsm.state == "fetching"`.
**How**: `enum Engine { case v8 }`; compare `car.engine == .v8`.
**Trade-offs**: the set of kinds becomes closed and compiler-checked. (Ch 5)

## Validate Behind a Computed Property
**When to use**: public stored properties with invariants (`age >= 0`).
**How**: `private var _age` plus `var age { get set }` whose setter checks `newValue`; call sites keep writing `user.age`.
**Trade-offs**: the guide's setter only prints on rejection — make the failure visible (Ch 9). (Ch 5)

## Chain by Returning `self`
**When to use**: several configuration calls in a row on a class.
**How**: mutators return `self`; keep stored properties `private`; mark methods whose result is often unused `@discardableResult`.
**Trade-offs**: fluency doesn't validate; on a struct, `self` is a copy. (Ch 6)

## Hold, Don't Inherit
**When to use**: a subclass that fails "is-a" (`EmployeeTaxData: Employee`).
**How**: a standalone type held as a property, optional if it may be absent (`taxData: EmployeeTaxData?`).
**Trade-offs**: one more property; no nonsense initializers. (Ch 6)

## Extract a Responsibility into a Collaborator
**When to use**: a class with two reasons to change (`UserSettings` with identity checks).
**How**: move the second concern to its own class (`UserAuth`) held as a property.
**Trade-offs**: two types; each changes for one reason. Inject it (DIP) rather than construct it. (Ch 7)

## One Method per Adapter
**When to use**: a dispatcher comparing `adapter.name` strings.
**How**: every adapter implements `request(url:)`; the dispatcher calls it.
**Trade-offs**: the base type or protocol must declare `request(url:)`. (Ch 7)

## Siblings, Immutably Constructed
**When to use**: a subtype overriding setters to keep an invariant (Square/Rectangle).
**How**: make both subtypes of a common `Shape`; set dimensions in `init`; declare `getArea()` on `Shape`.
**Trade-offs**: no in-place resizing; correctness through the base type. (Ch 7)

## Split a Fat Protocol by Role
**When to use**: conformers forced to supply requirements they don't use.
**How**: a data protocol (`StyleConfigurable`) and a behaviour protocol (`StyleApplicable`); a struct conforms to the data one; the view holds it.
**Trade-offs**: more protocol names. (Ch 8)

## Inject a Protocol Through `init`
**When to use**: a type constructs its own dependency.
**How**: declare the protocol the type needs (`RequesterProtocol`); store it; receive the implementation in `init`.
**Trade-offs**: the caller wires dependencies; implementations swap at the call site. (Ch 8)

## One Test Method per Concept
**When to use**: a test method with several unrelated assertions.
**How**: one `XCTestCase` method per behaviour, named for it.
**Trade-offs**: more methods; failures name the broken behaviour. (Ch 9)

## Await Instead of Nesting
**When to use**: completion-handler networking.
**How**: `func load() async`; `let (data, _) = try await URLSession.shared.data(from: url)` in one `do` block.
**Trade-offs**: needs Swift 5.5 and a `Task` to start from synchronous code. (Ch 9)

## Give Every `catch` a Plan
**When to use**: `catch { print(error) }`.
**How**: notify the user, report to an error service, or both — or let the error propagate.
**Trade-offs**: real code for the failure path. (Ch 9)

## Delegate Formatting to SwiftLint
**When to use**: whitespace arguments in review.
**How**: follow the Google Swift Style Guide; enforce with SwiftLint.
**Trade-offs**: one-time configuration; set the line length explicitly (the source says 80). (Ch 10)

## Replace a What-Comment
**When to use**: a comment restating the next line.
**How**: delete it, or extract a well-named function; keep only *why* comments (the Gauss formula).
**Trade-offs**: none. (Ch 11)
