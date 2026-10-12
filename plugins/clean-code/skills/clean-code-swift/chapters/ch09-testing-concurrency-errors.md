# Chapter 9: Testing, Concurrency and Error Handling

## Core Idea
Three short sections, one rule each. **Tests are more critical than shipping**, and each test checks **one concept**. **`async`/`await` beats completion handlers**: write asynchronous logic top to bottom. **A caught error needs a plan**: `print` in a `catch` is "not much better" than ignoring it. The section is thin — about 700 words — and its examples are where the guide most needs a compiler check.

## Frameworks Introduced
- **Tests are more critical than shipping**: "If you have no tests or an inadequate amount, then every time you ship code, you won't be sure if you didn't break anything."
  - Coverage: "Deciding what constitutes an adequate amount is up to your team, but having 100% coverage (all statements and branches) is how you achieve very high confidence and peace of mind." That needs "a good coverage tool" (the guide links SonarQube) alongside the test framework.
  - Discipline: "There's no excuse for not writing tests… aim to always write tests for every new feature/module you introduce." TDD is welcome but optional: "the main point is to ensure you are reaching your coverage goals before launching any feature or refactoring an existing one."
- **One concept per test**: split a test method that checks several behaviours into one `XCTestCase` method per behaviour — `testHandles30DayMonths`, `testHandlesLeapYear`, `testHandlesNonLeapYear`.
- **Async/await is even cleaner than promises**: "All you need is a function prefixed with the `async` keyword, and then you can write your logic imperatively without using `completions` to chain your functions. Use this if you can take advantage of Swift's features today!"
- **`throw` is good news**: "`throw error` is a good thing! They mean the program has successfully identified when something went wrong and is letting you know by halting the execution of the current function."
- **Don't ignore caught errors**: "Doing nothing with a caught error doesn't give you the ability to address it or react to the reported error. Just printing a log to the console (`print`) is not much better because it can often get lost among a bunch of other things printed to the console. If you wrap any piece of code in a `do/catch`, it means you believe an error might occur there and then you should have a plan, or create a code path for when it happens."
  - How: in the `catch`, notify the user, report to an error service, or both — the guide's Good example lists `print`, `notifyUserOfError(error)`, `reportErrorToService(error)`, "OR all three!"

## Key Concepts
- **Coverage (statements and branches)** — the share of code paths your tests execute; the guide's target is 100%.
- **One concept per test** — each test method asserts one behaviour, so a failure names it.
- **`XCTestCase` / `XCTAssertEqual`** — the XCTest class and assertion the guide's examples use.
- **Completion handler** — a closure called when async work finishes (`dataTask(with:) { data, response, error in … }`).
- **`async` / `await`** — a function marked `async` (`func f() async`) can suspend at each `await`; the code reads sequentially.
- **`Task { … }`** — starts asynchronous work from synchronous code.
- **`do` / `try` / `catch`** — Swift's error-handling block; `try` marks each call that can throw.
- **Error path** — the deliberate code path for when the `try` fails: user notification, error reporting, recovery.

## Mental Models
- **A test's name is its assertion.** `testHandlesLeapYear` failing tells you what broke; `testHandlesDateBoundaries` failing tells you to go read it.
- **`await` turns a pyramid into a list.** The completion-handler version nests the error check, the write and its own `do`/`catch` inside a closure and needs `.resume()`; the async version is one `do` block in reading order.
- **A `catch` that only prints is a `catch` that only hides.** Ask what the user, the on-call engineer, and the next line of code should do when this fails.
- **Apply the error rule to the guide's own examples.** Its async Good example ends in `print(error.localizedDescription)`, and its getters/setters validation (Ch 5) only prints — both fall short of the standard set here.

## Code Examples
One concept per test:

```swift
import XCTest

class MakeMomentSwiftGreatAgainTests: XCTestCase {

  func testHandles30DayMonths() {
    let date = MakeMomentSwiftGreatAgain("1/1/2015")
    date.addDays(30)
    XCTAssertEqual("1/31/2015", date)
  }

  func testHandlesLeapYear() {
    let date = MakeMomentSwiftGreatAgain("2/1/2016")
    date.addDays(28)
    XCTAssertEqual("02/29/2016", date)
  }

  func testHandlesNonLeapYear() {
    let date = MakeMomentSwiftGreatAgain("2/1/2015")
    date.addDays(28)
    XCTAssertEqual("03/01/2015", date)
  }
}
```

- **What it demonstrates**: the Bad version ran all three checks in one `testHandlesDateBoundaries` method, reassigning one `var date`; split, each failure is named and independent.

Don't ignore caught errors:

```swift
do {
    try funcThatMightThrow()
} catch {
    // One option (more noticeable than print):
    print(error)
    // Another option:
    notifyUserOfError(error)
    // Another option:
    reportErrorToService(error)
    // OR all three!
}
```

## Reference Tables

| Rule | Bad | Good |
|---|---|---|
| One concept per test | one test method, three date checks | three methods, one check each |
| Async/await | `URLSession.shared.dataTask(with:) { … }.resume()` | `try await URLSession.shared.data(from: url)` |
| Caught errors | `catch { print(error) }` | `catch` with a plan: notify the user, report it, or both |

## Worked Example
From completion handler to `async`/`await`, then held to the error-handling rule.

**Bad** — nested callback, manual `resume()`:

```swift
import Foundation

let url = URL(string: "https://en.wikipedia.org/wiki/Robert_Cecil_Martin")!

URLSession.shared.dataTask(with: url) { (data, response, error) in
    guard let data = data, error == nil else {
        print(error?.localizedDescription ?? "Unknown error")
        return
    }

    do {
        try data.write(to: URL(fileURLWithPath: "article.html"))
        print("File written")
    } catch {
        print(error.localizedDescription)
    }
}.resume()
```

Two error channels (the `error` parameter and the `catch`), a `guard` inside a closure, and a `.resume()` that, if forgotten, means nothing happens at all.

**Good**, as the guide writes it:

```swift
import Foundation

async func getCleanCodeArticle() {
    let url = URL(string: "https://en.wikipedia.org/wiki/Robert_Cecil_Martin")!

    do {
        let (data, _) = try await URLSession.shared.data(from: url)
        try await data.write(to: URL(fileURLWithPath: "article.html"))
        print("File written")
    } catch {
        print(error.localizedDescription)
    }
}

Task {
    await getCleanCodeArticle()
}
```

One `do` block, one error channel, top-to-bottom order. Two fixes before it compiles cleanly: the `async` keyword goes **after** the parameter list — `func getCleanCodeArticle() async` — and `Data.write(to:)` is synchronous, so its `await` is superfluous (the compiler warns that no async operation occurs).

**Then apply this chapter's other rule.** The `catch` only prints — exactly what "Don't ignore caught errors" calls "not much better" than nothing. Per the guide, it should notify the user, report the error, or both; or the function should `throw` and let the caller decide, since "`throw error` is a good thing".

## Source Caveats
- **"After iOS 13, Swift introduces `async` and `await`"**: `async`/`await` arrived with Swift 5.5 (2021); Apple's runtime support starts at iOS 15, back-deployed to iOS 13 by later Xcode toolchains.
- **"Cleaner than Promises"**: Swift has no built-in `Promise`; the title and the OCP example's `Promise<Response>` (Ch 7) come from the JavaScript original. The Bad example here is a completion handler, not a promise.
- **Testing example**: the Good tests declare `let date` and then call `date.addDays(30)`, which works only if `MakeMomentSwiftGreatAgain` is a class; and `XCTAssertEqual("1/31/2015", date)` compares a `String` to that object. Treat both as pseudocode.
- **Error handling**: the JavaScript original's "Don't ignore rejected promises" has no Swift counterpart here. The guide doesn't cover `Result`, `try?`, typed errors, custom `Error` types or `defer`.

## Anti-patterns
- **Shipping without tests**: "There's no excuse for not writing tests."
- **Several behaviours in one test method**: one failure hides the rest.
- **Callback pyramids** where `async`/`await` is available.
- **`print` as error handling**: lost "among a bunch of other things printed to the console."
- **Empty `catch` blocks**: "Doing nothing with a caught error doesn't give you the ability to address it."

## Key Takeaways
1. **Tests before shipping**, every feature and module; aim high on statement and branch coverage.
2. **One concept per test**, named for the concept.
3. **Prefer `async`/`await`** over completion handlers; write `func name() async`.
4. **`throw` is information** — let it propagate when the caller is better placed to decide.
5. **Every `catch` needs a plan**: notify, report, recover, or rethrow — not just `print`.

## Connects To
- **Ch 3**: one concept per test is "do one thing" for tests; small, one-thing functions are what make it possible.
- **Ch 5**: the `print`-and-ignore setter is the error-handling anti-pattern in another form.
- **Ch 7**: the OCP example's `Promise<Response>` is the pre-`async` shape this chapter replaces.
- **Ch 8**: dependencies injected as protocols are what a test can replace with a fake.
- **`clean-code-java`** (ch09 Unit Tests, ch07 Error Handling, ch13 Concurrency): the three laws of TDD and F.I.R.S.T.; never return or pass null; the concurrency hazards this guide's single `async` rule doesn't touch.
