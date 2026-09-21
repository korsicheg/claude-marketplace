# Chapter 13: Concurrency
*by Brett L. Schuchert*

> *"Objects are abstractions of processing. Threads are abstractions of schedule."*
> — James O. Coplien

## Core Idea
**Concurrency is a decoupling strategy: it separates *what* gets done from *when* it gets
done.** Writing clean concurrent code is very hard, and broken concurrent code looks fine
until the system is under stress. The primary defense is **SRP — keep concurrency code
separate from everything else.**

## Frameworks Introduced

- **Concurrency as decoupling** — in single-threaded code *what* and *when* are so
  coupled that the whole application state can be read off a stack backtrace. Decoupling
  them improves throughput **and structure**: the application becomes *"many little
  collaborating computers rather than one big main loop."*

- **SRP for concurrency** — *"concurrency design is complex enough to be a reason to
  change in its own right."* Three supporting reasons:
  1. Concurrency code has its own life cycle of development, change and tuning.
  2. Its challenges are different from, and often harder than, non-concurrent code.
  3. The number of ways miswritten concurrent code can fail is already challenging enough
     without the burden of surrounding application code.
  - **Recommendation: keep your concurrency-related code separate from other code.**

- **Corollary — Limit the Scope of Data.** The more places shared data can be updated:
  you'll forget to protect one (breaking *all* code touching that data); you'll duplicate
  guarding effort (a DRY violation); and failures — already hard to find — get harder to
  source.
  - **Recommendation: take data encapsulation to heart; severely limit access to any
    data that may be shared.**

- **Corollary — Use Copies of Data.** Avoid sharing entirely where you can: copy objects
  and treat them read-only, or collect results in per-thread copies and merge in a single
  thread.
  - On the cost objection: *"if using copies of objects allows the code to avoid
    synchronizing, the savings in avoiding the intrinsic lock will likely make up for the
    additional creation and garbage collection overhead."* Worth measuring.

- **Corollary — Threads Should Be as Independent as Possible.** Each thread processes one
  request, with all data from an unshared source, stored in **local variables**, behaving
  as if it were the only thread in the world.
  - **Recommendation: partition data into independent subsets that independent threads
    can operate on, possibly on different processors.**

- **Keep Synchronized Sections Small.** Locks are expensive — delays plus overhead — so
  don't litter code with `synchronized`. But critical sections must be guarded. **Naive
  programmers make their critical sections very large; extending synchronization beyond
  the minimal critical section increases contention and degrades performance.**

## Reference Table: concurrency vocabulary

| Term | Definition |
|---|---|
| **Bound Resources** | Resources of fixed size or number in a concurrent environment (database connections, fixed-size read/write buffers) |
| **Mutual Exclusion** | Only one thread can access shared data or a shared resource at a time |
| **Starvation** | A thread or group is prevented from proceeding for an excessively long time or forever — e.g. always letting fast threads through starves long-running ones |
| **Deadlock** | Two or more threads waiting on each other; each holds a resource the other needs |
| **Livelock** | Threads in lockstep, each finding another "in the way"; due to resonance they keep trying and never progress |
| **Critical section** | Any section of code that must be protected from simultaneous use for the program to be correct |

## Reference Table: the three fundamental execution models

| Model | Shape | The hard part |
|---|---|---|
| **Producer-Consumer** | Producers place work in a bounded queue; consumers take it out. Both signal each other — producers signal "no longer empty," consumers signal "no longer full" | The queue is a **bound resource**; both sides may have to wait to be notified |
| **Readers-Writers** | A shared resource mostly read, occasionally written | Balancing throughput against staleness and starvation. Make writers wait for zero readers → continuous readers starve writers. Give writers priority → throughput suffers |
| **Dining Philosophers** | N threads competing for adjacent shared resources | Deadlock, livelock, throughput and efficiency degradation. *"Replace philosophers with threads and forks with resources and this problem is similar to many enterprise applications"* |

**Recommendation: learn these basic algorithms and understand their solutions** — *"most
concurrent problems you will likely encounter will be some variation of these three."*

## Reference Table: myths vs. reality

| Myth | Reality |
|---|---|
| Concurrency always improves performance | Only when there is **a lot of wait time that can be shared** between threads or processors. *"Neither situation is trivial."* |
| Design doesn't change when writing concurrent programs | The design of a concurrent algorithm can be **remarkably different**; decoupling what from when usually has a huge effect on structure |
| You don't need to understand concurrency inside a Web/EJB container | *"You'd better know just what your container is doing"* and how to guard against concurrent update and deadlock |

**The balanced statements:** concurrency incurs overhead in both performance and extra
code; correct concurrency is complex even for simple problems; **concurrency bugs aren't
usually repeatable, so they're dismissed as one-offs instead of the true defects they
are**; concurrency often requires a fundamental change in design strategy.

## Worked Example: why one line of code has 12,870 execution paths

```java
public class X {
    private int lastIdUsed;

    public int getNextId() {
        return ++lastIdUsed;
    }
}
```

Set `lastIdUsed` to 42, share the instance between two threads, both call `getNextId()`.
**Three possible outcomes:**

- Thread one gets 43, thread two gets 44, `lastIdUsed` is 44. ✅
- Thread one gets 44, thread two gets 43, `lastIdUsed` is 44. ✅
- **Thread one gets 43, thread two gets 43, `lastIdUsed` is 43.** ❌

The surprising third result happens because `++lastIdUsed` is not one step. Working from
the generated byte-code, there are **12,870 different possible execution paths** for two
threads through that method. **Change `lastIdUsed` from `int` to `long` and it becomes
2,704,156.** Most produce valid results. *"The problem is that some of them don't."*

## Worked Example: instrumenting code to force failures

**Hand-coded** — insert a scheduling perturbation where you suspect trouble:

```java
public synchronized String nextUrlOrNull() {
    if (hasNext()) {
        String url = urlGenerator.next();
        Thread.yield();          // inserted for testing.
        updateHasNext();
        return url;
    }
    return null;
}
```

**The key insight:** *"If the code does break, it was not because you added a call to
`yield()`. Rather, your code was broken and this simply made the failure evident."*

**But hand-coding has four problems:** you must manually find the places; you can't know
which call to use or where; it slows production code down unnecessarily; and it's a
shotgun approach — *"the odds aren't with you."*

**Automated** — a jiggle point that is a no-op in production and random in test:

```java
public class ThreadJigglePoint {
    public static void jiggle() { }
}
```

```java
public synchronized String nextUrlOrNull() {
    if (hasNext()) {
        ThreadJigglePoint.jiggle();
        String url = urlGenerator.next();
        ThreadJigglePoint.jiggle();
        updateHasNext();
        ThreadJigglePoint.jiggle();
        return url;
    }
    return null;
}
```

Two implementations: one that does nothing (production), one that randomly chooses
between sleeping, yielding, or falling through (test). Run the tests a thousand times
with random jiggling. *"If the tests pass, at least you can say you've done due
diligence."* IBM's **ConTest** does this with more sophistication.

**Note the payoff of SRP here:** *"if we divide our system up into POJOs that know
nothing of threading and classes that control the threading, it will be easier to find
appropriate places to instrument the code."*

## Know your library (Java)

- **Use the provided thread-safe collections** — `java.util.concurrent`.
  **`ConcurrentHashMap` performs better than `HashMap` in nearly all situations**,
  allows simultaneous concurrent reads and writes, and supports composite operations
  that are otherwise not thread safe. **Start with it.**
- **Use the executor framework** for executing unrelated tasks.
- **Use nonblocking solutions when possible.**
- **Several library classes are not thread safe** — know which.

| Class | What it is |
|---|---|
| `ReentrantLock` | A lock that can be acquired in one method and released in another |
| `Semaphore` | The classic semaphore — a lock with a count |
| `CountDownLatch` | A lock that waits for N events before releasing all waiting threads, giving all threads a fair chance to start at about the same time |

**Recommendation: become familiar with `java.util.concurrent`,
`java.util.concurrent.atomic`, and `java.util.concurrent.locks`.**

## Anti-patterns

- **Concurrency details embedded in production code** — *"all too common."*
- **Dependencies between synchronized methods** — `synchronized` protects an *individual*
  method; more than one synchronized method on the same shared class may be wrong.
  - **Recommendation: avoid using more than one method on a shared object.** When you
    must, three correct approaches:
    1. **Client-Based Locking** — the client locks the server before the first call and
       holds the lock through the last.
    2. **Server-Based Locking** — the server exposes one method that locks, calls all the
       methods, and unlocks; the client calls that.
    3. **Adapted Server** — an intermediary performs the locking, for when the original
       server cannot be changed.
- **Huge synchronized sections** — increases contention, degrades performance.
- **Dismissing intermittent failures as one-offs** — *"It is best to assume that one-offs
  do not exist. The longer these 'one-offs' are ignored, the more code is built on top of
  a potentially faulty approach."*
- **Chasing threading and non-threading bugs simultaneously.**
- **Leaving shutdown to the end.**

## Testing threaded code — the seven recommendations

1. **Treat spurious failures as candidate threading issues.** Bugs may show once in a
   thousand or a million executions. Never write them off as cosmic rays or glitches.
2. **Get your nonthreaded code working first.** Put as much of the system as possible in
   POJOs that are not thread-aware and can be tested outside the threaded environment.
3. **Make your threaded code pluggable** — runnable with one thread, several, or varying;
   against real collaborators or test doubles; with doubles that run fast, slow or
   variably; and for a configurable number of iterations.
4. **Make your threaded code tunable** — time performance under different configurations,
   make thread count easy to change (possibly at runtime, possibly self-tuning on
   throughput and utilization).
5. **Run with more threads than processors** — the more frequently tasks swap, the more
   likely you hit a missing critical section or a deadlock.
6. **Run on different platforms.** A real anecdote from the authors: a 2007 concurrency
   course was developed on OS X and taught on Windows XP in a VM. **Tests written to
   demonstrate failure didn't fail as often on XP** — though the code was known to be
   incorrect. Different OSes have different threading policies. (And note: *the Java
   threading model does not guarantee preemptive threading* — modern OSes give it to you,
   but the JVM doesn't promise it.)
7. **Instrument your code to force failures** — jiggling, hand-coded or automated.

## Writing correct shut-down code is hard

Two concrete deadlock scenarios worth remembering:
- A parent spawns children and waits for all to finish. **One child deadlocks → the
  parent waits forever → the system never shuts down.**
- A producer/consumer pair. The parent signals shutdown; **the producer shuts down
  quickly; the consumer is blocked waiting for a message that will never come**, so it
  can't receive the shutdown signal, and the parent never finishes either.

**Recommendation: think about shutdown early and get it working early. It's going to take
longer than you expect — review existing algorithms, because this is probably harder than
you think.**

## Mental Models

- **Concurrency is a decoupling strategy first, a performance strategy second.** The
  structural benefit (many small collaborating computers) is often the real prize.
- **A single line of Java is not a single step.** `++x` has thousands of interleavings.
- **"Testability comes naturally from following the Three Laws of TDD, and implies some
  level of pluggability"** — which is exactly what lets you run threaded code in many
  configurations.
- **Change the design of shared-data objects to accommodate clients, rather than forcing
  clients to manage shared state.**

## Key Takeaways

1. **Separate thread-aware code from thread-ignorant POJOs** — SRP is the first defense.
2. **Severely limit shared data**; prefer copies and independent per-thread data.
3. **Keep synchronized sections minimal**, and avoid calling one locked section from
   another.
4. **Avoid multiple synchronized methods on one shared object**; if unavoidable, use
   client-based, server-based, or adapted-server locking.
5. **Learn producer-consumer, readers-writers, and dining philosophers** — everything
   else is a variation.
6. **Know `java.util.concurrent`** and start from `ConcurrentHashMap`.
7. **Never dismiss an intermittent failure.**
8. **Test on all target platforms, with more threads than processors, repeatedly, with
   jiggling.**
9. **Solve graceful shutdown early** — it is harder than you think.

## Connects To
- **Appendix A (Concurrency II)**: the detailed tutorial — client/server example,
  possible execution paths, dependencies between methods, increasing throughput, deadlock.
- **Ch10 (Classes)** / **Ch11 (Systems)**: SRP and POJOs are the structural precondition
  for testable concurrency.
- **Ch9 (Unit Tests)**: the Three Laws of TDD and the pluggability they produce.
- **Lea, *Concurrent Programming in Java***; **Hunt & Thomas, *The Pragmatic Programmer***
  (DRY); **IBM ConTest**.
