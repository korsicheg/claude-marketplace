# Chapter 7: Error Handling
*by Michael Feathers*

## Core Idea
**Error handling is important, but if it obscures logic, it's wrong.** Treat error
handling as a separate concern that can be read and reasoned about independently of the
main algorithm. Clean and robust are not conflicting goals.

## Frameworks Introduced

- **Use Exceptions Rather Than Return Codes** — error codes clutter the caller, who must
  check immediately after the call, and who can easily forget.
  - How: throw from the method that detects the error; let the caller's logic stay
    unobscured. The payoff is separation of two tangled concerns — the algorithm and the
    error handling — so each can be understood on its own.

- **Write Your Try-Catch-Finally Statement First** — a `try` block is a **transaction
  scope**: execution may abort anywhere inside it and resume at the `catch`, and the
  `catch` must leave the program in a consistent state regardless.
  - When to use: whenever you are about to write code that can throw.
  - How (TDD flavored): write a test that *expects* the exception → create the stub →
    watch it fail → implement enough to throw → the test passes → **now narrow the caught
    exception type** to what is actually thrown → then build the real logic inside the
    try, pretending nothing goes wrong.
  - Why it works: defining the scope first tells you what the caller should expect no
    matter what goes wrong, and preserves the transactional nature of the block.

- **Define Exception Classes in Terms of a Caller's Needs** — errors can be classified by
  source or by type, but *"our most important concern should be how they are caught."*
  - How: wrap the API, translate its many exception types into **one** exception type
    for that area of code. Distinguish specific errors by the information carried on the
    exception, not by the class.
  - **Use different exception classes only when you genuinely want to catch one and let
    the other pass through.**

- **Wrapping third-party APIs is a best practice** — it minimizes dependency (you can
  swap libraries later), makes third-party calls easy to mock in tests, and frees you
  from the vendor's API design choices so you can define an API you're comfortable with.

- **The Special Case Pattern** [Fowler] — create a class or configure an object that
  handles the exceptional case, so client code never sees exceptional behavior.

- **Provide Context with Exceptions** — a stack trace tells you *where*, never *what the
  operation was trying to do*. Every thrown exception carries an informative message
  naming **the operation that failed and the type of failure**, with enough detail to log
  usefully in the `catch`.

## Worked Example 1: return codes → exceptions

**Before** — device shutdown logic buried under nested checks:

```java
public void sendShutDown() {
    DeviceHandle handle = getHandle(DEV1);
    // Check the state of the device
    if (handle != DeviceHandle.INVALID) {
        retrieveDeviceRecord(handle);
        if (record.getStatus() != DEVICE_SUSPENDED) {
            pauseDevice(handle);
            clearDeviceWorkQueue(handle);
            closeDevice(handle);
        } else {
            logger.log("Device suspended.  Unable to shut down");
        }
    } else {
        logger.log("Invalid handle for: " + DEV1.toString());
    }
}
```

**After** — the two concerns separated; each readable alone:

```java
public void sendShutDown() {
    try {
        tryToShutDown();
    } catch (DeviceShutDownError e) {
        logger.log(e);
    }
}

private void tryToShutDown() throws DeviceShutDownError {
    DeviceHandle handle = getHandle(DEV1);
    DeviceRecord record = retrieveDeviceRecord(handle);
    pauseDevice(handle);
    clearDeviceWorkQueue(handle);
    closeDevice(handle);
}

private DeviceHandle getHandle(DeviceID id) {
    ...
    throw new DeviceShutDownError("Invalid handle for: " + id.toString());
    ...
}
```

**What it demonstrates:** *"This isn't just a matter of aesthetics."* The shutdown
algorithm and the error handling are now two things you can understand independently.

## Worked Example 2: exception-type explosion → one wrapper

**Before** — three catch blocks doing essentially the same work, pure duplication:

```java
ACMEPort port = new ACMEPort(12);
try {
    port.open();
} catch (DeviceResponseException e) {
    reportPortError(e);
    logger.log("Device response exception", e);
} catch (ATM1212UnlockedException e) {
    reportPortError(e);
    logger.log("Unlock exception", e);
} catch (GMXError e) {
    reportPortError(e);
    logger.log("Device response exception");
} finally { … }
```

**After** — one exception type, because the handling is the same regardless of cause:

```java
LocalPort port = new LocalPort(12);
try {
    port.open();
} catch (PortDeviceFailure e) {
    reportError(e);
    logger.log(e.getMessage(), e);
} finally { … }
```

The wrapper does the translation and nothing else:

```java
public class LocalPort {
    private ACMEPort innerPort;

    public LocalPort(int portNumber) {
        innerPort = new ACMEPort(portNumber);
    }

    public void open() {
        try {
            innerPort.open();
        } catch (DeviceResponseException e) {
            throw new PortDeviceFailure(e);
        } catch (ATM1212UnlockedException e) {
            throw new PortDeviceFailure(e);
        } catch (GMXError e) {
            throw new PortDeviceFailure(e);
        }
    }
    …
}
```

**What it demonstrates:** in most situations the work you do in a catch is standard
regardless of cause — record the error and make sure you can proceed. Classify by *how
it will be caught*, not by where it came from.

## Worked Example 3: Special Case Pattern kills the catch

**Before** — the exception is doing business logic, and it clutters:

```java
try {
    MealExpenses expenses = expenseReportDAO.getMeals(employee.getID());
    m_total += expenses.getTotal();
} catch (MealExpensesNotFound e) {
    m_total += getMealPerDiem();
}
```

**After** — make the DAO always return a `MealExpenses`:

```java
MealExpenses expenses = expenseReportDAO.getMeals(employee.getID());
m_total += expenses.getTotal();
```

```java
public class PerDiemMealExpenses implements MealExpenses {
    public int getTotal() {
        // return the per diem default
    }
}
```

**What it demonstrates:** "no meals expensed" is not an error — it is a business rule
with a default. Encapsulate it in a special-case object and the client never sees an
exceptional path.

## Anti-patterns

- **Returning `null`** — *"we are essentially creating work for ourselves and foisting
  problems upon our callers. All it takes is one missing null check to send an
  application spinning out of control."*
  - The deep point: code drowning in null checks doesn't have *too few* checks, it has
    **too many**. The fix is upstream.
  - Instead: throw an exception, or return a **Special Case object**. For collections,
    return `Collections.emptyList()` — a predefined immutable empty list — so the caller
    just iterates:
    ```java
    List<Employee> employees = getEmployees();   // never null
    for (Employee e : employees)
        totalPay += e.getPay();
    ```
  - If a third-party method returns null, **wrap it** with one that throws or returns a
    special case.

- **Passing `null`** — *worse than returning it.* Unless an API expects it, never pass
  null.
  - Neither remedy works: throwing `InvalidArgumentException` just relocates the problem
    (*what should the handler do? is there any good course of action?*), and `assert
    p1 != null` is good documentation but still a runtime error.
  - **In most languages there is no good way to handle an accidentally passed null, so
    the rational approach is to forbid passing null by default.** Then a null in an
    argument list is unambiguously a bug.

- **Checked exceptions (in general application code)** — the debate is over; the price is
  an **Open/Closed Principle violation**.
  - Mechanism: throw a checked exception three levels below the catch and every method
    in between must declare it. A change at a low level cascades signature changes
    upward, forcing rebuilds and redeploys of modules that care about nothing that
    changed. **Encapsulation breaks** — every function on the throw path must know about
    a low-level exception detail, which defeats the point of handling errors at a distance.
  - Evidence they're unnecessary: C#, C++, Python and Ruby have no checked exceptions and
    robust software is written in all of them.
  - **The exception to the exception:** checked exceptions can be useful when writing a
    **critical library** where the caller *must* catch. In general application
    development, dependency costs outweigh the benefits.

- **Error handling that dominates the codebase** — not that it's all the code does, but
  that scattered handling makes it impossible to see what the code does.

## Mental Models

- **A `try` block is a transaction.** Whatever happens inside, the `catch` must restore
  a consistent state.
- **Push error detection to the edges.** Wrap external APIs so you throw *your*
  exceptions, and define a handler above your code for aborted computations. The middle
  then reads as a clean unadorned algorithm.
- **Not everything abnormal is an error.** When the "exceptional" case has a defined
  business answer, it belongs in a Special Case object, not a catch block.
- **Ask "how will this be caught?"** when designing an exception hierarchy — not "where
  did this come from?"

## Key Takeaways

1. **Throw exceptions; don't return error codes.**
2. **Write the try-catch-finally first**, driven by a test that forces the exception.
3. **Prefer unchecked exceptions** in application code; reserve checked for critical
   libraries.
4. **Every exception carries context** — the operation and the failure type.
5. **Wrap third-party APIs** and translate to one exception type per area of code.
6. **Never return null; never pass null.** Use Special Case objects and empty collections.
7. **Use the Special Case Pattern** to delete catch blocks that encode business rules.

## Connects To
- **Ch3 (Functions)**: "Extract Try/Catch Blocks" and "Error Handling Is One Thing" —
  `try` must be the first word in its function.
- **Ch8 (Boundaries)**: wrapping third-party APIs is the same move, for the same reasons.
- **Ch9 (Unit Tests)**: the TDD loop that drives the try-catch scope into existence.
- **Ch11 (Systems)** / **OCP**: checked exceptions as an Open/Closed violation.
- **Fowler, *Refactoring***: Special Case Pattern (a.k.a. Null Object).
