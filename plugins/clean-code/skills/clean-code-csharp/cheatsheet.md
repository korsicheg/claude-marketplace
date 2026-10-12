# Cheatsheet — clean-code-csharp

## Thresholds & defaults
| Thing | Rule |
|---|---|
| Function arguments | **0 ideal · 1–2 ok · 3 avoid · 4+ consolidate** into a `record` |
| Things a function does | **1** — if the description needs "and", split |
| Abstraction levels per function | **1** |
| `bool` flag parameters | **0** — two methods |
| Writers per file/resource | **1** — "One and only one" |
| Reasons for a class to change | **1** |
| Test coverage target | **100% statements and branches**, measured by a tool |
| Concepts per test | **1**, in Arrange / Act / Assert |
| Magic strings / numbers | **0** — `const` (PascalCase) or `enum` |
| Type prefixes in names | **0** — no Hungarian, parameters included |
| `async void` methods | **0** outside event handlers |
| `.Result` / `.Wait()` in async code | **0** |
| `throw ex;` | **0** — `throw;` or wrap with inner exception |

## Casing (Ch 2, Ch 14)
| Symbol | Convention |
|---|---|
| Types, methods, properties, `const` fields | `PascalCase` |
| Interfaces | `I` + PascalCase (`IAdapter`) |
| Locals, parameters | `camelCase` |
| Private / internal fields | `_camelCase` |
| Static fields | `s_camelCase` |

The source's own `ADMIN_ROLE` and `ACCESS_READ` break this table — follow the table.

## The root decision
**Does this method do one thing?** Everything else is a detector:
- 3+ parameters → no · a `bool` parameter → no · a vague verb (`Handle`, `Process`) → no
- orchestration mixed with loops → no · rewrites shared state → no · a `switch` on a type code → no

## Behaviour varies by type?
```
Can you give the types a shared abstraction?
├─ Yes → interface/base + one implementation per case        (IAirplane, Traveler, IAdapter)
└─ No (types you don't own, a boundary)
   └─ C# type pattern: if (vehicle is Bicycle bicycle) …       (acceptable fallback)
Never: GetType() == typeof(T) + as-cast · object/dynamic parameters + runtime checks
```

## Too many parameters?
```
Related values travelling together?  → positional record + named arguments  (MenuConfig)
A bool among them?                   → split the method first                (CreateTempFile)
Still >2 after that?                 → the method likely does more than one thing — split it
```

## Need shared state or a single instance?
```
Global function / static accessor?  → instance class, data via constructor   (Configuration)
"There must be only one"?           → a container lifetime, not a Singleton  (resolve from IoC)
Needs settings?                     → IOptions<T> constructor parameter      (DBConnection)
```

## Inherit or compose? (Ch 8)
Inherit when the source's checklist holds — **is-a** (not has-a), **reuse** from the base, and you **want base changes to propagate**. Otherwise compose: hold a `record` or object as a property. Say it aloud: "an employee *has* tax data."

## Is it still a subtype? (LSP, Ch 9)
| Sign | Verdict |
|---|---|
| Override must change other state to keep its own invariant (`Square.SetWidth` sets height) | ✗ not a subtype → make it a sibling |
| Caller written against the base gets a wrong result (area 25, expected 20) | ✗ |
| Consumer still needs `is Square` after the fix | the shared abstraction is missing an operation |
| Same contract, behaviour fits callers' expectations | ✓ |

## Exceptions — what to do in a `catch`
```
Only logged?                       → throw;
Have context the caller lacks?     → throw new CustomException("context", ex);
Can recover / notify?              → do it; don't rethrow
Different handling per type?       → one catch per type, most specific first
Tempted to write throw ex;         → never — it resets the stack trace
Empty catch                        → never — "you should have a plan"
```

## Async — Old → New (Ch 12)
| In async code you see | Write instead |
|---|---|
| `task.Result`, `task.Wait()` | `await task` |
| `Task.WaitAll` / `Task.WaitAny` | `await Task.WhenAll` / `await Task.WhenAny` |
| `Thread.Sleep` | `await Task.Delay` |
| `new Task(…)` + `Start()` | `Task.Run` / `TaskFactory.StartNew` |
| `async void` (not an event handler) | `async Task` |
| CPU-heavy loop marked `async` | dedicated task, `TaskCreationOptions.LongRunning` |
| Library `await` | `ConfigureAwait(false)` unless the method needs its context |

## Comment or not? (Ch 15)
```
Says WHAT the code does?   → rename a variable / extract a method; delete the comment
Says WHY (a decision)?     → keep it (djb2 over sha-1)
Section banner or #region? → delete; let names and size give structure
Old code or a changelog?   → delete; git log has it
```

## Merge duplicates? (Ch 10)
```
Do both copies always change together, for the same reason?
├─ No  → leave them
└─ Yes → would the merge need a flag or a type test?
         ├─ Yes → don't: "Bad abstractions can be worse than duplicate code"
         └─ No  → one method over a shared interface/base; compact last
```

## Tells & smells
| If you see… | You're probably… | Go to |
|---|---|---|
| `iCounter`, `strName`, `pDay` | encoding the type in the name | Ch 2 |
| `dataFromDb` | naming provenance, not meaning | Ch 2 |
| `else` after `return`, 3+ nesting levels | missing guard clauses | Ch 3 |
| `== "Admin"`, `== 4` | holding a magic value | Ch 3 |
| `car.CarMake` | repeating context | Ch 3 |
| `matches[1].Value` | missing named regex groups | Ch 3 |
| `Handle()`, `Process()` | hiding several actions behind one verb | Ch 4 |
| `CreateFile(name, true)` | merging two methods behind a flag | Ch 4 |
| `!IsNotX()` | double-negating | Ch 5 |
| `switch (_type)` / `GetType() == typeof` | missing polymorphism | Ch 5 |
| `dynamic` + `TryParse` | escaping the type system | Ch 5 |
| `X.GetInstance()` | hiding a dependency in a Singleton | Ch 6 |
| `public double Balance = 1000;` | exposing a field | Ch 7 |
| `class TaxData : Employee` | inheriting a has-a | Ch 8 |
| `if (adapterName == "…")` | violating OCP | Ch 9 |
| a method that only throws or does nothing | implementing a fat interface | Ch 9 |
| constructor takes concrete classes | missing DIP | Ch 9 |
| `ShowDeveloperList` + `ShowManagerList` | duplicating near-miss logic | Ch 10 |
| `date = new …` halfway down a test | hiding a second test | Ch 11 |
| `.Result`, `Thread.Sleep` in async code | blocking on async | Ch 12 |
| `throw ex;`, empty `catch` | losing or swallowing the error | Ch 13 |
| `#region`, `////////` | using positional markers | Ch 15 |
