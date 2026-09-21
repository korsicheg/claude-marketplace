# Chapter 5: Structure and Dependencies

## Core Idea

A **module** is the named thing a language lets you group units of work inside, and every
language and configuration format has one: a class; a package or namespace; a Go package; a file
of related functions; a Terraform child module or root; a Helm chart; a Bash library you
`source`; a SQL schema; a Dockerfile stage. It is ch03's **unit of work** one altitude up, so a
module is measured against its **name** exactly as a unit is — **and also against its reasons to
change**. That second measure is SRP, which ch01 tags **Tier 1** because *one, and only one,
reason to change* assumes nothing but a name: the forces that would make someone edit a Helm
chart list as readily as a Java class's. Size is in **responsibilities, not lines**.

**Which of those supplies which construct is the whole question for the other four rows.** A
class or a Go package supplies a substitutability mechanism, a declared interface and an
injectable abstraction, so all nine rows reach it. A Terraform module supplies a declared
interface — its `output`s — and an injectable abstraction, and **no** substitutability mechanism;
a SQL schema supplies those same two through its views and no substitutability either; a Bash
library supplies function dispatch, which *is* substitutability, and nothing declared; a Helm
chart supplies **no** subtype, but its values surface **is** a declared interface, so ISP binds
there; a bare manifest supplies neither a subtype nor an interface you can narrow. Answer that
for the module in front of you, taking "nothing plays that part here" as a real answer.

So the other four do not travel on a name. OCP, LSP and the polymorphism rule need a
**substitutability mechanism** — one implementation standing in for another at a seam the
consumer never edits; ISP needs a **declared interface**, DIP an **injectable abstraction**.
Letting the acronym flatten SRP's tier into the other four's misapplies this chapter both ways:
SRP withheld from config as "an OO thing", LSP improvised onto a manifest.

**ch01 assigns this chapter nine rows, more than any other.** Two things below are *not* rows and
say so: the **extraction loop**, the mechanism SRP is applied by, and **boundaries**, shared with
ch06. What does not port is the **cost of acting**, which each rule below states where it bites.

## Frameworks Introduced

SRP comes first: it is the one Tier 1 row and the one every other rule leans on. The four SOLID
rows after it are stated over a **contract** rather than a class — which is what lets the
Reference Table answer them for a language with no type system — and each carries its **tell**
and its **fix**. **Boundaries and the extraction loop are not ch01 rows**, and each says so.

- **SRP — one, and only one, reason to change** *(Tier 1 — a name)*. Enumerate the forces that
  would compel an edit; more than one means split, and a real split leaves a reusable part —
  one that leaves nothing reusable was a split by size. Two cheap tests, neither naming a
  construct:
  - **The naming test** — *"naming is probably the first way of helping determine class size."*
    No concise name means too large; the vaguer the name, the more responsibilities hide in it.
  - **The 25-word test** — describe the module in about 25 words **without using "if", "and",
    "or" or "but"**. The first "and" is the tell, and it usually names the split.
  - Why it is the most-skipped rule in the book: *"Getting software to work and making software
    clean are two very different activities."* Most of us finish the first and move on.
- **The extraction loop** — **not a ch01 row**; it is how SRP gets applied. (1) Extract a unit
  out of a long one (ch03). (2) It needs four locals, so rather than pass four arguments you
  **promote them to module-level state** — a struct field, a script-level variable, a `locals`
  entry. (3) The module now carries state only a subset of its units touches, so **cohesion
  drops**. (4) *"If there are a few functions that want to share certain variables, doesn't that
  make them a class in their own right? Of course it does."* **Split**, and repeat.
- **Data/object anti-symmetry, and the axis-of-change test** *(Tier 2 — an object (behaviour
  bound to data))*. *"Procedural code (code using data structures) makes it easy to add new
  functions without changing the existing data structures. OO code makes it easy to add new
  classes without changing existing functions"* — and each is hard exactly where the other is
  easy. So **choose by the axis you expect to grow along**: mostly new types → objects and
  polymorphism; mostly new operations → data structures and procedures. A format supplying no
  object has chosen already — a manifest is a data structure, so new kinds of it cost most.
- **OCP — open for extension, closed for modification** *(Tier 2 — a substitutability
  mechanism)*. **A consumer depends on a contract; a new variant arrives as a new implementation
  of it, with no edit to the consumer.** A varying **value** becomes a declared default the
  variant overrides, a varying **step** a narrow hook it replaces — but a variant must never
  override the orchestrating unit, which freezes the base for everyone, because later changes to
  it silently skip that variant. **The tell**: a branch in the consumer keyed on the variant's
  identity — `if (adapter.name === 'ajaxAdapter')`, an `instanceof` chain, a `switch` on a kind
  field — growing a case every time a variant is added. **The fix**: declare the operation on the
  contract and let each variant implement it; the third adapter then touches zero existing code.
- **LSP — the subtype is accepted unchanged** *(Tier 2 — a substitutability mechanism)*. **Every
  implementation of a contract is usable wherever the contract is expected, with no change at the
  call site.** Two breaches, one mechanical: the signature — a required parameter added or
  removed, an input type narrowed, a return widened — which `clean-code-python` turns into a
  build gate by putting a type checker in CI. The other keeps the signature and breaks the
  promise: a strengthened precondition, a new failure type, a violated invariant, none checkable.
  **The canonical tell** is Square-under-Rectangle: `setWidth(4); setHeight(5); getArea()` returns
  25 where a caller written against `Rectangle` expects 20, because the subtype kept an invariant
  the supertype never had. **The fix is not to patch `Square`** but to stop forcing the is-a —
  make both siblings under a `Shape` contract carrying only the behaviour they genuinely share.
  The portable version: **what an implementation needs and the contract does not carry belongs in
  its own state, never in its signature.**
- **ISP — no client depends on what it does not use** *(Tier 2 — a declared interface)*. **The
  contract a consumer depends on is exactly as wide as what that consumer uses.** The tell is an
  implementer apologising — a stub, a `NotImplementedError`, a `throw new Error('Fax not
  supported.')` — which is *"useless code that we will need to maintain"* and an LSP breach no
  checker reports. Fix: one contract per capability, each consumer naming the narrowest that
  covers it. In HCL that interface is a module's `output` blocks: adding one is additive,
  **removing one breaks every caller that referenced it**, and a module exporting its whole
  internal shape can never be narrowed again (ch09).
- **DIP — depend on abstractions, with injection and a consumer-shaped abstraction** *(Tier 2 —
  an injectable abstraction)*. **The consumer names the abstraction it needs; the concrete thing
  is supplied from outside.** The tell is a consumer constructing its own collaborator, and what
  inverting buys is decoupling — *"coupling is a very bad development pattern because it makes
  your code hard to refactor."* In Terraform, DIP means passing a data source's value in as a
  variable rather than reading it inside the module: a `data` block there resolves at plan time
  against the provider's configured account, so a module reading its own dependencies can neither
  be planned against a fixture nor reused where that object is absent.
- **Polymorphism instead of a type switch** *(Tier 2 — a substitutability mechanism)* [`G23`].
  *"Most people use switch statements because it's the obvious brute force solution, not because
  it's the right solution."* The operative form is the **ONE SWITCH rule**: no more than one
  switch per selection, and its cases must create the polymorphic objects that replace every
  other such switch in the system, so a second switch on that selection is the violation. Where
  nothing can be dispatched to the rule does not apply — a `lookup` on a `type` attribute in HCL
  is not a type switch awaiting polymorphism, and one module per variant is SRP, not this row.
- **Boundaries — wrap a foreign vocabulary and translate it into one of yours.** **Not a ch01
  row**; it is the technique behind this chapter's DIP and ch06's failure-wrapping. The book's
  rule: **depend on something you control rather than on something you do not, lest it end up
  controlling you.** The operative part is travel distance — keep the foreign type in the module
  using it and **never accept or return it across your own public surface**; where the other side
  does not exist yet, define the interface you wish you had and adapt later. In configuration the
  boundary is the provider, chart and base image you did not write, and the wrapper that actually
  **translates** is a thin internal module exposing your own variable names over the upstream one,
  so an upstream rename is one file's change rather than every root's. Pinning is the adjacent
  discipline and translates nothing: an unpinned `required_providers` entry lets the next
  `terraform init -upgrade` change your plan with no change to your configuration, and
  `.terraform.lock.hcl` is what records the resolved versions and hashes — **commit it**, or each
  machine resolves its own. Child modules state a **floor** and the root pins, because two child
  modules pinning different exact versions leave no resolvable provider at all.
- **Concurrency as a decoupling concern** *(Tier 2 — a thread)*. *"Objects are abstractions of
  processing. Threads are abstractions of schedule."* The book's headline rule is that
  concurrency is a **separate concern**, defended first by SRP: *"concurrency design is complex
  enough to be a reason to change in its own right"*, so keep concurrency code separate from
  everything else. Its corollary is a dependency rule — **severely limit the scope of shared
  data**, prefer copies, keep threads independent — which is why ch01 puts the row here rather
  than in a chapter of its own. **Where the language has no thread, the rule does not apply.**
  Terraform and most CI platforms derive their schedule from your declared dependency graph, so
  no concurrency code of yours exists to separate, and two units racing on one external object
  are an **undeclared dependency**, not a concurrency defect: declare it (`depends_on`, a job's
  `needs`) and the graph serializes them. Bash supplies what the rule needs — `&` with `wait` is
  a process rather than a thread, but it is concurrent execution over shared state, the state
  being the filesystem — so the corollary reads as one output path per background job. **This
  skill carries the decoupling rule, not the hazards**: deadlock's four conditions, execution
  models, locking and concurrency testing are `clean-code-java` ch13 and ch18.

## Key Concepts

- **Cohesion, read off the artifact.** Units are grouped by the state they touch: the more of a
  module's state a unit manipulates, the more cohesive it is to that module. Maximal cohesion is
  neither advisable nor possible, so read it as a gradient: list the module's state down one axis
  and its units across the other, and a block touching a disjoint subset is the split. The grid
  reads the same on a struct and on a Terraform module's `locals`.
- **Law of Demeter and tell-don't-ask, scoped to objects only** *(Tier 2 — an object (behaviour
  bound to data))*. Talk to friends, not strangers: call methods of yourself, of what you
  created, of what you were handed and of what you hold — never of whatever those returned
  [`G36`]. **A chain through data structures is not a violation**: the same path over public
  fields would not prompt the question, and accessors are what make it ambiguous. So
  `var.tags.owner` in HCL and `.spec.template.metadata.labels` are not violations, nothing in
  either chain being an object. Where it applies, interposing a step means rewriting every call
  site — *"This is how architectures become rigid."*
- **Tell, don't ask — the fix half of the row above.** Splitting a train wreck into three named
  locals improves readability and fixes nothing; the caller still knows the shape, and the mixed
  abstraction levels that made the chain unreadable are still mixed [`G6`]. Ask what it was going
  to *do* with the value — that is the method belonging on the object.
- **DIP is not DI.** Injection is the mechanism, inversion the direction, and you can inject a
  concrete class and invert nothing. **The half people skip is the second**: the abstraction is
  shaped by what the **consumer** needs, never extracted mechanically from the concrete class, so
  an interface mirroring the class it came from still depends on a detail. `clean-code-python`
  states it sharpest — *"the writer just needs an object with a `.write()` method to do our
  bidding"* — where a two-line class meeting that deletes a page of workaround.
- **Apply OCP when a change arrives, not speculatively.** *"the primary spur for taking action
  should be system change itself."* A module judged complete is left alone; the moment you open
  it, fix the design then. ISP's caution is the same — no contract for a capability nobody has.

## Mental Models

- **Testability is a coupling detector, not a separate goal.** *"If a system is decoupled enough
  to be tested in this way, it will also be more flexible and promote more reuse."* If it is hard
  to test it is too coupled — and *where* it is hard tells you which dependency to invert.
- **The detector survives into configuration**: a module you cannot `terraform plan` on its own —
  it reads a data source, or assumes a named remote state — is too coupled, and the fix is DIP's.
  ch08 owns what verification means where there is no test runner.
- **Many small modules are not more to learn.** The system has no more moving parts either way;
  the difference is that you can understand only the directly affected part at a time.
- **A dependency is a promise you cannot withdraw alone.** Extracting, injecting and exporting
  each create one, and the far end gets a say in every later change — which is why DIP asks whose
  need shapes the abstraction, and why ch04 holds a bad abstraction costlier than a copy.

## Reference Table: SOLID by construct

| Principle | Needs | Tell | Fix | In a language with no types |
|---|---|---|---|---|
| **SRP** | a name (**Tier 1**) | the name, or the 25-word description, needs an "and" | extract the second responsibility; hand its result in | **Applies unchanged** — the only row here needing no type system, and why SRP reaches YAML |
| **OCP** | a substitutability mechanism | the consumer branches per variant and grows a case each time | move the behaviour onto the variant; the consumer calls the contract | **Applies via duck typing** — an object with the right member *is* the variant; nothing declares it, so tests and review are the check |
| **LSP** | a substitutability mechanism | an implementation demanding more, returning less, raising something new, or breaking an invariant the caller relied on | make them siblings under a shared contract instead of forcing the is-a | **Applies, unchecked** — with no checker the signature breach lands as a runtime error instead of a build failure |
| **ISP** | a declared interface | an implementer apologising: a stub, a `NotImplementedError`, a "not supported" throw | one contract per capability; each consumer names the narrowest that covers it | **Applies as a convention** — the contract is the set of members a consumer actually touches; keep it one member wide where you can |
| **DIP** | an injectable abstraction | the consumer constructs its own collaborator | name the abstraction from the consumer's need, then pass it in | **Applies fully** — nothing needs declaring in order to be injected; DIP is the row that loses least |

**Reading the last column.** It answers *no static types*, not *no substitutability*. Duck typing
**is** a substitutability mechanism, so JavaScript and Bash keep OCP, LSP and polymorphism as
conventions nothing enforces; where there is none at all, the answer is **does not apply**.

**SQL, worked through the rows that bind.** The module is a **schema**; the units inside it are
views, functions and procedures. A view's **column list is a declared interface**, so **ISP**
binds exactly as on a Terraform `output` set: a view defined `SELECT *` publishes every column of
every base table it touches, and each one a consumer referenced is a caller to negotiate with
before that column can change or go — so name the columns. A view is also **the indirection a
query depends on instead of a base table**, which is **DIP**: the consumer names the shape it
needs, and the table underneath can then be partitioned, renamed or replaced without the consumer
changing. **SRP** binds on the name as always — a view joining reporting and billing has two
reasons to change. And SQL supplies **no substitutability mechanism**, no subtype and nothing to
dispatch to, so **OCP, LSP and the polymorphism rule do not apply to it**, and a `CASE` over a
`type` column is not a type switch awaiting polymorphism. Refusing to approximate those three is
the honest answer, not a gap.

## Anti-patterns

- **The hybrid** — half object, half data structure: real behaviour plus public fields, or
  accessors publishing the same state. Hard to add functions *and* hard to add types, losing
  both advantages. Business rules on an Active Record are the instance: treat the record as the
  data structure it is. **Feature envy** [`G14`] lives here — a unit working through another
  module's accessors on data that belongs there, sometimes a necessary evil the book allows.
- **Auto-generated accessors on everything.** *"The worst option is to blithely add getters and
  setters"* — it decides object-versus-data-structure by default, and decides it badly.
- **A type switch repeated in more than one place** [`G23`]. The second occurrence is the
  violation, and it is where the two case lists start to drift apart.
- **Speculative interfaces.** A standard insisting on an interface for every class: *"Such dogma
  should be resisted and a more pragmatic approach adopted."* An abstraction for a capability
  nobody implements yet is a maintenance obligation bought against a guess.
- **God modules named for their vagueness** — `Manager`, `Processor`, `utils`, `common`: names
  reached for when no single word fits, because responsibilities aggregated. A file needing
  banners to navigate (ch07) is the same finding from the formatting side.
- **Splitting a configuration module as though it were a class.** The design call is right, the
  mechanics are not a compile: Terraform addresses a resource by its position in the module tree,
  so moving one into a new child module renames it and the next plan proposes
  **destroy-and-create** unless a `moved` block (or `terraform state mv`) carries it. Write the
  `moved` blocks with the split, read the plan, then apply.

## Worked Example: the extraction loop, run once, in a language with no classes

Go has no classes. It has a struct — *"just a useful scope in which its variables can be declared
and kept hidden"*, what step 2 promotes locals into — and interfaces, so the Tier 2 rows bind.

```go
// Step 2 already happened: rows and csv were locals in one long function, promoted to fields.
type ReportService struct {
    db   *sql.DB       // touched by load
    smtp *smtp.Client  // touched by send
    from string        // touched by send
    rows []Row         // touched by load, render
    csv  []byte        // touched by render, send
}
func (s *ReportService) Run(ctx context.Context, month string) error {
    if err := s.load(ctx, month); err != nil { return err }
    s.render()
    return s.send(month)
}
```

**Step 3 — cohesion dropped, and the state/unit grid shows it.** No field is touched by all three
units. Three reasons to change: the query when the schema does, `render` when the CSV layout
does, `send` when the mail transport does. The 25-word description needs two "and"s.

**Step 4 — split, one module per reason, and invert what `Run` depends on.**

```go
type RowSource interface{ For(ctx context.Context, month string) ([]Row, error) }
type Renderer  interface{ Render(rows []Row) []byte }
type Mailer    interface{ Send(subject string, body []byte) error }

type Report struct {
    rows   RowSource
    render Renderer
    mail   Mailer
}
func (r Report) Run(ctx context.Context, month string) error {
    rows, err := r.rows.For(ctx, month)
    if err != nil { return fmt.Errorf("loading rows for %s: %w", month, err) }
    return r.mail.Send("Report "+month, r.render.Render(rows))
}
```

**Which rules contributed, and which did not fire.** SRP (Tier 1) produced the split and needed
only the ability to name the three parts. DIP produced the collaborators, each abstraction named
for **what `Run` needs** rather than extracted from `sql.DB` — the half that gets skipped — and
ISP is why there are three one-method contracts instead of one `Storage` with three members. OCP
arrives free — a new output format is a new `Renderer` and `Run` does not change — and **LSP**
now has something to check: every `Renderer` must accept the rows any other accepts.
**Polymorphism** did not fire, there being no type switch, nor **concurrency**, nothing here
starting a thread — and Go supplies both constructs, so those two **apply and had nothing to bite
on**, which is a different finding from a rule that cannot reach the artifact at all. The last
two of the nine are the same case: **data/object anti-symmetry** chose objects here, and
**Demeter** has no train wreck to find. Naming the rules that did not fire is as much the method
as naming the **five** that did. `Run`'s arity stays at two because collaborators are state
(ch03), and the testability detector reads clean: each contract is one method wide, so its
double is a literal.

**The same split in Terraform costs what Go's did not.** Splitting the module gives every
resource it moves a new address, and without a `moved` block the plan destroys and recreates it.
Still the right move — but a state operation, landing alone with the plan read before the apply.

## Key Takeaways

1. **SRP is Tier 1; the other four SOLID principles are Tier 2.** SRP needs only a name, so it
   reaches a Helm chart and a SQL schema unchanged; do not let the acronym flatten that.
2. **Count responsibilities, not lines** — the naming and 25-word tests are the cheap detectors,
   and a reusable extraction confirms the split. **The mechanism is the extraction loop**:
   extract → promote shared locals to module state → cohesion drops → split → repeat. Not a row.
3. **Where there is no substitutability mechanism, OCP, LSP and the polymorphism rule have no
   meaning** — not a weak meaning, none. A bare manifest, a Helm chart, an HCL module and a SQL
   schema supply no subtype and nothing to dispatch to; **ISP** still binds on the last three,
   since a chart's values surface, an `output` set and a view's column list are all declared
   interfaces, and **DIP** on the last two, since a value can be passed in.
4. **No static types is a different question from no substitutability.** Duck typing *is* one, so
   all four hold in JavaScript and Bash as conventions that only tests and review enforce.
5. **Choose data or object by the axis of change** — new operations favour data structures, new
   types favour objects — and never build the hybrid, which gets neither.
6. **Demeter applies to objects only**, so no chain through a YAML path or an HCL value is a
   violation; where it does apply, the fix is tell-don't-ask, not splitting the chain.
7. **DIP's skipped half**: the abstraction is shaped by what the consumer needs. An interface
   mirroring the concrete class is still a dependency on a detail.
8. **Apply OCP when the change arrives**; an interface for every class is dogma, and so is a
   contract for a capability nobody implements yet.
9. **Concurrency is a separate concern, which is why it is here**: keep concurrency code
   separate and shared data tightly scoped. Where there is no thread the row does not apply, and
   for deadlock, execution models and concurrency testing go to `clean-code-java` ch13/ch18.
10. **Testability is the coupling detector** and it survives into config: a module you cannot
    plan on its own is too coupled. **And a split there is a state operation** — a Terraform
    module split renames every resource it moves, so carry `moved` blocks and read the plan.

## Connects To
- **[ch01 — what survives translation](ch01-what-survives-translation.md)**: the index of record
  for the nine rows above, the construct question, and what each declarative format supplies.
- **[ch02 — names and magic values](ch02-names-and-magic-values.md)**: noise words are this
  chapter's evidence — `Manager` and `utils` are aggregated responsibilities wearing a name.
- **[ch03 — units of work](ch03-units-of-work.md)**: this chapter one altitude up; the
  extraction loop begins there, and the arity budget stops a split becoming a five-argument unit.
- **[ch04 — duplication and abstraction](ch04-duplication-and-abstraction.md)**: the
  same-reason-to-change test decides duplication as SRP decides structure; `utils` is that
  mistake at module scale.
- **[ch06 — failure](ch06-failure.md)**: wrapping a foreign vocabulary is the boundary technique
  above applied to failure types, and error handling is a responsibility of its own.
- **[ch07 — comments and formatting](ch07-comments-and-formatting.md)**: a file needing banners
  is too big, and an over-long aligned list is low cohesion from the formatting side.
- **[ch08 — verification](ch08-verification.md)**: testability as the design signal, and what it
  becomes where there is no test runner.
- **[ch09 — declarative and config](ch09-declarative-and-config.md)**: these rows per ecosystem
  and where they do not apply — **ISP over Terraform `output`s, DIP over data sources passed in**,
  and no OCP, LSP or polymorphism where nothing can be dispatched to.
- **[ch10 — improving existing code](ch10-improving-existing-code.md)**: a split is a refactoring,
  so it runs in tiny steps under green verification.
- **`clean-code-java` ch06, ch08, ch10, ch11, ch12, ch13, ch18** — objects and data structures,
  boundaries, classes and SRP, DI at system scale, the dogma warning, and the two concurrency
  chapters this skill does not restate. Its **ch17** is the 66-item catalogue, not duplicated
  here: `G6` wrong abstraction level, `G14` feature envy, `G23` polymorphism over switch, `G28`
  encapsulate conditionals, `G31` hidden temporal couplings, `G36` transitive navigation.
- **`clean-code-python` ch04–ch08** — the richest SOLID source in the family, one chapter per
  principle, stating each as a contract rule. **`clean-code-typescript` ch06** and
  **`clean-code-javascript` ch06** — SOLID with and without a type system; the latter is the
  reference for the last column above.
