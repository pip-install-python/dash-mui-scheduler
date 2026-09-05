"""HEAD answers wherever GET answers — measured per backend, per wheel.

1.6.44 item 2 asks each fork to RETIRE `HeadAsGetMiddleware` or RECORD why it
keeps it. **This repo never had it** (see DIVERGENCES.md): the template's
1.6.32/33 shim was never ported here, the same gap pannellum found in itself.
So there was nothing to retire and nothing above the router papering over the
router's answer — which made the measurement worth taking rather than
assuming.

MEASURED on this tree, in-process, at the resolved wheel (dimll 2.8.0),
5 paths x 3 UAs, before any change:

    flask     15/15 pairs matched   (Werkzeug derives a HEAD rule per GET rule)
    fastapi   11/15                 405 on /healthz x3, and on / to a browser

and production, on the wire the same day, 15/15 — because the deployed image
resolved a newer wheel than this venv, which is precisely the CI-vs-production
gap `llms_version` was added to expose and cannot be read off requirements.txt.

Two different causes behind those four mismatches, and only one of them is
ours:

* `/healthz` is OUR route. FastAPI's `APIRoute` takes `methods` literally —
  unlike Werkzeug, and unlike `starlette.routing.Route`, which adds HEAD
  wherever GET is present. `lib/asgi_routes` now declares
  `methods=["GET", "HEAD"]`, and that fix is wheel-independent.
* `/` is Dash's lifespan-registered page catch-all. Nothing in this repo can
  declare methods on it; dimll >= 2.9.4 walks the router and adds HEAD
  itself. Below that floor the browser-UA pair legitimately mismatches — a
  crawler UA still passes because the package's prerender middleware answers
  above the router, which is exactly the single case that fooled an earlier
  probe into calling the app fine.

So the assertion is version-aware rather than either vacuous or falsely red:
strict everywhere the fix is ours, and strict on `/` too once the wheel can
deliver it. When the fleet pin lands at 1.6.45 the exemption evaporates on its
own and this file gets stricter without being edited.
"""
from __future__ import annotations

import pytest

from conftest import BROWSER_UA, CRAWLER_UA, backend

INTERNAL_PROBE_UA = "curl/8.7.1 2plot-internal/probe"

# The four crawler-facing surfaces plus the probe. Only `/healthz` is declared
# by this tree: `/llms.txt`, `/robots.txt` and `/sitemap.xml` come from
# dash-improve-my-llms' per-backend adapter and `/` from Dash's page
# catch-all, which is why the fix cannot live entirely in route declarations.
CORE_PATHS = ["/", "/healthz", "/llms.txt", "/robots.txt", "/sitemap.xml"]

UAS = {"browser": BROWSER_UA, "crawler": CRAWLER_UA, "probe": INTERNAL_PROBE_UA}


def _resolved_llms() -> tuple:
    import dash_improve_my_llms as pkg

    return tuple(int(n) for n in pkg.__version__.split(".")[:3] if n.isdigit())


def _route_level_head() -> bool:
    """True where the package adds HEAD to routes this repo cannot touch."""
    return _resolved_llms() >= (2, 9, 4)


def _exempt(path: str, ua_label: str) -> bool:
    """Dash's catch-all on the ASGI lane, below the wheel that can fix it.

    Narrow on purpose, in all three dimensions. Werkzeug derives a HEAD rule
    from every GET rule, so the FLASK lane has no excuse and gets none — it
    measured 15/15 before any change and must keep doing so. A wider
    exemption would have hidden that.
    """
    return (
        path == "/"
        and ua_label == "browser"
        and backend() != "flask"
        and not _route_level_head()
    )


@pytest.mark.parametrize("path", CORE_PATHS)
@pytest.mark.parametrize("ua_label", sorted(UAS))
def test_head_matches_get(client, path, ua_label):
    user_agent = UAS[ua_label]
    get = client.get(path, user_agent=user_agent)
    head = client.head(path, user_agent=user_agent)

    # Non-vacuity first: a 405/405 pair is "parity" too, and this file would
    # pass on a site that serves nothing at all.
    assert get.status == 200, (
        f"GET {path} answered {get.status} as {ua_label} — the parity "
        "assertion below would be vacuous"
    )

    if _exempt(path, ua_label):
        pytest.skip(
            f"Dash's page catch-all has no HEAD rule below dimll 2.9.4 "
            f"(resolved {'.'.join(str(n) for n in _resolved_llms())}); "
            "nothing in this repo can declare methods on it. The pin at "
            "1.6.45 closes this and re-arms the assertion."
        )

    assert head.status == get.status, (
        f"HEAD {path} answered {head.status} where GET answered {get.status} "
        f"as {ua_label}. On the ASGI lane a 405 here means the router has no "
        "HEAD rule for a GET route — FastAPI takes `methods` literally."
    )
    assert head.content_type == get.content_type, (
        f"HEAD {path} content-type {head.content_type!r} != GET "
        f"{get.content_type!r}"
    )


def test_healthz_answers_head_on_every_lane_regardless_of_the_wheel(client):
    """The one in the set that is OURS, so no exemption can ever apply.

    `/healthz` is the default probe method of most uptime monitors and this
    host's own deploy proof (cd.yml's build-match wait polls it). A 405 here
    is ours to fix at the route, and it is fixed at the route.
    """
    head = client.head("/healthz")
    assert head.status == 200, (
        f"HEAD /healthz answered {head.status} on the {backend()} lane — "
        "declare methods=['GET', 'HEAD'], do not shim it above the router"
    )


def test_no_head_shim_sits_above_the_router():
    """This repo records the ABSENCE of HeadAsGetMiddleware, and keeps it.

    The template retired its shim at 1.6.44 because converting HEAD to GET
    above the router makes every route look correct whatever the router does
    — it MASKS the package's fix as effectively as it hid the original
    defect. This repo never had one; re-introducing it would adopt, late, the
    exact thing the fleet just removed.

    PARSED, NOT GREPPED, and this test earned that the hard way. Its first
    form asserted `"HeadAsGet" not in text` and went RED the moment item 9
    added the module docstring explaining why there is no shim — a detect
    matching the documentation of the absence it hunts, which is item 13's
    rule reproducing itself inside the same build. `ast` answers the question
    actually being asked: is the class DEFINED or USED here.
    """
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parent.parent / "lib" / "asgi_middleware.py"
    tree = ast.parse(src.read_text())

    defined = {node.name for node in ast.walk(tree)
               if isinstance(node, (ast.ClassDef, ast.FunctionDef))}
    assert defined, "nothing parsed out of asgi_middleware.py"
    used = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}

    assert "HeadAsGetMiddleware" not in (defined | used), (
        "a HEAD-to-GET shim reappeared above the router — the fix belongs in "
        "the route declaration (ours) or the package floor (Dash's), and a "
        "shim would hide a regression in either"
    )
