# Clean Code Gateway

You have the `clean-code` skill family installed. It is a knowledge base, not a
linter: naming, unit size, the do-one-thing rule, duplication, SOLID, failure
handling, when NOT to write a comment, and the smells catalogue.

## The Rule

**Before writing or reviewing code, invoke the matching clean-code skill.**
Not after drafting. Not "if it turns out messy". First -- then write.

Announce it: "Using clean-code-<lang> to <purpose>."

## Dispatch -- pick by the file you are about to touch

| Files | Skill |
|---|---|
| `.ts` `.tsx` | `clean-code:clean-code-typescript` |
| `.js` `.mjs` `.cjs` `.jsx` | `clean-code:clean-code-javascript` |
| `.py` | `clean-code:clean-code-python` |
| `.java` | `clean-code:clean-code-java` |
| Go, Rust, C#, C++, Kotlin, Ruby, PHP, Swift, Scala, **YAML, Terraform, SQL, Bash, Dockerfile** | `clean-code:clean-code-universal` |

Mixed-language change: load the one for the language carrying the logic.
Reviewing for smells in any language: `clean-code-java` also holds the
66-item smells-and-heuristics catalogue.

## Scope -- when this does NOT apply

Answering a question about the codebase, git archaeology, reading a trace or a
log, writing prose or docs, running tests, or changing a config value with no
logic in it. Don't burn a tool call on those.

## Red Flags

These thoughts mean STOP -- you are rationalizing:

| Thought | Reality |
|---|---|
| "It's a one-line change" | A line that names something badly IS the change. |
| "I'm matching the surrounding style" | Match the idiom, not the defects. The skill tells you which is which. |
| "I already know clean code" | Knowing the principles is not applying the checklist. It's one tool call. |
| "It's only a test file" | Tests get the same rules. The skill has a section on them. |
| "I'm reviewing, not writing" | Review is its primary use -- that's where the smells catalogue earns its keep. |
| "I'll write it now and clean it up after" | The cleanup turn never comes. |

## Precedence

The project's own conventions win. Where a `CLAUDE.md` or the user contradicts
the skill, follow them -- and say which rule you set aside and why.
