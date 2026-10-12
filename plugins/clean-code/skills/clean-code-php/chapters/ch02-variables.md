# Chapter 2: Variables

## Core Idea
A variable name is the reader's only handle on intent: make it **meaningful, consistent, searchable and free of redundant context**, name the parts of opaque expressions, and keep control flow **flat** — return early instead of nesting, because "Explicit is better than implicit."

## Frameworks Introduced
- **Meaningful and pronounceable names**: `$ymdstr` → `$currentDate`.
  - When to use: every variable you declare.
  - How: say it aloud; if it isn't a word, rename it.
- **Same vocabulary for the same type of variable**: `getUserInfo()` / `getUserData()` / `getUserRecord()` / `getUserProfile()` → `getUser()`.
  - When to use: whenever two names could refer to the same entity.
  - How: pick one noun and one verb and use them everywhere. Synonyms make the next developer grep for `Profile`, miss `Record`, and write a second implementation.
- **Use searchable names (part 1) — named constants over magic numbers**: "We will read more code than we will ever write. It's important that the code we do write is readable and searchable."
  - How: `$serializer->serialize($data, 448)` → `JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE`. PHP's own predefined constants *are* the names — use them instead of their sum.
- **Use searchable names (part 2) — class constants for bit flags**: `public $access = 7;` and `$user->access & 4` → `public const ACCESS_READ = 1; … ACCESS_UPDATE = 4;` and `$user->access & User::ACCESS_UPDATE`.
  - When to use: any integer that encodes a set of permissions or options.
  - How: one `public const` per bit (powers of two), compose defaults with `|`, test with `&`, toggle with `^=`. The constant's name now appears at every use site and is greppable.
- **Use explanatory variables**: a three-rung ladder on one `preg_match()`.
  - Bad: `saveCityZipCode($matches[1], $matches[2]);`
  - Not bad: `[, $city, $zipCode] = $matches;` — "It's better, but we are still heavily dependent on regex."
  - Good: "Decrease dependence on regex by naming subpatterns" — `(?<city>.+?)` and `(?<zipCode>\d{5})`, read as `$matches['city']`.
- **Avoid nesting too deeply and return early (part 1)**: "Too many if-else statements can make your code hard to follow. Explicit is better than implicit."
  - How: declare the parameter type (`string $day`), reject the degenerate case with a guard clause, then express the rule as data — `in_array(strtolower($day), $openingDays, true)`.
- **Avoid nesting too deeply and return early (part 2)**: handle the base cases first, raise on unsupported input, then do the real work at the outermost indentation.
  - Also fixes the return type: the bad version returns either an `int` or the string `'Not supported'`; the good one declares `: int` and **throws** instead of returning an error string.
- **Avoid mental mapping**: "Don't force the reader of your code to translate what the variable means."
  - How: `$l` / `$li` with an index loop → `foreach ($locations as $location)`. The `foreach` removes the index *and* the cryptic name in one move.
- **Don't add unneeded context**: "If your class/object name tells you something, don't repeat that in your variable name." `Car::$carMake` → `Car::$make`.

## Key Concepts
- **Magic number** — an unexplained literal (`448`, `7`, `4`) whose meaning lives only in the author's head.
- **Bit-flag constant** — a power-of-two class constant combined with `|` and tested with `&`.
- **Named subpattern** — `(?<name>…)` in a PCRE pattern; `preg_match()` then fills `$matches['name']`.
- **List destructuring** — `[, $city, $zipCode] = $matches;` (PHP 7.1); skipping element 0 by leaving it empty.
- **Guard clause** — an early `return`/`throw` that disposes of an edge case so the main path stays unindented.
- **Mental mapping** — the translation a reader performs from a short name (`$li`) to the concept it stands for.
- **Unneeded context** — repeating the class name inside its own property names.

## Mental Models
- **Read a name at its use site, not its declaration.** `$car->carColor` stutters; `$car->color` doesn't.
- **Turn conditionals into data.** Three `elseif ($day === 'friday') return true;` branches are a list — `$openingDays = ['friday', 'saturday', 'sunday']`.
- **Indentation depth is a cost.** Each nested `if` is one more condition the reader must hold; a guard clause discharges it immediately.
- **Positional access is a silent contract.** `$matches[1]` and even `[, $city, $zipCode]` break quietly when a group is added; `$matches['city']` can't.

## Anti-patterns
- **Abbreviated type-encoding names** (`$ymdstr`): unpronounceable and unsearchable.
- **Synonym drift** (`Info`/`Data`/`Record`/`Profile`): breeds duplicate getters for one entity.
- **Raw bitmask literals** (`serialize($data, 448)`, `$user->access ^= 2`): "What the heck is 448 for?"
- **Pyramid nesting with a trailing `return false;` per level**: the reader must match each `return` to its `if`.
- **Returning a string to signal an error from a numeric function** (`return 'Not supported';`): a mixed return type the caller must check by hand.
- **Index loops with one-letter names** (`for ($i = 0; $i < count($l); $i++)`): mental mapping plus an index nobody needed.

## Code Examples
```php
class User
{
    public const ACCESS_READ = 1;

    public const ACCESS_CREATE = 2;

    public const ACCESS_UPDATE = 4;

    public const ACCESS_DELETE = 8;

    // User as default can read, create and update something
    public $access = self::ACCESS_READ | self::ACCESS_CREATE | self::ACCESS_UPDATE;
}

if ($user->access & User::ACCESS_UPDATE) {
    // do edit ...
}

// Deny access rights to create something
$user->access ^= User::ACCESS_CREATE;
```
- **What it demonstrates**: the PHP idiom for searchable flags — class constants as the vocabulary, bitwise operators as the grammar. `7`, `4` and `2` never appear.

## Reference Tables

| Smell | Bad | Good | Mechanism |
|---|---|---|---|
| Unpronounceable | `$ymdstr` | `$currentDate` | Rename |
| Synonym drift | `getUserInfo()`, `getUserData()` | `getUser()` | One vocabulary |
| Magic number | `serialize($data, 448)` | `JSON_PRETTY_PRINT \| …` | Predefined constants |
| Magic bitmask | `$user->access & 4` | `User::ACCESS_UPDATE` | Class constants |
| Positional regex | `$matches[1]` | `$matches['city']` | `(?<city>…)` |
| Deep nesting | `if { if { if {` | guard clause, then main path | Return early |
| Mixed return | `return 'Not supported';` | `throw new Exception(…)` | Typed return + throw |
| Mental mapping | `$l`, `$li`, `$i` | `$locations`, `$location` | `foreach` + real names |
| Repeated context | `Car::$carMake` | `Car::$make` | Read at use site |

## Worked Example
**Return early, part 1** — the shop-hours check, before and after.

```php
// Bad: three levels of nesting, four exits, no parameter type
function isShopOpen($day): bool
{
    if ($day) {
        if (is_string($day)) {
            $day = strtolower($day);
            if ($day === 'friday') {
                return true;
            } elseif ($day === 'saturday') {
                return true;
            } elseif ($day === 'sunday') {
                return true;
            }
            return false;
        }
        return false;
    }
    return false;
}
```

```php
// Good
function isShopOpen(string $day): bool
{
    if (empty($day)) {
        return false;
    }

    $openingDays = ['friday', 'saturday', 'sunday'];

    return in_array(strtolower($day), $openingDays, true);
}
```

What each move bought:
1. **`string $day`** deletes the `is_string()` level — the type declaration does that check (Ch 5's type-checking rule, applied early).
2. **The guard clause** deletes the outer `if ($day)` level and its trailing `return false;`.
3. **The list** replaces three `elseif` branches with data — adding Thursday is now a one-word change, not a new branch.
4. **`in_array(…, true)`** is strict comparison (Ch 3): without the third argument `in_array()` compares loosely.

Caveat worth knowing: `empty('0')` is `true` in PHP, so the guard also rejects the string `'0'`. Harmless here, but `$day === ''` states the intent exactly.

## Key Takeaways
1. **Pronounceable, searchable names**; one noun per entity across the codebase.
2. **Never pass a magic number** — use PHP's predefined constants or define `public const` bit flags.
3. **Name regex subpatterns** with `(?<name>…)`; destructuring is only the middle rung.
4. **Return early**: guard clauses first, the main path unindented, errors thrown rather than returned as strings.
5. **Express branchy rules as data** (`in_array($x, $list, true)`).
6. **`foreach` with real names** beats an index loop with `$l`/`$li`.
7. **Don't repeat the class name** in its own properties.

## Connects To
- **Ch 3 (Comparison)**: `===` and `in_array(…, true)` used throughout this chapter's good examples.
- **Ch 4 (Functions)**: default arguments and the ≤2-argument rule are this guide's next naming-adjacent rules.
- **Ch 5**: the type declaration in `isShopOpen(string $day)` is the "avoid type-checking" rule in miniature.
- **Ch 9 (DRY)**: synonym drift is how duplicate implementations start.
- **clean-code-java ch02 (Meaningful Names)**: the book's fuller naming chapter — pronounceable, searchable, no encodings, one word per concept.
