# Appendix A: Concurrency II
*The detailed tutorial behind Chapter 13*

## Core Idea
Concurrency problems are mechanical, not mystical: **a single `++` is eight byte-code
instructions and can interleave**. The disciplines that keep concurrent code clean are
SRP-driven isolation of thread management, knowing your library's non-blocking tools,
understanding the four conditions of deadlock, and instrumenting code so latent failures
surface early.

## Frameworks Introduced

- **Isolate thread management into one class** — the client/server example's `process`
  function held **four responsibilities**: socket connection management, client
  processing, threading policy, and server shutdown policy, *"across many different
  levels of abstraction."*
  - The fix: a `ClientScheduler` interface that is the **single place** all thread
    concerns live. *"If there are concurrency problems, there is just one place to look."*
  - The payoff is immediate — switching from thread-per-request to a Java 5 `Executor`
    pool is *"writing a new class and plugging it in."*
  - The reason it matters more here than elsewhere: *"tracking down concurrency issues
    is hard enough without having to unwind other nonconcurrency issues at the same
    time."*

```java
public interface ClientScheduler {
    void schedule(ClientRequestProcessor requestProcessor);
}

public class ExecutorClientScheduler implements ClientScheduler {
    Executor executor;
    public ExecutorClientScheduler(int availableThreads) {
        executor = Executors.newFixedThreadPool(availableThreads);
    }
    public void schedule(final ClientRequestProcessor requestProcessor) {
        Runnable runnable = new Runnable() {
            public void run() { requestProcessor.process(); }
        };
        executor.execute(runnable);
    }
}
```

- **Atomicity, precisely defined** — *"any operation that is uninterruptable."*
  - **Assignment to a 32-bit value is atomic** per the Java Memory Model.
  - **Assignment to a 64-bit value is not** — the JVM spec requires two 32-bit
    assignments, and another thread can change one of them in between. (It *might* be
    atomic on a particular processor; the spec doesn't promise it.)
  - **`++` is not atomic.** *"It is a common misconception that the ++ (pre- or
    post-increment) operator is atomic, and it clearly is not."*

- **The Executor framework** — pools threads, resizes automatically, recreates threads,
  supports **futures**, and works with `Callable` (like `Runnable`, but returns a
  result). *"If you are creating threads and are not using a thread pool or are using a
  hand-written one, you should consider using the `Executor`."*

```java
public String processRequest(String message) throws Exception {
    Callable<String> makeExternalCall = new Callable<String>() {
        public String call() throws Exception {
            String result = "";
            // make external request
            return result;
        }
    };
    Future<String> result = executorService.submit(makeExternalCall);
    String partialResult = doSomeLocalProcessing();
    return result.get() + partialResult;    // blocks until the future completes
}
```

- **Non-blocking solutions / Compare-and-Swap (CAS)** — `AtomicBoolean`, `AtomicInteger`,
  `AtomicReference` and others.

```java
// blocking                                  // non-blocking
public class ObjectWithValue {               public class ObjectWithValue {
    private int value;                           private AtomicInteger value =
    public synchronized void incrementValue() {          new AtomicInteger(0);
        ++value;                                 public void incrementValue() {
    }                                                value.incrementAndGet();
    public int getValue() { return value; }      }
}                                                public int getValue() { return value.get(); }
                                             }
```

  - **The analogy to remember:** CAS is **optimistic locking**; `synchronized` is
    **pessimistic locking**. `synchronized` *"always acquires a lock, even when a second
    thread is not trying to update the same value."*
  - Mechanism: CAS verifies the variable still holds its last known value; if so it
    sets, if not it retries. *"This detection is almost always less costly than acquiring
    a lock, even in moderate to high contention situations."*
  - **The performance claim:** the atomic version *"will nearly always beat"* the
    synchronized one — *"the cases where it will be slower are virtually nonexistent."*

- **Classes that are inherently not thread safe**: `SimpleDateFormat`, database
  connections, **containers in `java.util`**, servlets.

## Worked Example: why two threads can both get 43

```java
public class Example {
    int lastId;
    public void resetId()   { value = 0; }     // atomic
    public int  getNextId() { ++value; }       // NOT atomic
}
```

Byte-code for `++value`:

| Mnemonic | Operand stack after |
|---|---|
| `ALOAD 0` | `this` |
| `DUP` | `this, this` |
| `GETFIELD lastId` | `this, 42` |
| `ICONST_1` | `this, 42, 1` |
| `IADD` | `this, 43` |
| `DUP_X1` | `43, this, 43` |
| `PUTFIELD value` | `43` |
| `IRETURN` | `<empty>` |

**The interleaving:** Thread 1 completes through `GETFIELD` (42 is on its operand stack)
and is preempted. Thread 2 runs the whole method, gets 43, stores 43. Thread 1 resumes —
**42 is still on its stack** — adds one, stores 43, returns 43. *"One of the increments is
lost."*

**Contrast with `resetId()`** (`ALOAD 0`, `ICONST_0`, `PUTFIELD`): ten threads give
**4.38679733629e+24 possible orderings but only one possible outcome**, because all the
operands are local to the method and every thread assigns the same constant. *"The
different orderings are irrelevant."* The same holds for `long`s here, for the same
reason.

**What you actually need to know** (byte-code literacy is not required):
- where there are shared objects/values,
- which code can cause concurrent read/update issues,
- how to guard against them.

## Worked Example: synchronized methods are not enough

```java
public class IntegerIterator implements Iterator<Integer> {
    private Integer nextValue = 0;
    public synchronized boolean hasNext() { return nextValue < 100000; }
    public synchronized Integer next() {
        if (nextValue == 100000) throw new IteratorPastEndException();
        return nextValue++;
    }
    public synchronized Integer getNextValue() { return nextValue; }
}
```

```java
while (iterator.hasNext()) {
    int nextValue = iterator.next();
    // do something with nextValue
}
```

**Every method is synchronized and the code is still broken.** Thread 1 asks `hasNext()`
→ true, gets preempted. Thread 2 asks `hasNext()` → still true, calls `next()`, which
**has the side effect of making `hasNext()` false**. Thread 1 resumes believing
`hasNext()` is true and calls `next()` → exception.

*"Even though the individual methods are synchronized, the client uses two methods."*
And it only faults on the **final** iteration — *"the kind of bug that happens long after
a system has been in production, and it is hard to track down."*

**Three options:**

| Option | What it is | Verdict |
|---|---|---|
| **Tolerate the failure** | Catch the exception and clean up | *"A bit sloppy. It's rather like cleaning up memory leaks by rebooting at midnight."* |
| **Client-Based Locking** | Every client wraps the pair in `synchronized (iterator) { … }` | Violates DRY; **risky** — every programmer must remember. May be necessary with non-thread-safe third-party tools |
| **Server-Based Locking** | Change the server to expose one atomic operation; the client then uses it | Preferred |

### The Local 705 story — why client-based locking "really blows"

A 1971 time-sharing system for a truckers' union used client-based locking on a shared
resource referenced in **hundreds** of places. **One programmer forgot one lock.**

Symptoms: about once a day a random terminal would freeze, with no pattern in terminal or
time — sometimes several, sometimes none for days. The cause turned out to be a ring
buffer whose counter fell out of sync with its pointer: **empty by the pointer (nothing
to display) and full by the counter (nothing can be added)**.

The escalating workarounds are the real lesson:
1. Reboot — required calling headquarters and stopping every clerk.
2. A trap function on the computer's **front panel switches** that reset any buffer that
   was both empty and full; someone walked into the machine room and flicked a switch.
3. A scheduler task checking every ring buffer once a minute, *"so the displays unclogged
   before the Local could even get on the phone."*
4. **Several more weeks poring over monolithic assembly listings** — no search tools, no
   cross-references — to find the single unprotected use, whose frequency they had
   predicted mathematically.

> *"I learned an important lesson that cold Chicago winter of 1971. Client-based locking
> really blows."*

## Reference Table: the four conditions for deadlock

**All four must hold. Break any one and deadlock is impossible.**

| Condition | Definition | How to break it | Cost |
|---|---|---|---|
| **Mutual Exclusion** | Resources can't be used by multiple threads at once and are limited in number (DB connections, files open for write, record locks, semaphores) | Use simultaneously-usable resources (`AtomicInteger`); increase resource count to ≥ thread count; check all resources are free before seizing any | *"Most resources are limited in number and don't allow simultaneous use"*; the second resource's identity often depends on the first |
| **Lock & Wait** | A thread holds what it has until it has everything it needs | Refuse to wait: check each resource, and **release everything and start over** if one is busy | **Starvation** (low CPU utilization) and **livelock** (high, useless CPU utilization). Still *"better than nothing… it can almost always be implemented if all else fails"* |
| **No Preemption** | A thread can't take a resource from another | Request mechanism: ask the owner to release; if the owner is also waiting, it releases everything and restarts | Fewer restarts than breaking lock-and-wait, but *"managing all those requests can be tricky"* |
| **Circular Wait** ("the deadly embrace") | T1 holds R1 and wants R2; T2 holds R2 and wants R1 | **The most common approach** — a global ordering of resources that all threads allocate in | Acquisition order may not match use order, locking resources longer than necessary; and ordering is infeasible when the second resource's ID comes from operating on the first |

### The worked deadlock scenario

A web app with two pools of ten: database connections and MQ connections to a master
repository. `create` acquires master-then-database; `update` acquires
database-then-master.

1. Ten users call `create` → all ten **database** connections taken, each thread
   preempted before acquiring master.
2. Ten users call `update` → all ten **master** connections taken, each preempted before
   acquiring database.
3. The ten create threads wait for master; the ten update threads wait for database.
4. **Deadlock. The system never recovers.**

*"Who wants a system that freezes solid every other week? Who wants to debug a system
with symptoms that are so difficult to reproduce? This is the kind of problem that
happens in the field, then takes weeks to solve."*

**And the classic anti-fix:** adding debug statements changes the timing so the deadlock
moves and *"takes months to again occur."* The footnote is sharper still: *"someone adds
some debugging output and the problem 'disappears.' The debugging code 'fixes' the
problem so it remains in the system."*

**TANSTAAFL** — every deadlock strategy costs something (starvation, CPU,
responsiveness). *"Isolating the thread-related part of your solution to allow for tuning
and experimentation is a powerful way to gain the insights needed to determine the best
strategies."*

## Testing: the ConTest numbers

How to write a test that proves `takeNextId()` (`return nextId++;`) is broken:
1. Remember the current `nextId`.
2. Create two threads, each calling `takeNextId()` once.
3. Verify `nextId` increased by **two**.
4. **Loop until it only increased by one.**

**The measured effect of instrumentation** — this is the concrete case for jiggling:

| | Failures |
|---|---|
| Uninstrumented | ~1 in **10,000,000** iterations |
| Instrumented with IBM **ConTest** | ~1 in **30** iterations |

Actual loop counts to first failure across runs: **13, 23, 0, 54, 16, 14, 6, 69, 107,
49, 2.** *"Clearly the instrumented classes failed much earlier and with much greater
reliability."*

How to use it: write tests that simulate multiple users under varying loads → instrument
test **and** production code with ConTest → run the tests.

## Anti-patterns

- **A `process`/`run` method holding connection management, client processing, threading
  policy, and shutdown policy** at mixed abstraction levels.
- **Unbounded thread creation** — *"the code sets no limit, so we could feasibly hit the
  limit imposed by the JVM… If too many users connect at the same time, the system might
  grind to a halt."*
- **Assuming `++` is atomic.**
- **Synchronizing individual methods and calling two of them from the client.**
- **Client-based locking as a standing policy** — see Local 705.
- **Tolerating a concurrency failure** by catching and cleaning up.
- **Debugging a deadlock by adding print statements**, then shipping the print statements.

## Key Takeaways

1. **Put all thread management in one class** behind an interface; swapping the policy
   then costs one new class.
2. **Know what is atomic**: 32-bit assignment yes, 64-bit assignment no, `++` no.
3. **Use the `Executor` framework** instead of hand-rolled pools; use `Callable` and
   `Future` when you need results.
4. **Prefer atomics (CAS) to `synchronized`** for simple shared counters and flags.
5. **Synchronized methods don't compose** — a client calling two of them is unprotected.
   Fix it on the **server**, not in every client.
6. **Learn the four deadlock conditions and break one deliberately** — usually circular
   wait, via a global resource ordering.
7. **Instrument to force failures.** ConTest turned 1-in-10-million into 1-in-30.
8. **There is no free lunch** — every concurrency strategy trades throughput, latency, or
   fairness. Isolate the thread code so you can tune and measure.

## Connects To
- **Ch13 (Concurrency)**: the overview; this appendix is its deep dive. Every "see page…"
  reference in Ch13 points here.
- **Ch10 (Classes)** / **Ch11 (Systems)**: SRP and POJO separation are the structural
  precondition for everything above.
- **Ch9 (Unit Tests)**: tests that must be run thousands of times in many configurations.
- **Lea, *Concurrent Programming in Java: Design Principles and Patterns*** — the
  chapter's explicit recommendation for going further.
