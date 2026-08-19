# Employee Management & Reporting System

Two independent applications share the same `employee_system` package but run in
**separate virtual environments** with different third-party dependencies:

| Project | Purpose | Libraries |
|---|---|---|
| `hr_report_generator/` | Generates a text report per employee + a formatted table | Jinja2, PrettyTable |
| `employee_cli/` | Interactive CLI views of employee data | Tabulate, Rich |

```
python_training/
├── hr_report_generator/
│   ├── .venv/
│   ├── app.py
│   ├── requirements.txt
│   ├── sample_output.txt
│   ├── templates/
│   │   └── employee_report.txt
│   └── employee_system/
│       ├── __init__.py
│       ├── employee.py
│       ├── salary.py
│       └── attendance.py
│
└── employee_cli/
    ├── .venv/
    ├── app.py
    ├── requirements.txt
    ├── sample_output.txt
    └── employee_system/
        ├── __init__.py
        ├── employee.py
        ├── salary.py
        └── attendance.py
```

> **Note on `.venv/`:** virtual environments are machine-specific binary folders and
> are intentionally *not* shipped inside this submission. Recreate each one with the
> commands below — that's exactly what `requirements.txt` is for (see Part 7).

---

## How to run each project

### Project 1 — HR Report Generator
```bash
cd hr_report_generator
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Project 2 — Employee CLI
```bash
cd employee_cli
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Each `app.py` was run locally against its real dependencies to confirm it works;
the exact console output is captured in each project's `sample_output.txt`.

---

## Part 3 — Library comparison

| Library | Purpose | Output style | Why choose it |
|---|---|---|---|
| **Jinja2** | Template-based text/report generation | Free-form dynamic text | You need the *layout* of the output to live outside the code (in a `.txt`/`.html` template) so non-developers can edit wording without touching Python. Best when the output is a document, not just a table. |
| **PrettyTable** | Table formatting | ASCII box table | Zero-dependency, quick way to print a clean table to a report file or console. Very simple API (`field_names`, `add_row`). No styling/colors. |
| **Tabulate** | CLI table formatting | Many table styles (`grid`, `simple`, `github`, `pipe`, …) | You want a lightweight table but need to match a specific output style (e.g. Markdown-compatible tables for docs, or minimal `simple` style for logs). One function call, no table object to manage. |
| **Rich** | Rich terminal UI | Styled/colored terminal table (and much more — progress bars, markdown, panels) | You're building a CLI *product* people will stare at, not just a debug print. Column colors, alignment, titles, and general terminal UX make CLI tools feel polished. Costs more (larger dependency, terminal-only rendering — doesn't degrade well to plain text files). |

**In short:** Jinja2 solves a different problem (text templating) than the three table
libraries. Among the table libraries, PrettyTable and Tabulate are near-equivalent for
simple needs — Tabulate's format flexibility gives it an edge for docs/reports, while
Rich is the right choice specifically when the *terminal experience* itself matters.

---

## Parts 4 & 5 — Proving virtual environment isolation

```bash
# Terminal A
cd hr_report_generator
source .venv/bin/activate
pip list                 # shows Jinja2, prettytable — NOT tabulate, NOT rich
python -c "import rich"  # -> ModuleNotFoundError
deactivate

# Terminal B
cd employee_cli
source .venv/bin/activate
pip list                 # shows tabulate, rich — NOT Jinja2, NOT prettytable
python -c "import jinja2"      # -> ModuleNotFoundError
python -c "import prettytable" # -> ModuleNotFoundError
deactivate
```

Each `.venv/` has its own `site-packages` directory. Installing a library inside one
project's environment only writes files into *that* environment's folder — the other
project's interpreter never looks there, so it has no way to see the package. This is
proven by the `ModuleNotFoundError` each project throws when asked to import the
other project's libraries.

---

## Part 6 — Why pin dependency versions?

`hr_report_generator/requirements.txt` pins an exact version:

```
prettytable==3.11.0
```

If a teammate (or a CI server) runs `pip install prettytable` with no version pinned,
they could get a newer release with a changed API, different default table styling,
or a bug fix that subtly changes output — breaking a report that was already
validated. Pinning versions means:

- Everyone on the team, and every environment (dev/test/prod), installs the **exact**
  same code.
- Bugs are reproducible — "works on my machine" stops being a version mismatch.
- Upgrades become an explicit, reviewed decision (bump the pin, retest) instead of an
  accident that happens silently on the next `pip install`.

Project 2 is allowed to use different versions of its own dependencies — the two
projects are isolated, so their choices don't have to agree.

---

## Part 7 — Recreating an environment from requirements.txt

```bash
cd hr_report_generator
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py         # produces the same Jinja2 + PrettyTable output as before
```

Repeat identically inside `employee_cli/`. Because `requirements.txt` records exact
versions, the recreated environment behaves identically to the original — this is the
whole point of committing it alongside the code instead of committing `.venv/` itself.

---

## Documentation (Part: README questions)

**1. What is a module?**
A single `.py` file containing Python code (functions, classes, variables) that can be
imported elsewhere, e.g. `employee.py`.

**2. What is a package?**
A folder of related modules that contains an `__init__.py` file, which tells Python to
treat the folder as an importable unit, e.g. `employee_system/` containing
`employee.py`, `salary.py`, `attendance.py`.

**3. What is a virtual environment?**
An isolated, self-contained Python installation (its own `site-packages`) created with
`python -m venv .venv`. Packages installed inside it don't affect the system Python or
any other project's environment.

**4. Why are two virtual environments used?**
Project 1 and Project 2 need different, independent sets of third-party libraries
(Jinja2/PrettyTable vs. Tabulate/Rich). Separate `.venv` folders guarantee that
installing/upgrading one project's dependencies can never break, bloat, or version-clash
with the other project's dependencies — even though both projects reuse the same
`employee_system` code.

**5. What is Jinja2 used for?**
Rendering dynamic text from a template file — placeholders like `{{ employee.name }}`
get replaced with real data at runtime, keeping report *wording/layout* separate from
Python logic.

**6. What is PrettyTable used for?**
Turning a list of rows into a clean ASCII box-style table for console or plain-text
report output, without manually aligning columns or drawing `+---+` borders.

**7. What is Tabulate used for?**
Same general idea as PrettyTable (row data → table), but with many interchangeable
output formats (`grid`, `simple`, `github`, `pipe`, etc.) via one `tabulate()` call.

**8. What is Rich used for?**
Building richly styled terminal output — colored/styled tables (and panels, progress
bars, markdown rendering, etc.) for CLI applications where the terminal experience
matters.

**9. What is `requirements.txt`?**
A plain-text list of a project's exact dependencies and versions (produced with
`pip freeze`), used to recreate an identical environment anywhere with
`pip install -r requirements.txt`.

**10. Why should package versions be specified?**
So installs are reproducible: everyone gets the exact same library behavior, bugs are
easier to diagnose, and upgrades are a deliberate, tested choice rather than something
that silently happens on the next install (see Part 6 above).

---

## Final Question

**If both projects are on the same machine, why should they have separate virtual
environments instead of installing all four libraries globally?**

- **Isolation of failure:** an upgrade or conflict in one project's dependencies (e.g.
  Rich requiring a newer version of a shared sub-dependency) can't silently break the
  other project.
- **Reproducibility:** each project's `requirements.txt` describes *exactly* what that
  project needs — nothing extra, nothing borrowed from whatever happens to be
  installed globally on this particular machine.
- **Version conflicts:** if Project 1 needed `prettytable==2.x` and some future
  Project 3 needed `prettytable==3.x`, a single global environment couldn't satisfy
  both at once — separate venvs sidestep the problem entirely.
- **Clean teardown/handoff:** deleting a project's `.venv/` (or handing the project to
  someone else) never risks breaking unrelated projects on the same machine, since
  nothing was installed globally.
- **Matches production:** servers/CI typically run one app per isolated environment
  (or container) anyway, so developing this way avoids "works on my machine, breaks in
  deployment" surprises.

In short: global installs optimize for short-term convenience; per-project virtual
environments optimize for correctness, reproducibility, and long-term maintainability
— which is why the isolation was worth demonstrating explicitly in Parts 4 and 5.
