# clean-code

Robert C. Martin's *Clean Code* for Claude Code, as eleven knowledge-base skills: one per language with a solid community adaptation, and a shared core for every other language, YAML, Terraform, SQL, Bash and Dockerfiles included. Write or review code, and Claude first loads the rules for the file it's about to touch:

- **The rules, in the language's own idiom**: naming and magic values, function size and the do-one-thing rule, argument counts and flag parameters, side effects, SOLID, duplication, error handling, tests, formatting, and when *not* to write a comment.
- **The book's 66-item smells-and-heuristics catalogue**, for reviews in any language.
- **What each rule means where there are no functions, classes or unit tests**: a Kubernetes manifest, a Terraform module, a CI pipeline, and which rules simply don't apply there.
- **Where a source is wrong or dated**, the skill says so and corrects it instead of repeating it.

It's a knowledge base, not a linter: nothing runs on your code, and there's nothing to install besides the plugin.

## Install

```
/plugin marketplace add korsicheg/claude-marketplace
/plugin install clean-code@korsicheg-marketplace
```

The gateway (see below) starts with your next session or `/clear`.

## The skills

| Skill | For | Made from |
|---|---|---|
| `clean-code-java` | Java, and smell reviews in any language | the book (Java examples), with its refactoring case studies and the smells catalogue |
| `clean-code-typescript` | TypeScript | [labs42io/clean-code-typescript](https://github.com/labs42io/clean-code-typescript) |
| `clean-code-javascript` | JavaScript | [ryanmcdermott/clean-code-javascript](https://github.com/ryanmcdermott/clean-code-javascript) |
| `clean-code-python` | Python | [zedr/clean-code-python](https://github.com/zedr/clean-code-python) |
| `clean-code-php` | PHP | [piotrplenik/clean-code-php](https://github.com/piotrplenik/clean-code-php) |
| `clean-code-csharp` | C# and .NET | [thangchung/clean-code-dotnet](https://github.com/thangchung/clean-code-dotnet) |
| `clean-code-go` | Go | [Pungyeon/clean-go-article](https://github.com/Pungyeon/clean-go-article) |
| `clean-code-ruby` | Ruby | [uohzxela/clean-code-ruby](https://github.com/uohzxela/clean-code-ruby) |
| `clean-code-dart` | Dart and Flutter | [williambarreiro/clean-code-dart](https://github.com/williambarreiro/clean-code-dart) |
| `clean-code-swift` | Swift | [MaatheusGois/clean-code-swift](https://github.com/MaatheusGois/clean-code-swift) |
| `clean-code-universal` | Rust, C++, C, Kotlin, Scala and the rest; YAML, Terraform/HCL, SQL, Bash, Dockerfile | the book, cross-checked against the TypeScript, JavaScript and Python adaptations |

Each skill is a folder of Markdown that Claude reads as it needs it:

- `SKILL.md`: the core rules, a chapter index, a topic index, and *Scope & Limits* (what the source gets wrong, and what the skill leaves to a sibling).
- `chapters/`: one file per chapter, with worked examples.
- `cheatsheet.md`: thresholds, decision rules and tells, for while you code.
- `glossary.md` and `patterns.md`: the terms, and the refactorings by name, each with its trigger and cost.

`clean-code-universal` sorts its rules by what they assume of a language. Tier 1 needs only that you can name things and run some check, so it holds for a Helm chart as much as for a Rust crate; Tier 2 binds only where a construct exists (a parameter list, a type system, an exception, a test runner); Tier 3 is a language's own idiom, left to the siblings. `references/declarative-translation.md` gives, per rule, its meaning in YAML, HCL, SQL and Bash.

## How Claude picks one

- **Descriptions**: each skill's description names its language and its siblings, and sends every other language to `clean-code-universal`, so Claude loads one skill rather than guessing between eleven.
- **The gateway**: a SessionStart hook puts a short rule at the top of each session, and again after `/clear` or compaction: load the matching skill *before* writing or reviewing code, a file-extension dispatch table, and answers to the usual excuses for skipping it ("it's a one-line change"). It also carries the comment rule itself, since it is the only text always in context: no comment unless it says why, one line each, and explanations for a reviewer go in the commit or PR description. It says when not to bother, too: questions about the code, reading logs, writing docs, a config value with no logic in it. It costs about 3.3 kB of context and no extra model calls. The text is [`hooks/clean-code-gateway.md`](hooks/clean-code-gateway.md).

Your project's own conventions win: where your `CLAUDE.md` or you contradict a skill, Claude follows you and says which rule it set aside. A convention has to be written down (a `CLAUDE.md`, a style guide, a lint config); how heavily the existing code is commented is not one.

## Using it

Mostly you don't do anything: write or review code, and the matching skill loads. You can also ask for one, with a topic or a chapter:

```
/clean-code:clean-code-python parameter objects
/clean-code:clean-code-universal ch09
/clean-code:clean-code-java smells
```

Or just ask: "review this diff for code smells", "is this Terraform module doing one thing?".

## Sources and licences

The skills come from sources under different terms. The eight community adaptations are MIT. The Go article has no licence, so its skill restates its rules with citations. The book is copyrighted: `clean-code-java` and `clean-code-universal` are independently written restatements with chapter citations, not its text. [NOTICE.md](NOTICE.md) has the details and every licence notice. The plugin is not affiliated with Robert C. Martin or his publisher; buy the book.

## Development

What changed in each version is in [PLUGIN_CHANGELOG.md](PLUGIN_CHANGELOG.md): a new skill is a minor version, a content or doc fix a patch.

To add a language:

1. Make the skill from its adaptation's repository with [book-to-skill](https://github.com/virgiliojr94/book-to-skill), then shape it like its siblings: `SKILL.md`, `chapters/`, cheatsheet, glossary, patterns, and *Scope & Limits* for what the source gets wrong.
2. Keep its description within 1,024 characters (book-to-skill's `validate_skill.py` checks), and name the new skill in its siblings' descriptions and Related Skills.
3. Add its file extensions to the gateway's dispatch table.
4. Add its source and licence to NOTICE.md and an entry to the changelog, and raise the version in `.claude-plugin/plugin.json` and in the marketplace's `.claude-plugin/marketplace.json`.
