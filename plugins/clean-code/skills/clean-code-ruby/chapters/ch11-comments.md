# Chapter 11: Comments

## Core Idea
"Version control exists for a reason." The Ruby guide's comment section is half its JavaScript parent's: **two rules**, both about history — no commented-out code, no journal comments. It does not carry the JavaScript parent's positive rule ("only comment things that have business logic complexity") or its rule against positional markers, so it never says when a comment *is* worth writing.

## Frameworks Introduced
- **Don't leave commented out code in your codebase**: "Version control exists for a reason. Leave old code in your history."
  - When to use: any block of `#`-prefixed code.
  - How: delete it. If it's needed again, `git log` and `git show` will find it.
- **Don't have journal comments**: "Remember, use version control! There's no need for dead code, commented code, and especially journal comments. Use `git log` to get history!"
  - When to use: any dated change log at the top of a method or file.
  - How: delete it; write that information in commit messages, where it is attached to the change it describes.

## Key Concepts
- **Commented-out code** — disabled code kept in place "just in case"; dead code (Ch 4) that also looks like documentation.
- **Journal comment** — a dated, initialled change log inside the source (`# 2016-12-20: Removed monads, didn't understand them (RM)`).
- **Version control** — the system of record for history; `git log` replaces both kinds of comment.

## Mental Models
- **Ask "is this history or explanation?"** History belongs in version control. This guide says nothing about explanation — for that, see the related skills below.
- **Commented-out code is a question nobody will answer.** Every later reader has to decide whether it matters; nobody ever deletes it, so it accumulates.

## Anti-patterns
- **Commented-out calls left after a refactor** (`# do_other_stuff`).
- **Dated change logs above a method**: they drift from the code, duplicate `git log`, and are never complete.
- **Initials in comments** (`(RM)`, `(JP)`): attribution is what `git blame` is for.

## Code Examples
```ruby
# Bad
do_stuff
# do_other_stuff
# do_some_more_stuff
# do_so_much_stuff

# Good
do_stuff
```
- **What it demonstrates**: the three disabled calls carry no information a reader can act on; version control already holds them.

## Worked Example
**Removing a journal.**

```ruby
# 2016-12-20: Removed monads, didn't understand them (RM)
# 2016-10-01: Improved using special monads (JP)
# 2016-02-03: Removed type-checking (LI)
# 2015-03-14: Added combine with type-checking (JR)
def combine(a, b)
  a + b
end
```

Four lines of history above a two-line method. None of it explains what `combine` does, and the last entry describes type-checking the method no longer has — the same type-checking Ch 4 tells you to remove. The good version is just the method:

```ruby
def combine(a, b)
  a + b
end
```

The history still exists, attached to the commits that made each change, where `git log` will show it in order and with the full diff. **The transferable rule**: a comment recording *when* or *who* belongs in a commit message; a comment recording *what was there before* belongs in the repository history.

## Key Takeaways
1. **Delete commented-out code**; version control keeps it.
2. **Delete journal comments**; use commit messages and `git log`.
3. **This guide does not say when to write a comment** — for the positive rules (explain *why*, warn of consequences, never restate the code) use the related skills.

## Connects To
- **Ch 4**: "Remove dead code" — commented-out code is dead code with a disguise.
- **Ch 10**: the formatter carries style; version control carries history; neither belongs in comments.
- **clean-code-javascript**: "Only comment things that have business logic complexity" and "Avoid positional markers" — the two comment rules the Ruby port dropped.
- **clean-code-java**: the full treatment of good and bad comments.
