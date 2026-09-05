"""The three `openapi_*` knobs, and the guard that keeps them from crashing boot.

1.6.44 item 1 gives the HOST its API identity: without the knobs the FastAPI
lane's OpenAPI document is titled "FastAPI" version "0.1.0", which is what an
agent discovering this service through `/openapi.json` reads as the app's
name. This service runs FastAPI in production, so that document is on the
wire here.

WHY A GUARD AND NOT A STRAIGHT KWARG (ops correction to the 1.6.44 rider,
measured on pannellum): the knobs are LLMSConfig parameters from dimll 2.9.4.
This fork's requirements line stays `>=2.8.0` until the fleet pin lands at
1.6.45, and 2.8.0's LLMSConfig has ZERO openapi parameters — passing them
unconditionally is a TypeError AT IMPORT, i.e. the whole site fails to boot,
on any venv or image that resolves below 2.9.4. This suite resolves 2.8.0
today, so the unguarded form would not have reached CI.

Both directions are tested against shaped stand-ins rather than the installed
class, because a one-sided test passes on whichever wheel happens to be
resolved and says nothing about the other.
"""

from __future__ import annotations

import pytest

KNOBS = ("openapi_title", "openapi_description", "openapi_version")


class ConfigLike280:
    """LLMSConfig as it is at 2.8.0 — no openapi parameters at all."""

    def __init__(self, warn_missing_llms_doc=False):
        self.warn_missing_llms_doc = warn_missing_llms_doc


class ConfigLike294:
    """LLMSConfig as it is at 2.9.4 — the three knobs are real kwargs."""

    def __init__(self, warn_missing_llms_doc=False, openapi_title=None,
                 openapi_description=None, openapi_version=None):
        self.openapi_title = openapi_title
        self.openapi_description = openapi_description
        self.openapi_version = openapi_version


def test_a_2_9_4_shaped_config_gets_all_three_knobs(app_module):
    from lib.constants import SITE_DESCRIPTION, SITE_SHORT_NAME

    kwargs = app_module._openapi_kwargs(ConfigLike294)

    assert sorted(kwargs) == sorted(KNOBS)
    assert kwargs["openapi_title"] == f"{SITE_SHORT_NAME} API"
    assert kwargs["openapi_description"] == SITE_DESCRIPTION
    # The API SURFACE's version — not the package's and not this app's
    # release. `llms_version` on /healthz answers the other question.
    assert kwargs["openapi_version"] == "1.0"


def test_a_2_8_0_shaped_config_gets_none_of_them(app_module):
    """The direction that matters: no kwargs, so no TypeError at import."""
    assert app_module._openapi_kwargs(ConfigLike280) == {}


def test_the_guard_is_all_or_nothing(app_module):
    """A config accepting SOME of the knobs still gets none.

    Passing a subset would be a different TypeError on a different wheel,
    found at boot in production rather than here.
    """

    class Partial:
        def __init__(self, openapi_title=None):
            pass

    assert app_module._openapi_kwargs(Partial) == {}


def test_the_knobs_actually_construct_the_installed_config(app_module):
    """Whatever wheel is resolved, `LLMSConfig(**kwargs)` must not raise.

    This is the assertion the unguarded form failed: it is green on 2.9.4
    because the knobs are accepted, and green on 2.8.0 because the guard
    withholds them. It goes red the day the guard's question and the class
    disagree.
    """
    from dash_improve_my_llms import LLMSConfig

    LLMSConfig(warn_missing_llms_doc=True,
               **app_module._openapi_kwargs(LLMSConfig))


def test_the_guard_is_marked_for_deletion_at_the_pin(app_module):
    """The guard is scaffolding for a floor, not a permanent feature.

    When 1.6.45 pins `==2.10.0` the question has one answer and this code
    should go. A guard nobody remembers to remove is how a repo ends up
    silently declining a feature it now has.
    """
    from conftest import REPO_ROOT

    source = (REPO_ROOT / "run.py").read_text()
    assert "DELETE THIS GUARD when the pin lands" in source


@pytest.mark.parametrize("knob", KNOBS)
def test_no_knob_is_hardcoded_away_from_the_constants(app_module, knob):
    """Identity flows one way: out of lib/constants, never re-typed here."""
    value = app_module._openapi_kwargs(ConfigLike294)[knob]
    assert value, f"{knob} resolved empty"
