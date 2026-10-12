# Chapter 2: Variables

## Core Idea
A variable's name is the cheapest documentation you will ever write. Make it **pronounceable, searchable, consistent, and free of repetition** — and put fallbacks in the method signature as default arguments, where Ruby's `nil`/`false` semantics are explicit.

## Frameworks Introduced
- **Use meaningful and pronounceable variable names**: `yyyymmdstr` → `current_date`.
  - When to use: any name you couldn't say aloud in a code review.
  - How: name the concept, not the format. The `strftime('%Y/%m/%d')` call already says what the format is.
- **Use the same vocabulary for the same type of variable**: "Pick one word for the concept and stick to it."
  - When to use: whenever two names refer to the same entity or the same kind of value.
  - How: `user_info` / `user_data` / `user_record` → `user`; `starts_at` / `start_at` / `start_time` → `starts_at`. The Ruby version applies this to **suffix conventions** too — one timestamp suffix (`_at`) across the codebase.
- **Use searchable names and use constants**: "We will read more code than we will ever write." Instead of "magic numbers", create constants.
  - When to use: any literal whose meaning isn't evident at the call site.
  - How: `Timeout::timeout(86_400)` → `SECONDS_IN_A_DAY = 86_400`. The guide's comment says "Declare them as capitalized globals" — in Ruby that means a **constant**: any identifier beginning with a capital letter.
- **Use explanatory variables**: replace repeated, index-based access with named parts.
  - How: destructure the match — `_, city, zip_code = city_zip_code_regex.match(address).to_a` — discarding the full match with `_`.
- **Avoid mental mapping**: "Explicit is better than implicit."
  - When to use: block parameters most of all — `locations.each do |l|` forces every reader to remember what `l` was by the time `dispatch(l)` arrives.
  - How: `|location|`. Block bodies are where single letters live longest.
- **Don't add unneeded context**: "If your class/object name tells you something, don't repeat that in your variable name."
  - How: hash keys `car_make:` / `car_model:` / `car_color:` → `make:` / `model:` / `color:`, read as `car[:color]`.
- **Use default arguments instead of short circuiting or conditionals**.
  - How: `def create_micro_brewery(brewery_name = 'Hipster Brew Co.')` instead of `brewery_name = name || 'Hipster Brew Co.'`.
  - The guide's caveat: defaults apply only to omitted arguments — "Other 'falsy' values such as `false` and `nil` will not be replaced by a default value."

## Key Concepts
- **Pronounceable name** — one you can say in conversation; `yyyymmdstr` fails.
- **Vocabulary consistency** — one word per concept across every name that refers to it.
- **Magic number** — an unexplained literal, e.g. `86_400`.
- **Constant** — a capitalized identifier (`SECONDS_IN_A_DAY`); the guide's home for magic values.
- **Explanatory variable** — a named local for a sub-part of an opaque expression.
- **Parallel assignment with `_`** — `_, city, zip_code = ...to_a`; `_` marks a deliberately ignored element.
- **Mental mapping** — making the reader translate a short name into the concept it stands for.
- **Unneeded context** — repeating the container's name in its own keys or attributes.
- **Default argument** — a fallback declared in the signature; applies only when the argument is omitted.

## Mental Models
- **Test the name at the use site.** `car[:color]` reads fine because `car` is right there; `car[:car_color]` says "car" twice.
- **Think of `||` as "replace anything falsy" and a default argument as "replace only what's missing."** In Ruby only `nil` and `false` are falsy, so the two differ exactly when a caller passes `nil` or `false` on purpose.
- **Block parameters are names too.** The longer the block, the longer the name it has earned.

## Anti-patterns
- **Encoding the format in the name** (`yyyymmdstr`): the format is an implementation detail and changes.
- **Synonym drift** (`user_info`, `user_data`, `user_record`): three names breed three implementations.
- **Calling `match` twice and indexing it** (`match(address)[1]`, `match(address)[2]`): runs the regex twice and couples every reader to group order.
- **Single-letter block parameters in a long block** (`|l|`): mental mapping.
- **Prefixed hash keys** (`car_color`): context the variable name already supplies.
- **`name || 'default'` at the top of a method**: hides the fallback inside the body and silently replaces an explicit `false`.

## Code Examples
Explanatory variables — the Ruby version destructures the `MatchData` instead of indexing it twice:

```ruby
# Bad
address = 'One Infinite Loop, Cupertino 95014'
city_zip_code_regex = /^[^,\\]+[,\\\s]+(.+?)\s*(\d{5})?$/
save_city_zip_code(city_zip_code_regex.match(address)[1], city_zip_code_regex.match(address)[2])

# Good
address = 'One Infinite Loop, Cupertino 95014'
city_zip_code_regex = /^[^,\\]+[,\\\s]+(.+?)\s*(\d{5})?$/
_, city, zip_code = city_zip_code_regex.match(address).to_a
save_city_zip_code(city, zip_code)
```
- **What it demonstrates**: `MatchData#to_a` returns the whole match followed by each group; parallel assignment names the groups once, and `_` documents that the whole match is deliberately ignored.

Searchable constants:

```ruby
# Bad — what the heck is 86400 for?
status = Timeout::timeout(86_400) do
  # ...
end

# Good
SECONDS_IN_A_DAY = 86_400

status = Timeout::timeout(SECONDS_IN_A_DAY) do
  # ...
end
```
- **What it demonstrates**: the constant is greppable and self-describing; the underscore digit separator (`86_400`) is Ruby's readability aid for long literals.

## Reference Tables

`||` versus a default argument, per caller input (the guide's caveat, spelled out):

| Caller passes | `brewery_name = name \|\| 'Hipster Brew Co.'` | `def create_micro_brewery(brewery_name = 'Hipster Brew Co.')` |
|---|---|---|
| nothing (argument omitted) | — (the bad version requires the argument) | `'Hipster Brew Co.'` |
| `nil` | `'Hipster Brew Co.'` | `nil` |
| `false` | `'Hipster Brew Co.'` | `false` |
| `''` or `0` | kept (truthy in Ruby) | kept |
| `'Stone'` | `'Stone'` | `'Stone'` |

| Rule | Bad | Good |
|---|---|---|
| Pronounceable | `yyyymmdstr` | `current_date` |
| Same vocabulary | `user_info`, `user_data`, `user_record` | `user` |
| Same suffix | `starts_at`, `start_at`, `start_time` | `starts_at` |
| Searchable | `86_400` | `SECONDS_IN_A_DAY` |
| No mental mapping | `\|l\|` | `\|location\|` |
| No unneeded context | `car[:car_color]` | `car[:color]` |

## Worked Example
**Default arguments, walked through the falsy trap.**

The bad version reads the fallback out of the body:

```ruby
def create_micro_brewery(name)
  brewery_name = name || 'Hipster Brew Co.'
  # ...
end
```

Three problems. The signature `(name)` says the argument is required, but the body says it's optional — the reader has to open the method to learn the truth. The fallback is computed at run time from *any* falsy input, so `create_micro_brewery(false)` quietly becomes `'Hipster Brew Co.'`. And the parameter and the variable have two different names for one concept.

The good version moves the fallback into the signature:

```ruby
def create_micro_brewery(brewery_name = 'Hipster Brew Co.')
  # ...
end
```

Now the signature is the documentation: optional, defaulted, one name. The guide's warning is the price — `create_micro_brewery(nil)` now yields `nil`, because the default fires only when the argument is *omitted*. **The transferable rule**: choose the default argument when "missing" is the case you mean; reach for `||` only when you deliberately want `nil` and `false` treated as missing, and then say so.

## Key Takeaways
1. **Name the concept**, not its format: `current_date`, not `yyyymmdstr`.
2. **One word per concept**, including suffix conventions (`_at` for timestamps).
3. **Hoist magic numbers to capitalized constants** — searchable and self-describing.
4. **Destructure instead of indexing**: `_, city, zip_code = match.to_a`.
5. **Name block parameters fully** — `|location|`, not `|l|`.
6. **Don't repeat the container's name** in its keys: `car[:color]`.
7. **Prefer default arguments to `||`** — and remember they don't replace an explicit `nil` or `false`.

## Connects To
- **Ch 3**: method names follow the same discipline (`add_to_date` → `add_month_to_date`); keyword arguments extend the default-argument idea to several parameters.
- **Ch 4**: the vocabulary rule is how duplicate implementations are prevented in the first place.
- **Ch 10**: capitalization conventions — constants `SCREAMING_SNAKE`, variables and methods `snake_case`, classes `CamelCase`.
- **clean-code-python**: takes the regex rule one step further with named capture groups; Ruby supports the same `(?<city>…)` syntax, which this guide does not mention.
