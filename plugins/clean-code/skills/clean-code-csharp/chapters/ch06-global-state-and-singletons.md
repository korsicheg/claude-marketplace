# Chapter 6: Global State and Singletons

## Core Idea
Global state hides dependencies. Instead of a global accessor (a free-floating `Config()` method, a `GetInstance()` singleton), create an **instance**, hand it its data through the **constructor**, and pass it to whatever needs it — in .NET, typically by letting the dependency-injection container build it and configuring it with the **Options pattern** (`IOptions<T>`). These are the last two rules of the source's Functions section.

## Frameworks Introduced
- **Don't write to global functions** — "Polluting globals is a bad practice in many languages because you could clash with another library and the user of your API would be none-the-wiser until they get an exception in production."
  - When to use: a configuration or service exposed as a globally callable method (`Config()`), or any shared, process-wide state.
  - How: wrap it in a class that receives its data in the constructor (`new Configuration(dictionary)`), "and now you must use instance of `Configuration` in your application."
- **Don't use a Singleton pattern** — "Singleton is an anti-pattern." The source paraphrases **Brian Button**'s four objections:
  1. "They are generally used as a **global instance** … you **hide the dependencies** of your application in your code, instead of exposing them through the interfaces. Making something global to avoid passing it around is a code smell."
  2. "They violate the single responsibility principle: by virtue of the fact that **they control their own creation and lifecycle**."
  3. "They inherently cause code to be tightly coupled. This makes faking them out under **test rather difficult** in many cases."
  4. "They carry state around for the lifetime of the application … **you can end up with a situation where tests need to be ordered** which is a big no for unit tests."
  - It also points to **Miško Hevery**'s post on the root cause of singletons.
  - How: a public constructor that takes its configuration — `public DBConnection(IOptions<DbConnectionOption> options)` — with the instance resolved from the IoC container and configured through the Options pattern.

## Key Concepts
- **Global function / global state** — callable or readable from anywhere without being passed in; the dependency is invisible in signatures.
- **Singleton pattern** — a class with a private constructor and a static accessor that guarantees, and hides, a single instance.
- **Hidden dependency** — a collaborator a class uses but does not declare in its constructor or parameters.
- **Options pattern** — `Microsoft.Extensions.Options`: a typed settings class (`DbConnectionOption`) delivered as `IOptions<T>`.
- **IoC container** — the component that constructs objects and supplies their dependencies (`<resolve from IOC>` in the source).
- **Test-order dependence** — tests that pass only in a certain sequence because shared state leaks between them.

## Mental Models
- **If it isn't in the constructor, it's a secret.** A class that calls `DBConnection.GetInstance()` depends on the database, but nothing in its signature says so.
- **"One instance" is a lifetime, not a design.** The source's Good example still has one connection if the container says so; what changes is *who decides* — the composition root, not the class itself. (Reading of `<resolve from IOC>`; the source does not name container lifetimes.)
- **Ask whether a test can replace it.** A constructor parameter can be faked in one line; a static accessor needs the real thing, or a reset hook, or a fixed test order.

## Anti-patterns
- **Static accessors to mutable state** — `GetInstance()` over a lazily created `_instance`.
- **Global configuration functions** — `Config()` returning a fresh dictionary from anywhere.
- **Classes that create and manage their own lifetime** — creation is a second responsibility (SRP, Ch 9).
- **Tests that must run in order** — the symptom of state carried "for the lifetime of the application."

## Code Examples
From global function to instance:

```csharp
// Bad
public Dictionary<string, string> Config()
{
    return new Dictionary<string, string>()
    {
        ["foo"] = "bar"
    };
}

// Good
class Configuration
{
    private readonly Dictionary<string, string> _configuration;

    public Configuration(Dictionary<string, string> configuration)
    {
        _configuration = configuration;
    }

    public string? Get(string key)
    {
        return _configuration.ContainsKey(key) ? _configuration[key] : null;
    }
}

var configuration = new Configuration(new Dictionary<string, string>()
{
    ["foo"] = "bar"
});
```
- *Source snippet lightly repaired: `Get` returned `string[]` from a `Dictionary<string, string>`; now `string?`, and the field is `readonly`.*

## Worked Example
**The `DBConnection` singleton, replaced.**

**Bad** — the class owns its own creation and hands out one hidden instance:

```csharp
class DBConnection
{
    private static DBConnection _instance;

    private DBConnection()
    {
        // ...
    }

    public static DBConnection GetInstance()
    {
        if (_instance == null)
        {
            _instance = new DBConnection();
        }

        return _instance;
    }

    // ...
}

var singleton = DBConnection.GetInstance();
```

Read it against Button's four points. (1) Every caller of `GetInstance()` depends on the database without declaring it. (2) The class does two jobs: being a connection, and managing how many connections exist. (3) No test can hand a class a fake `DBConnection` — the class fetches the real one itself. (4) `_instance` lives as long as the process, so one test's connection state is the next test's starting point. (It is also not thread-safe: two threads can both see `null` — a problem the source doesn't raise, but which the hand-rolled pattern invites.)

**Good** — an ordinary class that declares its configuration:

```csharp
class DBConnection
{
    public DBConnection(IOptions<DbConnectionOption> options)
    {
        // ...
    }

    // ...
}

var options = /* resolve from IOC */;
var connection = new DBConnection(options);
```

"Create instance of `DBConnection` class and configure it with Option pattern … And now you must use instance of `DBConnection` in your application." The connection's settings arrive as a typed `IOptions<DbConnectionOption>`, the instance is built by the container (or by a test, with any options it likes), and every class that needs a connection asks for one in its own constructor — making the dependency visible.

- *Source snippet lightly repaired: `public static GetInstance()` lacked a return type.* The source links the Options pattern docs for ASP.NET Core 2.1; the pattern is unchanged in current .NET.

## Key Takeaways
1. **Global access hides dependencies** — "Making something global to avoid passing it around is a code smell."
2. **No hand-rolled Singletons**: they hide dependencies, own their lifecycle, resist fakes, and make tests order-dependent.
3. **Constructor + Options pattern**: declare configuration as `IOptions<T>`; let the container build the instance.
4. **Pass instances, don't fetch them** — then a test can substitute anything.
5. "One instance" is a **container lifetime decision**, made once at the composition root, not a property baked into the class.

## Connects To
- **Ch 2**: the "Use domain names" example *is* a Singleton — read it for the naming lesson only.
- **Ch 4**: global state is the extreme case of a side effect.
- **Ch 9**: SRP (a singleton has two responsibilities) and DIP (depend on what you're given, not what you fetch).
- **Ch 11**: order-dependent tests are what singletons cost the suite.
- **clean-code-java** ch11 (Systems): separating construction from use, dependency injection, and the main-module composition root.
- **clean-code-javascript**: the parent rule, "Don't write to global functions", there about `Array.prototype`.
