# Cheatsheet — clean-code-ruby

## Thresholds & defaults
| Thing | Rule |
|---|---|
| Method arguments | **≤2 ideally**; 3 "should be avoided"; more → keyword arguments or a higher-level object |
| Things a method does | **1** — if you need "and", split |
| Abstraction levels per method | **1**, descending from abstract to concrete |
| Boolean parameters | **0** |
| Magic literals | **0** — capitalized constants (`SECONDS_IN_A_DAY = 86_400`) |
| Reasons to change per class | **1** |
| Expectations per RSpec example | **1** |
| Coverage | **100% of statements and branches** — "how you achieve very high confidence" |
| `rescue` blocks without a plan | **0** |
| Formatting arguments | **0** — RuboCop decides |
| Ruby floor | 2.4+ implied (keyword arguments 2.1, `Array#sum` 2.4); `present?`/`blank?` need ActiveSupport |

## The root decision
**Does this method do one thing?** Everything else is a detector:

- 3+ arguments → no · boolean parameter → no · vague name (`add_to_date`) → no
- mixes orchestration with mechanics → no · `case` on a type → no · `is_a?` chain → no · mutates a `$global` or an argument → no

## Many arguments?
```
Is the method doing too much?          → split it first
Do the values belong together?         → a higher-level object
Otherwise                              → keyword arguments: def m(title:, body:)
                                          (self-documenting; ArgumentError names a missing keyword)
Bare options hash?                     → "the prevailing pattern", but declares nothing — prefer keywords
```

## Fallback values
```
Should nil / false mean "use the default"?
├─ No  → default argument: def m(name = 'Hipster Brew Co.')   (fires only when omitted)
└─ Yes → name || 'Hipster Brew Co.' — deliberately, and say so
```

## May this method change what it was given?
```
Is mutation the method's stated purpose (and in its name)?
├─ Yes → mutate; the guide calls this case "pretty rare"
└─ No  → return a new value: cart + [item], not cart.push(item)
         big structures → persistent collections (Hamster)
Global state ($name)? → never; take a value, return a value
```

## Removing a conditional — climb only as far as needed
| You see | Do | Ch |
|---|---|---|
| `a.present? && b.present?` inline | named `?` predicate: `send_message?(params)` | 4 |
| `if !x.blank?` | `unless x.blank?` or `if x.present?` | 4 |
| `case @type` in one class | one subclass per `when` | 4 |
| `is_a?` chain choosing a method | one message all types answer (`move`) | 4 |
| `is_a?(Numeric)` guards on primitives | contracts.ruby — or nothing; tests + review | 4 |
| `case collaborator.name` in a consumer | shared message on each collaborator (`request`) | 7 |

## Inherit or compose?
Inherit only if **all three** hold:
1. genuine **is-a**, not has-a (Human→Animal, not User→UserDetails);
2. you **reuse base-class code**;
3. you **want base changes to propagate**.

Otherwise hold it in an instance variable: `@tax_data = EmployeeTaxData.new(...)`.
**LSP check**: if a subclass overrides a writer to protect its own invariant (`Square#width=`), it is not a subtype → siblings under `Shape`.

## Return `self` for chaining?
```
Is the object a builder / query relation (e.g. ActiveRecord)?  → chaining is fine
Anything else                                                 → no: writers + separate statements
   (chaining breaks encapsulation and decorators, complicates mocks, muddies diffs)
```

## Accessors
| Need | Use |
|---|---|
| Read-only | `attr_reader` |
| Trivial read/write on a data-like object | `attr_accessor` (but question every public writer) |
| Validation, logging, lazy loading | hand-written `def balance` / `def balance=(amount)` |

## After `rescue StandardError => err`
```
Do you have a plan for this failure?
├─ No  → don't rescue; let it propagate
└─ Yes → logger.error(err) (level Logger::ERROR) · notify_user_of_error(err) · report to a service
         "OR do all three!"   — never logger.info(err) alone
Raising? → fail ArgumentError, 'Missing user'  — a class to rescue by, a message to read
```

## Tells & smells
| If you see… | You're probably… | Go to |
|---|---|---|
| `yyyymmdstr`, `user_info`/`user_data` | naming a format, or drifting synonyms | Ch 2 |
| `\|l\|` in a long block | forcing mental mapping | Ch 2 |
| `car[:car_color]` | repeating context | Ch 2 |
| `name \|\| 'default'` on line 1 | hiding a default argument in the body | Ch 2 |
| 4 positional arguments | needing keyword arguments or an object | Ch 3 |
| `$something =` inside a method | creating a side effect that breaks on the second call | Ch 3 |
| `push` / `<<` on a parameter | writing to your caller's state | Ch 3 |
| `total += …` inside `each` | missing `sum` / `map` / `select` | Ch 3 |
| `case employee.type` after a DRY refactor | one rung short of polymorphism | Ch 4 |
| `old_*` beside `new_*` | keeping dead code | Ch 4 |
| a hash read and written all over (`account[:balance] =`) | missing an object with accessors | Ch 5 |
| `self` at the end of setters (or of `initialize`) | building a fluent interface — or porting JavaScript | Ch 6 |
| `class X < Y` where X "has" a Y | inheriting instead of composing | Ch 6 |
| `.new` inside `initialize` | hard-coding a dependency | Ch 7 |
| comments "used by Driver" / "used by Mechanic" | one class serving two clients | Ch 7 |
| an `it` named "… and …" | several expectations in one example | Ch 8 |
| `rescue … logger.info(err)` | swallowing a failure | Ch 9 |
| bare `fail` / `raise` | raising without context | Ch 9 |
| `daysInMonth`, `class ANIMAL`, unfrozen `Artists = [...]` | inconsistent capitalization | Ch 10 |
| `# do_other_stuff`, dated `# 2016-12-20:` lines | doing version control's job | Ch 11 |

## Tooling the guide names
RSpec (tests) · Coveralls (coverage) · RuboCop (formatting) · contracts.ruby (runtime contracts) · Hamster (persistent collections) · `Logger` + Honeybadger (errors) · `git log` (history).
