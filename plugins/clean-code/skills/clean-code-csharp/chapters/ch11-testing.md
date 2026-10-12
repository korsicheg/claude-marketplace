# Chapter 11: Testing

## Core Idea
"Testing is more important than shipping." Aim for coverage of **all statements and branches**, measured by a real coverage tool, before you launch a feature or refactor one. And write each test about **one concept**, laid out as **Arrange–Act–Assert** — the source's examples use **xUnit** `[Fact]` methods. This is one of the source's thinnest sections: one framing entry and one rule.

## Frameworks Introduced
- **Basic concept of testing** — "If you have no tests or an inadequate amount, then every time you ship code you won't be sure that you didn't break anything."
  - Coverage target: "Deciding on what constitutes an adequate amount is up to your team, but having 100% coverage (all statements and branches) is how you achieve very high confidence and developer peace of mind."
  - Tooling: "in addition to having a great testing framework, you also need to use a good coverage tool" (the source links Visual Studio's code-coverage docs).
  - Framework choice: "There's no excuse to not write tests. There's plenty of good .NET test frameworks, so find one that your team prefers" (linking the *awesome-dotnet-core* testing list).
  - Discipline: "aim to always write tests for every new feature/module you introduce. If your preferred method is Test Driven Development (TDD), that is great, but the main point is to just make sure you are reaching your coverage goals before launching any feature, or refactoring an existing one."
- **Single concept per test** — "Ensures that your tests are laser focused and not testing miscellaneous (non-related) things, forces AAA pattern used to make your codes more clean and readable."
  - How: one `[Fact]` per behaviour, each with `// Arrange`, `// Act`, `// Assert` sections; name the test after the behaviour (`HandleLeapYear`), not the data.

## Key Concepts
- **Statement coverage** — share of statements executed by the suite.
- **Branch coverage** — share of decision outcomes (each side of every `if`) executed; the source asks for both at 100%.
- **Coverage tool** — measures the above; the source points at Visual Studio's built-in one.
- **AAA (Arrange–Act–Assert)** — set up, perform the one action, verify; three visible sections per test.
- **Single concept per test** — a test exercises one behaviour, so a failure names one cause.
- **`[Fact]`** — xUnit's attribute for a parameterless test method.
- **TDD** — writing the test before the code; welcomed by the source but not required.

## Mental Models
- **A test name is a bug report written in advance.** When `HandleLeapYear` fails you know what broke without opening it; when `HandleDateBoundaries` fails you have three suspects.
- **A reassigned variable inside a test is the tell.** `date = new MyDateTime(…)` halfway down means a second test is hiding in the first.
- **Coverage is a floor, not proof.** The source frames 100% as "very high confidence" — confidence that every line ran, not that every line is right.

## Anti-patterns
- **Shipping without tests** — "There's no excuse to not write tests."
- **One test, several scenarios** — 30-day months, leap years and non-leap years in one method.
- **Tests named after the setup** rather than the behaviour.
- **Tests without visible structure** — setup, action and checks interleaved.
- **Refactoring before coverage** — the source makes coverage the gate for refactoring too.

## Code Examples
```csharp
// Bad
public class MakeDotNetGreatAgainTests
{
    [Fact]
    public void HandleDateBoundaries()
    {
        var date = new MyDateTime("1/1/2015");
        date.AddDays(30);
        Assert.Equal("1/31/2015", date);

        date = new MyDateTime("2/1/2016");
        date.AddDays(28);
        Assert.Equal("02/29/2016", date);

        date = new MyDateTime("2/1/2015");
        date.AddDays(28);
        Assert.Equal("03/01/2015", date);
    }
}
```
- **What goes wrong**: if the first assertion fails, xUnit stops the method there, so the leap-year and non-leap-year cases never run. One red test hides two unknowns.

## Worked Example
The same three scenarios, one concept each, in AAA form:

```csharp
public class MakeDotNetGreatAgainTests
{
    [Fact]
    public void Handle30DayMonths()
    {
        // Arrange
        var date = new MyDateTime("1/1/2015");

        // Act
        date.AddDays(30);

        // Assert
        Assert.Equal("1/31/2015", date);
    }

    [Fact]
    public void HandleLeapYear()
    {
        // Arrange
        var date = new MyDateTime("2/1/2016");

        // Act
        date.AddDays(28);

        // Assert
        Assert.Equal("02/29/2016", date);
    }

    [Fact]
    public void HandleNonLeapYear()
    {
        // Arrange
        var date = new MyDateTime("2/1/2015");

        // Act
        date.AddDays(28);

        // Assert
        Assert.Equal("03/01/2015", date);
    }
}
```

**What changed.** Three behaviours, three methods, three names that state the behaviour. Each test has exactly one Act line, so a failure points at one rule of the date arithmetic. The source credits the example to the Coding Blocks podcast episode "How to Write Amazing Unit Tests".

**Reading the snippet in C#.** `Assert.Equal("1/31/2015", date)` compares a `string` with a `MyDateTime`; a real test would compare `date.ToString(…)` or another `MyDateTime`. The structure is the lesson, not the assertion.

## Key Takeaways
1. **"Testing is more important than shipping."** No feature launches, and no refactoring starts, without tests.
2. Target **100% statement *and* branch coverage**, measured by a coverage tool; your team sets the bar, the source sets the aim.
3. Pick any good **.NET test framework** your team likes; the examples use **xUnit**.
4. **One concept per test**, named for the behaviour.
5. Lay every test out as **Arrange / Act / Assert**.

## Connects To
- **Ch 3**: the Fibonacci guard-clause boundary shift is the kind of bug branch coverage plus boundary tests catch.
- **Ch 6**: singletons make tests order-dependent — "a big no for unit tests."
- **Ch 9**: DIP's injected interfaces are what make classes testable in isolation.
- **clean-code-java** ch09 (Unit Tests): the three laws of TDD, F.I.R.S.T., and one-assert-per-test, which this source does not cover.
- **clean-code-typescript** ch07: the same single-concept rule, plus the TDD laws and F.I.R.S.T.
