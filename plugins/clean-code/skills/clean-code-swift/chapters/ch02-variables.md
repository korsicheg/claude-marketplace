# Chapter 2: Variables

## Core Idea
A name should tell the reader what a value **means**, be **searchable**, and use **one word per concept**. In Swift that also means letting the type system hold the type, binding optionals to named constants instead of force-unwrapping, and letting the enclosing type supply context.

## Frameworks Introduced
- **Use meaningful and pronounceable variable names**: `currentDateStr` → `currentDate`.
  - When to use: any name carrying a type tag (`Str`, `Arr`, `Dict`) or an abbreviation you can't say aloud.
  - How: name the meaning. The guide's Bad labels: *Unclear Variable Name*, *Inconsistent Naming*, *Potential for Mistakes*; its Good labels: *Clear Variable Name*, *Type Consistency*, *Enhanced Readability*, *Easier Maintenance*.
- **Use the same vocabulary for the same type of variable**: `getUserInfo()`, `getClientData()`, `getCustomerRecord()` → `getUser()`.
  - When to use: when several names refer to one entity.
  - How: pick one noun and one verb per concept and use them everywhere.
- **Use searchable names**: "We will read more code than we write. It is important that the code we write is readable and searchable."
  - When to use: every literal whose meaning isn't obvious at the call site.
  - How: bind it to a named constant: `let millisecondsPerDay = 86400000`. Benefits named: *Descriptive Variable Name*, *Enhanced Clarity*, *Easier Maintenance* (one place to change).
- **Use explanatory variables**: replace `match![1]`, `match![2]` with named `city` and `zipCode`, extracted inside `if let match = …`.
  - When to use: any expression whose parts are read by index or force-unwrapped.
  - How: bind the optional with `if let`, then name each part. The Bad side's *Risk of Runtime Errors* label is the Swift-specific one: "Force unwrapping can lead to crashes if no matches are found."
- **Avoid mental mapping**: "Explicit is better than implicit." `locations.forEach({ l in … dispatch(l) })` → `location`.
  - When to use: closure parameters and loop variables in bodies longer than one line.
  - How: name the element for what it is. The guide's comment inside the Bad loop says it all: "Wait, what's `l` for again?"
- **Avoid unnecessary context**: `class User { var userName; var userAge }` → `var name; var age`.
  - When to use: properties that repeat their type's name.
  - How: drop the prefix; the access site (`user.name`) supplies the context. Named risk: *Maintenance Challenges* — renaming the type means renaming every property.

## Key Concepts
- **Type tag** — a type encoded in a name (`currentDateStr`); redundant where the declaration and the compiler already know the type.
- **Vocabulary consistency** — one noun per entity across all names (`User`, not User/Client/Customer).
- **Magic number** — an unexplained literal such as `86400000`; a *Lack of Context* and *Reduced Readability*.
- **Named constant** — a `let` binding that gives a literal a searchable name.
- **Explanatory variable** — a name given to a sub-part of an opaque expression (`city`, `zipCode`).
- **Force unwrap (`!`)** — asserts an optional is non-`nil` and traps at runtime if not; the guide's Bad regex example uses it on every access.
- **Optional binding (`if let`)** — unwraps an optional into a named constant only when it has a value; the guide's *Safe Handling of Matches*.
- **Mental mapping** — forcing the reader to remember what a short name stands for.
- **Unnecessary context** — repeating the enclosing type's name in its own members.

## Mental Models
- **Let the type system carry the type; let the name carry the meaning.** Swift infers and checks types, so a type tag in a name adds nothing the compiler doesn't already enforce — and goes stale when the type changes.
- **Every `!` is a crash you've chosen in advance.** The explanatory-variables rule doubles as an optional-safety rule: when you name the parts, bind the optional at the same time.
- **Short closure parameters are fine when the closure is short.** The guide itself writes `.map { $0.linesOfCode }` and `.filter { isActiveClient(client: $0) }` (Ch 3–4). Mental mapping bites when a closure spans several lines — that's where `l` becomes "what's `l` again?".
- **Read a property at its access site**: `user.name` already says "user". Name members for how they read there.

## Code Examples
Explanatory variables, the guide's Swift version (the one rule here with a Swift-specific safety angle):

```swift
let address = "One Infinite Loop, Cupertino 95014"
let cityZipCodeRegex = try! NSRegularExpression(
  pattern: "^[^,\\]+[,\\\\\\s]+(.+?)\\s*(\\d{5})?$"
)

if let match = cityZipCodeRegex.firstMatch(in: address) {
    let city = (address as NSString).substring(
      with: match.range(at: 1)
    )
    let zipCode = (address as NSString).substring(
      with: match.range(at: 2)
    )

    saveCityZipCode(city, zipCode)
}
```

- **What it demonstrates**: optional binding replaces two force-unwrapped, index-addressed calls, and each capture gets a name before use.

Avoid unnecessary context:

```swift
class User {
    var name: String
    var age: Int

    init(name: String, age: Int) {
        self.name = name
        self.age = age
    }
}
```

## Reference Tables

| Rule | Bad | Good |
|---|---|---|
| Meaningful names | `currentDateStr` | `currentDate` |
| Same vocabulary | `getUserInfo`, `getClientData`, `getCustomerRecord` | `getUser` |
| Searchable names | `setTimeout(blastOff, 86400000)` | `let millisecondsPerDay = 86400000` |
| Explanatory variables | `address.match(regex)![1]` | `if let match …` → `city`, `zipCode` |
| Mental mapping | `{ l in … dispatch(l) }` | `{ location in … dispatch(location) }` |
| Unnecessary context | `User.userName`, `User.userAge` | `User.name`, `User.age` |

## Worked Example
The searchable-names rule, read with its JavaScript heritage in view.

**Bad**, as the guide writes it:

```swift
// What the heck does 86400000 stand for?
setTimeout(blastOff, 86400000)
```

**Good**:

```swift
// Declare them as `let` or `var` in uppercase letters.
let millisecondsPerDay = 86400000

setTimeout(blastOff, millisecondsPerDay)
```

The rule is sound and the guide names three costs of the literal — *Unclear Magic Number*, *Lack of Context*, *Reduced Readability* — and one gain of the constant: *Easier Maintenance*, because "changes to the value can be made in one place."

Two details are JavaScript leftovers. `setTimeout` doesn't exist in Swift; the Swift equivalents (`DispatchQueue.main.asyncAfter(deadline:)`, `Task.sleep(for:)`) take seconds or a `Duration`, not milliseconds — exactly the unit confusion a named constant guards against. And the comment's "uppercase letters" contradicts the line under it: the snippet uses `millisecondsPerDay`, lowerCamelCase, which is the Swift convention for constants. **Follow the code, not the comment.**

## Source Caveats
- `address.match(…)` in the Bad regex example is not a Swift API, and Foundation's `firstMatch(in:)` also takes `options:` and `range:`; read both snippets as pseudocode for the shape.
- The guide uses `NSRegularExpression`; it never mentions Swift's native `Regex` and its named captures.
- The Good regex example keeps `try!` for building the pattern; the rule's force-unwrap warning applies to the *match*, which can legitimately fail, not to a pattern known at compile time.

## Anti-patterns
- **Type tags in names** (`currentDateStr`): *Potential for Mistakes* when the type changes or a reader trusts the tag.
- **Synonym drift** (`getUserInfo`/`getClientData`/`getCustomerRecord`): three names, one concept, and soon three implementations.
- **Bare literals** (`86400000`): unsearchable and changed in many places at once.
- **Force-unwrapping a fallible result** (`match(regex)!`): a crash path for input that simply didn't match.
- **Single-letter closure parameters in long closures**: the reader carries the mapping in their head.
- **Prefixing members with their type's name**: `user.userName` reads the context twice.

## Key Takeaways
1. **Name the meaning, not the type.** The declaration carries the type.
2. **One word per concept** across the codebase.
3. **Bind every meaningful literal to a named `let`** — searchable and changed in one place.
4. **Unwrap with `if let`, then name the parts** — explanatory variables and crash safety in one move.
5. **Name closure parameters** once the closure is longer than a line.
6. **Drop the type's name from its members**; the access site supplies it.

## Connects To
- **Ch 3**: "Function names should say what they do" applies the same discipline to functions, and default arguments (also in Ch 3) remove an optional rather than unwrapping it.
- **Ch 5**: "Make decisions based on an object" replaces string literals like `"v8"` with enum cases — the next step after naming a literal.
- **Ch 10**: formatting covers spacing, not naming; naming conventions beyond these six rules are left to the Google Swift Style Guide the source cites.
- **`clean-code-java`** (ch02, Meaningful Names): the full naming chapter — intention-revealing names, the scope-length rule — that these six rules condense.
