# Chapter 5: Objects and Data Structures

## Core Idea
Access an object's data through **methods**, not through a bare data structure. In Ruby that is the default rather than a discipline: instance variables are private, a "getter" is a public method named after the attribute, and a "setter" is a method ending in `=`. Write them by hand when they do something; use `attr_accessor` when they don't — and know that `attr_accessor` can itself be a smell. The source section is a single rule; this chapter is short accordingly.

## Frameworks Introduced
- **Use getters and setters**: "Using getters and setters to access data on objects could be better than simply looking for a property on an object." The guide's "unorganized list of reasons why":
  - "When you want to do more beyond getting an object property, you don't have to look up and change every accessor in your codebase."
  - "Makes adding validation simple when doing a `set`."
  - "Encapsulates the internal representation."
  - "Easy to add logging and error handling when getting and setting."
  - "You can lazy load your object's properties, let's say getting it from a server."
  - When to use: whenever a hash is standing in for an object whose data other code reads and writes (`account[:balance] = 100`).
  - How: a class with a private `@balance`, a reader `def balance` and a writer `def balance=(amount)` — each a place to hang logging and validation.
- **`attr_accessor` for trivial accessors**: "if your getters and setters are absolutely trivial, you should use `attr_accessor` to define them." The guide singles out "data-like objects which expose data to other parts of the system (e.g., ActiveRecord objects, response wrappers for remote APIs)."
- **…but `attr_accessor` can be a smell**: "in some situations, using `attr_accessor` is a code smell" — the guide links a 2012 post by Piotr Solnica (solnic.codes) on attributes as a code smell, rather than making the argument itself.
  - When to use: as a review question — does every caller really need to *write* this attribute?

## Key Concepts
- **Instance variable (`@balance`)** — per-object state; not reachable from outside without an accessor method. The guide's comment marks it: "this one is private".
- **Reader (getter)** — a public method returning an attribute: `def balance`.
- **Writer (setter)** — a public method named with a trailing `=`: `def balance=(amount)`, called as `account.balance = 100`.
- **`attr_accessor`** — class macro that generates a trivial reader and writer.
- **`attr_reader`** — generates a reader only; the guide uses it in Ch 7's adapters (`attr_reader :name`).
- **Data-like object** — an object whose job is to expose data (an ActiveRecord model, an API response wrapper); the guide's sanctioned home for `attr_accessor`.
- **Lazy loading** — computing or fetching an attribute on first access, possible only behind a method.

## Mental Models
- **Think of the hash as a public struct with no seams.** Once callers write `account[:balance] = 100`, there is nowhere to add validation without touching every call site.
- **The accessor is a seam, not ceremony.** A hand-written reader or writer earns its keep the moment it logs, validates, converts, or loads lazily; until then, `attr_*` says the same thing in one line.
- **Ruby already did JavaScript's privacy work.** The JavaScript parent needs closures to make state private; in Ruby, instance variables are private by construction, so that rule simply doesn't appear here.

## Anti-patterns
- **Hashes as domain objects** (`make_bank_account` returning `{ balance: 0 }`): no seam for validation or logging.
- **Hand-writing trivial accessors**: noise; `attr_accessor` exists for this.
- **`attr_accessor` by reflex**: exposes a public writer for every attribute, including ones nothing should set from outside.
- **Logic scattered at call sites** (`account[:balance] = amount if amount >= 0` in ten places): belongs in one writer.

## Code Examples
A data-like object with trivial accessors — the guide's `Toy`:

```ruby
class Toy
  attr_accessor :price
end

toy = Toy.new
toy.price = 50
toy.price # => 50
```
- **What it demonstrates**: one line generates `price` and `price=`; the call site reads exactly like the hand-written version below, so upgrading to a hand-written accessor later changes no caller.

## Reference Tables

| Need | Use | Example |
|---|---|---|
| Read-only attribute | `attr_reader` | `attr_reader :name` (Ch 7) |
| Trivial read/write on a data-like object | `attr_accessor` | `attr_accessor :price` |
| Validation, logging, conversion, lazy load | hand-written reader / writer | `def balance=(amount)` |
| Data other code must not write | no writer at all | — |

## Worked Example
**From a hash to a class with accessors.**

The bad version returns a bare hash, and every caller pokes at it directly:

```ruby
def make_bank_account
  # ...

  {
    balance: 0
    # ...
  }
end

account = make_bank_account
account[:balance] = 100
account[:balance] # => 100
```

Nothing stops a negative balance, nothing is logged, and the key name is now part of every caller's code. The good version makes the representation private and the access points explicit:

```ruby
class BankAccount
  def initialize
    # this one is private
    @balance = 0
  end

  # a "getter" via a public instance method
  def balance
    # do some logging
    @balance
  end

  # a "setter" via a public instance method
  def balance=(amount)
    # do some logging
    # do some validation
    @balance = amount
  end
end

account = BankAccount.new
account.balance = 100
account.balance # => 100
```

The call sites barely change — `account.balance = 100` reads like assignment because Ruby dispatches it to `balance=`. But validation and logging now have exactly one home each, and `@balance` can change representation without any caller noticing. **The transferable rule**: when data has rules, the rules live in the writer; when it has none, `attr_accessor` is enough — until it isn't, and then the switch is invisible to callers.

## Key Takeaways
1. **Prefer an object with accessor methods to a bare hash** for data with rules.
2. **Instance variables are private**; readers and writers (`name`, `name=`) are the public surface.
3. **Hand-write an accessor when it does something** — logging, validation, lazy loading.
4. **Use `attr_accessor` (or `attr_reader`) when it doesn't** — especially on data-like objects.
5. **Question every public writer**: the guide flags `attr_accessor` as a possible smell.

## Connects To
- **Ch 3**: deliberate state belongs behind accessors once side effects are centralized.
- **Ch 6**: the fluent-interface fix replaces chainable `set_*` methods with `attr_accessor` writers.
- **Ch 7 (LSP)**: Square/Rectangle breaks *because* of public writers (`width=`, `height=`).
- **clean-code-javascript**: its closure-privacy rule has no Ruby counterpart — Ruby's instance variables are already private.
