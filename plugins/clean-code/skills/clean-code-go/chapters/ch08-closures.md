# Chapter 8: Closures Are Function Pointers

## Core Idea
A function value is "simply an input parameter like any other, except it represents (points to) a function that can be invoked." Pass one in to let callers supply the operation, instead of growing a `switch` inside a method nobody else can extend — and when the logic inside the closure becomes complex, switch to an interface.

## Frameworks Introduced
- **Closures as parameters** — "what C programmers know as 'function pointers' and what most other programming languages call closures."
  - When to use: a method that performs one of several operations on its data, where new operations keep arriving or come from outside the package.
  - How: replace the operation enum and `switch` with a function-typed parameter; the method applies whatever function it is given.
  - Why: a predetermined `switch` is "quite rigid," bloats with "irrelevant logic," and can't be extended by other packages — "there is no way of extending structure methods in Go as there is in most OOP languages." Closures make "a loosely coupled architecture, making it easier to add functionality without affecting other parts of the code."
- **Closure factories** — when the function-typed parameter's signature gets messy or the operations need different inputs, have a constructor return the closure, capturing its extra inputs.
  - How: `concat(data)` returns `func([]byte) ([]byte, error)`; `Do` then takes a single-argument function.
  - Effect: "we've effectively moved some of the clutter out of the `Do` method signature and into the `concat` method signature."
- **Closure or interface?** — "Usually, whether an interface or a closure is used isn't really of importance; the right choice is whichever one solves the problem at hand. Typically, closures will be simpler to implement if the operation is simple by nature. However, as soon as the logic contained within a closure becomes complex, one should strongly consider using an interface instead."

## Key Concepts
- **Closure / function value** — a function passed or returned as a value; in Go, a first-class function.
- **Function-typed parameter** — e.g. `func something(closure func(float64) float64) float64`.
- **Operation switch** — a method branching on an operation constant (`COMPARE`, `CONCAT`); the rigid alternative.
- **Closure factory** — a function that returns a configured closure, capturing its arguments.
- **Captured variable** — a value from the enclosing function kept alive inside the returned closure.
- **Lack of generics (dated)** — the article presents closures partly as a way "to partially overcome … the lack of generics"; Go has had type parameters since 1.18.

## Mental Models
- **Think of a function-typed parameter as a one-method interface without the type declaration.** Use it while the operation is simple.
- **Use a closure factory to normalise arity**: whatever inputs an operation needs, the factory captures them and returns the one shape `Do` expects.
- **Use complexity as the switch point**: once a closure carries real logic or state, an interface (Ch 9) is easier to read and test.

## Anti-patterns
- **An ever-growing operation `switch`** inside a method — each new operation edits the method and every caller depends on the enum.
- **Closures with complex logic** — the point at which the article says to "strongly consider using an interface instead."
- **Leaving the messy signature in the method** — `Do(operation func(data []byte, data []byte) ([]byte, error), data []byte)` is hard to read; move the clutter into a factory.

## Code Examples
*Lightly corrected: the article's two-parameter function type reuses the name `data` (not valid Go), its `append` omits the `...`, and its call site uses `compare(data)` where it means `concat(data)`.*

The rigid version:

```go
func (datastore *Datastore) Do(operation Operation, data []byte) error {
    switch operation {
    case COMPARE:
        return datastore.compare(data)
    case CONCAT:
        return datastore.add(data)
    default:
        return ErrUnknownOperation
    }
}
```

A function-typed parameter — flexible, but the signature is messy and the arity fixed:

```go
func (datastore *Datastore) Do(operation func(a, b []byte) ([]byte, error), data []byte) error {
    result, err := operation(datastore.data, data)
    if err != nil {
        return err
    }
    datastore.data = result
    return nil
}

func concat(a []byte, b []byte) ([]byte, error) {
    // ...
}

// datastore.Do(concat, data)
```

## Worked Example
The third step: a closure factory, so `Do` takes a single-argument function and each operation captures what it needs.

```go
func concat(data []byte) func([]byte) ([]byte, error) {
    return func(concatting []byte) ([]byte, error) {
        return append(data, concatting...), nil
    }
}

func (datastore *Datastore) Do(operation func([]byte) ([]byte, error)) error {
    result, err := operation(datastore.data)
    if err != nil {
        return err
    }
    datastore.data = result
    return nil
}

func main() {
    // ...
    datastore.Do(concat(data))
    // ...
}
```

Walk the problem it solves. The two-argument version raised two questions the article asks directly: "What happens if we find out that we actually want the `concat` to be able to take more than just two byte arrays as input? Or if we want to add some completely new functionality that may also need more or fewer input values?" With the factory, any operation — however many inputs it needs — is built outside `Do` and handed in as the same one-argument shape. `Do` only applies it and stores the result. "Within the returned function, we store the input values originally passed in to our `concat` function."

The article acknowledges the pattern "may seem quite strange" at first, but recommends getting used to it: "it can help loosen up logic coupling and get rid of bloated functions."

## Key Takeaways
1. **A function is a parameter like any other** — use one to let callers supply the operation.
2. **Replace a growing operation `switch`** with a function-typed parameter; it also lets other packages extend behaviour.
3. **Use closure factories** to keep the receiving signature simple and the arity flexible.
4. **Closure for simple operations, interface for complex ones.**
5. The article's "lack of generics" motivation is dated (Go 1.18+), but the decoupling argument still stands.

## Connects To
- **Ch 4**: a long or messy signature is the same smell whether its parameters are values or functions.
- **Ch 9**: interfaces — where to go when a closure's logic stops being simple.
- **Ch 10**: the other pre-generics workaround, the empty `interface{}`.
- **Further reading the article cites**: Dave Cheney, "Do not fear first class functions" (2016) and talk; Jon Bodner's related talk.
- **clean-code-javascript**: closures as JavaScript's main encapsulation tool, a contrast with their narrower role here.
