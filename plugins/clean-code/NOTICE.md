# NOTICE — sources, licensing and attribution

The `clean-code` plugin ships five knowledge-base skills. They are **not** a single
work under a single licence: each derives from a different source, and those sources
carry different terms. This file records what each skill derives from, and reproduces
the licence notices the source projects ship.

Read this before redistributing the plugin or any skill in it.

---

## Sources at a glance

| Skill | Derived from | Licence of the source |
|---|---|---|
| `clean-code-java` | *Clean Code: A Handbook of Agile Software Craftsmanship*, Robert C. Martin et al., Prentice Hall, 2008 | **Copyrighted book — not open source** |
| `clean-code-typescript` | [labs42io/clean-code-typescript](https://github.com/labs42io/clean-code-typescript) | MIT |
| `clean-code-javascript` | [ryanmcdermott/clean-code-javascript](https://github.com/ryanmcdermott/clean-code-javascript) | MIT |
| `clean-code-python` | [zedr/clean-code-python](https://github.com/zedr/clean-code-python) | MIT |
| `clean-code-universal` | The book above, cross-checked against the three repositories above | **Mixed — see below** |

The three repositories are independent projects, not forks of one another.
Each states its own copyright; the notices below are reproduced verbatim from the
`LICENSE` file each project ships.

## The book-derived skills

`clean-code-java` and `clean-code-universal` restate rules, heuristics and the
smells-and-heuristics catalogue from *Clean Code*, a copyrighted book. The plugin
distributes **no part of the book's text**: the skills are independently written
restatements of its rules, with citations pointing back to the chapters they came
from, and code examples written for the skill rather than copied from the book.

Ideas, rules and methods are not copyrightable; particular expression is. These
skills are distributed on that basis. They are a study and reference aid and are
no substitute for the book — buy it:

> Martin, Robert C. et al. *Clean Code: A Handbook of Agile Software
> Craftsmanship.* Prentice Hall, 2008. ISBN 978-0132350884.

**This plugin is not affiliated with, endorsed by, or connected to Robert C. Martin,
his co-authors, or Pearson / Prentice Hall.**

`clean-code-universal` additionally draws on the three MIT-licensed repositories
below; their notices apply to it as well.

## MIT notices, reproduced verbatim

### labs42io/clean-code-typescript — applies to `clean-code-typescript`

```
The MIT License (MIT)

Copyright (c) 2019 Labs42 <hello@labs42.io>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### ryanmcdermott/clean-code-javascript — applies to `clean-code-javascript`

```
The MIT License (MIT)

Copyright (c) 2016 Ryan McDermott

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE
```

### zedr/clean-code-python — applies to `clean-code-python`

Reproduced exactly as the project ships it. The project is an independent
adaptation of Clean Code concepts for Python, maintained by Rigel Di Scala and
contributors; the copyright line in its `LICENSE` names Ryan McDermott.

```
The MIT License (MIT)

Copyright (c) 2016 Ryan McDermott

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE
```

## The plugin itself

The plugin packaging — `plugin.json`, this notice, the changelog, and the
skill-authoring work that turned these sources into skills (chapter structure,
cheatsheets, glossaries, pattern catalogues, the tier spine and declarative
translation table in `clean-code-universal`) — is by Alexandros Korsakov and is
offered under the MIT licence, subject to the terms above for the underlying
material.
