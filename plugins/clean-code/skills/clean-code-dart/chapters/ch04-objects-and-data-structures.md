# Chapter 4: Objects and Data Structures

## Core Idea
Dart gives you encapsulation in syntax, so use it sparingly and precisely: **a plain field until there is logic to run**, and **the `_` prefix for anything outside code has no business touching**. This is the chapter where the Dart port most clearly parts company with its JavaScript parent, which recommended accessors by default and closures for privacy.

*(A short chapter — two rules — but both feed Ch 5 and Ch 6.)*

## Frameworks Introduced
- **Use getters and setters only when necessary**: "Unlike other languages, in Dart it is recommended to use getters and setters only when there is some logic before using the attribute. If you just want to get or edit the attribute, don't use them."
  - When to use an accessor: when reading or writing the value has to *do* something — validate, compute, log, notify.
  - When not to: a private field wrapped in a getter and setter that only pass the value through. That's ceremony.
  - How: declare the field public (`int balance;`) and initialise it straight from the constructor (`BankAccount({this.balance = 0})`).
  - Why Dart can afford this (background, not stated in the guide): callers write `account.balance` whether `balance` is a field or a getter, so a field can later become a getter/setter pair with logic without changing a single caller. Wrapping it "just in case" buys nothing.
- **Use private methods and attributes when necessary**: "If a method or attribute has to be accessed only within the class, it must be private."
  - How: prefix the name with `_` and initialise it from a public constructor parameter through the initializer list — `Employee({required String name}) : _name = name;`.
  - What it prevents: outside code rewriting state it should only read or never see (`employee.name = 'Uncle Bob'`).

## Key Concepts
- **Field** — a class variable; in Dart it already behaves as an implicit getter (and setter, unless `final`).
- **Getter / setter** — `int get balance => _balance;` / `set balance(int amount) => _balance = amount;` — worth writing only when it carries logic.
- **`_` prefix (library privacy)** — a leading underscore makes a member private. Precisely, Dart privacy is per *library* (usually one file), not per class: code elsewhere in the same file can still reach `_name`. The guide's "only within the class" is the intent; the file is the actual boundary.
- **Initializer list** — the `: _name = name` after a constructor's parameters, which sets fields before the body runs; the bridge between a public named parameter and a private field.
- **Initializing formal** — `this.balance` in a constructor's parameter list, assigning the parameter to the field directly. The guide uses it for public fields; for the private `_name` it switches to the initializer list, so the caller-facing named parameter can stay `name:`.

## Mental Models
- **Think of a public field as a getter you haven't needed to write yet.** Because Dart's access syntax is the same either way, the decision can wait until there is logic.
- **Think of `_` as the default for state, and the public API as a choice.** Expose what callers must use; underscore the rest.
- **Use the file as the unit of privacy.** If two classes in one file can see each other's `_` members, that is Dart working as designed; move a class to its own file when the boundary matters.

## Anti-patterns
- **Pass-through accessors** — the guide's Bad `BankAccount`: a private `_balance`, a getter that returns it, a setter that assigns it, and nothing else.
- **Public mutable state that should be internal** — `String name;` on `Employee`, freely reassigned from outside.
- **Assuming `_` means class-private** — it is library-private; a second class in the same file is not locked out.
- **Treating "only when necessary" as "never"** — the guide reserves accessors for "some logic before using the attribute"; validation and derived values remain good reasons.

## Code Examples
Getters and setters only when necessary:

```dart
// Bad
class BankAccount {
  // "_" configure as private
  int _balance;

  int get balance => _balance;

  set balance(int amount) => _balance = amount;

  BankAccount({
    int balance = 0,
  }) : _balance = balance;
}

// Good
class BankAccount {
  int balance;
  // ...

  BankAccount({
    this.balance = 0,
    // ...
  });
}

final account = BankAccount();
account.balance = 100; // same call site in both versions
```
- **What it demonstrates**: the Bad and Good classes are indistinguishable to their callers. The four extra lines in Bad buy no validation, no logging, no computed value — only indirection.

Private attributes:

```dart
// Bad
class Employee {
  String name;

  Employee({required this.name});
}

final employee = Employee(name: 'John Doe');
employee.name = 'Uncle Bob'; // anyone can rewrite it

// Good
class Employee {
  String _name;

  Employee({required String name}) : _name = name;
}

final employee = Employee(name: 'John Doe');
print(employee.name); // Can't access outside the class.
```
- **What it demonstrates**: the public constructor parameter stays `name:` while the field becomes `_name`; the last line is a deliberate compile error showing the field is gone from the public surface. (From another library, that is; see Key Concepts.)

## Reference Tables

| Situation | Declare | Example |
|---|---|---|
| Callers read and write; no logic | public field | `int balance;` |
| Callers read; only the class writes | private field + getter | `int _count;` `int get count => _count;` |
| Writing must validate or notify | private field + setter with logic | `set balance(int v) { … }` |
| Value is derived | getter, no field | `double get area => width * height;` |
| Only the class uses it | private field or method | `String _name;` `void _recalculate()` |

*(The first and last rows are the guide's two rules; the middle rows are the "some logic" cases it leaves to the reader.)*

**How Dart's version differs from the JavaScript parent's chapter**

| Topic | `clean-code-javascript` | `clean-code-dart` |
|---|---|---|
| Accessors | Use getters and setters (five reasons) | Only when there's logic; plain fields otherwise |
| Privacy | Closures (`makeEmployee` returning methods) | `_` prefix + initializer list |

## Worked Example
Deciding whether `BankAccount.balance` needs an accessor, step by step.

1. **Start with a field.** `int balance;` with `BankAccount({this.balance = 0})`. Callers write `account.balance = 100`.
2. **A requirement arrives: balances can't go negative.** Now there is "some logic before using the attribute", so the accessor earns its place:
   - rename the field to `_balance`;
   - add `int get balance => _balance;`;
   - add a setter that checks the amount before assigning `_balance`.
3. **Callers don't change.** `account.balance = 100` still compiles and now passes through the check. Step 2 is exactly the guide's Bad shape *plus the logic that justifies it*.
4. **Had you written the accessors at step 1** "to be safe", you would have carried the indirection with no benefit until step 2, and gained nothing at step 2 either.

The guide states the rule without the reasoning; this sequence is the reasoning, and it rests on one Dart property: a field and a getter look the same at the call site.

## Key Takeaways
1. **Plain fields by default.** Write a getter or setter only when reading or writing runs logic.
2. **Pass-through accessors are noise**, and callers can't tell them from a field anyway.
3. **Underscore what callers don't need**: `_name`, set through the initializer list from a public named parameter.
4. **`_` is library-private, not class-private** — the file is the boundary.
5. This chapter **reverses the JavaScript parent's accessor rule**; don't carry JavaScript habits into Dart classes.

## Connects To
- **Ch 2**: "Don't add unneeded context" applies to fields too: `color`, not `carColor`.
- **Ch 5**: the classes in the cascade and composition examples use public fields with `required this.x` constructors, this chapter's default.
- **Ch 6**: the DIP and SRP examples store their collaborators as public fields; `_` would be the stricter choice.
- ***Effective Dart*** (Design): advises against wrapping a field in a getter and setter just to be safe, the same position this chapter takes.
- **`clean-code-javascript` Ch 4**: the parent chapter this one reverses.
