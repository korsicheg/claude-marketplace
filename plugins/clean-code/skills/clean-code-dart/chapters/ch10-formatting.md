# Chapter 10: Formatting

## Core Idea
"Formatting is subjective … The main point is DO NOT ARGUE over formatting." Defer style to *Effective Dart*, and keep two rules: **use the correct capitalization** (Dart has one, so this is not a matter of team taste) and **keep callers just above their callees** so a file reads top-down like a newspaper.

## Frameworks Introduced
- **Don't argue over formatting**: "Like many rules herein, there is no hard and fast rule that you must follow." The guide's recommendation: "I recommend you to read *Effective Dart*, there are several rules to be followed, but nothing is mandatory."
- **Use the correct capitalization**: the Good example's comments are the rule.
  - "lowerCamelCase for constant names" — `const daysInWeek = 7;`, `const bands = […]`.
  - "lowerCamelCase for functions" — `void restoreDatabase() {}`.
  - "UpperCamelCase for classes, enum types, typedefs, and type parameters" — `class Animal {}`, `typedef Predicate<T> = bool Function(T value);`.
  - **What's Dart-specific**: the JavaScript parent's rule is "Use *consistent* capitalization" — pick a convention and stick to it — and its Good example uses `DAYS_IN_WEEK`. The Dart port renames the rule "Use the *correct* capitalization" and puts `DAYS_IN_WEEK` in the **Bad** block, because Dart's community convention is fixed.
- **Function callers and callees should be close**: "If a function calls another, keep those functions vertically close in the source file. Ideally, keep the caller right above the callee. We tend to read code from top-to-bottom, like a newspaper. Because of this, make your code read that way."
  - How: order a class's members by the call graph — `showSpecifications()` first, then `showPlatform()` with its helpers `getOS()` and `getChipset()`, then `showDisplay()` with `getResolution()`.

## Key Concepts
- ***Effective Dart*** — the Dart team's style, documentation, usage and design guidelines; the guide's style authority.
- **lowerCamelCase** — first word lowercase, later words capitalized: variables, constants, functions, methods, parameters.
- **UpperCamelCase** — every word capitalized: classes, enum types, typedefs, type parameters.
- **SCREAMING_CAPS** — `DAYS_IN_WEEK`; correct in JavaScript and many other languages, **Bad** in Dart.
- **snake_case identifiers** — `restore_database`; Bad for Dart functions.
- **Newspaper order** — the high-level member first, then the members it calls, so a reader descends in detail as they read down.
- **Caller / callee** — the function that calls, and the function it calls.

## Mental Models
- **If a convention exists, it isn't a debate.** "DO NOT ARGUE" works in Dart because *Effective Dart* has already settled most questions; follow it and spend review time on structure.
- **Read a class like an article.** Headline first (`showSpecifications`), then each section (`showPlatform`, `showDisplay`), each followed by its details.
- **Case carries meaning in Dart.** UpperCamelCase means a type; lowerCamelCase means a value or function — constants included. A `DAYS_IN_WEEK` in Dart code reads as foreign.

## Anti-patterns
- **Formatting debates** in review.
- **SCREAMING_CAPS constants** (`const DAYS_IN_WEEK = 7;`) carried over from other languages.
- **UpperCamelCase values** (`const Bands = […]`).
- **snake_case functions** (`void restore_database() {}`).
- **Lowercase types** (`class animal {}`, `typedef predicate<T> …`).
- **Members in arbitrary order** — the guide's Bad `Smartphone` scatters `getOS`, `showPlatform`, `getResolution`, `showSpecifications`, `getChipset`, `showDisplay`, so following any call means scrolling.

## Code Examples

```dart
// Bad
const DAYS_IN_WEEK = 7;

const Bands = ['AC/DC', 'Led Zeppelin', 'The Beatles'];

void restore_database() {}

class animal {}

typedef predicate<T> = bool Function(T value);

// Good
// lowerCamelCase for constant names
const daysInWeek = 7;
const bands = ['AC/DC', 'Led Zeppelin', 'The Beatles'];

// lowerCamelCase for functions
void restoreDatabase() {}

// UpperCamelCase for classes, enum types, typedefs, and type parameters
class Animal {}
typedef Predicate<T> = bool Function(T value);
```
- **What it demonstrates**: one convention per kind of identifier, with constants on the value side of the line.

## Reference Tables

| Identifier | Dart case | Good | Bad |
|---|---|---|---|
| Constant | lowerCamelCase | `daysInWeek` | `DAYS_IN_WEEK` |
| Top-level value | lowerCamelCase | `bands` | `Bands` |
| Function / method | lowerCamelCase | `restoreDatabase` | `restore_database` |
| Class | UpperCamelCase | `Animal` | `animal` |
| Enum type | UpperCamelCase | *(named in the rule, no example)* | — |
| Typedef | UpperCamelCase | `Predicate<T>` | `predicate<T>` |
| Type parameter | UpperCamelCase | `T` | — |

The guide's list stops at identifiers. *Effective Dart* also sets the case for libraries, packages, directories, source files and import prefixes (`lowercase_with_underscores`) — not covered here.

## Worked Example
**Newspaper order for `Smartphone`.** The call graph:

- `showSpecifications()` calls `showPlatform()` and `showDisplay()`
  - `showPlatform()` calls `getOS()` and `getChipset()`
  - `showDisplay()` calls `getResolution()`

The guide's Good order is a depth-first walk of that graph, each caller directly above what it calls:

```dart
class Smartphone {
  // ...

  void showSpecifications() {
    showPlatform();
    showDisplay();
  }

  void showPlatform() {
    final os = getOS();
    final chipset = getChipset();
    // ...
  }

  String getOS() {
    // ...
  }

  String getChipset() {
    // ...
  }

  void showDisplay() {
    final resolution = getResolution();
    // ...
  }

  String getResolution() {
    // ...
  }
}
```

**How to apply it**: start with the entry point (the method outside code calls), then write out the methods it calls, in the order it calls them, each followed by its own helpers before moving to the next sibling. A reader who stops after the first method has the summary; one who keeps going gets the detail in the order they need it.

## Key Takeaways
1. **Don't argue about formatting**; *Effective Dart* is the reference.
2. **Constants are lowerCamelCase in Dart** — `daysInWeek`, never `DAYS_IN_WEEK`. This reverses the JavaScript parent's Good example.
3. **lowerCamelCase for values and functions; UpperCamelCase for classes, enum types, typedefs and type parameters.**
4. **Callers directly above callees** — order members by a depth-first walk of the call graph.

## Connects To
- **Ch 2**: the searchable-names rule already declared `setupTimeInMinutes` in lowerCamelCase.
- **Ch 3**: one level of abstraction per function is what makes newspaper order possible — each level is a separate member to place.
- **Ch 11**: the other half of reading code top-down: no banner comments splitting it into sections.
- **`clean-code-java`** ch. 5 (Formatting): the newspaper metaphor, vertical openness and density, and the book's file-size and line-length figures.
- **`clean-code-javascript` Ch 10**: the parent chapter, where capitalization is a team choice.
