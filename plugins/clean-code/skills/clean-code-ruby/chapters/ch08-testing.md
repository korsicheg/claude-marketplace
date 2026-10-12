# Chapter 8: Testing

## Core Idea
"Testing is more important than shipping." Aim for full coverage of statements **and branches**, use a real test framework (RSpec) plus a coverage tool, and keep each RSpec example to a **single expectation**. In a dynamically typed language this chapter carries the weight a type checker carries elsewhere. The source section is short — one rule plus a preamble — and this chapter is short accordingly.

## Frameworks Introduced
- **Testing over shipping**: "If you have no tests or an inadequate amount, then every time you ship code you won't be sure that you didn't break anything."
  - The target: "Deciding on what constitutes an adequate amount is up to your team, but having 100% coverage (all statements and branches) is how you achieve very high confidence and developer peace of mind."
  - The tooling: "in addition to having a great testing framework, you also need to use a good coverage tool" — the guide links RSpec and Coveralls.
  - The stance on process: "There's no excuse to not write tests. Aim to always write tests for every new feature/module you introduce. If your preferred method is Test Driven Development (TDD), that is great, but the main point is to just make sure you are reaching your coverage goals before launching any feature, or refactoring an existing one."
- **Single expectation per test**: one `expect` per `it` block.
  - When to use: whenever an example's description needs "and" — "performs addition, subtraction, multiplication and division".
  - How: one `it` per behaviour, each named for it, sharing setup through `let`.
  - Why (the guide shows rather than states it): the first failing `expect` stops the example, hiding every assertion after it; separate examples report every failure, each by name.

## Key Concepts
- **Statement coverage** — every line executed by some test.
- **Branch coverage** — every side of every conditional executed; the guide asks for both.
- **RSpec** — Ruby's behaviour-style test framework: `describe` groups, `it` examples, `expect(...).to eq(...)` expectations.
- **`let`** — RSpec's lazily evaluated, per-example helper (`let(:calculator) { Calculator.new }`); shared setup without shared state.
- **Expectation** — one `expect(...).to ...` assertion.
- **Coverage tool** — a tool reporting which statements and branches ran (the guide links Coveralls).
- **TDD** — writing the test first; endorsed but optional — coverage is the non-negotiable part.

## Mental Models
- **Think of each `it` as one claim with one name.** The example's description is the failure message you'll read at 2 a.m.; make it say exactly what broke.
- **Coverage before launching *or refactoring*.** The guide puts refactoring on the same footing as shipping: you can't safely restructure code (Chs 3–7) that nothing exercises.
- **Tests are the type system you have.** The guide's answer to type-checking (Ch 4) is "write good tests, and have good code reviews"; this chapter is where that promise is kept.

## Anti-patterns
- **Shipping without tests**, or with an inadequate amount.
- **Line coverage only**: the guide names branches explicitly.
- **A framework without a coverage tool**: you can't know what you haven't tested.
- **Several unrelated expectations in one example**: one failure masks the rest, and the name can't describe them all.
- **Treating TDD as the goal**: the goal is coverage before launch or refactor; TDD is one way to get there.

## Reference Tables

| RSpec piece | Role | In the guide's example |
|---|---|---|
| `require 'rspec'` | load the framework | top of file |
| `describe 'Calculator'` | group examples for one subject | the whole spec |
| `let(:calculator)` | per-example setup | `Calculator.new` |
| `it 'performs addition'` | one named behaviour | four examples |
| `expect(...).to eq(...)` | one expectation | one per example |

## Worked Example
**Splitting a four-claim example into four examples.**

```ruby
require 'rspec'

describe 'Calculator' do
  let(:calculator) { Calculator.new }

  it 'performs addition, subtraction, multiplication and division' do
    expect(calculator.calculate('1 + 2')).to eq(3)
    expect(calculator.calculate('4 - 2')).to eq(2)
    expect(calculator.calculate('2 * 3')).to eq(6)
    expect(calculator.calculate('6 / 2')).to eq(3)
  end
end
```

If subtraction breaks, the report says the "addition, subtraction, multiplication and division" example failed — and multiplication and division never run. The name is a list, so the failure is ambiguous.

```ruby
require 'rspec'

describe 'Calculator' do
  let(:calculator) { Calculator.new }

  it 'performs addition' do
    expect(calculator.calculate('1 + 2')).to eq(3)
  end

  it 'performs subtraction' do
    expect(calculator.calculate('4 - 2')).to eq(2)
  end

  it 'performs multiplication' do
    expect(calculator.calculate('2 * 3')).to eq(6)
  end

  it 'performs division' do
    expect(calculator.calculate('6 / 2')).to eq(3)
  end
end
```

Now a subtraction bug fails exactly one example, named for it, and the other three still report. `let` gives each example a fresh `Calculator`, so the examples stay independent. **The transferable rule**: if an example's description contains "and", it is two examples.

## Key Takeaways
1. **"Testing is more important than shipping."**
2. **Aim for 100% of statements and branches**; let the team decide what "adequate" means, but measure it.
3. **Use a framework (RSpec) and a coverage tool** — both.
4. **TDD is welcome; coverage before launch or refactor is required.**
5. **One expectation per `it`**, each example named for its behaviour.
6. **Share setup with `let`**, not with state carried between examples.

## Connects To
- **Ch 3**: the two-argument limit exists to keep test matrices small.
- **Ch 4**: "write good tests" is the guide's substitute for type-checking.
- **Ch 6**: fluent interfaces are "harder to mock" — a testing cost.
- **Ch 7 (DIP)**: injected collaborators are what tests replace.
- **clean-code-javascript**: the parent's rule is "single concept per test"; the Ruby port's heading is the stricter "single expectation per test".
- **clean-code-java**: F.I.R.S.T., the three laws of TDD, and clean-test rules, which this guide doesn't cover.
