# Chapter 7: Testing

## Core Idea
"Testing is more important than shipping." Write tests for every new feature or module, reach your coverage goal before launching or refactoring, and keep **one concept per test** — in Dart, a `group` per unit and a `test` per behaviour, using `package:test`.

*(A thin chapter in the source: one framing paragraph and one rule. For the craft of unit testing — F.I.R.S.T., one assert per test, test-driven development's three laws — see `clean-code-java`, ch. 9.)*

## Frameworks Introduced
- **Testing over shipping**: "If you have no tests or an inadequate amount, then every time you ship code you won't be sure that you didn't break anything."
  - The target: "Deciding on what constitutes an adequate amount is up to your team, but having 100% coverage (all statements and branches) is how you achieve very high confidence and developer peace of mind."
  - The rule: "Always write tests for every new feature/module you introduce."
  - On method: "If your preferred method is Test Driven Development (TDD), that is great, but the main point is to just make sure you are reaching your coverage goals before launching any feature, or refactoring an existing one."
- **Single concept per test**:
  - When to use: every test you write.
  - How (Dart): `group('String', …)` names the unit under test; each `test('.split() splits the string on the delimiter', …)` names one behaviour and checks it with `expect(actual, equals(expected))`.
  - Why: a test named `'String'` that checks `split` and then `trim` can only tell you "something about strings broke"; separate tests name the broken behaviour in the failure report.

## Key Concepts
- **`package:test`** — Dart's standard test library, imported as `package:test/test.dart`.
- **`group(description, body)`** — groups related tests under a shared description; the group name prefixes each test's name in output.
- **`test(description, body)`** — one test case; the description should read as the behaviour it checks.
- **`expect(actual, matcher)`** — the assertion; `equals(…)` is the matcher for value equality.
- **Coverage (statements and branches)** — the guide's 100% target counts both, not just lines.
- **TDD** — optional in the guide's view; coverage before launch or refactor is not.

## Mental Models
- **Think of the test description as the failure message.** `'.trim() removes surrounding whitespace'` is what you'll read when it breaks; write it for that moment.
- **A reassigned variable in a test is a seam.** The guide's Bad test reuses `var string` for a second input; the reassignment is exactly where it should be split. The Good tests each declare a `const string` of their own.
- **Coverage is a gate before risk.** The guide ties it to the two risky moments — launching a feature and refactoring an existing one.

## Anti-patterns
- **Multi-concept tests** — the Bad `test('String', …)` that checks `split` and `trim` in one body.
- **Shipping without tests "this once"** — the guide's premise is that every untested ship is a blind ship.
- **Treating TDD as the goal** — the guide accepts any method that reaches the coverage goal.

## Code Examples

```dart
// Bad
import 'package:test/test.dart';

test('String', () {
  var string = 'foo,bar,baz';
  expect(string.split(','), equals(['foo', 'bar', 'baz']));

  string = '  foo ';
  expect(string.trim(), equals('foo'));
});

// Good
import 'package:test/test.dart';

group('String', () {
  test('.split() splits the string on the delimiter', () {
    const string = 'foo,bar,baz';
    expect(string.split(','), equals(['foo', 'bar', 'baz']));
  });

  test('.trim() removes surrounding whitespace', () {
    const string = '  foo ';
    expect(string.trim(), equals('foo'));
  });
});
```
- **What it demonstrates**: the unit moves to the `group`, each behaviour gets its own `test` and its own `const` input, and the test names now describe behaviour (`.split() splits…`) rather than a type (`String`). (In a real test file these calls sit inside `void main() { … }`; the guide leaves it out.)

## Reference Tables

| Element | Dart | Holds |
|---|---|---|
| Unit under test | `group('String', …)` | the class or function name |
| One behaviour | `test('.split() splits the string on the delimiter', …)` | method + expected behaviour |
| Assertion | `expect(actual, equals(expected))` | one concept's check |
| Fixture | a `const` inside each `test` | that test's own input |

| Question | Guide's answer |
|---|---|
| How much coverage? | Up to your team; 100% of statements **and branches** gives "very high confidence" |
| When must coverage be met? | Before launching a feature or refactoring an existing one |
| Is TDD required? | No — "that is great", but coverage is the point |
| How many concepts per test? | One |

## Key Takeaways
1. **Testing is more important than shipping.** Every new feature or module gets tests.
2. **Aim for full statement and branch coverage** before launching or refactoring.
3. **One concept per test**: `group` the unit, one `test` per behaviour, one `expect` focus.
4. **Name tests by behaviour** — the description is the failure report.
5. **Don't reuse a variable across concepts**; give each test its own `const` input.

## Connects To
- **Ch 3**: small single-purpose functions are what make one-concept tests possible.
- **Ch 6**: DIP's injected abstractions let a test pass a fake (`InventoryRequester` implementations).
- **`clean-code-java`** ch. 9 (Unit Tests): the book's full treatment, which this guide does not reproduce.
- **`clean-code-javascript` Ch 7**: the same rule with mocha-style `describe`/`it`.
