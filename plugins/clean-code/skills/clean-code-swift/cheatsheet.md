# Cheatsheet — clean-code-swift

## Thresholds & defaults
| Thing | Rule |
|---|---|
| Function arguments | **≤2**, "avoid three whenever possible"; at 3+ use a `struct` parameter object |
| Things a function does | **1** — if the description needs "and", split |
| Abstraction levels per function | **1** |
| `Bool` flag parameters | **0** |
| Reasons for a class to change | **1** |
| Force unwraps on fallible results | **0** — bind with `if let` / `guard let` |
| Optional parameter + `??` fallback | **0** — non-optional with a default |
| Writers per file or resource | **1** service, "one and only one" |
| Test concepts per test method | **1** |
| Test coverage | aim for **100%** statements and branches |
| Line length | **80** per the source (its cited Google guide uses 100; SwiftLint warns at 120) |
| Indentation | spaces, consistently |
| Commented-out code | **0** |

## The root decision
**Does this function do one thing?** Everything else is a detector:

- 3+ arguments → no · `Bool` mode parameter → no · writes a global → no
- mixes parsing with persistence → no · `switch` on a type string → no · name needs "and" → no

## Which Swift construct?
```
Bundling 3+ arguments                  → struct with let properties (memberwise init)
Fallback for a missing argument        → default value in the signature, parameter non-optional
A closed set of kinds ("v8", "fat")    → enum; compare with .case
Per-kind behaviour on a closed set     → computed property with an exhaustive switch inside the enum
Per-kind behaviour on an open set      → polymorphism: a subtype or conformer per kind
Several return values                  → labelled tuple, e.g. (firstName:, lastName:)
"Has-a, maybe"                         → optional stored property
An abstraction to depend on            → protocol, injected through init
Validation on assignment               → private backing store + computed property get/set
```

## Mutate or return?
```
Is the state global or shared by reference (a top-level var, a class instance)?
├─ Yes → return a new value; centralize any effect that must remain
└─ No (a local value-type copy)
   └─ Mutating your own local copy is fine — Swift arrays copy on write
Do other objects change yours while it's in use?
└─ Yes → make the change return a new instance (refuel(amount:) -> Spaceship)
```

## Inherit or compose?
All three must hold to inherit — otherwise hold a property:
1. "is-a", not "has-a"
2. you reuse base-class code
3. you want base-wide changes to reach every subtype

## SOLID in this guide's Swift
| Principle | Smell | Move |
|---|---|---|
| SRP | class changes for two reasons | extract a collaborator, hold it |
| OCP | `if adapter.name == "…"` | each type implements `request(url:)` |
| LSP | subtype overrides setters to keep an invariant | siblings under a common base; set dimensions in `init` |
| ISP | conformers stub requirements they don't need | one protocol per role |
| DIP | `self.requester = InventoryRequester()` in `init` | depend on a protocol; inject it |

## Errors and async
- `do`/`catch` means "I expect this to fail" → **have a plan**: notify, report, or rethrow. `print` is "not much better" than nothing.
- Completion handler → `func f() async` + `try await` in one `do` block; start it with `Task { }`.
- `async` goes **after** the parameter list.

## Tells & smells
| If you see… | You're probably… | Go to |
|---|---|---|
| `!` on a regex match or lookup | one bad input from a crash | Ch 2 |
| `name: String?` then `?? "default"` | hiding a default argument | Ch 3 |
| `temporary: Bool` | merging two functions | Ch 3 |
| a top-level `var` written inside a function | hiding a side effect | Ch 4 |
| `extension Array { func diff… }` in a library | risking a name collision | Ch 4 |
| `vehicle: Any` + `as?` | dodging a protocol | Ch 4 |
| `switch` on a string with `default: return 0` | missing polymorphism or an enum | Ch 4, Ch 5 |
| `!isViewNotPresent(…)` | writing a double negative | Ch 4 |
| `== "v8"` | missing an enum | Ch 5 |
| a setter that only `print`s on bad input | silently dropping writes | Ch 5, Ch 9 |
| `class Child: Parent` that fails "is-a" | inheriting to borrow fields | Ch 6 |
| an override that changes what a setter means | breaking substitutability | Ch 7 |
| `ProtocolX` conformers with empty methods | a fat protocol | Ch 8 |
| `SomeConcreteType()` inside another type's `init` | missing injection | Ch 8 |
| `catch { print(error) }` | ignoring the error | Ch 9 |
| `// Initialize the total` | a what-comment | Ch 11 |

## Read the source critically
- Prose saying Swift "does not have types", is "duck typed", or passes arrays "by reference" is **JavaScript carryover**; follow the Swift in the Good snippet instead.
- Several Good snippets **don't compile** as written (`ExtendedArray: Array`, `Shape` without `getArea()`, `async func`). Copy the shape; let the compiler check it.
