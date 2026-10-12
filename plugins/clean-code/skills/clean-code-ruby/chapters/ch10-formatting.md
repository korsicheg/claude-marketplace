# Chapter 10: Formatting

## Core Idea
"Formatting is subjective." The rule is **DO NOT ARGUE** — automate it with RuboCop. What a tool can't settle, the guide settles in two rules: **consistent capitalization**, which in Ruby carries meaning, and **callers directly above callees**, so a file reads top to bottom like a newspaper.

## Frameworks Introduced
- **Don't argue over formatting**: "The main point is DO NOT ARGUE over formatting. There are tons of tools like RuboCop to automate this. Use one! It's a waste of time and money for engineers to argue over formatting."
  - What the guide adds is for "things that don't fall under the purview of automatic formatting" — its parenthetical lists indentation, tabs vs. spaces and quote style. (Read it as: the tool owns those, and the two rules below cover what it can't decide for you.)
- **Use consistent capitalization**: "Ruby is dynamically typed, so capitalization tells you a lot about your variables, methods, etc. These rules are subjective, so your team can choose whatever they want. The point is, no matter what you all choose, just be consistent."
  - The guide's convention, from its good example: constants `SCREAMING_SNAKE_CASE` (`DAYS_IN_MONTH`), collection constants frozen (`SONGS = [...].freeze`), methods `snake_case` (`erase_database`), classes `CamelCase` (`Animal`, not `ANIMAL`).
- **Method callers and callees should be close**: "If a method calls another, keep those methods vertically close in the source file. Ideally, keep the caller right above the callee. We tend to read code from top-to-bottom, like a newspaper."
  - How: put the public entry point first, then each helper directly below its first caller.

## Key Concepts
- **RuboCop** — Ruby's linter and formatter; the guide's answer to formatting debates.
- **Capitalization as meaning** — in Ruby an identifier starting with a capital letter is a constant, which is why the guide treats case as information, not taste.
- **`SCREAMING_SNAKE_CASE`** — the convention for value constants.
- **`.freeze`** — makes an object immutable; the guide applies it to constant arrays so `SONGS` can't be mutated in place.
- **`snake_case`** — the convention for methods and local variables.
- **`CamelCase`** — the convention for class names.
- **Newspaper rule** — caller above callee, so the file reads from the headline down to the details.

## Mental Models
- **Spend the argument once, in the config.** Every formatting debate settled in a RuboCop config is one the team never has again.
- **Case is a type annotation Ruby actually enforces.** `Artists = [...]` is a constant whether you meant it or not; `daysInMonth` is a local that merely looks like it came from another language.
- **Read the file like an article.** The first method should tell you what the class does; scrolling down should only ever add detail.

## Anti-patterns
- **Arguing formatting in review** — "a waste of time and money".
- **Mixed conventions in one file**: `DAYS_IN_WEEK` beside `daysInMonth`; `eraseDatabase` beside `restore_database`; `class ANIMAL` beside `class Alpaca`.
- **A constant spelled like a class** (`Artists`) and an unfrozen constant array that any caller can `push` to.
- **Helpers above their callers**, or the entry point buried mid-class: the reader jumps around to follow one flow.

## Code Examples
Consistent capitalization:

```ruby
# Bad
DAYS_IN_WEEK = 7
daysInMonth = 30

songs = ['Back In Black', 'Stairway to Heaven', 'Hey Jude']
Artists = ['ACDC', 'Led Zeppelin', 'The Beatles']

def eraseDatabase; end

def restore_database; end

class ANIMAL; end
class Alpaca; end

# Good
DAYS_IN_WEEK = 7
DAYS_IN_MONTH = 30

SONGS = ['Back In Black', 'Stairway to Heaven', 'Hey Jude'].freeze
ARTISTS = ['ACDC', 'Led Zeppelin', 'The Beatles'].freeze

def erase_database; end

def restore_database; end

class Animal; end
class Alpaca; end
```
- **What it demonstrates**: one convention per kind of name, and constants that are genuinely constant — a capitalized name alone only makes Ruby *warn* on reassignment and does nothing to stop `SONGS << 'x'`; `.freeze` stops the in-place mutation.

## Reference Tables

| Kind of name | Convention (guide's good example) | Bad variant shown |
|---|---|---|
| Value constant | `DAYS_IN_MONTH` | `daysInMonth` |
| Collection constant | `ARTISTS = [...].freeze` | `Artists = [...]` |
| Method | `erase_database` | `eraseDatabase` |
| Class | `Animal` | `ANIMAL` |

## Worked Example
**Reordering `PerformanceReview` so it reads top to bottom.**

The bad order scatters the flow: the two lookups come first, then `peer_reviews`, then the entry point `perf_review`, then `manager_review` and `self_review`. A reader starting at `perf_review` has to scroll up for `peer_reviews`, further up for `lookup_peers`, then down again.

The guide's order:

```ruby
class PerformanceReview
  def initialize(employee)
    @employee = employee
  end

  def perf_review
    peer_reviews
    manager_review
    self_review
  end

  def peer_reviews
    peers = lookup_peers
    # ...
  end

  def lookup_peers
    db.lookup(@employee, :peers)
  end

  def manager_review
    manager = lookup_manager
    # ...
  end

  def lookup_manager
    db.lookup(@employee, :manager)
  end

  def self_review
    # ...
  end
end

review = PerformanceReview.new(employee)
review.perf_review
```

`perf_review` is the headline: three steps. Each step follows in the order it's called, and each step's helper sits directly below it. Reading downward never requires scrolling back. **The transferable rule**: order methods by the call graph, depth-first from the entry point.

## Key Takeaways
1. **Don't argue formatting — configure RuboCop** and let it decide.
2. **Pick one capitalization convention per kind of name** and keep it; in Ruby, case carries meaning.
3. **Constants in `SCREAMING_SNAKE_CASE`, frozen** when they hold collections.
4. **Methods `snake_case`, classes `CamelCase`.**
5. **Caller directly above callee** — the newspaper rule.

## Connects To
- **Ch 2**: searchable constants are where capitalization rules first appear.
- **Ch 3**: one level of abstraction per method is what makes the newspaper order possible — `perf_review` is pure orchestration.
- **Ch 11**: version control, not comments, carries history; the formatter, not the reviewer, carries style.
- **clean-code-java**: vertical openness, density, distance, and file-size guidance this guide doesn't cover.
