"""One fleet Python — the image, the CI matrix and the release lane agree.

Found by the ops seat reading the template's tree, not a report (2026-08-25):
a Dockerfile saying `python:3.11.8-slim` — a PATCH pin, so the image never
received a 3.11.x security release — while the CI matrix said 3.12. Several
declared Pythons, the docker boot/battery testing an interpreter the matrix
never ran, and nothing on the wire able to contradict any of them. These pins
hold every encoding to ONE minor, sourced from the Dockerfile's FROM tag;
/healthz's `python` field plus the `python_matches_declared` battery check
(scripts/network_smoke.py) hold the serving host to the same one.

DIVERGENCE from the template's copy of this file (recorded in
DIVERGENCES.md): the template deploys on Render's NATIVE python runtime, so
its render.yaml carries a `PYTHON_VERSION` that must agree with the image.
This service is Render's DOCKER runtime — the image IS the runtime
declaration and `PYTHON_VERSION` is inert there — so the pin below asserts
the opposite: that no such key exists to drift. This repo also ships a
tag-driven PyPI release workflow the template has no equivalent for, which
is a third encoding of the interpreter and is pinned here too.

What is deliberately NOT here: no comparison of the RUNNING interpreter to
the fleet minor — the suite legitimately runs on the adjacent window legs
(the matrix's 3.13/3.12 rows), where that assertion would be false by
design. Image-vs-declaration is the battery's job, against a host.
"""
from __future__ import annotations

import re

from conftest import REPO_ROOT


def _fleet_minor() -> str:
    """The single source: the Dockerfile's FROM tag."""
    for line in (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8").splitlines():
        m = re.match(r"FROM\s+python:(\S+)", line)
        if m:
            return m.group(1)
    raise AssertionError("Dockerfile has no `FROM python:` line")


def _uncommented(path) -> list[str]:
    return [
        ln for ln in (REPO_ROOT / path).read_text(encoding="utf-8").splitlines()
        if not ln.lstrip().startswith("#")
    ]


def test_dockerfile_tag_is_minor_only():
    """The patch pin IS the security bug: `3.11.8-slim` never receives a
    3.11.x fix release. The minor tag tracks them through Docker Hub."""
    tag = _fleet_minor()
    assert re.fullmatch(r"\d+\.\d+-slim", tag), (
        f"Dockerfile FROM tag is {tag!r} — must be a MINOR tag "
        "(python:X.Y-slim), never a patch pin"
    )


def test_render_yaml_leaves_the_python_to_the_image():
    """This service is `runtime: docker`, where Render ignores
    PYTHON_VERSION entirely. Declaring one anyway would add a second,
    INERT Python to the repo that nothing enforces and nothing serves —
    the exact drift the rest of this file exists to prevent, with no way
    for the battery to see it. The image is the declaration; keep it the
    only one."""
    lines = _uncommented("render.yaml")
    assert any(re.match(r"\s*runtime:\s*docker\s*$", ln) for ln in lines), (
        "render.yaml is no longer the docker runtime — if this service moved "
        "to Render's native python runtime, this pin must become the "
        "template's: PYTHON_VERSION (full X.Y.Z) whose MINOR matches the "
        "image, and DIVERGENCES.md must be updated in the same commit"
    )
    declared = [ln for ln in lines if re.match(r"\s*- key: PYTHON_VERSION\s*$", ln)]
    assert not declared, (
        "render.yaml declares PYTHON_VERSION on a docker-runtime service — "
        "Render ignores it, so it can only ever drift from the image"
    )


def test_ci_matrix_main_and_singleton_jobs_agree_with_the_image():
    minor = _fleet_minor().removesuffix("-slim")
    ci = _uncommented(".github/workflows/ci.yml")

    mains = [m.group(1) for ln in ci
             if (m := re.match(r'\s*python:\s*\["([\d.]+)"\]', ln))]
    assert mains == [minor], (
        f"ci.yml matrix main {mains} vs image python:{minor}-slim"
    )

    # lint and pip-audit run literal python-version pins; the test job's is
    # `${{ matrix.python }}` and is deliberately not a literal.
    literals = [m.group(1) for ln in ci
                if (m := re.match(r'\s*python-version:\s*"([\d.]+)"', ln))]
    assert literals and set(literals) == {minor}, (
        f"ci.yml singleton jobs pin {literals}, image is python:{minor}-slim"
    )

    cd = _uncommented(".github/workflows/cd.yml")
    cd_literals = [m.group(1) for ln in cd
                   if (m := re.match(r'\s*python-version:\s*"([\d.]+)"', ln))]
    assert cd_literals and set(cd_literals) == {minor}, (
        f"cd.yml verify job pins {cd_literals}, image is python:{minor}-slim"
    )

    # This repo's own lane: the tag-driven PyPI release. The wheel it
    # publishes should be built on the interpreter production serves.
    rel = _uncommented(".github/workflows/release.yml")
    rel_literals = [m.group(1) for ln in rel
                    if (m := re.match(r'\s*python-version:\s*"([\d.]+)"', ln))]
    assert rel_literals and set(rel_literals) == {minor}, (
        f"release.yml pins {rel_literals}, image is python:{minor}-slim"
    )


def test_matrix_legs_are_the_adjacent_minors():
    """The compat window stays three wide: the two include legs on the
    default backend are X.Y-1 and X.Y-2 (or X.Y+1 once it exists)."""
    major, y = (int(p) for p in _fleet_minor().removesuffix("-slim").split("."))
    allowed = {f"{major}.{y}", f"{major}.{y - 1}", f"{major}.{y - 2}",
               f"{major}.{y + 1}"}
    ci = _uncommented(".github/workflows/ci.yml")
    legs = [m.group(1) for ln in ci
            if (m := re.match(r'\s*- python:\s*"([\d.]+)"', ln))]
    assert legs, "the matrix has no include legs — the window collapsed to one"
    outside = [leg for leg in legs if leg not in allowed]
    assert not outside, (
        f"matrix legs {outside} fall outside the three-wide window around "
        f"{major}.{y}"
    )
