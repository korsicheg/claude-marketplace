# Cheatsheet — clean-code-php

## Thresholds & defaults
| Thing | Rule |
|---|---|
| Function arguments | **0 ideal, 1–2 ok, 3 avoid, 4+ consolidate** into value objects — constructors included |
| Boolean flag parameters | **0** — write two functions |
| Abstraction levels per function | **1** |
| Reasons to change per class | **1** |
| Equality operator | **`===` / `!==`** by default; `in_array(…, true)` |
| Member visibility | **`private`** by default; `protected` counts as public |
| Class modifier | **`final`**, implementing an interface that is its entire public API |
| Setter return type | **`void`** — `return $this` only in builders |
| Magic numbers / bitmasks | **0** — PHP's predefined constants or `public const` flags |
| `global`, global functions, Singletons | **0** — construct once, inject |
| Class-to-class `extends` in the guide's Good examples | **0** — the abstraction is always an `interface` |
| PHP floor | examples **7.1+**; `composer.json` `>=7.2`; CI on 8.0 |

## Pick the comparison
```
Need "same type and value"?           → ===  (default)
Fallback when unset/null?             → ??   ($_GET['x'] ?? $_POST['x'] ?? 'default')
Fallback when empty/falsy?            → ?:   (⚠ '0' and '' fall through; notice on missing key)
Deliberately want PHP's conversion?   → ==   and leave a comment saying so
```

## Remove a conditional (best last)
```
$obj->state === 'published'     → $obj->isPublished()            (encapsulate)
! isNotX()                       → isX()                          (positive)
switch ($this->type)             → interface + one class per case (polymorphism)
instanceof A / elseif B          → one method name, Vehicle-typed param
is_numeric($x) guard             → int $x  + declare(strict_types=1)
```

## Hidden dependency → injected object
| You see | Do instead |
|---|---|
| `global $name;` | parameter in, return value out |
| `function config(): array` in the global namespace | `new Configuration([...])`, passed where needed |
| `DBConnection::getInstance()` | `new DBConnection($dsn)`, passed where needed |
| helper functions called from inside a method | helper classes taken by `__construct()` |
| `new UserAuth($user)` inside a constructor | take `UserAuth` as a constructor argument (DIP) |

## Inherit or compose?
```
Is it a true "is-a"  AND  reuses base behaviour  AND  should base changes reach it?
├─ all yes → extends is defensible
└─ any no  → hold it as a field (Employee has EmployeeTaxData)
Then: final class + interface; callers type-hint the interface.
```

## SOLID, one line each
| Principle | Tell | Move |
|---|---|---|
| SRP | class name needs "and"; settings class verifying credentials | extract a class per reason to change |
| OCP | `if ($adapter->getName() === '…')` | `interface Adapter { request() }`, delegate |
| LSP | subclass setter that also changes another property | flat implementations of an interface; set state in the constructor |
| ISP | method body that does nothing ("robot can't eat") | split by capability; `interface X extends A, B` |
| DIP | constructor type-hints a concrete class | type-hint an interface; let DI supply it |

## Deduplicate, or leave it?
```
Change together, for the same reason?   yes → merge into one function/class
Merged version needs a flag?             yes → don't; "Bad abstractions can be worse than duplicate code"
Code reads the distinction?              no  → generalize ($developers + $managers → $employees)
One copy is dead?                        yes → delete it
```

## Tells & smells
| If you see… | You're probably… | Go to |
|---|---|---|
| `'42' != 42` style comparisons | trusting type juggling | Ch 3 |
| `isset() ? … : …` ladders | missing `??` | Ch 3 |
| `$ymdstr`, `$l`, `$li` | forcing mental mapping | Ch 2 |
| `serialize($data, 448)`, `$access & 4` | hiding meaning in a magic number | Ch 2 |
| three levels of `if` with a `return false;` each | missing guard clauses | Ch 2 |
| a numeric function returning `'Not supported'` | mixing return types; throw instead | Ch 2 |
| `__construct()` with 8 `string`s | missing value objects | Ch 4 |
| `handle()`, `process()` | naming plumbing instead of the action | Ch 4 |
| `bool $temp = false` | two functions in one | Ch 4 |
| `public $balance` | letting callers bypass invariants | Ch 6 |
| `protected` "for flexibility" | exposing internals to every subclass | Ch 6 |
| `return $this;` on an entity | a fluent interface that breaks decorators and mocks | Ch 7 |
| `final class` with no interface | blocking substitution | Ch 7 |
| `Square extends Rectangle` | subtyping by taxonomy, not behaviour | Ch 8 |
| `oldX()` next to `newX()` | keeping dead code | Ch 5 |
| `showDeveloperList` + `showManagerList` | near-miss duplication | Ch 9 |

## Escalation ladders (best last)
- **Regex output**: `$matches[1]` → `[, $city, $zipCode] = $matches` → **`(?<city>…)` + `$matches['city']`**
- **Defaults**: untyped `$x = 'X'` → `$x = null` + `$x ?: 'X'` → **`string $x = 'X'`**
- **Abstraction**: one long function → extracted helper functions ("Bad too") → **injected helper classes**
- **Type safety**: `is_numeric()` guards → `int` declarations → **`int` + `declare(strict_types=1)`**
- **Dispatch**: `switch`/`instanceof` → **interface with one implementation per case**
- **Duplication**: two role functions → `showList()` → **compact `showList()`**
