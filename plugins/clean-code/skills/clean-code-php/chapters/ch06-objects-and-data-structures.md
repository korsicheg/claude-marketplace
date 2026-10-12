# Chapter 6: Objects and Data Structures

## Core Idea
Hide an object's data behind methods that express what callers may *do* with it (`withdraw()`, `deposit()`, `getBalance()`), and **make members `private` by default** — because `protected` gives every subclass the same power to break you that `public` gives every caller.

## Frameworks Introduced
- **Use object encapsulation**: "In PHP you can set `public`, `protected` and `private` keywords for methods. Using it, you can control properties modification on an object." The guide's six reasons:
  1. "When you want to do more beyond getting an object property, you don't have to look up and change every accessor in your codebase."
  2. "Makes adding validation simple when doing a `set`."
  3. "Encapsulates the internal representation."
  4. "Easy to add logging and error handling when getting and setting."
  5. "Inheriting this class, you can override default functionality."
  6. "You can lazy load your object's properties, let's say getting it from a server."
  - It is also "part of Open/Closed principle" (Ch 8): behaviour can change behind the method without callers changing.
  - How: replace `$bankAccount->balance -= 100;` with intention-revealing operations — `withdraw(int $amount)` (which refuses an overdraft by throwing), `deposit(int $amount)`, `getBalance(): int`.
- **Make objects have private/protected members** — the three visibility levels ranked by blast radius:
  - "`public` methods and properties are most dangerous for changes, because some outside code may easily rely on them and you can't control what code relies on them. **Modifications in class are dangerous for all users of class.**"
  - "`protected` modifier are as dangerous as public, because they are available in scope of any child class. This effectively means that difference between public and protected is only in access mechanism, but encapsulation guarantee remains the same. **Modifications in class are dangerous for all descendant classes.**"
  - "`private` modifier guarantees that code is **dangerous to modify only in boundaries of single class**" — no "Jenga effect".
  - Rule: "**use `private` by default and `public/protected` when you need to provide access for external classes.**" The guide cites Fabien Potencier's post on protected vs private.

## Key Concepts
- **Encapsulation** — controlling access to an object's state so that it can change only through the object's own methods.
- **Visibility** — PHP's `public` / `protected` / `private` modifiers on properties, methods and (since 7.1) class constants.
- **Accessor** — a getter (`getName()`) or mutating method (`withdraw()`) standing between callers and a property.
- **Invariant** — a rule the object guarantees about its own state (a balance never goes below the amount withdrawn); only enforceable if the state is private.
- **Jenga effect** — the guide's name for a change in one place collapsing code elsewhere that leaned on it.
- **Blast radius** — who can break when a member changes: everyone (`public`), every subclass (`protected`), only this class (`private`).

## Mental Models
- **Visibility is a promise about who can depend on you.** `public` promises it to the world, `protected` to every future subclass you'll never see; `private` promises nothing.
- **`protected` is public to the inheritance tree.** For encapsulation purposes, treat it as public — the guide says the guarantee is the same.
- **Ask for behaviour, not data.** `withdraw($price)` lets the account enforce its rules; `->balance -= $price` lets every caller bypass them.
- **Start closed, open on demand.** Loosening `private` to `public` later is a safe, local change; tightening `public` to `private` breaks unknown callers.

## Anti-patterns
- **Public mutable state** (`public $balance = 1000;`): any caller can overdraw the account.
- **`protected` "for flexibility"**: every subclass becomes a dependent you can't see, and the class can no longer change freely.
- **Arithmetic on another object's property** (`$account->balance -= 100`): the rule about overdrafts lives nowhere.
- **Getters added mechanically for every property**: encapsulation is about the operations the domain needs; the guide's `BankAccount` exposes `withdraw`/`deposit`, not `setBalance`.

## Code Examples
```php
class BankAccount
{
    private $balance;

    public function __construct(int $balance = 1000)
    {
      $this->balance = $balance;
    }

    public function withdraw(int $amount): void
    {
        if ($amount > $this->balance) {
            throw new \Exception('Amount greater than available balance.');
        }

        $this->balance -= $amount;
    }

    public function deposit(int $amount): void
    {
        $this->balance += $amount;
    }

    public function getBalance(): int
    {
        return $this->balance;
    }
}

$bankAccount = new BankAccount();

// Buy shoes...
$bankAccount->withdraw($shoesPrice);

// Get balance
$balance = $bankAccount->getBalance();
```
- **What it demonstrates**: the overdraft rule now has exactly one home. Note that `deposit(-100)` would still be accepted — and reason 2 above is the point: there is now a single place to add that validation.

## Reference Tables

| Modifier | Who can depend on it | Who a change can break | Guide's default |
|---|---|---|---|
| `public` | any code | "all users of class" | only for the API you intend to offer |
| `protected` | the class and every descendant | "all descendant classes" | only when a subclass genuinely needs it |
| `private` | the class itself | only this class | **default** |

| Instead of | Write |
|---|---|
| `public $balance` | `private $balance` + `withdraw()` / `deposit()` / `getBalance()` |
| `echo $employee->name;` | `echo $employee->getName();` with `private $name` |
| `$account->balance -= $x` | `$account->withdraw($x)` |

## Worked Example
**The `Employee` name, made private.**

Bad — the property is public, so every reader of `$employee->name` is a dependent:

```php
class Employee
{
    public $name;

    public function __construct(string $name)
    {
        $this->name = $name;
    }
}

$employee = new Employee('John Doe');
echo 'Employee name: ' . $employee->name;
```

Good — the property is private and exposed through a getter:

```php
class Employee
{
    private $name;

    public function __construct(string $name)
    {
        $this->name = $name;
    }

    public function getName(): string
    {
        return $this->name;
    }
}

$employee = new Employee('John Doe');
echo 'Employee name: ' . $employee->getName();
```

What changed is not the output but the **set of things that can break**. If `Employee` later stores first and last names separately, the public version breaks every caller; the private version changes `getName()` and nothing else. And because the property is `private` rather than `protected`, a future `Manager extends Employee` can't come to depend on it either — which is exactly the guide's argument against `protected`.

## Key Takeaways
1. **Expose operations, not fields** — `withdraw()` and `deposit()` instead of a public `$balance`.
2. **`private` by default**; open to `public` or `protected` only on demand.
3. **Treat `protected` as public** for encapsulation purposes — every subclass is a dependent.
4. **Accessors are seams**: validation, logging, lazy loading and representation changes all go there without touching callers.
5. **Enforce invariants inside the object** — the overdraft check lives in `withdraw()`, nowhere else.

## Connects To
- **Ch 7**: `final` classes complete the argument — with no subclasses, `protected` has no audience at all.
- **Ch 8 (OCP)**: the guide links encapsulation to Open/Closed — behaviour changes behind a stable method.
- **Ch 4 (Avoid side effects)**: centralizing writes to state in one place is the same instinct at object scope.
- **clean-code-java ch06 (Objects and Data Structures)**: the book's object/data-structure anti-symmetry and the Law of Demeter, which this guide omits.
- **Fabien Potencier, "Pragmatism over theory: Protected vs Private"**: the post the guide cites.
