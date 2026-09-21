# Chapter 1: Clean Code

## Core Idea
The only way to go fast is to keep the code clean at all times — messes slow you down
immediately, not eventually. Clean code is code someone cared about: focused, readable,
free of duplication, and covered by tests.

## Frameworks Introduced

- **LeBlanc's Law**: *Later equals never.* The cleanup you defer will not happen.
  - When to use: any time you catch yourself thinking "I'll come back and fix this."
  - How: do the small cleanup now, in the same change. If it is genuinely too large,
    it is a tracked work item, not a mental note.

- **The Boy Scout Rule**: *Leave the campground cleaner than you found it.*
  - When to use: every single check-in, on every file you touch.
  - How: one improvement per commit is enough — rename one variable for the better,
    split one function that grew too long, delete one duplicated block, simplify one
    composite `if`. The rule is that the codebase must be *strictly better* after your
    change, never merely "not worse."
  - Why it works: rot is incremental, so the cure must be incremental too. A team that
    applies this cannot accumulate a mess, because every commit pays down more than it
    borrows.

- **Beck's Rules of Simple Code** (cited via Ron Jeffries, **in priority order**):
  1. Runs all the tests
  2. Contains no duplication
  3. Expresses all the design ideas that are in the system
  4. Minimizes the number of entities (classes, methods, functions)
  - When to use: as the tie-breaker whenever two designs both look acceptable.
  - How: apply in order. A design that passes tests beats one that is prettier;
    removing duplication beats adding an abstraction layer; expressiveness beats
    entity-count golf. Rule 4 never overrides rules 2 and 3 — you do not merge two
    well-named functions just to have fewer functions.

- **The Primal Conundrum**: developers know past messes slow them down, yet make new
  messes to hit deadlines. *You will not make the deadline by making the mess.*
  - How: when schedule pressure appears, the response is to cut scope, not cleanliness.

- **The Broken Windows metaphor** (Hunt & Thomas): one visible mess signals that nobody
  cares, which licenses the next mess. Bad code *tempts* people to make it worse.

## Key Concepts

- **Clean code** — code that is focused (does one thing well), reads like well-written
  prose, has no duplication, has tests, and looks like someone cared.
- **Wading** — slogging through bad code trying to find the thread of what it does.
- **Code-sense** — the acquired ability to not just recognize a mess but see the
  sequence of behavior-preserving transformations that cleans it up.
- **The Grand Redesign in the Sky** — the doomed rewrite a team demands when the mess
  becomes unmanageable; the new system becomes a mess before it ships.
- **The Total Cost of Owning a Mess** — team productivity asymptotically approaching
  zero as every change breaks two or three other things.
- **The 10:1 read/write ratio** — you read roughly ten times more code than you write,
  so optimize for reading even when it makes writing harder.
- **Literate programming** (Knuth) — compose code so it reads as a document for humans.

## Mental Models

- **Think of yourself as an author, not a typist.** The `@author` field is literal: you
  have readers, and they will judge your effort. Write for them.
- **Use the 10:1 ratio to settle any readability-vs-convenience argument.** Making code
  easy to read makes it easier to write, because you cannot write code without reading
  the code around it. Reading cost is paid ten times; writing cost once.
- **Treat "we don't have time to do it right" as a claim that can be falsified.** The
  mess slows you down *instantly*, not next quarter.
- **The doctor-and-handwashing test:** when someone with authority asks you to skip a
  discipline whose risks they don't understand, complying is unprofessional, not
  obedient. It is your job to defend the code as passionately as they defend the schedule.

## Anti-patterns

- **"I'll clean it up later"** — LeBlanc's Law: later equals never.
- **Demanding a grand rewrite instead of incremental cleanup** — the tiger team must
  chase a moving target for years, and its own output rots before it ships.
- **Blaming requirements, schedules, or managers for bad code** — they rely on us for
  the information they use to set those schedules. The fault is ours.
- **Adding staff to a mess to raise productivity** — new people don't know the design
  intent, so they make more messes, driving productivity further toward zero.
- **Abbreviated error handling, memory leaks, race conditions, inconsistent naming** —
  all the same failure: glossing over details.

## Worked Example: what the experts actually agreed on

Martin asked well-known practitioners to define clean code. The value is in the overlap —
it is the book's table of contents in disguise:

| Source | Definition | Maps to |
|---|---|---|
| **Bjarne Stroustrup** | Elegant and efficient; straightforward logic so bugs can't hide; minimal dependencies; complete error handling per an articulated strategy; performance close to optimal so nobody is tempted to make a mess optimizing. **Does one thing well.** | Ch3 (functions), Ch7 (error handling) |
| **Grady Booch** | Simple and direct. **Reads like well-written prose.** Never obscures intent; full of crisp abstractions and straightforward control flow. | Ch2, Ch5 |
| **"Big" Dave Thomas** | Can be read and *enhanced* by someone other than the author. Has unit and acceptance tests. Meaningful names. **One** way to do a thing, not many. Minimal, explicit dependencies; clear minimal API. | Ch9, Ch8, Ch11 |
| **Michael Feathers** | **Looks like it was written by someone who cares.** Nothing obvious left to improve. | whole book |
| **Ron Jeffries** | Beck's four rules; focus mostly on **duplication**, then expressiveness, then early simple abstractions. | Ch12 |
| **Ward Cunningham** | Each routine turns out to be **pretty much what you expected**; the language looks like it was made for the problem. | Ch2, Ch3 |

**The consensus, which is the whole book compressed:** *no duplication, one thing,
expressiveness, tiny abstractions.*

Note the two that get stated twice across sources: **minimal/small** and **no
duplication**. When forced to pick one rule from this chapter, pick duplication —
Jeffries says repeated code means an idea in your head that is not yet represented in
the code.

## Key Takeaways

1. **Go fast by staying clean.** There is no speed to be gained by making a mess; the
   penalty is immediate.
2. **Apply the Boy Scout Rule on every commit.** Small, continuous improvement is the
   only thing that beats rot.
3. **Duplication is the highest-yield smell.** Repeated code means a missing abstraction.
4. **Code with no tests is not clean**, however elegant it reads.
5. **Optimize for the reader** — the read/write ratio is over 10:1.
6. **Clean code does one thing well** and is "pretty much what you expected."
7. **Recognizing clean code ≠ writing it.** Code-sense comes from disciplined practice
   of many small techniques, not from taste alone.

## Connects To
- **Ch12 (Emergence)**: Beck's four rules are expanded there into the four rules of
  simple design.
- **Ch17 (Smells and Heuristics)**: the concrete catalogue of what "someone cared"
  looks like in practice.
- **Ch14 (Successive Refinement)**: the Boy Scout Rule demonstrated at full scale.
- **SOLID (SRP, OCP, DIP)**: referenced throughout; defined in Martin's *Agile Software
  Development: Principles, Patterns, and Practices* (PPP), of which this book is the
  "prequel" at the code level.
