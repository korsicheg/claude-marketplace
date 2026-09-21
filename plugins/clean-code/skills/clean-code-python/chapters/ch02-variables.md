# Chapter 2: Variables

## Core Idea
Names are the primary interface to your code: make them meaningful, pronounceable, searchable, and free of redundant context — and let **type hints carry the type** so the name doesn't have to.

## Frameworks Introduced
- **Meaningful and pronounceable names**: `ymdstr` → `current_date`.
  - When to use: every binding you declare.
  - How: say the name aloud. If it isn't a word, rename it. Then delete any type prefix/suffix — annotate instead: `current_date: str`.
  - Why it works: Python has type hints, so encoding the type in the name (Hungarian notation) duplicates information the annotation states better and `mypy` can check.
- **One entity, one vocabulary**: `get_user_info` / `get_client_data` / `get_customer_record` → one consistent noun.
  - When to use: whenever two names could refer to the same underlying entity.
  - How: pick one noun (`user`) and use it everywhere. **Even better** — if the functions all revolve around that entity, package them onto a class as an instance attribute, a `@property`, and a method.
  - Failure mode: synonym drift breeds duplicate implementations, because the next developer greps for `customer` and doesn't find `user`.
- **Searchable names**: hoist every meaningful literal to a module-level constant.
  - When to use: any number or string whose meaning isn't self-evident at the call site.
  - How: `time.sleep(86400)` → `SECONDS_IN_A_DAY = 60 * 60 * 24`, declared "in the global namespace for the module". Note the guide keeps the *arithmetic* (`60 * 60 * 24`) rather than the computed value — the derivation is itself documentation.
- **Explanatory variables**: name the sub-parts of an opaque expression.
  - When to use: regexes, index arithmetic, tuple unpacking, any expression read by position.
  - How: three tiers, best last — (1) `matches[1]`, `matches[2]`; (2) `city, zip_code = matches.groups()`; (3) **named capture groups** `(?P<city>.+?)` read as `matches['city']`. Tier 3 "decreases dependence on regex" by moving the name into the pattern itself.
- **Avoid mental mapping**: `seq`/`item` → `locations`/`location`.
  - When to use: every loop variable and short-lived binding.
  - How: name the element after what it *is*. The guide invokes the Zen of Python: **"Explicit is better than implicit."**
- **Don't add unneeded context**: `car.car_make` → `car.make`.
  - When to use: attributes on a class whose name already supplies the context.
  - How: read the name at its access site, not its declaration site. `Car.car_color` reads `car.car_color`; the class name already said "car".
- **Default arguments over short-circuiting**: `name = "X" if name is None else name` → `def f(name: str = "X")`.
  - When to use: any parameter with a fallback value.
  - How: put the default in the signature. This "also makes it clear that you are expecting a string as the argument" — the default documents the type and the annotation confirms it.

## Key Concepts
- **Type hint** — an annotation (`current_date: str`) that states a binding's type so the name needn't encode it, and `mypy` can verify it.
- **Named capture group** — `(?P<name>...)` in a regex, retrieved as `matches['name']`; turns positional regex output into self-documenting access.
- **Module-level constant** — an `UPPER_SNAKE_CASE` name in the module namespace, the guide's home for hoisted magic values.
- **Mental mapping** — forcing the reader to translate a short name into the concept it stands for.
- **Unneeded context** — repeating the enclosing class/object's name inside its own attribute names.
- **Short-circuiting** — using `or` / conditional expressions to supply a fallback, in place of a real default argument.
- **Property method** — `@property`, the "Even better" way to expose a derived value as an attribute rather than a `get_*` function.

## Code Examples
The vocabulary rule's **"Even better"** tier — the one that distinguishes this adaptation from its JavaScript parent, because it answers the rule with Python's object model rather than with renaming:

```python
from typing import Union, Dict


class Record:
    pass


class User:
    info: str

    @property
    def data(self) -> Dict[str, str]:
        return {}

    def get_record(self) -> Union[Record, None]:
        return Record()
```

- **What it demonstrates**: three loose functions (`get_user_info`, `get_user_data`, `get_user_record`) collapse into one `User` type exposing an attribute, a property, and a method. The shared noun stops being a naming convention and becomes a type.

## Reference Tables

| Smell | Bad | Good | Mechanism |
|---|---|---|---|
| Type in name | `ymdstr` | `current_date: str` | Type hint |
| Synonym drift | `get_client_data` | `User.data` | One noun, or a class |
| Magic number | `time.sleep(86400)` | `SECONDS_IN_A_DAY = 60 * 60 * 24` | Module constant |
| Positional regex | `matches[1]` | `matches['city']` | `(?P<city>...)` |
| Mental mapping | `for item in seq` | `for location in locations` | Plural/singular pair |
| Repeated context | `car.car_make` | `car.make` | Read at access site |
| Short-circuit default | `x if x is None else…` | `def f(x: str = "…")` | Default argument |

## Worked Example
The explanatory-variables rule, walked through all three tiers on one address parser. Start: everything is positional and the reader must count capture groups.

```python
# Bad — what are [1] and [2]?
city_zip_code_regex = r"^[^,\\]+[,\\\s]+(.+?)\s*(\d{5})?$"
matches = re.match(city_zip_code_regex, address)
if matches:
    print(f"{matches[1]}: {matches[2]}")
```

**Not bad** — unpacking names the parts, but the pattern itself is still opaque, so the names live far from what produced them:

```python
if matches:
    city, zip_code = matches.groups()
    print(f"{city}: {zip_code}")
```

**Good** — the names move *into* the pattern, so the regex documents its own output and there is no positional coupling left to break when a group is added:

```python
address = "One Infinite Loop, Cupertino 95014"
city_zip_code_regex = r"^[^,\\]+[,\\\s]+(?P<city>.+?)\s*(?P<zip_code>\d{5})?$"

matches = re.match(city_zip_code_regex, address)
if matches:
    print(f"{matches['city']}, {matches['zip_code']}")
```

**Why the third tier wins**: in tier 2 the unpacking order is a silent contract with the pattern — insert a group and every downstream name shifts by one, with no error. In tier 3 that class of bug is unrepresentable.

## Key Takeaways
1. **Annotate the type; don't spell it in the name.** `current_date: str`, never `ymdstr`.
2. **One entity, one noun** — and if several functions share that noun, promote it to a class.
3. **Hoist magic values to module constants, keeping the arithmetic** (`60 * 60 * 24`) as documentation.
4. **Name regex sub-patterns with `(?P<name>...)`** so access is by name, never by index.
5. **Explicit is better than implicit** — loop variables get real names (`location`, not `item`).
6. **Don't repeat the class's name in its attributes**; read names at the access site.
7. **Put fallbacks in the signature as default arguments**, which documents both the value and the expected type.

## Connects To
- **Ch 3**: naming and argument count are the two cheapest detectors for "this function does more than one thing"; `create_micro_brewery`'s default argument is also an argument-count rule.
- **Ch 4 (SRP)**: the "Even better" class-packaging move is SRP applied at the naming layer.
- **Ch 9 (DRY)**: synonym drift is how duplicate implementations get created in the first place — `Developer` and `Manager` are the same entity under two names.
- **PEP 8 / Zen of Python**: "Explicit is better than implicit" is quoted directly; naming *conventions* (snake_case, UPPER_SNAKE) come from PEP 8, which this guide defers to.
