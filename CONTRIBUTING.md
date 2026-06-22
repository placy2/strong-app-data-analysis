# Contributing

Thanks for contributing to the Strong Data Project. This document covers the
project's testing convention and how the CI gate works.

## Testing convention

**New or changed functionality must ship with tests.** This is not just a
guideline — it is enforced mechanically:

- Tests live in `tests/`, one file per source module (`test_<module>.py`).
- Core logic — parsing (`parsers.py`, `utils/parse_utils.py`), data models
  (`models.py`), GUI helpers (`utils/gui_utils.py`), and the mapping CLI
  (`scripts/parse_raw_data.py`) — is covered by unit tests.
- A coverage gate (`fail_under` in `pyproject.toml`) runs on every PR. Adding
  untested logic lowers coverage and **fails CI**, so the convention is upheld
  even when a reviewer forgets to check.

Pure Streamlit page modules (`home.py`, `graphs.py`, `edit.py`, `upload.py`,
`scripts/gui.py`) are render glue and are excluded from coverage measurement via
the `omit` list in `pyproject.toml`. Put testable logic in the helper/parser
modules so it can be covered.

## Running tests locally

Install dev dependencies, then run the suite with coverage:

```bash
pip3 install -r requirements-dev.txt

pytest --cov=src --cov-report=term-missing

pylint src/ --fail-under=8.0
```

`pytest` is configured via `pyproject.toml` (`pythonpath = ["src"]`), so imports
like `from models import Workout` work without any manual path setup.

## CI gate

The **Test & Lint** workflow (`.github/workflows/test-lint.yml`) runs `pytest`
with coverage and `pylint` on every pull request and on pushes to `main`. A PR
must pass this workflow to be merge-ready.

> **Maintainer note:** to make the workflow a *required* status check (blocking
> merge), enable branch protection on `main` in the GitHub repository settings
> (Settings → Branches → Add rule → require status checks → "test-lint"). This is
> a one-time GitHub setting and cannot be configured from version-controlled
> files.
