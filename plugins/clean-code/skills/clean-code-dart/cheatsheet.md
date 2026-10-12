# Cheatsheet — clean-code-dart

## Thresholds & defaults
| Thing | Rule |
|---|---|
| Function arguments | **≤2 ideally**, 3 "should be avoided", more "should be consolidated"; name them with `{required …}` |
| Things a function does | **1** — if the description needs "and", split |
| Abstraction levels per function | **1** |
| Boolean parameters | **0** |
| Reasons for a class to change | **1** |
| Magic literals | **0** — `const` lowerCamelCase name, unit in the name |
| Pass-through getters/setters | **0** — a plain field until there's logic |
| `throw UnimplementedError()` in an implementer | **0** — split the interface |
| Concepts per test | **1** |
| Test coverage | up to the team; **100% statements and branches** is the guide's ideal |
| Comments | only for **business-logic complexity** |
| Dart floor (inferred) | 2.17+ (super parameters), null-safe, pre-Dart 3 |

## The root decision
**Does this function do one thing?** Everything else is a detector:
- 3+ arguments → no · `bool` flag → no · vague name (`addToDate`) → no
- orchestration mixed with mechanics → no · `switch`/`is` on a type → no · mutates a global or an argument → no

## Declare it how?
```
Known at compile time?          → const   (lowerCamelCase: daysInWeek)
Assigned once, at run time?     → final
Reassigned later?               → var
Optional param, constant fallback → {T name = constant}   (non-nullable)
Optional param, computed fallback → {T? name} + name ?? compute()
```

## Field, accessor, or private?
```
Callers need it, no logic on read/write   → public field          int balance;
Read/write must validate, compute, notify → getter/setter over _field
Only this class (library) uses it         → _field / _method()
Value is derived                          → getter, no field
```
Field ↔ getter is invisible to callers, so start with the field.

## Reuse: extends, implements, or a field?
```
Is it genuinely "is-a" AND reuses base code AND should base changes propagate?
├─ all three → extends  (+ super parameters, @override)
├─ only needs to promise the same shape → implements an abstract class
└─ it "has" the thing → a field (nullable if it may be absent)
Would an implementer need throw UnimplementedError()? → the interface is too fat; split it
Mixins (with) → not covered by the guide
```

## Removing conditionals — escalation ladder
Compound `if` → **named predicate** (`isValidDartProgrammer`) · `!isNotX()` → **positive predicate** · `switch (type)` in a method → **subclass per case** · `is` chain in a function → **abstract method + `@override`** (OCP)

## Async and errors
| Situation | Do |
|---|---|
| Consuming a `Future` | `async` function, `await`, typed `Future<T>` return |
| `await` on a `.then` chain | rewrite as sequential `await`s |
| Catching | `on Exception catch (e, s)`, then log with trace / notify user / report |
| Keeping `.then` | `.onError((e, s) { … })` with the same options |
| No plan for the error | no `try`/`catch`; let it propagate |

## Capitalization (Effective Dart)
| lowerCamelCase | UpperCamelCase |
|---|---|
| variables, **constants**, functions, methods, parameters | classes, enum types, typedefs, type parameters |
`DAYS_IN_WEEK`, `restore_database`, `class animal` are all **Bad** in Dart.

## Tells & smells
| If you see… | You're probably… | Go to |
|---|---|---|
| `dynamic` on a variable that changes type | hiding a side effect from the type checker | Ch 3 |
| `.add(...)` on a parameter | mutating the caller's data | Ch 3 |
| `{String? x}` then `x ?? 'literal'` | missing a `const` default value | Ch 2 |
| `carColor` on `Car` | repeating context | Ch 2 |
| `int get x => _x; set x(v) => _x = v;` and nothing else | writing ceremony | Ch 4 |
| `obj.a = …; obj.b(); obj.c();` | missing a cascade | Ch 5 |
| `class X extends Y` where X is something Y has | inheriting instead of composing | Ch 5 |
| `if (x is A) … else if (x is B)` | violating OCP; behaviour belongs on the types | Ch 6 |
| a subclass overriding setters to stay valid | breaking LSP | Ch 6 |
| `throw UnimplementedError()` in a concrete class | implementing a fat interface | Ch 6 |
| `final dep = Concrete();` as a field initializer | depending on a detail; inject an abstraction | Ch 6 |
| `var` reassigned inside a test | two concepts in one test | Ch 7 |
| `await x.then(...)` | mixing async styles | Ch 8 |
| `catch (e) { print(e); }` | ignoring the error | Ch 9 |
| `// doOtherStuff();`, dated headers, `/////` banners | keeping history in the file | Ch 11 |

## JavaScript habits to drop in Dart
| JavaScript guide | Dart guide |
|---|---|
| Destructured options object | named `required` parameters |
| `MILLISECONDS_PER_DAY` | `const` lowerCamelCase (`daysInWeek`) |
| Use getters and setters | plain fields; accessors only for logic |
| Closures for privacy | `_` prefix (library-private) |
| `return this` for chaining | cascade `..` |
| `reduce` | `fold<T>` when the result type differs |
| `.catch()`, `console.error` | `.onError((e, s) …)`, `log(…, error:, stackTrace:)` |
| `describe` / `it` | `group` / `test` / `expect` |
