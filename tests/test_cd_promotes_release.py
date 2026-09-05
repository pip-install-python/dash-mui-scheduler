"""CD promotes main → release on a green matrix; nothing else writes release.

The road since 1.6.35 (owner decision A, 2026-08-29): Render auto-deploys
the `release` branch and ONLY cd.yml's `deploy` job writes it, as a
fast-forward push of the run's own sha after the CI matrix is green. The
measurement behind it: 14:12Z that day, de0bcff pushed to main; Render,
watching main, built it within the minute; its CD run went red at 14:13Z
with the deploy job skipped; /healthz served the red build for ~6 minutes.
CI cannot stop a deploy while the platform watches the branch CI is still
judging.

These pins hold the STRUCTURE — the part a fork can drift silently:
`deploy` still needs `test`; the promote step exists and is not a force
push; the write grant is on that one job, not the workflow; the hook
step is gone; render.yaml watches `release`.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CD = REPO / ".github" / "workflows" / "cd.yml"
CI = REPO / ".github" / "workflows" / "ci.yml"
RENDER = REPO / "render.yaml"


def _cd() -> dict:
    return yaml.safe_load(CD.read_text())


def _deploy() -> dict:
    return _cd()["jobs"]["deploy"]


def _promote_step() -> dict:
    steps = [s for s in _deploy()["steps"] if s.get("name") == "Promote to release"]
    assert len(steps) == 1, "cd.yml deploy job must have exactly one 'Promote to release' step"
    return steps[0]


def test_release_is_only_written_after_a_green_matrix():
    """needs: [test] is the whole gate — a red matrix never reaches the push."""
    assert "test" in _deploy()["needs"]
    assert _cd()["jobs"]["test"]["uses"].endswith("ci.yml")


def test_the_promote_step_is_a_fast_forward_push_of_this_sha():
    # Commands only — the step's comments explain why NOT to force.
    run = "\n".join(
        line for line in _promote_step()["run"].splitlines()
        if not line.lstrip().startswith("#")
    )
    assert re.search(r"git push origin\s+\"?HEAD:refs/heads/release\"?", run), run
    assert "--force" not in run and " -f " not in run and "+HEAD" not in run, (
        "a non-fast-forward push must FAIL the job — someone wrote release "
        "by hand — never be forced over"
    )


def test_the_promote_checkout_is_not_shallow():
    """A depth-1 clone cannot fast-forward an EXISTING ref: the push is
    rejected as non-fast-forward. Run 33262495272 (747d8b3, 2026-08-29)
    failed its promote step in one second for exactly this; the first
    promote had only passed because `release` did not exist yet."""
    steps = _deploy()["steps"]
    checkouts = [s for s in steps if str(s.get("uses", "")).startswith("actions/checkout")]
    assert checkouts, "the promote job must check out before it can push"
    assert checkouts[0].get("with", {}).get("fetch-depth") == 0, (
        "promote's checkout must be fetch-depth: 0 — a shallow HEAD pushed "
        "onto an existing release is rejected ('fetch first')"
    )


def test_a_verify_only_dispatch_does_not_promote():
    cond = _promote_step().get("if", "")
    assert "inputs.target_url == ''" in cond and "github.event_name == 'push'" in cond, cond


def test_the_write_grant_is_on_the_deploy_job_only():
    assert _deploy()["permissions"] == {"contents": "write"}
    assert _cd()["permissions"] == {"contents": "read"}, (
        "the workflow-level grant stays read; only the promote job writes"
    )
    for name, job in _cd()["jobs"].items():
        if name != "deploy":
            assert job.get("permissions", {}).get("contents") != "write", name


def test_the_deploy_hook_is_gone():
    """Sync item 13's detect, from the inside: the secret's name must not
    appear anywhere in the file, comments included."""
    assert "RENDER_DEPLOY_HOOK" + "_URL" not in CD.read_text()
    assert not any("hook" in (s.get("id") or "") for s in _deploy()["steps"])


def test_verify_never_runs_on_a_failed_deploy():
    """Run 33262495272 (747d8b3): the promote step failed, verify ran
    anyway under `!= 'cancelled' && != 'skipped'` and went GREEN against
    the previous build. Verify must require success AND check the sha."""
    verify = _cd()["jobs"]["verify"]
    assert "deploy" in verify["needs"]
    assert verify.get("if", "").strip() == "needs.deploy.result == 'success'", verify.get("if")
    sha_steps = [s for s in verify["steps"] if s.get("name") == "The live build IS this run's sha"]
    assert len(sha_steps) == 1, "verify must assert /healthz build == github.sha itself"
    run = sha_steps[0]["run"]
    assert "/healthz" in run and "GITHUB_SHA" in run and "exit 1" in run


def test_render_watches_release():
    doc = yaml.safe_load(RENDER.read_text())
    web = [s for s in doc["services"] if s.get("type") == "web"]
    assert web and all(s.get("branch") == "release" for s in web), (
        "render.yaml must deploy `release` — main is where CI judges, "
        "release is what it certified"
    )
    # autoDeploy stays unset (Render default: on) — it IS the mechanism.
    assert all("autoDeploy" not in s or s["autoDeploy"] is True for s in web)


def test_the_posture_fence_declares_the_road():
    text = (REPO / "DIVERGENCES.md").read_text()
    fence = re.search(r"^```yaml posture[ \t]*\n(.*?)^```", text, re.M | re.S).group(1)
    assert re.search(r"^deploy:\s*release-branch\s*$", fence, re.M), fence


# ----------------- 1.6.44 item 12: the double-run trap, pinned before it bites --


def _triggers(path):
    """A workflow's `on:` block, read the only way that works.

    PyYAML resolves an UNQUOTED `on:` key to the BOOLEAN True (YAML 1.1
    treats on/off/yes/no as booleans), so `workflow["on"]` raises KeyError on
    every GitHub workflow file ever written. MEASURED on this tree:

        yaml.safe_load(ci.yml) -> top keys ['name', True, 'permissions', ...]
        d.get("on") -> None

    A test that catches that KeyError and moves on asserts NOTHING, which is
    the failure mode the item names. This raises instead: an unreadable `on:`
    block is a finding, not a skip.
    """
    doc = yaml.safe_load(path.read_text())
    for key in (True, "on", "On", "ON"):
        if key in doc:
            return doc[key] or {}
    raise AssertionError(
        f"{path.name} has no `on:` block under any spelling — top-level keys "
        f"are {sorted(map(str, doc))}. This test cannot assert anything about "
        "a workflow it cannot read."
    )


def test_the_boolean_on_key_trap_is_real_on_this_tree():
    """Pinned as a measurement, so the helper above is never 'simplified'."""
    doc = yaml.safe_load(CI.read_text())
    assert True in doc, "PyYAML no longer folds `on:` to a boolean here"
    assert doc.get("on") is None, (
        "`on` is now a string key too — re-read _triggers before trusting it"
    )


def test_cd_calls_ci_rather_than_duplicating_it():
    """The precondition for the item. Without it there is no double-run to
    avoid and the assertion below would be vacuous."""
    calls = [job for job in _cd()["jobs"].values()
             if str(job.get("uses", "")).endswith(".github/workflows/ci.yml")]
    assert len(calls) == 1, (
        f"{len(calls)} jobs call ci.yml; this pin assumes exactly one"
    )


def test_ci_does_not_also_run_itself_on_push_to_main():
    """Item 12. A CD lane that CALLS ci.yml must not also trigger it on push.

    Both would run on the same commit, and this repo's concurrency group is
    `ci-${{ github.ref }}` with cancel-in-progress — so the two runs would
    cancel each other and which one survives is a race. This tree is already
    correct and the item is a guard, not a fix: ci.yml's `on:` is
    pull_request + workflow_dispatch + workflow_call, with a comment saying
    exactly why there is no push. The comment is not the enforcement.
    """
    triggers = _triggers(CI)
    assert "workflow_call" in triggers, (
        "ci.yml is no longer callable — cd.yml's `uses:` would fail"
    )
    push = triggers.get("push")
    assert push is None, (
        "ci.yml now runs on push AND is called by cd.yml: the matrix runs "
        f"twice on every commit to main and the two runs cancel each other "
        f"(concurrency group ci-<ref>, cancel-in-progress). Got push: {push}"
    )


def test_cd_is_the_one_that_owns_main():
    """The other half: something must run on push, or nothing gates main."""
    push = _triggers(CD).get("push") or {}
    assert "main" in (push.get("branches") or []), (
        "cd.yml no longer triggers on push to main — with ci.yml's push "
        "trigger deliberately absent, nothing would run on a merge at all"
    )
