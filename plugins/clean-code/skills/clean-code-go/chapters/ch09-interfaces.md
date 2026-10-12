# Chapter 9: Interfaces and Composition

## Core Idea
Go interfaces are satisfied **implicitly**, which makes them cheap to use and hard to see. So keep them **small**, prove a type satisfies one with a compile-time assertion (`var _ io.Writer = &NullWriter{}`), share fields by **embedding structs** behind a constructor, never embed an interface in a struct to "show" it is implemented, and **accept interfaces, return concrete types**.

## Frameworks Introduced
- **Implicit satisfaction, small interfaces** — interfaces "aren't explicitly implemented like they would be in Java or C#"; a type satisfies one by having its methods. The downside: "it can be difficult to see which interfaces are implemented by a struct. Therefore, it's common to define interfaces with as few methods as possible."
- **Three ways to make satisfaction explicit**:
  1. **A constructor returning the interface** — `func NewNullWriter() io.Writer`. Delete `Write` and compilation fails. Redundant when the type has nothing to initialise, and it hides the concrete type.
  2. **A blank-identifier assertion** — `var _ io.Writer = &NullWriter{}`. Checked at compile time, then discarded; list several for several interfaces. "This is generally the preferred solution for checking interface contract fulfillment."
  3. **Embedding the interface in the struct** — "achieves the opposite of what we want" (see Anti-patterns and the Worked Example).
- **Embedded structs for shared fields** — embed a `Metadata` struct in `Document` and `AudioFile`, and build it with one constructor, so "we can change it in just a single place." Adding `CreatedAt` means editing `NewMetadata`; adding a method (`AddUpdateInfo`) reaches every embedding type "without breaking our existing code." The article calls this "a type of inheritance"; it is composition — "Go doesn't support inheritance (and thus has no notion of a superclass). We can imitate the behaviour, but it is not a built-in part of the language."
- **Accept interfaces, return concrete types** — from Jon Postel's robustness principle, *"Be conservative in what you do; be liberal in what you accept from others"* (a TCP specification proverb, as the article notes). "You should write functions that accept an interface and return a concrete type."
  - Why: callers can pass any implementation — in tests, a do-nothing mock — while getting a concrete type back.
  - Small interfaces make this cheap: the `NullWriter` mock is four lines. "This is why it is encouraged to make interfaces as small as possible in idiomatic Go."

## Key Concepts
- **Implicit interface satisfaction** — a type implements an interface by having its methods; no `implements` keyword.
- **Interface contract** — the method set an interface requires.
- **Compile-time interface assertion** — `var _ Iface = &T{}`, a blank-identifier assignment the compiler must type-check.
- **Blank identifier** — `_`, which discards the value but not the type check.
- **Embedded struct** — a struct type listed without a field name; its fields and methods are promoted to the outer type.
- **Embedded interface (in a struct)** — an interface-typed anonymous field; it compiles as satisfying the interface even when its value is `nil`.
- **Partial override** — redefining one method of an embedded interface while the rest still call through to the (possibly `nil`) embedded value.
- **Accept interfaces, return concrete types** — the article's reading of Postel's law for Go functions.
- **Null object / mock writer** — a do-nothing implementation such as `NullWriter` (the standard library's is `io.Discard`; the article names the older `ioutil.Discard`).

## Mental Models
- **Think of an implicit interface as a contract nobody signed.** A compile-time assertion is the signature.
- **Think of an embedded interface field as a `nil` function pointer** — "An interface method in Go is essentially a function pointer."
- **Use embedding for shared *fields and behaviour*, not to claim an interface.**
- **Use Postel at every function boundary**: widen what you accept (interfaces), narrow what you return (concrete types).

## Anti-patterns
- **Embedding an interface to "show" implementation** — `type NullWriter struct { Writer }` compiles and panics on the first `Write`.
- **Embedded interfaces as nil-able public fields** — the nil-safe getter from Ch 7 can't help, because embedded interfaces "are by nature always public."
- **Partial overrides of an embedded interface** — overriding `Read` on a type embedding `io.ReadCloser` looks like Java/C# overriding, but `Close` still calls the nil embedded value.
- **Embedded interfaces for partial mocks** — some use them to implement only the methods a test needs; "I can see this argument, but I am still not a fan of this approach."
- **Large interfaces** — the larger the method set, the harder implicit satisfaction is to see and to mock.

## Code Examples
*Lightly corrected: in the article, `NullWriter`'s `Write` has a pointer receiver but tests pass `NullWriter{}` by value (which does not satisfy `io.Writer`); `NewMetadata` is declared to return `Metadata` but returns `&Metadata{…}` and is then called with no argument; and the second assertion block names `NullWriter` where it means `NullReaderWriter`.*

Compile-time assertions, the preferred check:

```go
type NullWriter struct{}

func (writer *NullWriter) Write(data []byte) (n int, err error) {
    return len(data), nil // do nothing
}

var _ io.Writer = &NullWriter{}

type NullReaderWriter struct{}

var _ io.Writer = &NullReaderWriter{}
var _ io.Reader = &NullReaderWriter{}
```

Shared fields through an embedded struct and one constructor:

```go
type Metadata struct {
    CreatedBy types.User
    CreatedAt time.Time
    UpdatedBy types.User
    UpdatedAt time.Time
}

type Document struct {
    *Metadata
    Title string
    Body  string
}

func NewMetadata(user types.User) *Metadata {
    return &Metadata{
        CreatedBy: user,
        CreatedAt: time.Now(),
    }
}

func NewDocument(user types.User, title string, body string) Document {
    return Document{
        Metadata: NewMetadata(user),
        Title:    title,
        Body:     body,
    }
}

func (metadata *Metadata) AddUpdateInfo(user types.User) {
    metadata.UpdatedBy = user
    metadata.UpdatedAt = time.Now()
}
```

Accept an interface, and mock it in a test:

```go
type Pipe struct {
    writer io.Writer
    buffer bytes.Buffer
}

func NewPipe(w io.Writer) *Pipe {
    return &Pipe{
        writer: w,
    }
}

func TestFn(t *testing.T) {
    // ...
    pipe := NewPipe(&NullWriter{})
    // ...
}
```
- **What it demonstrates**: `NewPipe` accepts any `io.Writer` and returns a concrete `*Pipe`; the test injects a four-line `NullWriter` so `Save` writes nothing — "basic dependency injection and mocking, but … extremely easy to achieve in Go."

## Reference Tables

| How to make "T implements I" explicit | Checked at compile time | Verdict |
|---|---|---|
| Constructor returning `I` (`func NewT() I`) | ✓ | Fine when a constructor is needed anyway; hides the concrete type |
| `var _ I = &T{}` | ✓ | **Preferred**; can list several interfaces |
| Embedding `I` in `T` | ✗ (always compiles) | **Avoid**: methods of a `nil` embedded value panic |

## Worked Example
The embedded-interface trap, step by step.

```go
type NullWriter struct {
    io.Writer
}

func NewNullWriter() io.Writer {
    return &NullWriter{}
}

func main() {
    w := NewNullWriter()
    w.Write([]byte{1, 2, 3})
}
```

It compiles: `NullWriter` satisfies `io.Writer` "via the embedded interface." It then panics — `invalid memory address or nil pointer dereference`. "Since we are pointing to the function of an interface, rather than an actual method implementation, we are trying to invoke a function that's actually a `nil` pointer."

You can make it work by supplying a real implementation — `NullWriter{Writer: &bytes.Buffer{}}` — but that is "not much different from having properties that are initialised as `nil`," and unlike an ordinary field you cannot make it private and guard it with a getter.

Partial overriding makes it worse:

```go
type MyReadCloser struct {
    io.ReadCloser
}

func (closer *MyReadCloser) Read(data []byte) (int, error) {
    // ...
}

func main() {
    closer := MyReadCloser{}

    closer.Read([]byte{1, 2, 3}) // works fine: MyReadCloser's own method
    closer.Close()               // panics: calls the nil embedded ReadCloser
}
```

"Even though this might look like we're overriding methods, which is common in languages such as C# and Java, we actually aren't." (The article adds that `closer.ReadCloser.Close()` would not panic; it would — it is the same call on the same `nil` interface value.)

**The transferable lesson**: to assert an interface, use `var _ I = &T{}`; to share behaviour, embed a concrete struct built by a constructor. Never embed an interface just to satisfy it.

## Key Takeaways
1. **Keep interfaces small** — implicit satisfaction is only readable when the method set is.
2. **Assert satisfaction at compile time** with `var _ I = &T{}`.
3. **Embed structs, not interfaces**, and build embedded structs through one constructor.
4. **Go has composition, not inheritance**; embedding does not give you overriding.
5. **Accept interfaces, return concrete types** — and enjoy four-line mocks in tests.

## Connects To
- **Ch 6**: `error` is the canonical small interface — one `Error() string` method.
- **Ch 7**: embedded interfaces are the nil-able public field that chapter's getter can't guard.
- **Ch 8**: closures, the lighter alternative while an operation stays simple.
- **Ch 10**: the empty interface — the limit case where no methods means every type satisfies it.
- **clean-code-python ch08**: duck-typed dependency inversion — the nearest relative of Go's implicit interfaces in the family.
- **clean-code-java ch10**: the book's classes chapter (SRP, cohesion, OCP via abstractions), the principles behind small interfaces and injection.
