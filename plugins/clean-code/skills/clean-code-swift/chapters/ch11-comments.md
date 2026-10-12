# Chapter 11: Comments

## Core Idea
**Comment only what the code can't say** — "parts of the code that have non-obvious complexity or… additional information about business logic." Delete commented-out code (version control keeps it), and don't use comment banners — including Xcode's `// MARK:` — to divide a type; let structure and formatting do that.

## Frameworks Introduced
- **Only comment on things that have business logic complexity**: "Avoid commenting on the obvious or trivial details that can be easily understood by reading the code."
  - When to use: before writing any comment, ask whether it says *what* (delete it) or *why* (keep it).
  - How: the guide's Good example replaces a loop with the closed-form sum and keeps one comment that names the formula — the non-obvious part.
- **Don't leave commented-out code in your codebase**: "Version control (like Git) is a powerful tool for tracking changes over time. There's no need to keep commented-out code in the codebase as it only adds noise and makes it harder to read."
- **Avoid change markers**: "Avoid using change markers, such as slashes or lines of asterisks, to divide or highlight sections of code. Instead, use good code structure with proper indentation and formatting to make the code easily understandable." The Bad example is a struct divided by `// MARK: - Properties`, `// MARK - Initializer` and `// MARK - Functions`.

## Key Concepts
- **What-comment** — restates the code ("// Initialize the total score"); the guide's target for deletion.
- **Why-comment** — explains non-obvious reasoning or business logic ("// The total score is calculated using the Gauss sum formula").
- **Commented-out code** — disabled code kept "for future reference"; noise that git already preserves.
- **Change marker** — a banner comment dividing a type into sections (`// MARK: -`, slashes, asterisks).
- **`// MARK:`** — Xcode's section comment, shown in the jump bar; the guide counts it as a change marker.
- **Gauss sum** — `n * (n + 1) / 2`, the closed form for 1 + 2 + … + n; the guide's example of a fact worth a comment.

## Mental Models
- **If the comment repeats the line below it, one of them is redundant — and it isn't the code.**
- **Comment the *why*, name the *what*.** A comment explaining what a block does is usually a function name waiting to be extracted (Ch 3).
- **Git is the archive.** Commented-out code and "previous version" notes duplicate what version control stores more accurately.
- **Structure over decoration.** A type small enough not to need `MARK` sections is the guide's real target; banners treat the symptom.

## Code Examples
Change markers removed — the guide's Good version:

```swift
struct Example {
    var name: String
    var age: Int
    
    init(name: String, age: Int) {
        self.name = name
        self.age = age
    }
    
    func performAction() {
        // ...
    }
}
```

- **What it demonstrates**: blank lines and declaration order already separate properties, initializer and methods; the `MARK` banners and the "// Method to perform an action" comment are gone.

Commented-out code, Bad:

```swift
func doSomething() {
    // Previous code that is no longer needed
    // ...
    
    // Code commented out for future reference
    /*
    if someCondition {
        // Code to be executed
    }
    */
    
    // ...
}
```

## Reference Tables

| Comment kind | Keep? | Instead |
|---|---|---|
| Restates the code (*what*) | ✗ | clearer names; extract a function |
| Explains non-obvious logic or business rules (*why*) | ✓ | — |
| Commented-out code | ✗ | delete; Git has it |
| Section banners (`// MARK: -`, `////`, `****`) | ✗ (per the guide) | structure, indentation, formatting |

## Worked Example
`calculateTotalScore` again (Ch 10 tidied its blank lines), now judged on its comments.

**Bad** — a comment on every line, each restating the code:

```swift
func calculateTotalScore(score: Int) {
  // Initialize the total score
  var totalScore = 0
  
  // Loop through each individual score
  for i in 1...score {
    // Add the individual score to the total score
    totalScore += i
  }
  
  // Print the total score
  print("The total score is: \(totalScore)")
}
```

**Good** — the loop becomes the closed form, and the one comment left explains the part a reader can't see:

```swift
func calculateTotalScore(score: Int) {
    // The total score is calculated using the Gauss sum formula
    var totalScore = (score * (score + 1)) / 2
    
    // Print the total score
    print("The total score is: \(totalScore)")
}
```

The Gauss comment earns its place: `(score * (score + 1)) / 2` is not self-explanatory, and the name of the formula lets a reader check it. Read critically, the Good version keeps one comment its own rule bans — "// Print the total score" restates `print(…)` — and `totalScore` could be a `let`. The lesson stands: a why-comment beside a non-obvious expression; no what-comments.

## Source Caveats
- **`// MARK:` is common Swift practice.** Xcode shows `MARK` sections in its jump bar and minimap, and many Swift codebases and style guides use them. The guide's ban comes from the JavaScript original's "avoid positional markers" rule, applied to `MARK`; treat it as this source's position rather than a Swift consensus.
- The JavaScript original's fourth comment rule, "Don't have journal comments", was dropped; "Don't leave commented-out code" makes the same version-control argument.
- Documentation comments (`///`, DocC) aren't covered; the rules are about inline comments.

## Anti-patterns
- **What-comments on every line**: noise that drifts from the code it describes.
- **Commented-out code "for future reference"**: version control is the reference.
- **Banner sections inside a type**: decoration standing in for structure.
- **A comment where a name would do**: the comment is the first thing to go stale.

## Key Takeaways
1. **Comment only non-obvious logic and business rules** — the *why*.
2. **Delete what-comments**; improve the names instead.
3. **Delete commented-out code**; Git keeps history.
4. **Don't divide code with banners**, `// MARK:` included per this guide — structure it so it doesn't need them.

## Connects To
- **Ch 2–3**: names and small functions are what make what-comments unnecessary.
- **Ch 4**: "Remove dead code" is the same argument for code that's uncommented but unused.
- **Ch 10**: formatting and blank lines are the guide's replacement for section markers.
- **`clean-code-java`** (ch04, Comments): the full good-and-bad comment catalogue, including the legitimate kinds (TODOs, warnings of consequences) this three-rule section doesn't list.
