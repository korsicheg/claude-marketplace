# Chapter 8: Boundaries
*by James Grenning*

## Core Idea
**It's better to depend on something you control than on something you don't control,
lest it end up controlling you.** Manage every third-party boundary by having very few
places in your code that refer to it.

## Frameworks Introduced

- **The Provider/User Tension** — providers of third-party packages strive for **broad
  applicability** (many environments, wide audience); users want an interface **focused
  on their particular needs**. This tension is what causes boundary problems.

- **Don't Pass Boundary Interfaces Around** — the operative rule of the chapter.
  - How: if you use a boundary interface like `Map`, **keep it inside the class, or
    close family of classes, where it is used. Avoid returning it from, or accepting it
    as an argument to, public APIs.**
  - Explicitly *not* a rule that every `Map` must be wrapped — it is a rule about how far
    the boundary type travels.

- **Learning Tests** (Jim Newkirk's term, via Beck's *TDD*) — instead of experimenting
  with a new library inside production code, write tests that check your understanding
  of the third-party API.
  - When to use: any time you adopt a library you don't already know.
  - How: call the API exactly as you expect to use it in the application; run controlled
    experiments focused on **what you want out of the API**, not on testing their code.
  - Why it works: *learning the third-party code is hard; integrating it is hard; doing
    both at once is doubly hard.* Learning tests separate the two.

- **Write the Interface You Wish You Had** — when the code on the other side doesn't
  exist yet, define your own interface for it and keep working.
  - How: name the operation in your own domain terms, build against it, and later write
    an **Adapter** [GoF] to bridge to the real API when it arrives.
  - Benefits: the interface is under your control, client code stays readable and focused
    on intent, and the Adapter becomes the single place to change when the API evolves.
  - Bonus: it creates a **seam** [Feathers, *WELC*] for testing — a `FakeTransmitter`
    lets you test the controller before the real subsystem exists.

## Worked Example 1: hiding `java.util.Map`

**The problem with `Map`:** it has a very broad interface. `clear()` sits right at the
top — any recipient of your map can wipe it. And a raw `Map` *"does not reliably
constrain the types of objects placed within them."*

```java
Map sensors = new HashMap();
...
Sensor s = (Sensor) sensors.get(sensorId);   // repeated over and over across the code
```

Generics improve readability but don't solve the real problem:

```java
Map<Sensor> sensors = new HashMap<Sensor>();
...
Sensor s = sensors.get(sensorId);
```

**`Map<Sensor>` still offers more capability than you want, and passing it liberally
around means many places to fix if `Map` ever changes.** That is not hypothetical — it
changed when generics arrived in Java 5, and Grenning reports seeing *"systems that are
inhibited from using generics because of the sheer magnitude of changes needed to make
up for the liberal use of `Map`s."*

**The clean version:**

```java
public class Sensors {
    private Map sensors = new HashMap();

    public Sensor getById(String id) {
        return (Sensor) sensors.get(id);
    }
    //snip
}
```

**What it demonstrates:** the boundary interface is now hidden and free to evolve. Casting
and type management live in one class. Whether generics are used has become — *and always
should have been* — an implementation detail. The interface is tailored and constrained
to the application's needs, which makes it **easier to understand and harder to misuse**,
and it gives `Sensors` a place to enforce design and business rules.

## Worked Example 2: learning log4j by test

The chapter's honest walkthrough of adopting an unfamiliar library. Start naive:

```java
@Test
public void testLogCreate() {
    Logger logger = Logger.getLogger("MyLogger");
    logger.info("hello");
}
```

Error: needs an `Appender`. Add one:

```java
@Test
public void testLogAddAppender() {
    Logger logger = Logger.getLogger("MyLogger");
    ConsoleAppender appender = new ConsoleAppender();
    logger.addAppender(appender);
    logger.info("hello");
}
```

Error: the appender has no output stream. After documentation and googling:

```java
@Test
public void testLogAddAppender() {
    Logger logger = Logger.getLogger("MyLogger");
    logger.removeAllAppenders();
    logger.addAppender(new ConsoleAppender(
        new PatternLayout("%p %t %m%n"),
        ConsoleAppender.SYSTEM_OUT));
    logger.info("hello");
}
```

That works — and the experiments then reveal genuinely strange behavior: removing
`ConsoleAppender.SYSTEM_OUT` still prints, but removing `PatternLayout` breaks it again.
The default `ConsoleAppender` constructor is documented as "unconfigured." *"This feels
like a bug, or at least an inconsistency, in log4j."*

The knowledge ends up encoded as tests:

```java
public class LogTest {
    private Logger logger;

    @Before
    public void initialize() {
        logger = Logger.getLogger("logger");
        logger.removeAllAppenders();
        Logger.getRootLogger().removeAllAppenders();
    }

    @Test
    public void basicLogger() {
        BasicConfigurator.configure();
        logger.info("basicLogger");
    }

    @Test
    public void addAppenderWithStream() {
        logger.addAppender(new ConsoleAppender(
            new PatternLayout("%p %t %m%n"), ConsoleAppender.SYSTEM_OUT));
        logger.info("addAppenderWithStream");
    }

    @Test
    public void addAppenderWithoutStream() {
        logger.addAppender(new ConsoleAppender(
            new PatternLayout("%p %t %m%n")));
        logger.info("addAppenderWithoutStream");
    }
}
```

**Then encapsulate that knowledge in your own logger class** so the rest of the
application never touches the log4j boundary.

## Worked Example 3: the Transmitter that didn't exist

Grenning's radio-communications team needed a "Transmitter" subsystem whose owners hadn't
defined an interface yet. Rather than block, they started far from the unknown, and when
they bumped into the boundary they articulated what they *wanted* to say:

> *Key the transmitter on the provided frequency and emit an analog representation of the
> data coming from this stream.*

So they defined `Transmitter` with a `transmit(frequency, dataStream)` method — **the
interface they wished they had** — and insulated `CommunicationsController` behind it.
When the real API arrived, a `TransmitterAdapter` bridged the gap, encapsulating the
interaction and giving one place to change as the API evolves. A `FakeTransmitter` made
the controller testable in the meantime.

## Why learning tests are "better than free"

1. **They cost nothing** — you had to learn the API anyway; tests are an easy, isolated
   way to acquire that knowledge, as precise experiments.
2. **They have positive ROI** — run them against each new release of the package to
   detect behavioral differences.
3. **They protect you from the vendor's roadmap** — the original authors face their own
   pressures: they fix bugs, add capabilities, and each release carries risk. If a change
   is incompatible with your expectations, **you find out right away**.
4. **They make upgrades possible** — without boundary tests to ease migration, *"we might
   be tempted to stay with the old version longer than we should."*

**Note the generalization:** whether or not you need the learning, *"a clean boundary
should be supported by a set of outbound tests that exercise the interface the same way
the production code does."*

## Anti-patterns

- **Passing `Map` (or any boundary type) through public APIs** — spreads third-party
  particulars across the system and multiplies the fix-up cost of any change.
- **Casting at every call site** — `(Sensor) sensors.get(id)` repeated everywhere puts
  the responsibility on every client and hides the story of the code.
- **Learning a library inside production code** — you end up in long debugging sessions
  unable to tell whether the bug is yours or theirs.
- **Blocking on an undefined interface** — instead, define the interface you wish you had.
- **Letting too much of your code know about third-party particulars.**

## Mental Models

- **A boundary is where change happens.** Good designs accommodate change without huge
  investment and rework; boundaries are where you pay or save.
- **You are not testing their code — you are testing your understanding of it.**
- **Two tools, one goal**: *wrap* (as with `Map`) or *adapt* (as with `Transmitter`).
  Both reduce the number of places that know about the foreign API.
- **"The interface you wish you had" is a design technique, not a workaround.** It keeps
  client code expressive because it speaks your domain, not the vendor's.

## Key Takeaways

1. **Wrap or adapt every third-party boundary**; refer to it from as few places as possible.
2. **Never return or accept a boundary type in your public API.**
3. **Write learning tests** for unfamiliar libraries, and keep them as regression tests
   against new releases.
4. **Define the interface you wish you had** when the other side is unknown or unfinished,
   then bridge with an Adapter.
5. **Boundary tests define expectations** and are what make version upgrades affordable.
6. **Constrain the boundary to your needs** — a narrower interface is harder to misuse
   and can enforce your rules.

## Connects To
- **Ch7 (Error Handling)**: "wrapping third-party APIs is a best practice" — same
  technique, applied to exception translation.
- **Ch9 (Unit Tests)**: learning tests and boundary tests are unit tests with a specific job.
- **Ch11 (Systems)**: boundaries and adapters are how a system stays decoupled at scale.
- **Ch17 (Smells)**: G36 "Avoid Transitive Navigation" and the dependency heuristics.
- **GoF Adapter**; **Feathers, *Working Effectively with Legacy Code*** (seams);
  **Beck, *Test Driven Development*** (learning tests).
