# Chapter 8: Classes

## Core Idea
Two rules: **chain methods** so a sequence of operations reads as one expression — in C#, via **extension methods** that return their receiver — and **prefer composition over inheritance**, inheriting only for a genuine *is-a* with real reuse. The C# fix for the classic `EmployeeTaxData : Employee` mistake is a small **`record`** held as a **nullable property**.

## Frameworks Introduced
- **Use method chaining** — "This pattern is very useful and commonly used in many libraries. It allows your code to be expressive, and less verbose."
  - How (C#): a `static` class of **extension methods** (`this List<T> list`) that perform an operation and `return list;` — so calls compose: `list.FluentAdd(1).FluentInsert(0, 0).FluentReverse()`.
  - Why extension methods: they add a chainable surface to a type you don't own (`List<T>`) without subclassing it.
- **Prefer composition over inheritance** — "As stated famously in *Design Patterns* by the Gang of Four, you should prefer composition over inheritance where you can … if your mind instinctively goes for inheritance, try to think if composition could model your problem better."
  - The source's three conditions under which "inheritance makes more sense than composition":
    1. "Your inheritance represents an 'is-a' relationship and not a 'has-a' relationship (Human->Animal vs. User->UserDetails)."
    2. "You can reuse code from the base classes (Humans can move like all animals)."
    3. "You want to make global changes to derived classes by changing a base class (Change the caloric expenditure of all animals when they move)."
  - How: `class EmployeeTaxData : Employee` ("Bad because Employees 'have' tax data. EmployeeTaxData is not a type of Employee") → `record EmployeeTaxData(string Ssn, double Salary)` held by `Employee` as `EmployeeTaxData? TaxData { get; private set; }`.

## Key Concepts
- **Method chaining / fluent interface** — each call returns an object the next call can be made on.
- **Extension method** — a `static` method whose first parameter is marked `this`, callable as if it were an instance method.
- **Composition** — a class *has* another object as a member and delegates to it.
- **Inheritance** — a class *is* a specialized form of its base and inherits its members.
- **is-a vs has-a** — the test for which relationship you are modelling.
- **`record`** — a reference type with value equality and a concise positional syntax (C# 9).
- **Nullable reference annotation** — `EmployeeTaxData?`: may legitimately be `null` (no tax data yet). The only place the source's examples use one.

## Mental Models
- **Say the relationship out loud.** "An employee *has* tax data" settles it; "tax data *is an* employee" is absurd.
- **Use the three conditions as a checklist.** The source calls them "a decent list", not a law; the strict reading (all three, as the TypeScript sibling applies it) is the safe default. An is-a with no reuse is an interface; reuse without is-a is composition; is-a plus reuse where you *don't* want base changes to propagate is still composition.
- **A chain reads like a sentence only if each link is one thing.** `FluentAdd`, `FluentReverse`, `FluentClear` — each verb does one operation and hands the list on.

## Anti-patterns
- **Inheriting for reuse alone** — `EmployeeTaxData : Employee` to get `Name` and `Email`.
- **Duplicating base members in the subclass** — the Bad example redeclares `Name` and `Email`.
- **Mutating fluent APIs mistaken for pure ones.** The source's `Fluent*` extensions change the list in place *and* return it; a reader who expects LINQ-style new sequences gets surprised. (Observation; the source doesn't discuss it — see Ch 4 on side effects.)

## Code Examples
Fluent extension methods on `List<T>`:

```csharp
public static class ListExtensions
{
    public static List<T> FluentAdd<T>(this List<T> list, T item)
    {
        list.Add(item);
        return list;
    }

    public static List<T> FluentClear<T>(this List<T> list)
    {
        list.Clear();
        return list;
    }

    public static List<T> FluentForEach<T>(this List<T> list, Action<T> action)
    {
        list.ForEach(action);
        return list;
    }

    public static List<T> FluentInsert<T>(this List<T> list, int index, T item)
    {
        list.Insert(index, item);
        return list;
    }

    public static List<T> FluentRemoveAt<T>(this List<T> list, int index)
    {
        list.RemoveAt(index);
        return list;
    }

    public static List<T> FluentReverse<T>(this List<T> list)
    {
        list.Reverse();
        return list;
    }
}

internal static void ListFluentExtensions()
{
    List<int> list = [1, 2, 3, 4, 5];
    list = list
        .FluentAdd(1)
        .FluentInsert(0, 0)
        .FluentRemoveAt(1)
        .FluentReverse()
        .FluentForEach(value => Console.WriteLine(value))
        .FluentClear();
}
```
- *Source snippet lightly repaired: `value.WriteLine()` → `Console.WriteLine(value)`.*
- **What it demonstrates**: `List<T>`'s own `Add`, `Insert`, `Reverse` return `void` and so can't chain; six one-line extensions give it a fluent surface without touching the type.

## Worked Example
**Composition over inheritance — tax data.**

**Bad** — tax data inherits from employee to reuse `Name` and `Email`:

```csharp
class Employee
{
    private string Name { get; set; }
    private string Email { get; set; }

    public Employee(string name, string email)
    {
        Name = name;
        Email = email;
    }

    // ...
}

// Bad because Employees "have" tax data.
// EmployeeTaxData is not a type of Employee

class EmployeeTaxData : Employee
{
    private string Name { get; }
    private string Email { get; }

    public EmployeeTaxData(string name, string email, string ssn, string salary)
    {
         // ...
    }

    // ...
}
```

Run the three conditions. *Is-a?* No — tax data is not a kind of employee. *Reuse?* Not even that: the members are `private`, so the subclass redeclares them. *Want base changes to propagate?* Adding a `Department` to `Employee` would silently give every tax record a department. All three fail. (As written, it also doesn't compile: `Employee` has no parameterless constructor for the subclass to call.)

**Good** — the employee *has* tax data:

```csharp
record EmployeeTaxData(string Ssn, double Salary);

class Employee(string name, string email)
{
    public string Name { get; } = name;
    public string Email { get; } = email;
    public EmployeeTaxData? TaxData { get; private set; }

    public void SetTax(string ssn, double salary)
    {
        TaxData = new EmployeeTaxData(ssn, salary);
    }

    // ...
}
```
- *Source snippet lightly repaired: the record declared `string Salary` while `SetTax` passes a `double`; unified to `double`.*

Every piece is C#-idiomatic: a one-line positional `record` for the value, get-only properties from a primary constructor (Ch 7), and a `private set` so only `SetTax` can attach tax data. `EmployeeTaxData?` says, in the type, that an employee may have none yet — callers must handle `null`.

## Key Takeaways
1. **Chain** by returning the receiver; in C#, add chaining to types you don't own with **extension methods**.
2. Prefer **composition**; inherit when the source's checklist holds — **is-a, reuse, and wanted propagation**.
3. **Say it aloud**: "has" means a member, "is" means maybe a base class.
4. Model owned values as small **`record`s** held in **`{ get; private set; }`** properties.
5. Use a **nullable annotation** (`T?`) when "not yet set" is a legitimate state.

## Connects To
- **Ch 4**: the `Fluent*` methods mutate in place — a side effect worth naming.
- **Ch 7**: get-only properties and primary constructors, used again here.
- **Ch 9**: LSP's Square–Rectangle is what happens when the is-a test is passed on paper but fails in behaviour; DIP's `Manager` composes employees rather than inheriting from them.
- **clean-code-java** ch10 (Classes): class size measured in responsibilities, and cohesion — both absent from this source.
- **clean-code-typescript** ch05: the same three-condition test, with `return this` chaining.
