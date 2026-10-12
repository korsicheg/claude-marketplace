# Chapter 2: Variables

## Core Idea
Names are the first interface to your code: make them meaningful, consistent, searchable and free of redundant context — and let Dart's declarations carry the rest. `const` or `final` says how the value behaves, type inference says what it is, and a default parameter value says what it falls back to.

## Frameworks Introduced
- **Use meaningful and pronounceable variable names**: `yyyymmdstr` → `currentDate`.
  - When to use: every binding you declare.
  - How: say the name aloud; if it isn't a word, rename it. The Dart example keeps the format string where it belongs, in the call: `final currentDate = DateFormat('yyyy/MM/dd').format(DateTime.now());`.
- **Use the same vocabulary for the same type of variable**: `getUserInfo()` / `getClientData()` / `getCustomerRecord()` → `getUser()`.
  - When to use: whenever two names could refer to the same entity.
  - How: pick one noun and use it everywhere. Synonym drift is how a second implementation of the same lookup gets written.
- **Use searchable names**: "We will read more code than we will ever write."
  - When to use: any literal whose meaning isn't obvious at the call site.
  - How — the Dart example spells out four decisions in its comments: "Declare them as **const** if the value is known at compile time; Declare as **final** if the variable is assigned just once; Use **lowerCamelCase**; `setupTimeInMinutes` is `int`, because the type is **inferred**."
- **Use explanatory variables**: name the parts of an expression read by position.
  - When to use: list indices, tuple-like access, any value whose meaning comes from its *position*.
  - How: `saveCityZipCode(address[1], address[2])` → `final city = address[1]; final zipCode = address[2];`. (The JavaScript parent used a regex here; the Dart port uses a plain `List<String>`, so this is the whole technique.)
- **Avoid mental mapping**: "Explicit is better than implicit."
  - When to use: loop and closure parameters.
  - How: name the element after what it *is* — `locations.forEach((location) { … dispatch(location); })`, never `(l)`.
  - Note: the example's `forEach` with a function literal is a shape that *Effective Dart*, which the guide recommends in Ch 10, advises against; `for (final location in locations)` names the element the same way. The naming lesson is unaffected.
- **Don't add unneeded context**: `Car(carMake:, carModel:, carColor:)` → `Car(make:, model:, color:)`.
  - When to use: fields and named parameters of a class whose name already supplies the context.
  - How: read the name at its use site. `car.carColor` says "car" twice. With named constructor parameters the duplication shows at every call site too, so the cost is paid twice.
- **When possible, use default parameters instead of short circuiting or conditionals**: `{String? name}` + `name ?? 'Hipster Brew Co.'` → `{String breweryName = 'Hipster Brew Co.'}`.
  - When to use: any optional parameter with a fixed fallback.
  - How: put the fallback in the signature. **The Dart caveat**, in the guide's words: "Default parameters are often cleaner than short circuiting, however they must be const, so you cannot use them on every case." A fallback computed at run time (`DateTime.now()`, a value from a service) still needs a nullable parameter and `??`.
  - Why it works under null safety: the default lets the parameter type be non-nullable (`String`, not `String?`), so the body never has to handle `null` at all.

## Key Concepts
- **`const`** — a compile-time constant; the guide's first choice for a named magic value.
- **`final`** — a variable assigned exactly once, at run time; the default for everything else.
- **Type inference** — `const setupTimeInMinutes = 32;` is an `int` without saying so; the name carries meaning, the literal carries the type.
- **lowerCamelCase** — Dart's case for variables *and constants* (`setupTimeInMinutes`, not `SETUP_TIME_IN_MINUTES`); see Ch 10.
- **Named parameter** — `{…}` in a signature; called as `name: value`, which is why redundant context in its name is visible at every call.
- **Default parameter value** — a fallback declared in the signature; must be a compile-time constant.
- **`??` (if-null operator)** — supplies a fallback for a `null` value; the short-circuit this rule replaces where a constant default suffices.
- **Mental mapping** — making the reader translate a short name (`l`) into the concept it stands for.

## Mental Models
- **Use the declaration keyword as documentation.** `const` tells the reader "fixed before the program runs", `final` tells them "set once, here". A reader who sees `var` should expect reassignment.
- **Think of a nullable parameter with `??` as a default that didn't make it into the signature.** If the fallback is a constant, move it there and drop the `?`.
- **Read names where they're used, not where they're declared.** `Car(carMake: 'Honda')` and `car.carColor` both fail at the call site, which is where every reader meets them.

## Anti-patterns
- **Abbreviated or encoded names** (`yyyymmdstr`): unpronounceable and ungreppable.
- **Synonym drift** (`getUserInfo` / `getClientData` / `getCustomerRecord`): three names, one entity, eventually three implementations.
- **Bare magic numbers** — the guide's example is `Future.delayed(Duration(minutes: 32), launch)` with the comment "What the heck is 32 for?"
- **Positional access passed straight into a call** (`saveCityZipCode(address[1], address[2])`).
- **One-letter closure parameters** (`(l) { … dispatch(l); }`) — "Wait, what is `l` for again?"
- **Prefixing fields with the class name** (`carMake`, `carColor`).
- **`String?` plus `??` for a constant fallback**: an avoidable nullable type and an extra line.

## Code Examples
Searchable names — the guide's Dart version, where the comments *are* the lesson:

```dart
// Bad
// What the heck is 32 for?
Future.delayed(Duration(minutes: 32), launch);

// Good
// Declare them as const if the value is known at compile time;
// Declare as final if the variable is assigned just once;
// Use lowerCamelCase;
// setupTimeInMinutes is int, because the type is inferred.
const setupTimeInMinutes = 32;

Future.delayed(Duration(minutes: setupTimeInMinutes), launch);
```
- **What it demonstrates**: the unit lives in the *name* (`…InMinutes`) and in the `Duration` constructor argument (`minutes:`), so the bare number never needs a comment.

## Reference Tables

| Smell | Bad | Good | Dart mechanism |
|---|---|---|---|
| Encoded name | `yyyymmdstr` | `currentDate` | `final` + a real word |
| Synonym drift | `getClientData()` | `getUser()` | one noun |
| Magic number | `Duration(minutes: 32)` | `const setupTimeInMinutes = 32;` | `const`, inferred `int` |
| Positional access | `address[1], address[2]` | `final city = address[1];` | explanatory `final` |
| Mental mapping | `(l) => …` | `(location) => …` | named closure parameter |
| Repeated context | `carColor:` | `color:` | read at the call site |
| Short-circuit default | `{String? name}` + `??` | `{String breweryName = '…'}` | `const` default value |

**Choosing the declaration** (from the guide's searchable-names comments):

| The value is… | Declare it | Case |
|---|---|---|
| known at compile time | `const` | lowerCamelCase |
| assigned once, at run time | `final` | lowerCamelCase |
| reassigned later | `var` (or an explicit type) | lowerCamelCase |

## Worked Example
The default-parameter rule shows Dart's null safety and its constant-default restriction pulling against each other.

**Bad** — the parameter is nullable only so the body can substitute a fallback:

```dart
void createMicrobrewery({String? name}) {
  final breweryName = name ?? 'Hipster Brew Co.';
  // ...
}
```

**Good** — the fallback moves into the signature, the type becomes non-nullable, and the local variable disappears:

```dart
void createMicrobrewery({String breweryName = 'Hipster Brew Co.'}) {
  // ...
}
```

**Where it stops working** — the guide's own caveat ("they must be const, so you cannot use them on every case"). A default of `DateTime.now()` or of an injected service's value is not a compile-time constant, so the analyzer rejects it as a default value. For those, the `String?` + `??` shape in the "Bad" block is the correct one, and the rule's own wording ("When possible…") allows for it.

**The decision**: constant fallback → default parameter value, non-nullable type. Computed fallback → nullable parameter with `??`, kept on the first line of the body.

## Key Takeaways
1. **Meaningful, pronounceable names**: `currentDate`, never `yyyymmdstr`.
2. **One entity, one noun** across every function and field that refers to it.
3. **Name every magic value with `const`** when it's known at compile time; `final` when it's assigned once at run time. Let inference supply the type.
4. **Constants are lowerCamelCase in Dart** — `setupTimeInMinutes`, not `SETUP_TIME_IN_MINUTES`.
5. **Explanatory `final`s** for anything read by position.
6. **No mental mapping, no repeated context** — check names at the call site, including named arguments.
7. **Constant fallback → default parameter value** (non-nullable); **computed fallback → `??`**.

## Connects To
- **Ch 3**: named parameters return as the fix for argument count; `getUser`'s single vocabulary is the start of DRY.
- **Ch 10**: lowerCamelCase for constants is the capitalization rule's first example, and the one that reverses the JavaScript parent.
- ***Effective Dart*** (Style): the source of the lowerCamelCase-for-constants convention the comments encode.
- **`clean-code-javascript` Ch 2**: same seven rules; the Dart port swaps the regex example for list indices and `||` defaults for `??` defaults.
