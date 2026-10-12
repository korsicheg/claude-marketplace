# Chapter 2: Comments

## Core Idea
Separate **doc comments** on exported identifiers — written like documentation, at a high level of abstraction — from **every other comment**, and hold the second kind to a hard test: *"Document why, not how."* Usually even the "why" turns out to be a "what" that better names can say in code.

## Frameworks Introduced
- **Two kinds of comment** — the author accepts that every public variable and function should be annotated ("it gives us consistent rules for documenting our code"), but always distinguishes "comments that enable auto-generated documentation and *all other* comments."
  - When to use: before writing any comment, decide which kind it is.
  - How: doc comments "should be written like documentation — they should be at a high level of abstraction and concern the logical implementation of the code as little as possible." All other comments must earn their place.
  - ⚠ The article attributes the rule that every public identifier must be annotated to `gofmt`. `gofmt` does not check comments; the convention comes from Effective Go and linters (golint, now `staticcheck`/`revive`). The rule stands; the attribution is wrong.
- **Document why, not how** — the article quotes Venkat Subramaniam.
  - When to use: any comment that narrates what the next lines do.
  - How: delete the narration. If something is still unclear, say *why* the code exists — then check whether the "why" is really a *what* that names can carry.
- **Comments as a smell** — "Unnecessary comments can indicate problems with the underlying code, such as the use of poor naming conventions."
  - Not absolutist: "the logic of well-written code may still be so complex that it requires a comment to clarify what is going on. In that case, one might argue that the comment is *helpful* and therefore necessary."
  - But comments don't rescue unclear code: "most people simply won't read comments," and nobody enjoys reviewing "unclear code that's been slathered with comments." *"The less that people have to read to understand what your code is doing, the better off they'll be."*

## Key Concepts
- **Tutorial comment** — a comment explaining a language construct (a `for` loop, an `if`); "absolutely useless in production code."
- **Doc (annotation) comment** — the comment on an exported identifier that feeds generated documentation.
- **Why-comment** — explains intent or reason; the only kind of non-doc comment the article endorses.
- **What-comment in disguise** — a comment that claims to give the reason but still describes the action ("instantiate 10 threads"); names can say it instead.
- **Prose-to-code mapping** — the reader's work of matching a comment to the lines it describes; removing the comment removes the work.
- **Wrong comments** — the article's QueueDeclare example (Ch 4) warns that comments labelling arguments can themselves be wrong, and then cost more to debug than no comment.

## Mental Models
- **Think of a comment as a second copy of the logic, in a language the compiler can't check.** Prefer the copy the compiler checks: names.
- **Use the three-step refinement** on any inline comment: narration → reason → expressive names with no comment left.
- **Treat a comment you feel you need as a naming bug report** — fix the names first, then see whether the comment still says anything.

## Anti-patterns
- **Tutorial comments in production code** — "Hopefully, we aren't collaborating with programmers who don't understand something as simple as a looping construct."
- **Commenting convoluted logic instead of untangling it** — "some people find it acceptable to introduce a comment explaining the convoluted logic. Unfortunately, that doesn't really help."
- **Comments standing in for parameter names** — `false, // durable` at a call site; the fix is a signature change (Ch 4), not a better comment.
- **Doc comments that describe implementation** — doc comments belong at the level of what the identifier is for, not how it works.

## Code Examples
The article's three stages, verbatim apart from formatting:

```go
// iterate over the range 0 to 9
// and invoke the doSomething function
// for each iteration
for i := 0; i < 10; i++ {
  doSomething(i)
}
```

```go
// instantiate 10 threads to handle upcoming workload
for i := 0; i < 10; i++ {
  doSomething(i)
}
```

```go
for workerID := 0; workerID < 10; workerID++ {
  instantiateThread(workerID)
}
```
- **What it demonstrates**: two renames (`i` → `workerID`, `doSomething` → `instantiateThread`) carry everything both comments said, and the reader no longer has "to read the comment and then map the prose to the code."

## Worked Example
Walk the loop above through the article's reasoning.

**Stage 1 — the tutorial comment.** It restates the `for` header and the call. "We know that we're iterating over the range 0 to 9 because we can simply read the code." Nothing is gained; three lines of prose are added.

**Stage 2 — the "why" comment.** "Instantiate 10 threads to handle upcoming workload" looks like a reason. The article is not satisfied: "Now we understand *why* we have a loop and can tell *what* we're doing by simply reading the code … Sort of." The comment is "worrying because it probably should not be necessary to express such an explanation in prose." And on a second look, "technically, we're still saying what we're doing, not why we're doing it."

**Stage 3 — names.** "We can easily express this 'what' directly in our code by using more meaningful names." `workerID` says what the counter counts; `instantiateThread` says what each iteration does. The comment has nothing left to add, so it goes.

**The transferable lesson**: when a comment survives the "why, not how" test, test it once more — is it a reason, or an action phrased like one? Actions belong in names. The article admits the example is trivial and that this gets harder as complexity grows, which is why it frames the habit as practice: "The more you practice writing comments in this mindset … the cleaner your code will become."

## Key Takeaways
1. **Doc comments on exported identifiers: yes**, at a high level of abstraction, describing purpose rather than implementation.
2. **Every other comment must explain why**, never how.
3. A comment that explains *what* is a naming problem; **rename until the comment is redundant**, then delete it.
4. Comments do not fix unclear code — people skip them, and they can be wrong.
5. A genuinely complex block may still deserve a helpful comment; the article is pragmatic, not absolutist.

## Connects To
- **Ch 3**: the renames that retire a comment follow the naming gradients there.
- **Ch 4**: the QueueDeclare call shows argument-label comments as a symptom of a bad signature.
- **clean-code-java ch04**: the book's full taxonomy of good comments (legal, intent, clarification, warning, TODO, public API docs) and bad ones, which this article does not enumerate.
- **Effective Go / Go doc comments**: the conventions for *how* to write the doc comments this chapter says you must write (begin with the identifier's name, full sentences) — the article itself does not cover them.
