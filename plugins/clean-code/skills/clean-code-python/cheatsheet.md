# Cheatsheet — clean-code-python

## Thresholds & defaults
| Thing | Rule |
|---|---|
| Function arguments | **≤2 ideally**, "ideally less than three"; at 3+ bundle into a typed object |
| Responsibilities per class | **1 reason to change** |
| Abstraction levels per function | **1** |
| Boolean parameters | **0** |
| Things a function does | **1** — if you need "and", split |
| Magic literals | **0** — hoist to `UPPER_SNAKE` module constants, keep the arithmetic |
| Type in a name | **0** — annotate instead |
| Methods in a duck-typed seam | as few as the dependency requires (often **1**) |
| Python floor | 3.7+ (`TypedDict` needs 3.8+) |

## The root decision
**Does this function do one thing?** Everything else is a detector:

- 3+ arguments → no · boolean parameter → no · vague verb (`handle`, `process`) → no
- mixes orchestration with mechanics → no · uses `global` → no · name needs "and" → no

## Pick a parameter object
```
Need immutability + unpacking?      → NamedTuple
Need mutation, repr, equality?      → @dataclass  (astuple() to unpack)
Want dict access, on 3.8+?          → TypedDict   (⚠ all keys required)
Want a bare dict?                   → No. "Java-esque": bundles but forfeits type checking
```

## Deduplicate, or leave it?
```
Must both copies always change together, for the same reason?
├─ Yes → deduplicate; one place to update
└─ No / unsure
   ├─ Would the merge need a flag or a role branch?
   │  └─ Yes → ABANDON. "Bad abstractions can be worse than duplicate code"
   ├─ Is the difference invisible to this code?
   │  └─ Yes → generalize the type; keep the distinction in call-site names
   └─ Only one example so far → wait; you can't see the axis of variation yet
```

## Subtype safety — is it still an LSP-compatible override?
| Change to the override | Verdict | mypy catches it |
|---|---|---|
| Add **required** param · remove param · narrow param type · widen return | ✗ breaks | **yes** |
| Add **optional** param · widen param type · narrow return | ✓ safe | — |
| Same signature, violated invariant · new exception raised | ✗ breaks | **no — review** |

**Rule**: an override needing more data puts it in **state**, never in the **signature**. Satisfies LSP and OCP at once.

## Choose an extension mechanism (OCP)
```
Variation is a value            → class attribute      (content_type = "text/html")
Variation is a step in a flow   → hook method          (render_body())
Reusable across unrelated types → mixin                (inherit object, place FIRST, never instantiate alone)
Variation is the whole workflow → you're modifying, not extending — rethink
```
Overriding is fine **only** when the method was designed to be overridden.

## Interface too fat? (ISP)
```
`Can't instantiate abstract class X with abstract method y`
   → shared state → carrier base (DataCarrier)
   → each capability → its own ABC (Loadable, Saveable)
   → implementers inherit only what they use
   → consumers annotate the NARROWEST sufficient ABC
Never: a stub / NotImplementedError to satisfy an ABC.
Never: design an interface for a feature you haven't built.
```

## Tells & smells
| If you see… | You're probably… | Go to |
|---|---|---|
| `seek(0)`/`read()`/`truncate()` around a library call | accommodating a concrete class instead of its abstraction | Ch 8 |
| a nested helper existing only to extract results | choosing the wrong abstraction | Ch 8 |
| `global` in a function body | breaking idempotence *and* the declared type | Ch 3 |
| `() -> None` that changes behaviour | hiding a side effect — ask "what if I call it twice?" | Ch 3 |
| `# type: ignore` on an override | converting a build failure into a runtime `TypeError` | Ch 6 |
| a method that only raises `NotImplementedError` | paying for a fat interface; breaking substitutability invisibly | Ch 7, Ch 6 |
| `matches[1]`, `matches[2]` | one group-insertion away from a silent bug | Ch 2 |
| two classes differing only in name | duplication from a distinction the code never reads | Ch 9 |
| `car.car_color` | repeating context; read the name at its access site | Ch 2 |
| a class name with "and", or `Manager`/`Handler` | holding two reasons to change | Ch 4 |
| an ABC nobody implements fully | interface written ahead of need | Ch 7 |
| several functions writing the same file | missing the one-and-only-one service | Ch 3 |

## Enforce mechanically, not in review
This adaptation's core move: put **`mypy` in CI**. It catches LSP signature breaks (`Signature of "get" incompatible with supertype "View"`), side effects that change a name's type (`Incompatible types in assignment`), and missing `TypedDict` keys. `pytest` + `mypy` is the guide's entire toolchain. Reserve human review for what a checker cannot see: invariants, history properties, and whether an abstraction is a *good* one.

## Escalation ladders (best last)
- **Filtering**: fused loop → extracted function → **generator** (`Iterator` in, `Generator` out)
- **Regex output**: `matches[1]` → `city, zip = matches.groups()` → **`(?P<city>...)`**
- **Params**: 4 positional → `dict` → plain class → `NamedTuple` → `@dataclass` → **`TypedDict`** (3.8+)
- **Vocabulary**: 3 synonym functions → 3 consistent names → **one class** with attribute/property/method
- **Side effects**: `global` mutation → pure function → **class owning state with a `@property`**
