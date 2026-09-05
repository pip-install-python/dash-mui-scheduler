"""The docs sweep CI runs, and the reason flake8 cannot make it (1.6.44 item 7).

`.flake8` excludes `docs/*/`. So `flake8 docs/` is not passing those files —
it is NOT READING THEM, and the difference is invisible from the exit code.
MEASURED ON THIS TREE, with a file containing `def broken(:` written under
`docs/quickstart/`:

    flake8 docs/        exit 0, ZERO lines of output
    py_compile          exit 1, "File ... line 1  def broken(:"

That matters more here than in most repos. Every doc page's markdown carries
`.. exec::docs.<page>.<page>`, which IMPORTS the module at page load, so a
syntax error in any one of 51 files does not break one page — it breaks the
site. CI had no check that would have caught it.

The rider, and it is a different failure with the same shape: a page that
emits its own `Title(order=1)` renders a SECOND top-level heading under
`pages/markdown.py`'s `order=2` page title. Asserted structurally rather than
by grep, because a page that does not render through markdown.py is entitled
to its own order=1.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"


def _doc_modules() -> list[Path]:
    return sorted(p for p in DOCS.rglob("*.py")
                  if "__pycache__" not in p.parts)


def test_the_corpus_is_not_empty():
    """Asserted before anything below it is believed.

    A sweep that found nothing and a sweep that swept nothing produce the
    same green, and the count is printed rather than left to be inferred.
    """
    modules = _doc_modules()
    assert len(modules) >= 10, (
        f"only {len(modules)} python files under docs/ — every assertion in "
        "this file would be near-vacuous"
    )


def test_every_docs_module_compiles():
    """What CI's `py_compile sweep of docs/` step does, in-process."""
    modules = _doc_modules()
    broken = []
    for path in modules:
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as exc:
            broken.append(f"{path.relative_to(REPO)}:{exc.lineno}: {exc.msg}")
    assert broken == [], (
        f"{len(broken)} of {len(modules)} docs modules do not compile — each "
        f"one breaks the whole site at page load:\n" + "\n".join(broken)
    )


def test_the_lint_config_excludes_docs():
    """The sweep's premise, checked WITHOUT running the linter.

    This is the tool-free half, and it is the half CI's TEST job can actually
    run: that job installs the app's requirements plus pytest and httpx —
    NOT flake8, which lives in the lint job. The first version of this module
    shelled out to `python -m flake8` and took every matrix leg red for that
    reason (CD run 33996771397: all four test legs failed at the test step,
    `ci / lint` itself green).

    Item 10's own rule, met from the other side, and I had written that rule
    into the kit four commits earlier: NAME THE TOOLS WHOSE INVOCATION IS NOT
    THE ONE YOUR CHECK WILL HAVE. I applied it to my reports and not to a
    test I wrote in the same release. A test that needs a tool the job does
    not install is not testing the code, it is testing the job.
    """
    config = (REPO / ".flake8").read_text()
    exclude = config.split("exclude", 1)[1].split("per-file-ignores", 1)[0]
    assert "docs/*/" in exclude, (
        "`.flake8` no longer excludes docs/*/ — the sweep's premise changed, "
        "so read it again before trusting either check"
    )


def test_py_compile_catches_a_broken_docs_file(tmp_path):
    """The other half, and it needs nothing but the interpreter.

    Written to tmp_path, NOT into docs/: py_compile does not care where the
    file lives, and a test that writes into the repository is a test that
    errors on any read-only checkout. Two peer sandboxes read that error as
    a defect in this repo before it was tracked down.
    """
    probe = tmp_path / "_pycompile_probe.py"
    probe.write_text("def broken(:\n    pass\n")
    compiled = subprocess.run(
        [sys.executable, "-m", "py_compile", str(probe)],
        cwd=REPO, capture_output=True, text=True,
    )
    assert compiled.returncode != 0, (
        "py_compile accepted `def broken(:` — the sweep would not catch a "
        "syntax error either, and item 7 has no teeth"
    )


def test_flake8_is_actually_silent_on_docs_where_it_is_installed():
    """The MEASUREMENT, wherever the tool exists — and a SKIP where it does not.

    Skipped rather than passed (item 5's rule): a check that could not run is
    not a check that passed, and this one only exists to demonstrate the
    linter's silence. It runs locally and in the lint job's environment; the
    two tests above carry the claim everywhere else.
    """
    # Ask whether the tool RUNS, not whether a module name resolves.
    # `find_spec` answers None only when the package is absent, which is CI's
    # case — but a present-and-broken install resolves fine and then fails in
    # the subprocess, and I met exactly that shape while reproducing this
    # failure locally. The question the test needs answered is "can I invoke
    # it", so that is the question it asks.
    probe_tool = subprocess.run([sys.executable, "-m", "flake8", "--version"],
                                cwd=REPO, capture_output=True, text=True)
    if probe_tool.returncode != 0:
        pytest.skip("flake8 cannot be invoked here — the lint job has it, the "
                    "test job does not, and that asymmetry is the point")

    # This one genuinely must live under docs/ — the whole claim is about
    # what `flake8 docs/` does with a file there. So the WRITE is guarded
    # rather than the path moved: a read-only checkout skips instead of
    # erroring, which is the difference between "cannot check" and "broken".
    probe = DOCS / "quickstart" / "_flake8_probe.py"
    try:
        probe.write_text("def broken(:\n    pass\n")
    except OSError as exc:
        pytest.skip(f"docs/ is not writable here ({exc.__class__.__name__}), "
                    "so the linter's silence cannot be demonstrated")
    try:
        linted = subprocess.run(
            [sys.executable, "-m", "flake8", "docs/"],
            cwd=REPO, capture_output=True, text=True,
        )
    finally:
        probe.unlink(missing_ok=True)

    assert linted.returncode == 0 and linted.stdout.strip() == "", (
        "flake8 now reports on docs/ — this module's premise has changed:\n"
        f"{linted.stdout}"
    )


def test_the_ci_step_exists_by_name_and_fails_on_an_empty_corpus():
    """Item 7's detect. The step is named so a report can say which check ran.

    And the emptiness guard is part of the step, not an afterthought: a
    `find | xargs py_compile` over zero files exits 0.
    """
    ci = (REPO / ".github" / "workflows" / "ci.yml").read_text()
    assert "py_compile sweep of docs/" in ci, "the CI step is missing"
    step = ci.split("py_compile sweep of docs/", 1)[1].split("- name:", 1)[0]
    assert "py_compile" in step
    assert "-lt 1" in step and "exit 1" in step, (
        "the step does not fail on an empty corpus"
    )


# ------------------------------------------- the rider: one H1 per page --


def test_no_docs_module_emits_its_own_order_1_title():
    """`pages/markdown.py` already renders the page title at order=2.

    A doc module that emits `Title(..., order=1)` therefore puts a second
    top-level heading on the page — the duplicate-H1 shape this repo's
    floor notes already care about, arriving from the other direction.

    Structural, via ast: a page that does NOT render through markdown.py is
    entitled to its own order=1, so a grep across the tree would be wrong.
    These 51 modules all do.
    """
    modules = _doc_modules()
    assert modules, "no docs modules — this sweep would be vacuous"

    offenders = []
    for path in modules:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "attr", getattr(node.func, "id", ""))
            if name != "Title":
                continue
            for kw in node.keywords:
                if (kw.arg == "order"
                        and isinstance(kw.value, ast.Constant)
                        and kw.value.value == 1):
                    offenders.append(f"{path.relative_to(REPO)}:{node.lineno}")
    assert offenders == [], (
        "these doc modules emit their own order=1 heading under "
        "markdown.py's order=2 page title, so the page renders two: "
        + ", ".join(offenders)
    )


def test_markdown_py_really_renders_the_page_title_at_order_2():
    """The premise of the test above, held against the file rather than
    remembered. If markdown.py stops emitting a title, order=1 in a doc
    module is no longer a duplicate and that test is wrong."""
    src = (REPO / "pages" / "markdown.py").read_text()
    assert "order=2" in src, (
        "pages/markdown.py no longer renders the page title at order=2 — "
        "the duplicate-heading rule above needs re-deriving"
    )
