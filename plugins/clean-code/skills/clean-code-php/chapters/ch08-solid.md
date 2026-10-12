# Chapter 8: SOLID

## Core Idea
"**SOLID** is the mnemonic acronym introduced by Michael Feathers for the first five principles named by Robert Martin." The PHP guide works all five with one recurring move: **replace a base class — abstract or concrete — with an `interface`, and make every collaborator depend on that interface.** Where JavaScript could only describe implicit contracts, PHP declares them, and the engine refuses a class that doesn't honour one.

## Frameworks Introduced
- **Single Responsibility Principle (SRP)**: "As stated in Clean Code, 'There should never be more than one reason for a class to change'."
  - The suitcase image: "It's tempting to jam-pack a class with a lot of functionality, like when you can only take one suitcase on your flight." The cost: "if too much functionality is in one class and you modify a piece of it, it can be difficult to understand how that will affect other dependent modules."
  - How: `UserSettings` both changes settings and checks the user's credentials → extract `UserAuth` with `verifyCredentials(): bool`; `UserSettings` keeps `changeSettings()` and asks `UserAuth`.
- **Open/Closed Principle (OCP)**: "As stated by Bertrand Meyer, 'software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification.'" In practice: "allow users to add new functionalities without changing existing code."
  - How: `HttpRequester::fetch()` inspecting `$this->adapter->getName()` and calling `makeAjaxCall()` or `makeHttpCall()` → `interface Adapter { public function request(string $url): Promise; }`, with `fetch()` reduced to `return $this->adapter->request($url);`. A new transport is a new class; `HttpRequester` never changes.
- **Liskov Substitution Principle (LSP)**: formally, "If S is a subtype of T, then objects of type T may be replaced with objects of type S… without altering any of the desirable properties of that program (correctness, task performed, etc.)." Plainly: "if you have a parent class and a child class, then the base class and child class can be used interchangeably without getting incorrect results."
  - How: the Square–Rectangle example. "Mathematically, a square is a rectangle, but if you model it using the 'is-a' relationship via inheritance, you quickly get into trouble." Fix: a common `Shape` interface with `getArea(): int`; `Rectangle` and `Square` implement it independently. "A square, a rectangle, a rhombus and a parallelogram are separate shapes with their own properties, albeit similar."
- **Interface Segregation Principle (ISP)**: "Clients should not be forced to depend upon interfaces that they do not use."
  - How: a fat `interface Employee { work(); eat(); }` forces `RobotEmployee` to implement `eat()` ("robot can't eat, but it must implement this method") → split into `Workable` and `Feedable`, recombine as `interface Employee extends Feedable, Workable`, and let `RobotEmployee implements Workable` only. "Not every worker is an employee, but every employee is a worker."
- **Dependency Inversion Principle (DIP)**: two statements — "1. High-level modules should not depend on low-level modules. Both should depend on abstractions. 2. Abstractions should not depend upon details. Details should depend on abstractions."
  - In PHP practice: "if you've worked with PHP frameworks (like Symfony), you've seen an implementation of this principle in the form of Dependency Injection (DI). While they are not identical concepts, DIP keeps high-level modules from knowing the details of its low-level modules and setting them up. It can accomplish this through DI." The payoff: it "reduces the coupling between modules. Coupling is a very bad development pattern because it makes your code hard to refactor."
  - How: `Manager` takes a concrete `Employee` class that `Robot extends` → `interface Employee { public function work(): void; }`, implemented by `Human` and `Robot`; `Manager::__construct(Employee $employee)` now depends on the abstraction.

## Key Concepts
- **Reason to change** — an external force that would require editing the class; the unit SRP counts.
- **Open for extension / closed for modification** — new behaviour arrives as new code (a new `Adapter`), not edits to old code.
- **Substitutability** — any implementation can stand in for its declared type without changing results.
- **Fat interface** — an interface whose members no single client needs in full.
- **Interface inheritance** — `interface Employee extends Feedable, Workable`; PHP interfaces may extend several interfaces at once.
- **Dependency Injection (DI)** — supplying a collaborator from outside (constructor argument, container) rather than constructing it inside; the mechanism by which PHP frameworks deliver DIP.
- **Abstraction** — in this guide, almost always a PHP `interface`.

## Mental Models
- **Every SOLID fix in this guide ends in `interface`.** OCP: `Adapter`. LSP: `Shape`. ISP: `Workable`/`Feedable`. DIP: `Employee`. When a class hierarchy hurts, extract the interface and implement it flat.
- **A string-typed dispatch is an OCP violation with a name tag.** `if ($adapterName === 'ajaxAdapter')` is the branch every new adapter must edit.
- **Mutable setters are where LSP breaks.** The Square only misbehaves because `setWidth()`/`setHeight()` exist; the good version constructs shapes with their dimensions and offers no setters.
- **An empty method body is an ISP alarm.** A class implementing a method it can't meaningfully perform is depending on an interface it doesn't use.

## Anti-patterns
- **Classes that mix concerns** (`UserSettings` that also authenticates): two reasons to change in one file.
- **Behaviour selected by inspecting a name** (`getName()` then `if/elseif`): adding a variant means editing the dispatcher.
- **Inheriting for a mathematical "is-a"** (`Square extends Rectangle`): substitutability, not taxonomy, decides subtyping.
- **Stub implementations** (`RobotEmployee::eat()` doing nothing): a fat interface forcing lies.
- **Depending on a concrete class** (`Manager(Employee $employee)` where `Employee` is a class `Robot` extends): the high-level module is bound to a detail.
- **Constructing a collaborator inside a constructor** — see the SRP note in the Worked Example.

## Code Examples
```php
interface Workable
{
    public function work(): void;
}

interface Feedable
{
    public function eat(): void;
}

interface Employee extends Feedable, Workable
{
}

class HumanEmployee implements Employee
{
    public function work(): void
    {
        // ....working
    }

    public function eat(): void
    {
        //.... eating in lunch break
    }
}

// robot can only work
class RobotEmployee implements Workable
{
    public function work(): void
    {
        // ....working
    }
}
```
- **What it demonstrates**: ISP through PHP's multiple interface inheritance. Clients that only need work type-hint `Workable`; `RobotEmployee` is never asked to eat.

## Reference Tables

| Principle | Guide's Bad | Guide's Good | The PHP mechanism |
|---|---|---|---|
| SRP | `UserSettings` changes settings *and* verifies credentials | `UserAuth` extracted | one class per reason to change |
| OCP | `abstract class Adapter` + `HttpRequester` branching on `getName()` | `interface Adapter` with `request()` | interface + delegation |
| LSP | `Square extends Rectangle`, overriding setters | `Rectangle` and `Square` both `implements Shape` | flat implementations, constructor-set dimensions |
| ISP | `interface Employee { work(); eat(); }` | `Workable`, `Feedable`, `Employee extends Feedable, Workable` | interface segregation + multiple interface inheritance |
| DIP | `Manager` depends on class `Employee`; `Robot extends Employee` | `Manager` depends on `interface Employee` | constructor injection of an interface |

**Interface or base class?** Across the whole guide, **every class-to-class `extends` sits in a "Bad" example**: `EmployeeTaxData extends Employee` (Ch 7), `AjaxAdapter`/`NodeAdapter extends Adapter` (OCP), `Square extends Rectangle` (LSP) and `Robot extends Employee` (DIP). The only `abstract class` is OCP's `Adapter`, which existed to carry a `protected $name`. Every one is replaced by an interface; the only `extends` in a "Good" example is interface-to-interface (`Employee extends Feedable, Workable`). The guide never weighs abstract classes against interfaces explicitly — but its examples answer the question the same way every time.

## Worked Example
**LSP — the Square that broke `printArea()`.**

```php
class Rectangle
{
    protected $width = 0;

    protected $height = 0;

    public function setWidth(int $width): void
    {
        $this->width = $width;
    }

    public function setHeight(int $height): void
    {
        $this->height = $height;
    }

    public function getArea(): int
    {
        return $this->width * $this->height;
    }
}

class Square extends Rectangle
{
    public function setWidth(int $width): void
    {
        $this->width = $this->height = $width;
    }

    public function setHeight(int $height): void
    {
        $this->width = $this->height = $height;
    }
}

function printArea(Rectangle $rectangle): void
{
    $rectangle->setWidth(4);
    $rectangle->setHeight(5);

    // BAD: Will return 25 for Square. Should be 20.
    echo sprintf('%s has area %d.', get_class($rectangle), $rectangle->getArea()) . PHP_EOL;
}
```

`printArea()` is correct for `Rectangle`. `Square` satisfies the type checker — same method signatures — yet the function now prints the wrong answer. That is the gap LSP names: **matching signatures are necessary, not sufficient.**

The guide's fix removes both causes at once: no inheritance between the two, and **no setters** — dimensions arrive through the constructor.

```php
interface Shape
{
    public function getArea(): int;
}

class Rectangle implements Shape
{
    private $width = 0;
    private $height = 0;

    public function __construct(int $width, int $height)
    {
        $this->width = $width;
        $this->height = $height;
    }

    public function getArea(): int
    {
        return $this->width * $this->height;
    }
}

class Square implements Shape
{
    private $length = 0;

    public function __construct(int $length)
    {
        $this->length = $length;
    }

    public function getArea(): int
    {
        return $this->length ** 2;
    }
}

function printArea(Shape $shape): void
{
    echo sprintf('%s has area %d.', get_class($shape), $shape->getArea()).PHP_EOL;
}

$shapes = [new Rectangle(4, 5), new Square(5)];
```

Note also that `protected` became `private` (Ch 6): with no subclasses, nothing needs the wider visibility.

**Two caveats about the other examples**, so they are applied for their idea rather than copied:
- **SRP's "Good" version constructs its collaborator** — `$this->auth = new UserAuth($user);` inside `UserSettings::__construct()`. By this chapter's own DIP, `UserAuth` (or an interface for it) should be injected instead.
- **OCP's "Bad" version would not run as written**: the subclasses call `parent::__construct()` on an abstract class that defines no constructor (a fatal error), and the dispatcher checks for `'httpNodeAdapter'` while `NodeAdapter` names itself `'nodeAdapter'` — which, by accident, demonstrates exactly how brittle string dispatch is. `Promise` throughout the OCP example is not a PHP built-in; it is carried over from the JavaScript original and stands for whatever promise type your HTTP library returns.

## Key Takeaways
1. **SRP**: one reason to change per class — split by reason, not by size.
2. **OCP**: if adding a variant means editing an `if` on a name, extract an interface and delegate.
3. **LSP**: substitutability, not "is-a" in the real world, decides inheritance; setters that couple two properties are the usual breach.
4. **ISP**: split fat interfaces by capability; recombine with `interface X extends A, B`; implement only what you use.
5. **DIP**: high-level classes take interfaces in their constructors — the same thing Symfony's container does for you.
6. **In this guide, the abstraction is always an `interface`.**

## Connects To
- **Ch 5**: "Avoid conditionals" is OCP at function scale — the airplane `switch` becomes `interface Airplane`.
- **Ch 6–7**: `private` by default and `final` + interface are the class-level preconditions that make these principles cheap.
- **Ch 4**: the Singleton breaks SRP and DIP by the guide's own argument; the `BetterPHPAlternative` refactor is DIP before it is named.
- **Ch 9 (DRY)**: "Getting the abstraction right is critical, that's why you should follow the SOLID principles."
- **clean-code-java ch10 (Classes)**: the book's SRP and cohesion treatment, in longer form.
