# Chapter 11: Systems
*by Dr. Kevin Dean Wampler*

> *"Complexity kills. It sucks the life out of developers, it makes products difficult to
> plan, build, and test."* — Ray Ozzie

## Core Idea
**Separate constructing a system from using it.** Clean code handles the low levels of
abstraction; at the system level, cleanliness means modularized domains of concern
implemented as POJOs, integrated by minimally invasive aspect-like mechanisms — an
architecture you can **test drive** and grow incrementally rather than plan up front.

> *A note on currency:* the chapter's examples are EJB2/EJB3 and Spring XML, circa 2008.
> The **principles** (separation of construction from use, DI, POJOs, cross-cutting
> concerns, incremental architecture) are the durable content; the framework specifics
> are historical illustration.

## Frameworks Introduced

- **Separate Construction from Use** — the startup process, where application objects are
  constructed and dependencies wired, must be modularized separately from the runtime
  logic that takes over afterward.
  - Metaphor: a hotel under construction has a crane, an exterior elevator, hard hats.
    A year later it has glass walls and guests. Construction and use are different
    processes with different people.

- **Separation of Main** — move all construction into `main` (or modules called by it),
  and design the rest of the system assuming everything is already built and wired.
  - The test: **all dependency arrows cross the barrier in one direction, pointing away
    from `main`.** The application has no knowledge of `main` or of construction.

- **Abstract Factory** [GoF] — when the *application* must control **when** an object is
  created (an order processing system creating `LineItem`s for an `Order`), give it a
  factory interface while the implementation stays on the `main` side of the line.
  - Result: the application controls timing and can pass application-specific
    constructor arguments, while staying decoupled from *how* a `LineItem` is built.

- **Dependency Injection (DI)** — Inversion of Control applied to dependency management.
  IoC moves secondary responsibilities off an object onto objects dedicated to the
  purpose, **thereby supporting SRP**.
  - **True DI means the class is completely passive** — it takes no direct steps to
    resolve its dependencies, and instead offers setters and/or constructor arguments
    for them to be injected.
  - **JNDI lookup is only *partial* DI**: `jndiContext.lookup("NameOfMyService")` — the
    invoking object doesn't control what comes back, but it still *actively resolves*
    the dependency.

- **Cross-Cutting Concerns and AOP** — persistence, transactions, security, caching,
  failover cut across natural object boundaries. In principle you can reason about a
  persistence strategy modularly; in practice the same code gets spread across many
  objects. *"The problem is the fine-grained intersection of these domains."*
  - In AOP, **aspects** declare which points in the system have their behavior modified
    for a concern, applied **noninvasively** (no manual editing of target source).
  - Martin's caution: *"AOP is sometimes confused with techniques used to implement it,
    such as method interception and wrapping through proxies. The real value of an AOP
    system is the ability to specify systemic behaviors in a concise and modular way."*

- **POJOs** (Plain Old Java Objects) — domain objects with **no dependencies on
  enterprise frameworks or other domains**. Conceptually simpler, easier to test-drive,
  easier to evolve.

- **Domain-Specific Languages** — small scripting languages or APIs in a standard
  language that let code read as structured prose a domain expert might write.
  - Value: minimizes the **communication gap** between a domain concept and its
    implementation, reducing the risk of mistranslating the domain.
  - *"DSLs allow all levels of abstraction and all domains in the application to be
    expressed as POJOs, from high-level policy to low-level details."*

## Worked Example 1: the lazy-initialization trap

```java
public Service getService() {
    if (service == null)
        service = new MyServiceImpl(...);  // Good enough default for most cases?
    return service;
}
```

Its merits are real: no construction overhead unless used, faster startup, never returns
null. **Four things are wrong with it anyway:**

1. **A hard-coded dependency** on `MyServiceImpl` and everything its constructor needs —
   *"We can't compile without resolving these dependencies, even if we never actually
   use an object of this type at runtime!"*
2. **Testing suffers** — a heavyweight `MyServiceImpl` requires a test double assigned to
   the field before the method is called.
3. **SRP violation** — construction logic mixed with runtime processing means you must
   test all execution paths, including the null branch. *"The method is doing more than
   one thing."*
4. **Worst of all: it presumes global knowledge.** *"Why does the class with this method
   have to know the global context? Can we ever really know the right object to use here?
   Is it even possible for one type to be right for all possible contexts?"*

**The scaling argument:** one occurrence isn't serious. But applications contain many
such idioms, so *"the global setup strategy (if there is one) is scattered across the
application, with little modularity and often significant duplication."*

**Does DI kill lazy initialization?** No — most DI containers won't construct until
needed, and many provide factories or proxies for lazy evaluation. But remember: *"lazy
instantiation/evaluation is just an optimization and perhaps premature!"*

## Worked Example 2: EJB2 vs EJB3 — what invasive architecture costs

The EJB2 `Bank` entity bean required a local/remote interface, an implementation
subclassing `javax.ejb.EntityBean`, container lifecycle methods (`ejbActivate`,
`ejbPassivate`, `ejbLoad`, `ejbStore`, `ejbRemove` — *"usually empty"*), a `LocalHome`
factory interface, and XML deployment descriptors.

**The damage, itemized:**
- Business logic **tightly coupled to the container** — you must subclass container types.
- **Isolated unit testing is difficult** — mock out the container (hard) or deploy to a
  real server (slow).
- **Reuse outside EJB2 is effectively impossible.**
- **OO itself is undermined** — one bean cannot inherit from another, which forces DTO
  "structs with no behavior," redundant types holding the same data, and boilerplate to
  copy between them.

EJB3 — after Spring's model forced an overhaul of the standard — moves it all into
annotations on a near-POJO:

```java
@Entity
@Table(name = "BANKS")
public class Bank implements java.io.Serializable {
    @Id @GeneratedValue(strategy = GenerationType.AUTO)
    private int id;

    @Embeddable          // An object 'inlined' in Bank's DB row
    public class Address {
        protected String streetAddr1;
        protected String streetAddr2;
        protected String city;
        protected String state;
        protected String zipCode;
    }
    @Embedded private Address address;

    @OneToMany(cascade = CascadeType.ALL, fetch = FetchType.EAGER, mappedBy = "bank")
    private Collection<Account> accounts = new ArrayList<Account>();

    public void addAccount(Account account) {
        account.setBank(this);
        accounts.add(account);
    }
    // ...
}
```

**What it demonstrates:** entity details still exist, but *"because none of that
information is outside of the annotations, the code is clean, clear, and hence easy to
test drive."* Move the persistence info to XML descriptors and you have a pure POJO —
a choice teams can make based on how often mapping details change.

## Worked Example 3: the "Russian doll" of decorators

A Spring config nests a `Bank` POJO inside a data access object, inside a JDBC data
source. *"The client believes it is invoking `getAccounts()` on a `Bank` object, but it
is actually talking to the outermost of a set of nested DECORATOR objects."* Transactions
and caching can be added as further decorators.

The application's entire coupling to the framework is two lines:

```java
XmlBeanFactory bf =
    new XmlBeanFactory(new ClassPathResource("app.xml", getClass()));
Bank bank = (Bank) bf.getBean("bank");
```

**What it demonstrates:** *"Because so few lines of Spring-specific Java code are
required, the application is almost completely decoupled from Spring, eliminating all
the tight-coupling problems of systems like EJB2."* And although XML is verbose, *"the
'policy' specified in these configuration files is simpler than the complicated proxy and
aspect logic that is hidden from view and created automatically."*

## Reference Table: three aspect mechanisms in Java

| Mechanism | Strength | Drawback |
|---|---|---|
| **Java Proxies** | Simple cases — wrapping method calls in individual objects | JDK dynamic proxies **only work with interfaces** (classes need CGLIB/ASM/Javassist). High code volume and complexity even for simple cases — *"they make it hard to create clean code."* No way to specify system-wide points of interest, so not true AOP |
| **Pure Java AOP frameworks** (Spring AOP, JBoss AOP) | Handles the proxy boilerplate automatically; business logic stays POJO; concerns declared in config or annotations. **Sufficient for 80–90% of cases where aspects are useful** | Configuration verbosity |
| **AspectJ** | The most full-featured — an extension of Java with first-class aspects as modularity constructs | Requires adopting several new tools and learning new language constructs and idioms (partly mitigated by the annotation form) |

## Anti-patterns

- **Ad hoc startup code mixed into runtime logic** — the default state of most applications.
- **Big Design Up Front (BDUF)** — *"BDUF is even harmful because it inhibits adapting to
  change, due to the psychological resistance to discarding prior effort and because of
  the way architecture choices influence subsequent thinking about the design."*
  - Distinguish it from the *good* practice of up-front design: BDUF means designing
    **everything** before implementing **anything**.
- **Adopting a standard because it is a standard** — many teams used EJB2 when lighter
  designs would have sufficed. *"I have seen teams become obsessed with various strongly
  hyped standards and lose focus on implementing value for their customers."*
- **Over-engineered APIs** — *"A good API should largely disappear from view most of the
  time,"* so the team's creative effort goes to user stories.
- **Premature decisions** — a decision made with suboptimal knowledge, before customer
  feedback and implementation experience are available.

## Mental Models

- **The city metaphor.** No one manages a city alone. It works because teams own water,
  power, traffic, law enforcement, building codes — and because the city evolved
  **appropriate levels of abstraction and modularity** so components work without anyone
  understanding the whole. Software teams are organized this way; their systems often
  are not.
- **Architecture can grow incrementally — software is not a building.** *"It is a myth
  that we can get systems 'right the first time.'"* Implement today's stories, then
  refactor and expand tomorrow. Building architects must do BDUF because radical change
  to a physical structure mid-construction is infeasible; **software's ephemeral nature
  makes radical change economically feasible — if concerns are separated.**
  - The road analogy answers the obvious objection: who would fund (or want) a six-lane
    highway through a small town anticipating growth?
- **Postpone decisions to the last responsible moment.** *"This isn't lazy or
  irresponsible; it lets us make informed choices with the best possible information."*
- **Not rudderless.** You still hold expectations about scope, goals, schedule, and
  general structure — you just keep the ability to change course.
- **"Use the simplest thing that can possibly work"** — at every level, for systems and
  modules alike.

## The chapter's own summary

> *An optimal system architecture consists of modularized domains of concern, each of
> which is implemented with Plain Old Java (or other) Objects. The different domains are
> integrated together with minimally invasive Aspects or Aspect-like tools. This
> architecture can be test-driven, just like the code.*

## Key Takeaways

1. **Move all construction and wiring to `main` or a DI container**; dependencies point
   one way, away from `main`.
2. **Use Abstract Factory** when the application must control creation timing.
3. **Inject dependencies; never let a class resolve its own.**
4. **Write domain logic as POJOs**, free of framework dependencies.
5. **Handle cross-cutting concerns declaratively and noninvasively.**
6. **Don't do BDUF** — grow architecture incrementally with a naively simple, decoupled
   start.
7. **Postpone decisions until the last responsible moment.**
8. **Adopt standards only when they add demonstrable value.**
9. **Build a DSL for the domain** to close the gap between concept and code.

## Connects To
- **Ch10 (Classes)**: DIP and the `Portfolio`/`StockExchange` injection — the same idea
  at class scale.
- **Ch8 (Boundaries)**: keeping framework particulars out of your code.
- **Ch12 (Emergence)**: "simplest thing that can possibly work" and incremental design.
- **Ch3 (Functions)**: *"functions are the verbs, classes are the nouns"* of the DSL this
  chapter argues for at system level.
- **GoF** (Abstract Factory, Decorator); **Fowler, *IoC Containers and the Dependency
  Injection pattern***; **Mezzaros, *xUnit Patterns*** (test doubles);
  **Alexander, *A Timeless Way of Building***.
