# Chapter 4: Objects and Data Structures

## Core Idea
Encapsulate object state behind accessors and closures so that the internal representation can change, validation can be added, and properties cannot be deleted out from under your own methods.

*(A short chapter — two rules — but both are prerequisites for Ch 5 and Ch 6.)*

## Frameworks Introduced
- **Use getters and setters**: access data through methods rather than reading/writing raw properties.
  - When to use: any object property that is part of a public surface.
  - How: return an object exposing `getX`/`setX` instead of the bare field.
  - Why it works — the guide's five reasons:
    1. You can do more than get a property without changing every accessor in the codebase.
    2. Validation on `set` becomes simple.
    3. The internal representation is encapsulated.
    4. Logging and error handling are easy to add on get/set.
    5. You can **lazy load** properties — e.g. fetch from a server on first access.
- **Make objects have private members**: hide state in a closure.
  - When to use: whenever external code must not be able to reach, overwrite, or `delete` a field.
  - How: declare the state as a local variable in a factory function and return only the methods that close over it. (The guide notes this is the ES5-and-below technique; it remains the clearest closure-based approach.)
  - Failure mode it prevents: `delete employee.name` silently breaking `getName()`.

## Key Concepts
- **Getter / setter** — a method mediating read/write access to internal state.
- **Encapsulation** — callers depend on the accessor, not on the field's existence or shape.
- **Closure privacy** — state captured in a function scope, unreachable from outside.
- **Factory function** — a plain function returning an object literal of methods (`makeBankAccount`, `makeEmployee`), as opposed to a constructor.
- **Lazy loading** — deferring a property's computation or fetch until the getter is first called.
- **Prototype property** — a field on `this`, publicly readable, writable, and **deletable**.

## Mental Models
- **Think of a bare property as a public API you never designed.** Every `obj.field = x` in the codebase is a caller you must support forever.
- **Use the setter as the only place validation can't be skipped.** If assignment is direct, validation is optional; if it's a method, it isn't.
- **Think of a closure as the only genuinely private scope in ES5-era JavaScript.** Convention (`_name`) asks nicely; a closure makes it impossible.

## Anti-patterns
- **Exposing mutable balance-like state** (`account.balance = 100`): no validation point, no logging point, and the representation is frozen into every call site.
- **Public fields on the prototype** (`this.name` + `Employee.prototype.getName`): `delete employee.name` makes `getName()` return `undefined` — the object breaks its own contract from the outside.
- **Adding getters/setters everywhere reflexively**: the rule is that accessors "could be better than simply looking for a property" — it buys the five benefits above, and where none apply, the indirection is cost without return.

## Code Examples
Getters and setters, giving you a validation seam:

```javascript
// Bad
function makeBankAccount() {
  return {
    balance: 0
  };
}
const account = makeBankAccount();
account.balance = 100;

// Good
function makeBankAccount() {
  // this one is private
  let balance = 0;

  // a "getter", made public via the returned object below
  function getBalance() {
    return balance;
  }

  // a "setter", made public via the returned object below
  function setBalance(amount) {
    // ... validate before updating the balance
    balance = amount;
  }

  return {
    getBalance,
    setBalance
  };
}
const account = makeBankAccount();
account.setBalance(100);
```
- **What it demonstrates**: `balance` is no longer reachable at all — the closure supplies privacy and the setter supplies the single place validation, logging, or a server round-trip can live.

## Reference Tables

| Need | Public property | Getter/setter + closure |
|---|---|---|
| Validate on write | impossible | `setBalance` validates |
| Change internal representation | breaks every call site | callers unaffected |
| Log / handle errors on access | scattered | one place |
| Lazy load from server | no hook | getter does it on demand |
| Survive `delete obj.field` | no | yes — field isn't on the object |

## Worked Example
The `Employee` case, which shows privacy as a *correctness* issue, not a purity one.

Public-field version:

```javascript
const Employee = function(name) {
  this.name = name;
};

Employee.prototype.getName = function getName() {
  return this.name;
};

const employee = new Employee("John Doe");
console.log(`Employee name: ${employee.getName()}`); // Employee name: John Doe
delete employee.name;
console.log(`Employee name: ${employee.getName()}`); // Employee name: undefined
```

The object has a method whose contract is "return the employee's name", and any outside code can break that contract with one statement. `getName()` did nothing wrong; the state it reads was never hers to guard.

Closure version:

```javascript
function makeEmployee(name) {
  return {
    getName() {
      return name;
    }
  };
}

const employee = makeEmployee("John Doe");
console.log(`Employee name: ${employee.getName()}`); // Employee name: John Doe
delete employee.name;
console.log(`Employee name: ${employee.getName()}`); // Employee name: John Doe
```

`delete employee.name` now deletes a property that does not exist — a no-op. `name` lives in the factory's scope, reachable only by the closure. The method's contract is enforceable because the state backing it is unreachable.

**Trade-off to weigh:** each call to `makeEmployee` creates fresh function objects rather than sharing them on a prototype. For the object counts in ordinary application code this is irrelevant; for millions of instances, measure before choosing (and see Ch 3, *Don't over-optimize*, before assuming it matters).

## Key Takeaways
1. Prefer accessors over raw property access when you need validation, logging, lazy loading, or freedom to change the representation.
2. A setter is the **only** place you can guarantee validation runs.
3. Closures give real privacy; `this.x` gives none — external `delete` can break your own methods.
4. The factory-function pattern (`makeThing` returning methods) is the idiomatic JS way to get private members without classes.
5. Encapsulation here is what makes the SOLID refactors in Ch 6 possible — callers depend on behavior, not shape.

## Connects To
- **Ch 5 (Classes)**: when objects get larger and need inheritance, move from these factories to ES6 classes — "prefer small functions over classes until you find yourself needing larger and more complex objects."
- **Ch 6 (SOLID)**: encapsulated internals are the precondition for OCP and DIP; callers bind to the accessor contract, not the field.
- **Ch 3 (Functions)**: "Avoid Side Effects" — centralizing mutation behind a setter is the same instinct at object scope.
- **Ch 2 (Variables)**: "Don't add unneeded context" — `account.getBalance()`, not `account.getAccountBalance()`.
