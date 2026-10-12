# Chapter 7: Objects and Data Structures

## Core Idea
Don't expose an object's fields; expose **properties** and **intention-revealing methods**, and make state read-only from outside unless callers genuinely need to change it. The source titles the first rule with JavaScript's word — "Use getters and setters" — but in C# the mechanism is the **property**: `public double Balance { get … }` over a private `_balance`, with `WithdrawBalance` and `DepositBalance` as the only ways in.

## Frameworks Introduced
- **Use getters and setters** (in C#: properties) — "In C# / VB.NET you can set `public`, `protected` and `private` keywords for methods. Using it, you can control properties modification on an object." The source's six reasons:
  1. "When you want to do more beyond getting an object property, you don't have to look up and change every accessor in your codebase."
  2. "Makes adding validation simple when doing a `set`."
  3. "Encapsulates the internal representation."
  4. "Easy to add logging and error handling when getting and setting."
  5. "Inheriting this class, you can override default functionality."
  6. "You can lazy load your object's properties, let's say getting it from a server."
  - "Additionally, this is part of Open/Closed principle."
  - How: `public double Balance = 1000;` (a public field anyone can `-= 100`) → private `_balance`, a get-only `Balance` property, and methods that enforce the rules (`WithdrawBalance` throws when the amount exceeds the balance).
- **Make objects have private/protected members**
  - How: `public string Name { get; set; }` assigned in a constructor → a C# 12 **primary constructor** plus a **get-only auto-property**: `class Employee(string name) { public string Name { get; } = name; }`. The value is set once, at construction, and can't be reassigned from outside.

## Key Concepts
- **Field** — raw storage (`public double Balance = 1000;`); no hook for validation, logging, or change.
- **Property** — a member with `get`/`set` accessors that reads like a field but runs code.
- **Auto-property** — `{ get; set; }`; the compiler supplies the backing field.
- **Get-only auto-property** — `{ get; }`; assignable only in a constructor or initializer.
- **Private setter** — `{ get; private set; }`; readable everywhere, writable only inside the class (used in Ch 8).
- **Primary constructor** — `class Employee(string name)`; C# 12 parameters in scope for the whole class body.
- **Intention-revealing mutator** — a method named for the business operation (`WithdrawBalance`) rather than a setter.

## Mental Models
- **A public field is a promise you can never take back.** Switching it to a property later is a binary-breaking change and every `-=` in the codebase already bypasses whatever rule you want to add. Start with the property.
- **Expose operations, not storage.** "Buy shoes" is `WithdrawBalance(price)`, not `Balance -= 100`. The method can refuse; the field can't.
- **Default to read-only.** `{ get; }` until a caller proves it needs to write, then `{ get; private set; }`, then a method — `{ get; set; }` last.

## Anti-patterns
- **Public mutable fields** — `public double Balance = 1000;` lets any caller drain the account.
- **Public setters on values that shouldn't change after construction** — `Employee.Name { get; set; }`.
- **Setters that bypass business rules** — `Balance` writable directly when withdrawals must be validated.

## Code Examples
From an exposed field to an encapsulated balance:

```csharp
// Bad
class BankAccount
{
    public double Balance = 1000;
}

var bankAccount = new BankAccount();

// Fake buy shoes...
bankAccount.Balance -= 100;

// Good
class BankAccount
{
    private double _balance = 0.0D;

    public double Balance
    {
        get
        {
            return _balance;
        }
    }

    public BankAccount(double balance = 1000)
    {
        _balance = balance;
    }

    public void WithdrawBalance(int amount)
    {
        if (amount > _balance)
        {
            throw new Exception("Amount greater than available balance.");
        }

        _balance -= amount;
    }

    public void DepositBalance(int amount)
    {
        _balance += amount;
    }
}

var bankAccount = new BankAccount();

// Buy shoes...
bankAccount.WithdrawBalance(price);

// Get balance
balance = bankAccount.Balance;
```
- *Source snippet lightly repaired: `pubic` → `public`, `BankAccount(balance = 1000)` → `BankAccount(double balance = 1000)`, single-quoted message → string.*
- **What it demonstrates**: callers can still *read* `Balance`, but can only change it through operations that enforce the rule. The overdraft check exists in one place.

## Worked Example
**Private members via a primary constructor** — the source's second rule, which shows how much boilerplate C# 12 removes.

**Bad** — a settable property, assigned in an explicit constructor:

```csharp
class Employee
{
    public string Name { get; set; }

    public Employee(string name)
    {
        Name = name;
    }
}

var employee = new Employee("John Doe");
Console.WriteLine(employee.Name); // Employee name: John Doe
```

Anything holding an `Employee` can write `employee.Name = "Someone Else"`. Nothing in the domain asked for that.

**Good** — the constructor parameter initializes a get-only property:

```csharp
class Employee(string name)
{
    public string Name { get; } = name;
}

var employee = new Employee("John Doe");
Console.WriteLine(employee.Name); // Employee name: John Doe
```

The caller's code is identical — reading `Name` still works — but the setter is gone. Four lines of constructor boilerplate disappear, and the type now states its invariant: an employee's name is fixed at creation.

**One caution the source doesn't raise**: a primary-constructor parameter (`name`) stays in scope for the whole class and is mutable inside it. Capturing it into a get-only property, as here, is the safe pattern; using `name` directly in methods quietly creates a hidden mutable field.

## Key Takeaways
1. In C#, "getters and setters" means **properties**: never expose public fields.
2. Properties give you **validation, logging, lazy loading and overriding** later without touching callers.
3. **Mutate through named operations** (`WithdrawBalance`), not through setters.
4. **Default to `{ get; }`**; open up to `private set` or a method only when needed.
5. **Primary constructor + get-only property** is the C# 12 short form of an immutable member.

## Connects To
- **Ch 3**: "Don't add unneeded context" — properties named `Make`, not `CarMake`.
- **Ch 8**: `TaxData { get; private set; }` is the next rung — readable outside, settable only by the class's own `SetTax`.
- **Ch 9**: the source ties encapsulation to OCP — behaviour can change behind the property.
- **clean-code-java** ch06 (Objects and Data Structures): the deeper object/data-structure asymmetry and the Law of Demeter, which this source omits.
- **clean-code-typescript** ch04: the same rule with `readonly` and `Readonly<T>`.
