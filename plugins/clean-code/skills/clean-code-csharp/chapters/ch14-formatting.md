# Chapter 14: Formatting

## Core Idea
Don't format by hand or by argument: **commit an `.editorconfig`** at the repository root and let the IDE and the .NET analyzers apply it. The source's single formatting rule comes with a full, opinionated file covering indentation, brace placement, `this.` qualification, predefined types, naming conventions (`PascalCase` constants, `s_` static fields, `_camelCase` private fields), expression-bodied members, pattern matching, null checks and spacing.

## Frameworks Introduced
- **Use an `.editorconfig` file**
  - Bad: "Has many code formatting styles in the project. For example, indent style is `space` and `tab` mixed in the project."
  - Good: "Define and maintain consistent code style in your codebase with the use of an `.editorconfig` file."
  - How: put the file at the repository root with `root = true`; general settings under `[*]`, C# settings under `[*.cs]`, and per-file-type indentation sections for project and config XML.
- **Codify naming, not just whitespace.** The file's `dotnet_naming_rule` blocks turn the Ch 2 capitalization table into analyzer suggestions.
- **Express preferences with severities.** Each style option is `value:severity` — e.g. `dotnet_style_qualification_for_field = false:suggestion` — so the IDE suggests the change rather than leaving it to review.

## Key Concepts
- **`.editorconfig`** — a cross-editor settings file, read by Visual Studio, Rider, VS Code and the .NET SDK analyzers.
- **`root = true`** — stops the search for parent `.editorconfig` files.
- **Section glob** — `[*]`, `[*.cs]`, `[*.{csproj,props}]`: which files the settings apply to.
- **`csharp_new_line_before_open_brace = all`** — Allman braces: every `{` on its own line.
- **`dotnet_style_qualification_for_*`** — whether to write `this.` (here: avoid it "unless absolutely necessary").
- **`dotnet_style_predefined_type_*`** — `int`, `string` rather than `Int32`, `String` ("use language keywords instead of BCL types").
- **`dotnet_naming_rule` / `_symbols` / `_style`** — the three-part grammar for naming conventions: *what* (symbols), *how* (style), *how strongly* (severity).
- **Severity** — `none`, `suggestion`, `warning`, `error`; the file uses `suggestion` throughout.

## Mental Models
- **Formatting is a solved problem; solve it once, in a file.** Every hour spent on brace placement in review is an hour the file would have spent for free.
- **The naming rules are the valuable part.** Indentation fights are cheap to settle; naming drift (`ADMIN_ROLE` vs `AdminRole`) is what the file quietly prevents.
- **`suggestion` informs; it doesn't enforce.** The source's file nudges in the IDE; it does not fail a build.

## Anti-patterns
- **Mixed tabs and spaces** — the source's Bad example.
- **Style rules that live only in people's heads or a wiki page.**
- **A style file that contradicts the code samples** — the source's own examples (`ADMIN_ROLE`, `ACCESS_READ`) break its `.editorconfig` naming rule for constants. Fix the code, not the file.

## Code Examples
The heart of the source's file (the full file also sets spacing, expression-level preferences and XML indentation):

```ini
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

# C# files
[*.cs]
indent_size = 4
# New line preferences
csharp_new_line_before_open_brace = all
csharp_new_line_before_else = true
csharp_new_line_before_catch = true
csharp_new_line_before_finally = true

# avoid this. unless absolutely necessary
dotnet_style_qualification_for_field = false:suggestion
dotnet_style_qualification_for_property = false:suggestion
dotnet_style_qualification_for_method = false:suggestion
dotnet_style_qualification_for_event = false:suggestion

# only use var when it's obvious what the variable type is
# csharp_style_var_for_built_in_types = false:none
# csharp_style_var_when_type_is_apparent = false:none
# csharp_style_var_elsewhere = false:suggestion

# use language keywords instead of BCL types
dotnet_style_predefined_type_for_locals_parameters_members = true:suggestion
dotnet_style_predefined_type_for_member_access = true:suggestion

# name all constant fields using PascalCase
dotnet_naming_rule.constant_fields_should_be_pascal_case.severity = suggestion
dotnet_naming_rule.constant_fields_should_be_pascal_case.symbols  = constant_fields
dotnet_naming_rule.constant_fields_should_be_pascal_case.style    = pascal_case_style
dotnet_naming_symbols.constant_fields.applicable_kinds   = field
dotnet_naming_symbols.constant_fields.required_modifiers = const
dotnet_naming_style.pascal_case_style.capitalization = pascal_case

# static fields should have s_ prefix
dotnet_naming_rule.static_fields_should_have_prefix.severity = suggestion
dotnet_naming_rule.static_fields_should_have_prefix.symbols  = static_fields
dotnet_naming_rule.static_fields_should_have_prefix.style    = static_prefix_style
dotnet_naming_symbols.static_fields.applicable_kinds   = field
dotnet_naming_symbols.static_fields.required_modifiers = static
dotnet_naming_style.static_prefix_style.required_prefix = s_
dotnet_naming_style.static_prefix_style.capitalization = camel_case

# internal and private fields should be _camelCase
dotnet_naming_rule.camel_case_for_private_internal_fields.severity = suggestion
dotnet_naming_rule.camel_case_for_private_internal_fields.symbols  = private_internal_fields
dotnet_naming_rule.camel_case_for_private_internal_fields.style    = camel_case_underscore_style
dotnet_naming_symbols.private_internal_fields.applicable_kinds = field
dotnet_naming_symbols.private_internal_fields.applicable_accessibilities = private, internal
dotnet_naming_style.camel_case_underscore_style.required_prefix = _
dotnet_naming_style.camel_case_underscore_style.capitalization = camel_case

# Expression-bodied members
csharp_style_expression_bodied_methods = false:none
csharp_style_expression_bodied_constructors = false:none
csharp_style_expression_bodied_properties = true:none
csharp_style_expression_bodied_accessors = true:none

# Pattern matching
csharp_style_pattern_matching_over_is_with_cast_check = true:suggestion
csharp_style_pattern_matching_over_as_with_null_check = true:suggestion
csharp_style_inlined_variable_declaration = true:suggestion

# Null checking preferences
csharp_style_throw_expression = true:suggestion
csharp_style_conditional_delegate_call = true:suggestion
```
- The source fences this file as `csharp`; it is INI-style `.editorconfig` syntax.

## Reference Tables

What the source's file decides, in plain words:

| Area | Decision | Key setting |
|---|---|---|
| Indentation | Spaces; 4 for C#, 2 for project/config XML and the default | `indent_style`, `indent_size` |
| Line endings, charset | LF, UTF-8, trim trailing whitespace, final newline | `end_of_line`, `charset` |
| Braces | Every `{` on a new line; `else`, `catch`, `finally` on new lines | `csharp_new_line_before_*` |
| `this.` | Avoid unless necessary | `dotnet_style_qualification_for_* = false` |
| `int` vs `Int32` | Language keywords | `dotnet_style_predefined_type_* = true` |
| `var` | **Left undecided** — the three `csharp_style_var_*` lines are commented out | (none active) |
| Constants | PascalCase | `constant_fields_should_be_pascal_case` |
| Static fields | `s_camelCase` | `static_fields_should_have_prefix` |
| Private/internal fields | `_camelCase` | `camel_case_for_private_internal_fields` |
| Expression bodies | Yes for properties, indexers, accessors; no for methods, constructors, operators | `csharp_style_expression_bodied_*` |
| Pattern matching | Prefer `is T t` over `is` + cast and `as` + null check | `csharp_style_pattern_matching_*` |
| Null checks | Throw expressions; `?.Invoke()` for delegates | `csharp_style_throw_expression`, `csharp_style_conditional_delegate_call` |
| `using` order | `System.*` first | `dotnet_sort_system_directives_first` |

## Worked Example
**How one naming rule reads.** Each convention is three linked entries; take the private-field rule:

1. **The rule** names the other two and sets the strength: `dotnet_naming_rule.camel_case_for_private_internal_fields.severity = suggestion`, `.symbols = private_internal_fields`, `.style = camel_case_underscore_style`.
2. **The symbols** say *which* declarations: `applicable_kinds = field`, `applicable_accessibilities = private, internal`.
3. **The style** says *what they must look like*: `required_prefix = _`, `capitalization = camel_case`.

So `private readonly Employee employee;` earns a suggestion to rename it `_employee` — which is what the source's own `PerformanceReview` and `BankAccount` examples do. The same pattern makes `const string ADMIN_ROLE` (Ch 3) a suggestion to become `AdminRole`.

**Where the conventions come from.** `_camelCase` private fields and `s_camelCase` statics match the coding style of the .NET runtime repository itself; the file's `[*.{asm,inc}]` and `[CMakeLists.txt]` sections, irrelevant to most application code, suggest it was adapted from a repository of that kind. Delete what doesn't apply to your project.

## Key Takeaways
1. **Commit an `.editorconfig`** with `root = true`; stop formatting by hand.
2. Put the **naming conventions** in it — constants PascalCase, `_camelCase` private fields, `s_` statics — not only whitespace.
3. **Allman braces, spaces, 4-wide for C#** is the source's choice; consistency matters more than the choice.
4. Prefer **language keywords**, **pattern matching**, and **throw expressions**; avoid `this.` unless needed.
5. The source leaves **`var` undecided** — decide it for your team and uncomment the lines.
6. `suggestion` nudges; it doesn't enforce. Raise severities if you want the build to hold the line.

## Connects To
- **Ch 2**: the capitalization rules this file encodes.
- **Ch 3**: the `ADMIN_ROLE` / `ACCESS_READ` examples this file would flag.
- **Ch 4**: the newspaper order of callers and callees — the layout rule no `.editorconfig` can express.
- **Ch 5**: `csharp_style_pattern_matching_over_is_with_cast_check` is the analyzer form of "use `is Bicycle bicycle`".
- **clean-code-java** ch05 (Formatting): vertical openness, density and distance, the newspaper metaphor, and the team-rules argument behind tools like this.
- **clean-code-typescript** ch10: the same "don't argue, automate" stance with ESLint and Prettier.
