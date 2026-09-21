# Clean Code — Decision Cheatsheet

## Thresholds Martin commits to

| Thing | Limit | Source |
|---|---|---|
| Function length | *"hardly ever 20 lines"*; target 2–4 | Ch3 |
| Indent depth in a function | **≤ 2** | Ch3 |
| Function arguments | 0 ideal · 1 good · 2 costly · **3 avoid** · 4+ never | Ch3, F1 |
| File length | ~200 lines typical, **500 hard-ish max** | Ch5 |
| Line width | ≤ 120 (*"beyond that is probably just careless"*) | Ch5 |
| Class size | measured in **responsibilities = reasons to change**, not lines | Ch10 |
| Class description | ≤ ~25 words with **no "if/and/or/but"** | Ch10 |
| Asserts per test | minimize; **one *concept* per test** | Ch9 |
| Switch statements per selection type | **exactly one**, in a factory | G23 |

## Before writing a comment

```
Can a better function name say it?      → rename, don't comment
Can a named variable say it?            → extract explanatory variable (G19)
Is it a section marker inside a function? → extract that section as a function
Is it on a closing brace?               → the function is too long
Is it a change log / byline / old code? → DELETE (source control has it)
Is it explaining WHY, warning of a consequence, or amplifying non-obvious importance?
                                        → keep it, and write it well
Otherwise                               → you're commenting bad code; clean the code
```

## Object or data structure? (the axis-of-change test)

| Expect to add mostly… | Choose | Because |
|---|---|---|
| new **types** | objects, polymorphism, hidden data | new classes don't touch existing functions |
| new **operations** | data structures + procedures | new functions don't touch existing structures |
| both, equally | pick per subsystem — **never build a hybrid** | hybrids make *both* hard |

Law of Demeter applies to **objects only**. A train wreck through data structures is not a violation — a train wreck through objects means you should be *telling*, not *asking*.

## Error handling

```
Is the "error" a business case with a default?  → Special Case object, no exception
Would you return null?                          → throw, or Special Case, or emptyList()
Would you pass null?                            → forbid it; a null arg means a bug
Writing a library others MUST handle?           → checked exception (rare)
Everything else                                 → unchecked exception + context message
Many exception types, same handling?            → wrap the API, translate to one type
```

## Naming decision rules

- **Name needs a comment → rename.** That's the whole test.
- **Length ∝ scope.** `i` in a 2-line loop is right; `i` across a class is not.
- **Class = noun. Method = verb.** `get`/`set`/`is` for accessors.
- **One word per concept**, and never pun (`add` ≠ `insert`).
- **If you can't name the class concisely, it's too big.** `Manager`/`Processor`/`Super`/`Data`/`Info` = aggregated responsibilities.
- **Name at the abstraction level of the class, not the implementation** (`connectionLocator`, not `phoneNumber`).
- **Name must include side effects** (`createOrReturnOos`, not `getOos`).

## Tells & smells — fast recognition

| If you see… | You're probably in… | Do |
|---|---|---|
| The same 3 lines twice | missing abstraction (G5) | extract now, even for 3 lines |
| `if/switch` on a type, repeated elsewhere | missing polymorphism | Abstract Factory, ONE SWITCH |
| A boolean argument | a function doing two things | split it |
| `+1` / `-1` scattered | unencapsulated boundary (G33) | name the boundary value |
| Section comments in a function | functions waiting to be extracted | extract each |
| Instance fields used by only some methods | a class trying to get out (Ch10) | split the class |
| Urge to column-align a field list | the class is too big | split it, don't align |
| A method reaching through another object's getters | Feature Envy (G14) | move the behavior |
| Functions that must be called in order | hidden temporal coupling (G31) | bucket brigade |
| Repeated "bug fixes" in one function | wrong algorithm, not wrong line | rewrite it |
| A never-executed line in coverage | an impossible condition (G9, T8) | prove and delete |
| Intermittent failure "one-off" | a real threading defect | never dismiss it |
| A constant a low-level function shouldn't know | misplaced responsibility (G17, G35) | pass it down from above |

## When to stop adding features and refactor (Ch14)

Stop when **each new case requires parallel edits in the same N places**. That pattern
("many types, all with similar methods") *is* the class trying to be born. Bulldozing
past it leaves *"a mess that was too large to fix."*

## Refactoring protocol

1. Tests green and covering the behavior **first** (unit + acceptance).
2. Add the new abstraction as a **harmless skeleton** alongside the old code.
3. Migrate **one** use; run tests.
4. A test breaks → fix that before anything else. Failing *"in exactly the same way"* = no new error introduced.
5. Expect to **undo earlier steps**; that's convergence, not failure.
6. Prefer structure that *communicates* a constraint over a parameter that merely *enforces* it — otherwise the next person removes it.

## Priority order when rules conflict (Beck's four rules, Ch12)

```
1. Runs all the tests          ← never traded away
2. Contains no duplication
3. Expresses intent
4. Minimizes classes/methods   ← never overrides 1–3
```

So: **don't merge two well-named functions just to have fewer functions**, and don't
create an interface per class out of dogma. *"Such dogma should be resisted."*

## Judgment calls the book explicitly allows

- **Magic numbers**: `feetWalked/5280.0`, `hourlyRate * 8`, `radius * Math.PI * 2` read
  fine raw. π does **not** — nobody proofreads a literal they recognize.
- **Multiple asserts** in a test, when forcing one would need a Template Method base
  class — *"too much mechanism for such a minor issue."*
- **Loosening encapsulation** to `protected`/package for a test — *"tests rule"* — but
  only as a last resort.
- **Feature Envy**, when removing it would couple a domain object to a report format.
- **Test code may be inefficient** (string concat over `StringBuilder`); it may **never**
  be unclean.
- **Don't pre-split a class speculatively** — OCP restructuring is triggered by a change
  actually arriving.
