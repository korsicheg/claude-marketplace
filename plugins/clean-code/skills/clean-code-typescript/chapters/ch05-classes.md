# Chapter 5: Classes

## Core Idea
**A class's size is measured by its responsibility, not its line count** — keep cohesion high
and coupling low, reach for composition before inheritance, and return `this` to make
multi-step configuration read as one expression.

## Frameworks Introduced
- **Size = responsibility.** Following the Single Responsibility Principle, a class should be
  small — and "small" counts *reasons to change*, not lines.
  - When to use: on any class whose method list has started to look like a menu.
  - How: read the method names as a list. If they cluster into unrelated groups
    (language settings / progress display / dirty state / subscriptions / users / navigation /
    profile / version), each cluster is a class.
- **High cohesion, low coupling** — the stated definition of good software design.
  - **Cohesion**: the degree to which class members are related to each other. Ideally **all
    fields are used by every method** — then the class is *maximally cohesive*. The source is
    explicit that this "is not always possible, nor even advisable," but **prefer cohesion to
    be high**.
  - **Coupling**: how dependent two classes are. Low coupling means *changes in one don't
    affect the other*.
  - How to detect low cohesion: **each private field is used by one or another group of
    methods** — "clear evidence that the class is holding more than a single responsibility."
  - The concrete cost named in the source: *"If I need only to create the service to get the
    transactions for a user, I'm still forced to pass an instance of `emailSender`."*
- **Prefer composition over inheritance** (Gang of Four, *Design Patterns*). The stated point is
  not that inheritance is wrong, but that **if your mind instinctively goes for inheritance,
  stop and check whether composition models the problem better.**
  - **Inheritance is the right call when all of these hold** — the source's own list:
    1. It represents an **"is-a"** relationship, not a "has-a" (`Human`→`Animal`, ✓;
       `User`→`UserDetails`, ✗).
    2. You can **reuse code from the base class** (humans move like all animals).
    3. You want **global changes to derived classes** by changing the base (change the caloric
       expenditure of all animals when they move).
- **Method chaining (fluent interface)**: return `this` from every mutator so calls compose.
  - When to use: multi-step construction or configuration — the pattern is "very useful and
    commonly used in many libraries."
  - How: change each method's return type from `void` to **`this`** (not the class name —
    `this` preserves the type through subclassing) and `return this`.

## Key Concepts
- **Responsibility** — a single reason the class would have to change; the unit class size is
  measured in.
- **Cohesion** — relatedness of a class's members; measured by whether the fields are used by
  all the methods.
- **Maximally cohesive** — every field used by every method. An ideal, not a requirement.
- **Coupling** — dependency between classes; low coupling = changes don't propagate.
- **"is-a" vs "has-a"** — the test that decides inheritance vs composition.
- **Fluent interface / method chaining** — mutators returning `this` so calls compose into one
  expression.
- **`this` return type** — TypeScript's polymorphic self-type; keeps chains type-correct in
  subclasses where a hardcoded class name would not.

## Mental Models
- **Read the constructor to find the responsibility count.** `constructor(db, emailSender)` is
  two dependencies serving two disjoint method groups — that is the smell, visible before you
  read a single method body.
- **Think of forced dependencies as the tax on low cohesion.** You don't feel low cohesion while
  writing the class; you feel it when a caller who wants transactions has to construct an email
  sender. That moment is the argument.
- **Use "would I say *is-a* out loud?" as the inheritance gate.** `EmployeeTaxData extends
  Employee` fails immediately — an employee *has* tax data. Say it aloud and the bug is obvious.
- **Return `this`, not the class name.** `from(c): this` survives subclassing; `from(c):
  QueryBuilder` degrades a subclass's chain back to the base type.
- **Composition is the default; inheritance is the justified exception.** Three conditions must
  hold, not one.

## Code Examples

Low cohesion → split by field usage:

```ts
// Bad — `db` serves two methods, `emailSender` serves three. Two responsibilities.
class UserManager {
  constructor(
    private readonly db: Database,
    private readonly emailSender: EmailSender) {}

  async getUser(id: number): Promise<User> { return await db.users.findOne({ id }); }
  async getTransactions(userId: number): Promise<Transaction[]> { return await db.transactions.find({ userId }); }
  async sendGreeting(): Promise<void> { await emailSender.send('Welcome!'); }
  async sendNotification(text: string): Promise<void> { await emailSender.send(text); }
  async sendNewsletter(): Promise<void> { /* ... */ }
}

// Good — one dependency each; each class is cohesive.
class UserService {
  constructor(private readonly db: Database) {}
  async getUser(id: number): Promise<User> { return await this.db.users.findOne({ id }); }
  async getTransactions(userId: number): Promise<Transaction[]> { return await this.db.transactions.find({ userId }); }
}

class UserNotifier {
  constructor(private readonly emailSender: EmailSender) {}
  async sendGreeting(): Promise<void> { await this.emailSender.send('Welcome!'); }
  async sendNotification(text: string): Promise<void> { await this.emailSender.send(text); }
  async sendNewsletter(): Promise<void> { /* ... */ }
}
```
- **What it demonstrates**: the split is *derived* from field usage, not guessed. Group the
  methods by which field they touch and the class boundaries fall out.

Composition over inheritance — the "has-a" case:

```ts
// Bad — EmployeeTaxData is NOT a type of Employee; employees HAVE tax data.
class EmployeeTaxData extends Employee {
  constructor(name: string, email: string,
              private readonly ssn: string,
              private readonly salary: number) { super(name, email); }
}

// Good — Employee composes it.
class Employee {
  private taxData: EmployeeTaxData;
  constructor(private readonly name: string, private readonly email: string) {}

  setTaxData(ssn: string, salary: number): Employee {
    this.taxData = new EmployeeTaxData(ssn, salary);
    return this;
  }
}

class EmployeeTaxData {
  constructor(public readonly ssn: string, public readonly salary: number) {}
}
```

## Reference Tables

| Symptom | Diagnosis | Fix |
|---|---|---|
| Method list reads as a menu of unrelated groups | too many responsibilities | split by group |
| Each private field used by only one method group | low cohesion | split by field usage |
| Caller must construct a dependency it never uses | low cohesion, leaking as coupling | split |
| `X extends Y` but you'd say "X *has* a Y" | wrong relationship | compose |
| Sequence of `void` setter calls before a `build()` | missing fluency | return `this` |

**Inheritance checklist** — use inheritance only if all three hold:

| # | Condition |
|---|---|
| 1 | Relationship is **is-a**, not has-a |
| 2 | Real **code reuse** from the base class |
| 3 | You want base-class changes to **propagate** to all derived classes |

## Worked Example
**Method chaining, before and after** — a `QueryBuilder`, which is the source's example and also
the clearest demonstration of what `this` buys over `void`.

**Before** — every mutator returns `void`, so the caller must name and re-reference a variable:

```ts
class QueryBuilder {
  private collection: string;
  private pageNumber: number = 1;
  private itemsPerPage: number = 100;
  private orderByFields: string[] = [];

  from(collection: string): void { this.collection = collection; }
  page(number: number, itemsPerPage: number = 100): void {
    this.pageNumber = number; this.itemsPerPage = itemsPerPage;
  }
  orderBy(...fields: string[]): void { this.orderByFields = fields; }
  build(): Query { /* ... */ }
}

const queryBuilder = new QueryBuilder();
queryBuilder.from('users');
queryBuilder.page(1, 100);
queryBuilder.orderBy('firstName', 'lastName');
const query = queryBuilder.build();
```

Five statements, a variable that exists only to be re-mentioned four times, and nothing in the
code says these calls belong together or that order matters.

**After** — one change per method: `: void` → `: this`, plus `return this`:

```ts
class QueryBuilder {
  private collection: string;
  private pageNumber: number = 1;
  private itemsPerPage: number = 100;
  private orderByFields: string[] = [];

  from(collection: string): this { this.collection = collection; return this; }
  page(number: number, itemsPerPage: number = 100): this {
    this.pageNumber = number; this.itemsPerPage = itemsPerPage; return this;
  }
  orderBy(...fields: string[]): this { this.orderByFields = fields; return this; }
  build(): Query { /* ... */ }
}

const query = new QueryBuilder()
  .from('users')
  .page(1, 100)
  .orderBy('firstName', 'lastName')
  .build();
```

**Why it works**: the chain is a single expression, so the intermediate object never needs a
name and the grouping is syntactic rather than conventional. `build()` deliberately does *not*
return `this` — it terminates the chain, which is what makes the chain read as one operation
with an endpoint.

**Why `this` and not `QueryBuilder`**: annotate `from(c): QueryBuilder` and a subclass's chain
collapses to the base type after the first call —
`new MongoQueryBuilder().from('users').withHint(...)` stops compiling because `from` handed back
a `QueryBuilder`. `this` is the polymorphic self-type and tracks the actual receiver.

**Failure mode**: chaining hides *when* mutation happens. A fluent builder that is shared or
reused across calls accumulates state invisibly — build fresh instances, or return new objects
instead of `this` if the builder escapes its expression.

## Key Takeaways
1. **Measure class size in responsibilities**, not lines.
2. **Group methods by the fields they use** — that grouping *is* the class boundary.
3. The tell for low cohesion: a caller forced to supply a dependency it will never use.
4. Aim for **high cohesion and low coupling**; maximal cohesion is an ideal the source says is
   not always even advisable.
5. **Composition is the default.** Use inheritance only when is-a, code reuse, *and*
   propagation all apply.
6. Say the relationship aloud — "an employee *has* tax data" settles it.
7. Return **`this`** (not the class name) from mutators to make configuration chain, and let one
   terminal method (`build()`) end the chain.

## Connects To
- **Ch 6 (SOLID)**: SRP here is stated as a sizing rule; ch06 states it as a principle and
  works it in TS. ISP is the interface-level version of the cohesion argument.
- **Ch 4 (Objects and Data Structures)**: `private readonly` parameter properties are the
  mechanism every example here uses to inject dependencies.
- **Ch 3 (Functions)**: the extract-small-functions habit is the precursor — you cannot see a
  class's responsibility groups until its methods are small.
- **Ch 6 / DIP**: the `UserService` split takes `Database` concretely; DIP would have it depend
  on an interface instead.
- **`clean-code-java` ch10 (Classes)**: the extraction loop this chapter implies but never
  spells out — *extract small functions → promote shared locals to fields → cohesion drops →
  split the class*, repeated — plus the "describe it in ~25 words without and/or/but" test.
