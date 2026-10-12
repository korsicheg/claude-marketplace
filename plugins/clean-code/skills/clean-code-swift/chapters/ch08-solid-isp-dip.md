# Chapter 8: SOLID — Interface Segregation and Dependency Inversion with Protocols

## Core Idea
Swift's **protocols** carry the last two SOLID principles. Split a protocol with many requirements into **small protocols each client actually needs** (ISP), and have high-level types **depend on a protocol injected through `init`**, not on a concrete class they construct (DIP). This is where the adaptation is most Swift-specific — and where its carried-over prose ("duck typing", "implicit contracts") is most wrong.

## Frameworks Introduced
- **Interface Segregation Principle (ISP) with protocols**: "Clients should not be forced to depend on interfaces they do not use." — "Although Swift doesn't adopt the traditional concept of interfaces, we can apply the Interface Segregation Principle (ISP) through protocols."
  - When to use: a protocol whose conformers need only some of its requirements, or that mixes configuration data with behaviour.
  - How: split by role. The guide's `Styling` (three style properties *and* `applyStyles()`) becomes `StyleConfigurable` (the data) and `StyleApplicable` (the behaviour). A plain `struct AppearanceConfig` conforms to the first; the view conforms to the second and **holds** a `StyleConfigurable`.
- **Dependency Inversion Principle (DIP)**: the guide's two statements —
  1. "High-level modules should not depend on low-level modules. Both should depend on abstractions."
  2. "Abstractions should not depend on details. Details should depend on abstractions."
  - Relation to Dependency Injection: "While they are not identical concepts, DIP does not allow high-level modules to know the details of their low-level modules but configures them. This can be achieved through DI."
  - Why: "it reduces coupling between modules. Coupling is a very bad development pattern because it makes your code harder to refactor."
  - How: declare `protocol RequesterProtocol { func requestItem(item: String) }`; `InventoryTracker` stores a `RequesterProtocol` received in `init`; concrete requesters (`InventoryRequesterV1`, `V2`) conform. "Building our dependencies externally and injecting them, we can easily swap our request module for a new fancy one that uses WebSockets."

## Key Concepts
- **Protocol** — a named set of requirements (properties with `{ get }`, methods) that types declare conformance to; Swift's interface.
- **Protocol conformance** — `struct AppearanceConfig: StyleConfigurable`; declared explicitly and checked by the compiler.
- **Protocol-typed property** — `var styleConfig: StyleConfigurable`; holds any conforming value, so the view depends on the abstraction.
- **Segregated protocol** — one role per protocol (`StyleConfigurable` for data, `StyleApplicable` for behaviour).
- **Fat protocol** — a protocol bundling requirements no single client needs in full (`Styling`).
- **High-level / low-level module** — policy (`InventoryTracker`: request every item) vs mechanism (how one request goes out).
- **Initializer injection** — passing a dependency into `init` instead of constructing it inside.
- **Coupling** — how much one module must know about another to work; the guide's reason DIP matters.

## Mental Models
- **Split protocols by who uses them.** Code that *reads* a style needs `StyleConfigurable`; code that *applies* one needs `StyleApplicable`. Neither should carry the other's requirements.
- **Data protocol + value-type conformer.** The guide's segregation lands configuration in a `struct` and behaviour in a `class` — the one place it pairs a protocol with a value type on purpose.
- **"Who calls `init`?" decides DIP.** If `InventoryTracker` writes `InventoryRequester()`, it depends on that class. If its caller passes a `RequesterProtocol`, it depends on the abstraction, and the caller chooses V1, V2 or a WebSocket version.
- **The protocol belongs to the high-level side.** `RequesterProtocol` states exactly what `InventoryTracker` needs (`requestItem(item:)`) and nothing else — details depend on it, not the reverse.

## Code Examples
ISP — data and behaviour in separate protocols:

```swift
// Protocol for styling configuration
protocol StyleConfigurable {
    var font: UIFont { get }
    var backgroundColor: UIColor { get }
    var cornerRadius: CGFloat { get }
}

// Protocol for applying styles
protocol StyleApplicable {
    func applyStyles()
}

// Default implementation for styling configuration
struct AppearanceConfig: StyleConfigurable {
    var font: UIFont
    var backgroundColor: UIColor
    var cornerRadius: CGFloat
}

// View adopting the protocols
class GoodStylableView: StyleApplicable {
    var styleConfig: StyleConfigurable

    init(styleConfig: StyleConfigurable) {
        self.styleConfig = styleConfig
        self.setup()
    }

    func setup() {
        applyStyles()
    }

    func applyStyles() {
        // Apply styles based on configuration
    }
}
```

- **What it demonstrates**: the view no longer has to *be* a style configuration; it *has* one, through a protocol-typed property.

## Reference Tables

| | Bad | Good |
|---|---|---|
| ISP protocol | `Styling`: `font`, `backgroundColor`, `cornerRadius`, `applyStyles()` | `StyleConfigurable` (3 properties) + `StyleApplicable` (1 method) |
| ISP conformer | `BadStylableView: Styling` stores all three properties itself | `AppearanceConfig` struct holds data; `GoodStylableView: StyleApplicable` holds a `StyleConfigurable` |
| DIP dependency | `var requester: InventoryRequester` | `var requester: RequesterProtocol` |
| DIP construction | `self.requester = InventoryRequester()` inside `init` | passed in: `init(items:requester:)` |
| Swapping implementations | edit `InventoryTracker` | pass `InventoryRequesterV2()` |

## Worked Example
Dependency inversion for `InventoryTracker`.

**Bad** — the tracker builds its own requester:

```swift
class InventoryRequester {
  init() {
    self.REQ_METHODS = ["HTTP"]
  }

  func requestItem(item: String) {
    // ...
  }
}

class InventoryTracker {
  var items: [String]
  var requester: InventoryRequester

  init(items: [String]) {
    self.items = items

    // Bad: We created a dependency on a specific request implementation.
    // We should only have requestItems depend on a request method: `request`
    self.requester = InventoryRequester()
  }

  func requestItems() {
    self.items.forEach { item in
      self.requester.requestItem(item: item)
    }
  }
}
```

The high-level policy ("request every item") is welded to one low-level mechanism. Changing transport means editing `InventoryTracker`.

**Good** — the tracker depends on a protocol and receives an implementation:

```swift
class InventoryTracker {
  var items: [String]
  var requester: RequesterProtocol

  init(items: [String], requester: RequesterProtocol) {
    self.items = items
    self.requester = requester
  }

  func requestItems() {
    self.items.forEach { item in
      self.requester.requestItem(item: item)
    }
  }
}

protocol RequesterProtocol {
  func requestItem(item: String)
}

class InventoryRequesterV1: RequesterProtocol {
  func requestItem(item: String) {
    // ...
  }
}

class InventoryRequesterV2: RequesterProtocol {
  func requestItem(item: String) {
    // ...
  }
}

// Building our dependencies externally and injecting them, we can easily
// swap our request module for a new fancy one that uses WebSockets
let inventoryTracker = InventoryTracker(items: ["apples", "bananas"], requester: InventoryRequesterV2())
inventoryTracker.requestItems()
```

Three things moved. The **abstraction** (`RequesterProtocol`) states only what the tracker uses. **Construction** moved to the caller. And **variation** became new conforming types rather than edits. The same seam is where a test would pass a fake requester.

## Source Caveats
- **"Swift doesn't have interfaces, so the abstractions needed are implicit contracts"** and **"where duck typing prevails"** are carried over from the JavaScript original. Swift protocols are explicit, compiler-checked contracts; conformance must be declared. The guide's own Good examples use them exactly that way, which is the lesson to keep.
- **"If you've worked with AngularSwift"** is a find-and-replace artifact of "AngularJS" in the JavaScript original; there is no AngularSwift.
- **ISP usage**: `AppearanceConfig(font: .systemFont(ofSize: 14))` omits `backgroundColor` and `cornerRadius`, which the memberwise initializer requires, so the usage line doesn't compile.
- **"Default implementation"**: the comment labels a struct, not a protocol extension. The guide never shows a protocol extension or a default implementation — Swift's main tool for sharing behaviour across conformers.
- **DIP Bad**: `self.REQ_METHODS = ["HTTP"]` assigns a property `InventoryRequester` never declares.

## Anti-patterns
- **Fat protocols**: conformers must supply requirements they don't use.
- **Mixing configuration and behaviour in one protocol**: `Styling` forces every view to also be a style record.
- **Constructing dependencies inside `init`**: `self.requester = InventoryRequester()` — "We created a dependency on a specific request implementation."
- **Depending on the concrete class**: `var requester: InventoryRequester` closes the door on V2.

## Key Takeaways
1. **Protocols are Swift's interfaces** — explicit and compiler-checked, not duck-typed.
2. **One role per protocol**; clients depend only on the role they use.
3. **Put configuration in a value type conforming to a data protocol**; have behaviour hold it.
4. **Depend on a protocol, receive the implementation through `init`.**
5. **Let the high-level type define the protocol** it needs, and let details conform.
6. **Swapping an implementation should be a change at the call site**, not inside the dependent type.

## Connects To
- **Ch 4**: `travelToTexas(vehicle: Vehicle)` is the same protocol-typed-parameter move at function scale.
- **Ch 6**: `GoodStylableView` holding a `StyleConfigurable` is composition over inheritance through a protocol.
- **Ch 7**: SRP's `UserSettings` still constructs its `UserAuth`; DIP would inject it. A protocol would also make the OCP and LSP examples compile.
- **Ch 9**: testing — the guide doesn't link the two, but an injected protocol is the seam a test double plugs into.
- **`clean-code-java`** (ch11, Systems): separating construction from use — the system-level form of injecting through `init`.
