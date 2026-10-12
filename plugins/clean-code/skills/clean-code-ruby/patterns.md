# Patterns & Techniques — clean-code-ruby

Concrete refactorings from the guide, each with its trigger and cost.

## Hoist a Literal to a Constant
**When to use**: a literal whose meaning isn't evident at the call site (`Timeout::timeout(86_400)`).
**How**: `SECONDS_IN_A_DAY = 86_400`, then use the name. Capitalized, so Ruby treats it as a constant.
**Trade-offs**: none; the value becomes greppable and self-describing. (Ch 2)

## Destructure a Match Instead of Indexing It
**When to use**: `regex.match(s)[1]`, `regex.match(s)[2]` — the regex runs twice and readers count groups.
**How**: `_, city, zip_code = regex.match(address).to_a`; `_` discards the whole match.
**Trade-offs**: still positional — adding a group shifts the names. (Ch 2)

## Name the Block Parameter
**When to use**: `each do |l|` with a body long enough to forget what `l` is.
**How**: `each do |location|`.
**Trade-offs**: none. (Ch 2)

## Default Argument Instead of `||`
**When to use**: `brewery_name = name || 'Hipster Brew Co.'` at the top of a method.
**How**: `def create_micro_brewery(brewery_name = 'Hipster Brew Co.')`.
**Trade-offs**: an explicit `nil` or `false` is no longer replaced — decide whether that's what you mean. (Ch 2)

## Keyword Arguments for a Long Signature
**When to use**: three or more parameters, or positional call sites whose values you can't identify.
**How**: `def create_menu(title:, body:)`, called as `create_menu(title: 'Foo', body: 'Bar')`. Before that, ask whether the method is doing too much, or whether a higher-level object would serve.
**Trade-offs**: wordier call sites; in exchange, order-independence and an `ArgumentError` naming any missing keyword. (Ch 3)

## Extract the Filter into a Predicate
**When to use**: a loop that both selects and acts (`email(client) if client_record.active?`).
**How**: `active?(object)` for the test, `active(objects)` using `select`, and `email_clients(active(clients))` at the call site.
**Trade-offs**: more methods, each testable alone. (Ch 3)

## Descend One Abstraction Level per Method
**When to use**: a method mixing orchestration with mechanics (`interpret` doing regexes, splitting, tokenizing and walking).
**How**: the parent calls `tokenize` → `lex` → `parse`; each holds one level of mechanics.
**Trade-offs**: more methods; the parent reads as a table of contents. (Ch 3)

## Split a Flag into Two Methods
**When to use**: a boolean parameter selecting a path (`create_file(name, temp)`).
**How**: `create_file(name)` plus `create_temp_file(name)`, the second calling the first with `"./temp/#{name}"`.
**Trade-offs**: two names; each call site reads correctly. (Ch 3)

## Return a Value Instead of Mutating a Global
**When to use**: a method that rewrites a `$global` (`$name = $name.split(' ')`).
**How**: `def split_into_first_and_last_name(name)` returning `name.split(' ')` — take a value, return a value; the caller keeps both the original and the result.
**Trade-offs**: the caller holds the result; the method becomes safe to call twice. (Ch 3)

## Return a New Collection Instead of Mutating the Argument
**When to use**: a method calling `push`, `<<` or `merge!` on something it was given.
**How**: `cart + [{ item: item, time: Time.now }]`; for big structures, persistent collections (Hamster).
**Trade-offs**: a copy per call; the guide notes that in-place mutation is occasionally what you want, and "pretty rare". (Ch 3)

## Centralize a Side Effect
**When to use**: several methods or classes write the same file or resource.
**How**: "Have one service that does it. One and only one."
**Trade-offs**: one more indirection; one place to change, test and audit. (Ch 3)

## Replace an Accumulator Loop with `Enumerable`
**When to use**: `total += x[:n]` inside `each`.
**How**: `programmer_output.sum { |output| output[:lines_of_code] }`; likewise `select`, `map`, `each_with_object`.
**Trade-offs**: none for simple reductions. (Ch 3)

## Merge Near-Duplicates, Branch Only on the Difference
**When to use**: two methods identical except for one field (`show_developer_list` / `show_manager_list`).
**How**: one method builds the shared data and `merge`s a position-specific hash.
**Trade-offs**: the residual `case employee.type` is itself a smell (next pattern). If the merge needs many branches, the abstraction may be wrong — "Bad abstractions can be worse than duplicate code." (Ch 4)

## Extract a Predicate Method for a Compound Condition
**When to use**: `if params[:message].present? && params[:recipient].present?`.
**How**: `def send_message?(params)`, then `if send_message?(params)`.
**Trade-offs**: none; the condition gains a name and a test. (Ch 4)

## Flip a Negative Conditional
**When to use**: `if !genres.blank?`.
**How**: `unless genres.blank?`, or the positive predicate `if genres.present?`.
**Trade-offs**: `present?`/`blank?` come from ActiveSupport; outside Rails, write the positive predicate yourself. (Ch 4)

## Replace a Type `case` with Subclasses
**When to use**: `case @type when '777' … when 'Cessna'` inside one class.
**How**: one subclass per `when` (`Boeing777`, `AirForceOne`, `Cessna`), each defining the method.
**Trade-offs**: more classes; new types add code without editing old code. Check the inheritance tests first. (Ch 4)

## Replace an `is_a?` Chain with One Message
**When to use**: `if vehicle.is_a?(Bicycle) … elsif vehicle.is_a?(Car)` calling different methods.
**How**: give every type the same method (`move`) and call it unconditionally.
**Trade-offs**: every new type must answer `move` — an implicit contract only tests enforce. (Ch 4)

## Drop Hand-Written Primitive Type Guards
**When to use**: `is_a?(Numeric)` / `is_a?(String)` guards before an operation.
**How**: call the operation (`val1 + val2`); use contracts.ruby if you truly need checks; otherwise rely on tests and review.
**Trade-offs**: failures surface later and less specifically. (Ch 4)

## Wrap a Hash in a Class with Accessors
**When to use**: a hash serving as a domain object (`account[:balance] = 100`).
**How**: a class with private `@balance`, a reader `balance` and a writer `balance=` holding the logging and validation; `attr_accessor` when they're trivial.
**Trade-offs**: a class to maintain; one home for the rules. (Ch 5)

## Replace Chained Setters with Writers
**When to use**: `set_color` and friends returning `self` for chaining.
**How**: `attr_accessor :make, :model, :color`; separate statements (`car.color = 'pink'`, `car.save`).
**Trade-offs**: more lines at call sites; decorators, mocks and diffs work again. Keep chaining for builders. (Ch 6)

## Compose Instead of Inherit
**When to use**: a subclass that isn't an "is-a" (`EmployeeTaxData < Employee`).
**How**: a standalone class held in an instance variable (`@tax_data`).
**Trade-offs**: delegation is explicit; no accidental inheritance of state. (Ch 6)

## Extract a Class per Reason to Change
**When to use**: a class doing two jobs (`UserSettings` that also authenticates).
**How**: move one job out (`UserAuth`); the original holds an instance and calls it.
**Trade-offs**: two classes to wire; inject the new one if it must be swappable. (Ch 7)

## Give Every Variant the Same Message
**When to use**: a consumer doing `case @adapter.name`.
**How**: each adapter implements `request(url)`; the consumer calls `@adapter.request(url)`.
**Trade-offs**: none; new adapters edit nothing. (Ch 7)

## Make a False Subtype a Sibling
**When to use**: a subclass overriding writers to preserve its own invariant (`Square#width=`).
**How**: a shared parent (`Shape`) promising only common behaviour; `Rectangle` and `Square` as siblings with dimensions fixed at construction.
**Trade-offs**: no shared writers; callers can't resize generically — which was the bug. (Ch 7)

## Split a Class Along Its Clients
**When to use**: methods grouped by comments like "used by Driver" / "used by Mechanic".
**How**: one class per client's message set (`Car`, `CarInternals`).
**Trade-offs**: more classes; changes for one client stop reaching the other. (Ch 7)

## Inject the Collaborator
**When to use**: `@requester = InventoryRequester.new` inside `initialize`.
**How**: `def initialize(items, requester)`; callers pass `InventoryRequesterV2.new`.
**Trade-offs**: callers do the wiring; swapping implementations or test doubles becomes a call-site change. (Ch 7)

## One Expectation per Example
**When to use**: an `it` whose description lists several behaviours.
**How**: one `it` per behaviour, setup shared through `let`.
**Trade-offs**: more examples; every failure is reported, by name. (Ch 8)

## Give Every `rescue` a Plan
**When to use**: `rescue StandardError => err` followed by `logger.info(err)` or nothing.
**How**: `logger.error(err)` at `Logger::ERROR`, notify the user, report to a service — or don't rescue.
**Trade-offs**: more code at the rescue site; failures stop vanishing. (Ch 9)

## Raise with a Class and a Message
**When to use**: a bare `fail` or `raise`.
**How**: `fail ArgumentError, 'Missing user' unless user`.
**Trade-offs**: none; callers can rescue by class and readers learn why. (Ch 9)

## Order Methods by the Call Graph
**When to use**: a reader has to scroll up and down to follow one flow.
**How**: entry point first, each callee directly below its first caller.
**Trade-offs**: none. (Ch 10)

## Delete Commented-Out Code and Journals
**When to use**: `# do_other_stuff`, or a dated change log above a method.
**How**: delete; history lives in version control.
**Trade-offs**: none. (Ch 11)
