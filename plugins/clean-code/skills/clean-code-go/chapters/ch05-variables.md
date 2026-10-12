# Chapter 5: Variables — Scope and Declaration

## Core Idea
Keep every variable in the **smallest scope** and modify it as little as possible. No mutable globals; no wide-scoped `var` that an inner `:=` silently shadows; declare at first use; and when a non-primitive value must not change, make it an **unexported field reachable only through methods** — Go's only way to make it publicly immutable.

## Frameworks Introduced
- **Globals don't belong in clean code** — *"Global variables are problematic and don't belong in clean code."* A mutable global "can be changed by any part of the codebase. At no point can you guarantee that this variable is going to be a specific value."
  - How: small functions remove the need — "Writing smaller functions can typically eliminate reliance on mutable variables that leak into the global scope."
- **Shrink the scope instead of blaming the syntax** — wide-scoped (even non-global) variables invite **variable shadowing**. The fix is structural: move the logic into a function that *returns* the value, so the outer variable is assigned once. "Developers need to take responsibility for their own code rather than blaming these issues on the variable declaration syntax of a particular language like Go."
- **Return a new value instead of mutating** — if later logic would mutate the same variable again, "extract that logic out as its own self-contained function … instead of expanding the mutable scope of our variables, we can just return a new value."
- **Declare as close to use as possible** — the C habit of declaring everything at the top "keeps the readers on their toes, in all the wrong ways." Short-term memory is limited, and tracking which variables might be mutated where is what makes the eventual result hard to work out.
  - Ladder: declare at use → assign from an immediately invoked function literal → move that literal into a **named constructor** (`NewSenderChannel()`).
- **Publicly immutable via an unexported field** — Go has no `const struct` and no `static` variables (`const` covers only basic types), so restraint is the only guard for a local. At package level, wrap the value in a struct with an **unexported** field and expose behaviour through methods. "As of writing this document, this is the only way of creating publicly immutable non-primitive variables."
  - Bonus: it hides the implementation, so "we are free to change it at any point" without breaking callers.

## Key Concepts
- **Global variable** — package-level and mutable; any code may change it, so no code can rely on its value.
- **Variable scope** — the region in which a name is visible and assignable; the smaller, the safer.
- **Variable shadowing** — `val, err := …` in an inner block declares a *new* `val`, leaving the outer one untouched.
- **Mutable scope** — the region over which a variable can change; returning new values keeps it small.
- **Declaration at use** — declaring a variable where it is first needed, not at the top of the function.
- **Immediately invoked function literal** — `x := func() T { … }()`, tying a variable to the logic that builds it.
- **Named constructor** — `NewSender()`, the named form of that literal.
- **Unexported field** — a lowercase struct field, invisible outside its package; Go's tool for publicly immutable state.
- **Point of contact** — the API surface users depend on; shrinking it frees you to change the implementation.

## Mental Models
- **Think of a mutable variable's scope as a list of suspects.** Every line that can see it can change it; shrink the list.
- **Use "return, don't reassign"** when a value goes through several stages — each stage a function returning the next value.
- **Think of an unexported field plus methods as Go's `const` for structs.** The compiler enforces it at the package boundary.
- **Use the reader's short-term memory as the budget**; every variable declared early is one more thing held in it.

## Anti-patterns
- **Mutable package-level variables** — unpredictable by definition.
- **A wide-scoped `var` assigned with `:=` in a branch** — the classic shadowing bug; it compiles and prints the wrong thing.
- **C-style declaration blocks** at the top of a function.
- **Growing a variable's mutable scope** to accommodate one more modification instead of extracting a function that returns.
- **Exporting a channel or other mutable field** that callers can replace or close.

## Code Examples
*Lightly corrected: the article's immediately invoked literal omits its call parentheses, and its final `Send` call passes `&Item{}` to a method taking `Item`.*

From declaration at use to a named constructor:

```go
func main() {
    sender := func() chan Item {
        channel := make(chan Item)
        go func() {
            for {
                select { /* ... */ }
            }
        }()
        return channel
    }()
}
```

```go
func main() {
    sender := NewSenderChannel()
}

func NewSenderChannel() chan Item {
    channel := make(chan Item)
    go func() {
        for {
            select { /* ... */ }
        }
    }()
    return channel
}
```

Publicly immutable through an unexported field:

```go
type Sender struct {
    sender chan Item
}

func NewSender() *Sender {
    return &Sender{
        sender: NewSenderChannel(),
    }
}

func (s *Sender) Send(item Item) {
    s.sender <- item
}

func main() {
    sender := NewSender()
    sender.Send(Item{})
}
```
- **What it demonstrates**: callers can send but cannot reach, replace or close the channel; "if we no longer wish to use a channel implementation in our package, we can easily change this without breaking the usage of the `Send` method."

## Worked Example
The shadowing bug, from an article the author cites ("Golang scope issue"):

```go
func doComplex() (string, error) {
    return "Success", nil
}

func main() {
    var val string
    num := 32

    switch num {
    case 16:
        // do nothing
    case 32:
        val, err := doComplex()
        if err != nil {
            panic(err)
        }
        if val == "" {
            // do something else
        }
    case 64:
        // do nothing
    }

    fmt.Println(val)
}
```

From a skim, it should print `Success`. It prints an empty line: `val, err := doComplex()` "declares a new variable `val` in the switch's `case 32` scope and has nothing to do with the variable declared in the first line of `main`." The article grants that the syntax is "a little tricky," but names the real defect: "The declaration of `var val string` as a mutable, largely scoped variable is completely unnecessary."

**The fix is to delete the wide variable**, not to switch `:=` to `=`:

```go
func getStringResult(num int) (string, error) {
    switch num {
    case 16:
        // do nothing
    case 32:
        return doComplex()
    case 64:
        // do nothing
    }
    return "", nil
}

func main() {
    val, err := getStringResult(32)
    if err != nil {
        panic(err)
    }
    if val == "" {
        // do something else
    }
    fmt.Println(val)
}
```

"`val` is no longer modified, and the scope has been reduced." If `// do something else` is another attempt to change `val`, extract that too and return the new value:

```go
func getVal(num int) (string, error) {
    val, err := getStringResult(num)
    if err != nil {
        return "", err
    }
    if val == "" {
        return NewValue() // pretend function
    }
    return val, nil
}
```

**The transferable lesson**: shadowing is a symptom of a variable living longer and wider than it needs to. Remove the long-lived variable and there is nothing left to shadow.

## Key Takeaways
1. **No mutable globals.** If you can't guarantee a value, neither can anyone reading it.
2. **Kill shadowing by shrinking scope** — extract a function that returns the value.
3. **Return new values** instead of widening a variable's mutable scope.
4. **Declare at first use**, ideally from a constructor function.
5. For non-primitive values that must not change, use an **unexported field behind methods**.
6. Hiding the field also **frees the implementation** to change behind a stable method signature.

## Connects To
- **Ch 3**: narrow scopes are what make short variable names safe.
- **Ch 4**: small functions are the mechanism that removes wide, mutable variables.
- **Ch 7**: a pointer parameter is the same scope problem in another form — "*almost* expanding the scope of the variable to the global level" — and the same unexported-field technique guards against `nil` fields.
- **clean-code-java ch06**: the book's objects-and-data-structures chapter — hiding implementation behind behaviour, the general form of the `Sender` wrapper.
