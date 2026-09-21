# Chapter 8: Classes — Dependency Inversion Principle (DIP)

## Code Note
This chapter's "Good" snippet is the guide's own contribution upstream: the example "was taken from [a submission made to the Django documentation](https://code.djangoproject.com/ticket/21179) by this author."

## Core Idea
> "Depend upon abstractions, not concrete details." — Uncle Bob

**Find the narrowest abstraction a dependency actually requires, then satisfy exactly that.** In Python that abstraction is usually a single duck-typed method — and satisfying it directly replaces pages of low-level workaround code.

## Frameworks Introduced
- **Identify the real abstraction your dependency depends on**: the chapter's distinctive move — read the library's contract instead of accommodating its default implementation.
  - When to use: whenever you find yourself manipulating a library's internals (buffers, cursors, temp files) to extract a result.
  - How: (1) ask what the dependency *minimally requires* of the object you hand it; (2) supply a small object implementing exactly that; (3) delete the machinery you built to work around the concrete default.
  - Worked here as: `csv.writer` "just needs an object with a `.write()` method to do our bidding." So pass one — not a `StringIO`.
  - Why it works: "the writer class depends on the `.write()` abstraction of the object it receives, without caring about the low level, concrete details of what the method actually does."
- **Duck typing as dependency inversion**: in Python the abstraction needn't be declared — a class with the right method *is* the abstraction.
  - When to use: when a dependency's requirement is one or two methods.
  - How: write a minimal class implementing just those methods. No ABC, no `Protocol`, no inheritance required.
  - Trade-off: nothing declares or checks the contract, so it can drift silently on a library upgrade. Add a `Protocol` (Ch 7) when the seam matters enough to type-check.
- **Subvert the contract, don't merely satisfy it**: `Echo.write()` *returns* its value instead of storing it — legal under the `.write()` contract, and it converts a buffered writer into a streaming one.
  - When to use: when you need a different data-flow direction than the library's default gives you.
  - How: keep the signature, change what the method does with the value. The library's own loop then yields your values.

## Key Concepts
- **Abstraction** — the minimal behavioural contract a dependency requires (here: "has `.write(value)`").
- **Concrete detail** — a specific implementation of that contract (`StringIO`, a real file).
- **Duck typing** — satisfying a contract by having the right methods, with no declared relationship.
- **File-like interface** — the informal protocol (`read`, `write`, `seek`, `truncate`) that `Echo` implements one method of.
- **`Echo`** — the guide's name for the object that implements "just the write method of the file-like interface."
- **Streaming response** — a response whose body is produced lazily from an iterator, so nothing buffers in memory.
- **Buffer shuffling** — the `seek(0)` / `read()` / `seek(0)` / `truncate()` cycle needed to drain a `StringIO` after each row; the smell DIP removes here.

## Reference Tables

| What `csv.writer` needs | Concrete detail | Narrow abstraction |
|---|---|---|
| An object with `.write()` | `StringIO()` — a full file-like buffer | `Echo()` — one method |
| Row output | Left in the buffer; must be drained | Returned directly by `writerow()` |
| Memory profile | Buffer per row, manually reset | None — values pass straight through |
| Code required | Generator + 4 buffer operations | One 2-line class |

| Tell | Likely DIP violation |
|---|---|
| `seek`/`truncate`/`read` cycles around a library call | Accommodating a concrete default |
| A nested helper that exists only to extract results | Wrong abstraction chosen |
| `import io` purely to feed another library | Look for the one-method contract |
| Constructing collaborators inside a function/constructor | Inject them instead |

## Worked Example
**The task**: a web view returning an HTTP response that streams rows of a CSV file created on the fly, using the standard library's CSV writer.

**Bad.** `csv.writer` wants somewhere to write, so we give it the obvious concrete thing — a `StringIO` — then fight to get each row back out:

```python
import csv
from io import StringIO


def some_view(request):
     rows = (
          ['First row', 'Foo', 'Bar', 'Baz'],
          ['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"]
     )

     # Define a generator to stream data directly to the client
     def stream():
          buffer_ = StringIO()
          writer = csv.writer(buffer_, delimiter=';', quotechar='"')
          for row in rows:
               writer.writerow(row)
               buffer_.seek(0)
               data = buffer_.read()
               buffer_.seek(0)
               buffer_.truncate()
               yield data

     response = StreamingHttpResponse(stream(), content_type='text/csv')
     response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
     return response
```

Four buffer operations per row, a nested generator existing only to perform them, and a `StringIO` import that serves no purpose but to be written to. The guide's verdict: *"It's a lot of work and not very elegant."*

**The insight.** Stop asking what a writer normally writes *to*, and ask what it *requires*: *"the writer just needs an object with a `.write()` method to do our bidding. Why not pass it a dummy object that immediately returns the newly assembled row, so that the `StreamingHttpResponse` class can immediately stream it back to the client?"*

**Good.**

```python
import csv


class Echo:
     """An object that implements just the write method of the file-like
     interface.
     """

     def write(self, value):
          """Write the value by returning it, instead of storing in a buffer."""
          return value


def some_streaming_csv_view(request):
     """A view that streams a large CSV file."""
     rows = (
          ['First row', 'Foo', 'Bar', 'Baz'],
          ['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"]
     )
     writer = csv.writer(Echo(), delimiter=';', quotechar='"')
     return StreamingHttpResponse(
          (writer.writerow(row) for row in rows),
          content_type="text/csv",
          headers={
               'Content-Disposition': 'attachment; filename="somefilename.csv"'},
     )
```

**Why it's better** — and the guide says the reason "should be obvious": *"less code (and more performant) to achieve the same result."*

The mechanism deserves spelling out, because it's the reusable part. `csv.writer.writerow()` internally calls `self.write(formatted_line)` and returns whatever that call returns. With `StringIO`, `write()` returns a character count and the data stays behind in the buffer — hence the drain cycle. With `Echo`, `write()` hands the formatted line straight back, so `writerow(row)` *is* the row. The generator expression becomes the response body directly: no buffer, no nested function, no per-row bookkeeping, and no row ever held in memory after it's sent.

Note what did *not* happen: no ABC was declared, nothing was registered, and `Echo` inherits from nothing. The abstraction was always there in `csv`'s contract — the bad version simply hadn't looked for it.

## Anti-patterns
- **Reaching for the obvious concrete class** (`StringIO` because "a writer needs a file"): the root error; check the required contract first.
- **Buffer shuffling** (`seek`/`read`/`seek`/`truncate`): a strong tell that you're accommodating an implementation rather than depending on an abstraction.
- **A helper that exists only to extract results from a library**: the nested `stream()` generator; delete it by choosing the right abstraction.
- **Instantiating collaborators inside a constructor or function**: hardwires the concrete class; inject it (Ch 4's `VersionCommentElement(get_version("pip"))`).
- **Building a full protocol implementation when one method is required**: `Echo` implements `write` and nothing else, deliberately.
- **Leaving a duck-typed seam undocumented**: at minimum say which method is relied on, as `Echo`'s docstring does; add a `Protocol` when the seam is load-bearing.

## Key Takeaways
1. **Depend on abstractions, not concrete details** — and in Python the abstraction is usually one duck-typed method.
2. **Ask what the dependency minimally requires.** `csv.writer` needs `.write()`, not a file.
3. **A two-line class can delete a page of workaround code**, and run faster while doing it.
4. **`seek`/`truncate` cycles are a DIP smell.** They mean you're working around a concrete default.
5. **You may reinterpret a contract, not just satisfy it** — `Echo.write()` returns instead of storing, turning buffering into streaming.
6. **No ABC required.** Duck typing is dependency inversion in Python; reach for `Protocol` only when the seam needs checking.
7. **Inject collaborators; never construct them internally.**
8. **Read the library's source or docs for its contract.** The abstraction is usually already documented — the bad version just didn't look.

## Connects To
- **Ch 7 (ISP)**: ISP keeps abstractions small; DIP says depend on them. `Echo`'s single method satisfies both at once.
- **Ch 4 (SRP)**: constructor injection of `get_version("pip")` is the same inversion at class-construction time.
- **Ch 3 (side effects)**: `Echo.write()` is pure — value in, value out — which is exactly why it can stream.
- **Ch 5 (OCP)**: both add behaviour without modifying the library; OCP via hooks, DIP via a narrower dependency.
- **Ch 6 (LSP)**: a narrow abstraction shrinks the protocol any substitute must preserve.
- **Django `StreamingHttpResponse`** and [Django ticket #21179](https://code.djangoproject.com/ticket/21179): the upstream home of this example.
- **`typing.Protocol`**: declares a duck-typed contract like `Echo`'s so `mypy` can verify it.
