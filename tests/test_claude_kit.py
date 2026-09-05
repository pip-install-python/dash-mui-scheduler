"""The shipped .claude/ development kit — the F1 fabric build (2026-08-24).

The kit is how every fork inherits the network's behavioral contract,
skills, and settings. These pins keep it shipped (the old blanket
`.claude/` ignore silently kept the project instructions local-only —
forks inherited NOTHING), keep it case-correct (macOS is
case-insensitive; the fleet's CI and Render are not), and keep each
fork's settings pointing at ITS OWN host rather than the template's.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent

KIT_FILES = (
    ".claude/CLAUDE.md",
    ".claude/settings.json",
    ".claude/skills/wire-verify/SKILL.md",
    ".claude/skills/sync-template/SKILL.md",
    ".claude/skills/report/SKILL.md",
    "DIVERGENCES.md",
)


def _ignored(path: str) -> bool:
    return (
        subprocess.run(
            ["git", "check-ignore", "-q", path], cwd=REPO
        ).returncode
        == 0
    )


def _in_repo(rel: str) -> bool:
    return ".." not in rel and not rel.startswith("/")


def _machine_fence(kind: str, text: str, where: str) -> None:
    """The shared pin for machine fences (```yaml sync-verbatim in specs,
    ```yaml byte-owned in DIVERGENCES.md): exactly one block, `- path`
    lines with `#` comments, every path repo-relative and real at HEAD.
    Empty is valid — an empty block is a statement, a missing one is an
    omission. Gate lines (the fan-out's adoption gates) are validated
    like paths — a typo'd gate gates nothing:

      `# requires: <path>` (1.6.23) — the block applies only where
        <path> exists. For paths no pre-existing file can occupy;
        where one can, the gate must name a contract instead
        (sync/README.md — flows' pre-existing CLAUDE.md, 1.6.28).
      `# requires-contract: <path> :: <clause>` (1.6.28) — the block
        applies only where <path> exists AND contains <clause>. The
        clause must be real in THIS repo's copy at HEAD too.
      `- <path>  # requires: <other>` (1.6.28) — per-file gate: the
        fan-out skips this one copy where <other> is absent, instead
        of gating the whole block (clerkhook: a lockdown fork has no
        lib/auth_demos.py, legitimately, and must still receive the
        rest)."""
    fences = re.findall(
        r"^```yaml " + kind + r"[ \t]*\n(.*?)^```[ \t]*$", text, re.M | re.S
    )
    assert len(fences) == 1, (
        f"{where}: expected exactly one ```yaml {kind} fence, "
        f"found {len(fences)}"
    )
    for raw in fences[0].splitlines():
        stripped = raw.strip()
        if re.match(r"#\s*requires-contract:", stripped):
            gate = re.match(
                r"#\s*requires-contract:\s*(.+?)\s*::\s*(.+)$", stripped
            )
            assert gate, (
                f"{where} {kind}: {raw!r} — `# requires-contract:` takes "
                "`<path> :: <clause>`; a malformed gate gates nothing"
            )
            req, clause = gate.group(1).strip(), gate.group(2).strip()
            assert _in_repo(req), (
                f"{where} {kind}: `# requires-contract:` path {req!r} "
                "escapes the repo"
            )
            assert (REPO / req).is_file(), (
                f"{where} {kind}: `# requires-contract:` names {req!r} "
                "which does not exist at HEAD — a typo'd gate gates nothing"
            )
            assert clause in (REPO / req).read_text(), (
                f"{where} {kind}: `# requires-contract:` clause {clause!r} "
                f"is not in this repo's own {req} — a typo'd clause gates "
                "nothing"
            )
            continue
        required = re.match(r"#\s*requires:\s*(.+)$", stripped)
        if required:
            req = required.group(1).strip()
            assert _in_repo(req), (
                f"{where} {kind}: `# requires:` path {req!r} escapes the repo"
            )
            assert (REPO / req).is_file(), (
                f"{where} {kind}: `# requires:` names {req!r} which does "
                "not exist at HEAD — a typo'd gate gates nothing"
            )
            continue
        entry, _, comment = raw.partition("#")
        entry = entry.strip()
        if not entry:
            continue
        assert entry.startswith("- "), (
            f"{where} {kind}: {raw!r} is not a `- path` line"
        )
        path = entry[2:].strip()
        assert _in_repo(path), (
            f"{where} {kind}: {path!r} escapes the repo"
        )
        assert (REPO / path).is_file(), (
            f"{where} {kind}: {path!r} does not exist at HEAD "
            "— the machine would act on nothing or the wrong thing"
        )
        # A per-file gate is the WHOLE trailing comment, `requires: <path>`
        # from its first character; prose comments that merely mention the
        # word stay prose.
        per_file = re.match(r"\s*requires:\s*(.+)$", comment)
        if per_file:
            gate_path = per_file.group(1).strip()
            assert _in_repo(gate_path), (
                f"{where} {kind}: per-file gate on {path!r} escapes the "
                f"repo: {gate_path!r}"
            )
            assert (REPO / gate_path).is_file(), (
                f"{where} {kind}: per-file gate on {path!r} names "
                f"{gate_path!r} which does not exist at HEAD — a typo'd "
                "gate gates nothing"
            )


_POSTURE_KEYS = {"ai_bots", "healthz", "runtime", "deploy"}
_POSTURE_ENUMS = {
    "healthz": {"minimal", "full"},
    "runtime": {"docker", "python"},
    "deploy": {"release-branch"},
}


def _posture_fence(text: str, where: str) -> dict:
    """The ```yaml posture block in DIVERGENCES.md (1.6.30, F4).

    Declared postures used to live in the hub's own table — a copy of a
    measurement somebody took once, aging in a repo that cannot see the
    host. The fence homes each posture in the repo that serves it. SHAPE
    is all this validates: no test can tell a stale 200 from a fresh one,
    so the grammar is kept narrow enough that a wrong value is visibly
    wrong. Empty is valid and means "the template defaults".
    """
    fences = re.findall(
        r"^```yaml posture[ \t]*\n(.*?)^```[ \t]*$", text, re.M | re.S
    )
    assert len(fences) == 1, (
        f"{where}: expected exactly one ```yaml posture fence, "
        f"found {len(fences)}"
    )
    declared: dict = {}
    for raw in fences[0].splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, sep, value = stripped.partition(":")
        key, value = key.strip(), value.strip()
        assert sep, f"{where} posture: {raw!r} is not a `key: value` line"
        assert key in _POSTURE_KEYS, (
            f"{where} posture: unknown key {key!r} — the hub reads "
            f"{sorted(_POSTURE_KEYS)} and would ignore this one silently"
        )
        assert key not in declared, f"{where} posture: {key!r} declared twice"
        if key in _POSTURE_ENUMS:
            assert value in _POSTURE_ENUMS[key], (
                f"{where} posture: {key}: {value!r} — expected one of "
                f"{sorted(_POSTURE_ENUMS[key])}"
            )
            declared[key] = value
            continue
        try:
            statuses = json.loads(value)
        except ValueError as exc:
            raise AssertionError(
                f"{where} posture: ai_bots must be a JSON object like "
                f'{{"/": 403, "/llms.txt": 200}} — {exc}'
            ) from None
        assert isinstance(statuses, dict) and statuses, (
            f"{where} posture: ai_bots is {statuses!r} — a non-empty JSON "
            "object of path -> status, or omit the key entirely"
        )
        for path, status in statuses.items():
            assert path.startswith("/"), (
                f"{where} posture: ai_bots key {path!r} is not a path"
            )
            assert isinstance(status, int) and 100 <= status <= 599, (
                f"{where} posture: ai_bots[{path!r}] is {status!r} — an "
                "HTTP status, measured with a real vendor UA"
            )
        declared[key] = statuses
    return declared


def test_kit_files_exist_and_are_not_ignored():
    """The blanket `.claude/` ignore kept the contract local-only for the
    template's whole life — every fork inherited nothing. The allow-list
    must keep these shippable."""
    for rel in KIT_FILES:
        assert (REPO / rel).is_file(), f"kit file missing: {rel}"
        assert not _ignored(rel), (
            f"{rel} is gitignored — the kit cannot propagate to forks"
        )


def test_local_and_scratch_stay_local():
    """settings.local.json is the per-seat model override and must never
    ship; session working documents are local by convention network-wide
    (two public repos were caught tracking theirs)."""
    for rel in (
        ".claude/settings.local.json",
        ".claude/scratch-probe.png",
        "HANDOFF-probe.md",
        "KICKOFF-probe.md",
        "X402-SYNC-REPORT.md",
    ):
        assert _ignored(rel), f"{rel} would be committable — must stay local"


def test_claude_md_is_case_canonical_and_carries_the_contract():
    """macOS tolerates `claude.md`; the fleet's Linux CI does not. And the
    contract section is the point of shipping the file at all."""
    assert "CLAUDE.md" in os.listdir(REPO / ".claude"), (
        ".claude/CLAUDE.md must be exact-case for case-sensitive systems"
    )
    body = (REPO / ".claude" / "CLAUDE.md").read_text()
    for clause in (
        "behavioral contract",
        "Check the prompt against this tree",
        "Corrections are your job",
        "Verify your own deploy on the wire",
        "DIVERGENCES.md",
    ):
        assert clause in body, f"contract clause missing from CLAUDE.md: {clause!r}"


def test_skills_carry_frontmatter():
    for name in ("wire-verify", "sync-template", "report"):
        text = (REPO / ".claude" / "skills" / name / "SKILL.md").read_text()
        head = text.split("---", 2)
        assert len(head) >= 3, f"{name}: SKILL.md has no frontmatter block"
        front = head[1]
        assert re.search(r"^name:\s*\S", front, re.M), f"{name}: no name"
        assert re.search(r"^description:\s*\S", front, re.M), f"{name}: no description"


def test_settings_point_at_this_forks_own_host():
    """The anti-drift pin: settings ship with the TEMPLATE's host, and a
    fork that keeps them verbatim gets a sandbox that can wire-verify the
    template instead of itself. BASE_URL is the identity source — the
    settings must follow it."""
    from lib.constants import BASE_URL

    host = urlparse(BASE_URL).hostname
    settings = json.loads((REPO / ".claude" / "settings.json").read_text())

    domains = settings["sandbox"]["network"]["allowedDomains"]
    assert host in domains, (
        f"sandbox.network.allowedDomains lacks this repo's own host {host!r} "
        "— sessions here could not wire-verify their own production. "
        "Fork ritual: replace the template's host with yours."
    )
    assert "2plot.ai" in domains, "the hub must stay reachable (boards, presence)"

    allows = settings.get("permissions", {}).get("allow", [])
    assert f"WebFetch(domain:{host})" in allows, (
        f"permissions.allow lacks WebFetch(domain:{host})"
    )


def test_sync_specs_are_specifiable():
    """F2: every sync spec item must carry class/detect/acceptance — an
    item without detect and acceptance is not specifiable (write a
    kickoff instead and fix the item until it is; sync/README.md).

    Skips where no sync/ exists: forks CONSUME specs, only the template
    authors them — emojimart's F2 correction: this file is a byte-
    verbatim kit port, and without the guard it failed on arrival at
    every fork. The pin wakes up the day a fork starts authoring specs.

    F3b: every spec also carries exactly one ```yaml sync-verbatim
    fence — the machine block the fan-out workflow byte-copies from.
    Every listed path must exist at HEAD and stay inside the repo; a
    wrong entry becomes twelve wrong PRs.
    """
    import pytest

    sync_dir = REPO / "sync"
    if not sync_dir.is_dir():
        pytest.skip("no sync/ — this repo consumes specs, it does not author them")
    assert (sync_dir / "README.md").is_file(), "sync/README.md (the format) missing"
    specs = sorted(sync_dir.glob("SYNC-*.md"))
    assert specs, "no sync specs — releases ship one (F2)"
    for spec in specs:
        text = spec.read_text()
        blocks = re.split(r"^### ", text, flags=re.M)[1:]
        assert blocks, f"{spec.name}: no items"
        for block in blocks:
            title = block.splitlines()[0]
            for field in ("class:", "detect:", "acceptance:"):
                assert field in block, (
                    f"{spec.name} item {title!r} lacks {field}"
                )

        _machine_fence("sync-verbatim", text, spec.name)


def test_divergences_carry_the_byte_owned_block():
    """F3b A1's finding: the fan-out honours DIVERGENCES.md by never
    overwriting a byte-owned path, and a prose MENTION over-flags —
    muicharts' host-pin nuance names tests/test_claude_kit.py while its
    bytes are template-owned, a false positive recurring every release.
    The fence is the machine answer; when present it is authoritative,
    and empty means "the template owns every sync-verbatim path here".

    ABSENCE SKIPS, never fails (1.6.22, the ops seat's own correction):
    the machine tolerates a missing fence (the mention heuristic —
    over-flags, never restores), so the pin must too. Failing here
    would let one unported contract item keep every later mechanical
    PR red, revoking the fan-out's "verbatim class = green merge"
    promise indefinitely. CI guards what a fork HAS declared; the
    spec's contract item and its session round drive adoption.
    """
    import pytest

    div = REPO / "DIVERGENCES.md"
    if not div.is_file():
        pytest.skip("no DIVERGENCES.md — nothing for the fan-out to honour")
    text = div.read_text()
    if not re.search(r"^```yaml byte-owned[ \t]*$", text, re.M):
        pytest.skip(
            "DIVERGENCES.md has no byte-owned fence — port "
            "SYNC-1.6.17-1.6.21 item 1; until then the fan-out uses the "
            "mention heuristic"
        )
    _machine_fence("byte-owned", text, "DIVERGENCES.md")


def test_divergences_posture_fence_is_wellformed():
    """The declared posture (1.6.30, F4): shape only, plus the one value
    the repo can contradict by itself.

    ABSENCE SKIPS, like the byte-owned fence and for the same reason — a
    fork that has not ported the item yet keeps its CI green and gets the
    contract item, not a red on arrival. What is declared is held: an
    unknown key would be read by nobody, and a `runtime:` disagreeing with
    render.yaml is the posture lying about something in its own tree.
    """
    import pytest

    div = REPO / "DIVERGENCES.md"
    if not div.is_file():
        pytest.skip("no DIVERGENCES.md — nothing to declare a posture in")
    text = div.read_text()
    if not re.search(r"^```yaml posture[ \t]*$", text, re.M):
        pytest.skip(
            "DIVERGENCES.md has no posture fence — port the 1.6.30 item; "
            "until then the hub reads its own seeded table"
        )
    declared = _posture_fence(text, "DIVERGENCES.md")

    render = REPO / "render.yaml"
    if "runtime" in declared and render.is_file():
        for line in render.read_text().splitlines():
            m = re.match(r"\s*runtime:\s*(\S+)", line)
            if m:
                assert declared["runtime"] == m.group(1), (
                    f"posture declares runtime {declared['runtime']!r}, "
                    f"render.yaml says {m.group(1)!r} — the posture is "
                    "wrong about this repo's own tree"
                )
                break


# ------------- 1.6.44 item 9: DIVERGENCES' recorded-conventions section --

_DIVERGENCES = REPO / "DIVERGENCES.md"


def test_the_recorded_conventions_section_exists():
    """Item 9's detect. The header, and the sentence that explains it.

    A DIVERGENCE says "this repo differs, on purpose". A RECORDED CONVENTION
    says "this repo MATCHES, and the match is a decision" — almost always
    something deliberately removed or deliberately not added. Nothing in a
    diff distinguishes the second from an accident, so a sync restores it and
    nobody notices.
    """
    text = _DIVERGENCES.read_text()
    assert "## Recorded conventions (not divergences)" in text
    flat = " ".join(text.split()).lower()
    assert "a sync restores it" in flat, (
        "the section header is there but the reason a reader needs is not"
    )


def test_the_guard_entries_name_code_that_still_exists():
    """A guard entry pointing at a file or symbol that has moved is worse
    than no entry: it reads as settled while guarding nothing.

    THE DETECT HAS TO PARSE, not grep — and this file is where that lesson
    keeps proving itself. A raw grep for `HeadAsGetMiddleware` in
    lib/asgi_middleware.py matches the COMMENT that explains its absence; a
    comment strip then matches the DOCSTRING doing the same. `ast` reads
    definitions and references, and is the only one that answers the
    question actually being asked.
    """
    import ast

    text = _DIVERGENCES.read_text()
    section = text.split("## Recorded conventions (not divergences)", 1)[1]
    section = section.split("\n## ", 1)[0]

    # Every TEST a guard entry cites as its pin must exist. Scoped to tests/
    # deliberately: an entry may legitimately name a file to say this repo
    # does NOT have it — `lib/directives/headings.py` is named for exactly
    # that reason — and an existence sweep that did not know the difference
    # would fail on the very sentence doing the recording. What cannot be
    # wrong is the pin: an entry citing a test that has moved reads as
    # settled while guarding nothing.
    pins = set(re.findall(r"`(tests/[\w./]+)(?:::[\w.]+)?`", section))
    assert pins, "no guard entry cites a test — this sweep would be vacuous"
    for rel in pins:
        path = REPO / rel.split("::", 1)[0]
        assert path.exists(), f"a guard entry cites {rel}, which does not exist"

    # ...and where an entry says a file is absent, it must really be absent.
    if "lib/directives/headings.py" in section:
        assert not (REPO / "lib" / "directives" / "headings.py").exists(), (
            "the entry says this fork has no headings.py, and it now does"
        )

    # ...and the shim it says is absent must really be absent from the CODE,
    # not merely from a grep that the prose about it would satisfy.
    middleware = REPO / "lib" / "asgi_middleware.py"
    tree = ast.parse(middleware.read_text())
    defined = {node.name for node in ast.walk(tree)
               if isinstance(node, (ast.ClassDef, ast.FunctionDef))}
    assert defined, "nothing parsed out of asgi_middleware — a broken parse "
    assert "HeadAsGetMiddleware" not in defined, (
        "the shim came back; the guard entry says it must not"
    )
    referenced = {node.id for node in ast.walk(tree)
                  if isinstance(node, ast.Name)}
    assert "HeadAsGetMiddleware" not in referenced


def test_a_raw_grep_would_have_got_this_wrong():
    """The reason item 13 says "parse it", pinned as a measurement.

    lib/asgi_middleware.py's own prose explains why there is no HEAD shim, so
    the string is present in the file while the class is not. A detect that
    greps reports the defect that the documentation of its absence describes
    — and the better the comment, the more reliably it does so.
    """
    raw = (REPO / "lib" / "asgi_middleware.py").read_text()
    assert "HeadAsGet" in raw, (
        "the prose explaining the absent shim is gone; if that is deliberate, "
        "this pin has lost its subject"
    )


# ------------------ 1.6.44 item 13: parse, or strip comments AND strings --
#
# The item's own file is `sync/README.md`, which is the TEMPLATE's — specs are
# authored there and this fork has no sync/ directory. What ports is the RULE,
# and it belongs in the kit, which is what a seat at this repo actually reads.


def _normalise(text: str) -> str:
    """Flatten whitespace, strip emphasis and blockquote markers, casefold.

    Three formatting hazards, all of which have produced a false negative
    somewhere in the fleet:
      * a phrase that WRAPS across two lines is one string to a reader and
        two to a regex;
      * `**measured on a GREEN\\npush**` carries `**` INSIDE the phrase
        (ops' correction, from pannellum);
      * an indented blockquote's `> ` markers land mid-sentence.
    """
    flat = re.sub(r"^\s*>\s?", " ", text, flags=re.M)
    flat = flat.replace("**", "").replace("__", "").replace("*", "")
    flat = flat.replace("`", "")          # a code span splits a phrase too
    return re.sub(r"\s+", " ", flat).lower()


SYNC_1_6_43_ITEM_3_PHRASES = (
    "measured on a green push",
    "corpus is non-empty",
    "when a lane disagrees",
    "verify the artifact the claim is about",
)


def test_the_1_6_43_trap_phrases_are_present_read_case_insensitively():
    """Item 13's acceptance, run against this tree.

    All four read 1 flattened and case-folded. All four read 0 against the
    capitalised literal — the phrases ARE here, and a case-sensitive grep
    reports them missing. That mechanism is kept as evidence rather than as a
    sentence about the past.
    """
    kit = (REPO / ".claude" / "CLAUDE.md").read_text()
    flat = _normalise(kit)

    missing = [p for p in SYNC_1_6_43_ITEM_3_PHRASES if p not in flat]
    assert missing == [], f"trap phrases absent from the kit: {missing}"

    literal = [p for p in SYNC_1_6_43_ITEM_3_PHRASES if p in kit]
    assert literal == [], (
        "a phrase now matches the lowercase literal too, so this test no "
        f"longer demonstrates why the read must be case-insensitive: {literal}"
    )


def test_the_normaliser_survives_the_formatting_that_broke_the_detects():
    """The three hazards, each shown to break a naive match and be fixed."""
    wrapped = "WHICH BRANCH RENDER BUILDS CAN BE **measured on a GREEN\n  push**, by TIMING"
    # the marker lands INSIDE the phrase, which is the case that bites
    quoted = "> ASSERT THE corpus is\n>   non-empty BEFORE TRUSTING ANY NEGATIVE"

    for sample, phrase in ((wrapped, "measured on a green push"),
                           (quoted, "corpus is non-empty")):
        assert phrase not in sample.lower(), (
            "this sample no longer demonstrates the hazard"
        )
        assert phrase in _normalise(sample)


def test_the_kit_states_the_rule_about_strings_not_only_comments():
    """Item 13's detect: the rule must name STRINGS, not only comments."""
    flat = _normalise((REPO / ".claude" / "CLAUDE.md").read_text())
    assert "strip comments and strings" in flat, (
        "the kit's rule still says comments only — a docstring is a string, "
        "and that half is where this repo's own 1.6.44 build went red"
    )
    assert "a docstring is a string" in flat


# ------------------------ 1.6.44 item 14: traps-section currency, per fork --


def _kit_traps():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "kit_traps", REPO / "scripts" / "kit_traps.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_this_forks_traps_section_is_not_thin():
    """A count, printed, before anything is concluded from a comparison."""
    kt = _kit_traps()
    entries = kt.trap_entries((REPO / ".claude" / "CLAUDE.md").read_text())
    assert len(entries) >= 25, (
        f"only {len(entries)} trap entries — this fork was 14 against the "
        "template's 28 before item 14 merged the fleet-class ones"
    )


def test_the_matcher_does_not_report_an_adaptation_as_an_absence():
    """The whole reason matching is by TOKEN OVERLAP and not exact text.

    A fork is EXPECTED to have merged a trap into its own wording and added
    host-specific clauses. A strict check would report those as absence and
    train the fork to paste over its own adaptations — the opposite of what
    item 14 asks for.
    """
    kt = _kit_traps()
    template_entry = (
        "Probe with GET, not HEAD — HEAD responses omit the Link headers, "
        "and the discovery relations live there."
    )
    adapted = [
        "Probe with GET, never HEAD — HEAD responses omit the Link headers "
        "where the discovery relations live, and this host's FastAPI lane "
        "405s them anyway below dimll 2.9.4."
    ]
    assert kt._present(template_entry, adapted), (
        "an adapted trap reads as missing — the matcher is too strict and "
        "will train forks to overwrite their own wording"
    )
    assert not kt._present(template_entry, ["Something else entirely."])


def test_a_colon_early_in_an_adapted_sentence_defeats_the_matcher():
    """A KNOWN LIMIT of the template's matcher, pinned rather than hidden.

    `_tokens` compares only the FIRST SENTENCE, and the sentence splitter
    treats a colon as a terminator. So a fork that opens its adaptation with
    a clause like "…, on this host too: …" has its comparable text truncated
    to a handful of words and the trap reads as ABSENT — the false absence
    item 14 exists to avoid, arriving through the sentence splitter rather
    than through strictness.

    Not fixed here: `scripts/kit_traps.py` is the template's tool and a fork
    quietly改 its matching semantics would make every fork's count
    incomparable. Recorded, reported upstream, and pinned so the day the
    template fixes it this test says so.
    """
    kt = _kit_traps()
    template_entry = (
        "Probe with GET, not HEAD — HEAD responses omit the Link headers, "
        "and the discovery relations live there."
    )
    colon_first = [
        "Probe with GET, never HEAD, on this host too: HEAD responses omit "
        "the Link headers that carry the discovery relations."
    ]
    assert not kt._present(template_entry, colon_first), (
        "the matcher now handles an early colon — the upstream fix landed "
        "and this limitation note can go"
    )


def test_the_deploy_proof_line_names_the_release_branch():
    """The contradiction item 14 found HERE, amended in place.

    This kit carried an unqualified `build == HEAD is the deploy proof` a
    hundred lines above the fuller `HEAD of release` trap. A reader meeting
    the first one was sent to the wrong ref, and `main` ahead of `release`
    then reads as drift instead of an uncertified push pending. A correction
    that only appends leaves the wrong answer where a reader looks first.
    """
    text = (REPO / ".claude" / "CLAUDE.md").read_text()
    flat = _normalise(text)
    assert "build == head is the deploy proof" not in flat, (
        "the unqualified deploy-proof line is back"
    )
    assert "build == head of release is the deploy proof" in flat


def test_the_currency_check_reports_a_comparison_it_did_not_make(tmp_path):
    """A missing template must print UNKNOWN, never a number.

    Same rule as item 5's skip verdict: an answer that was not computed must
    not be printed in the shape of one that was.
    """
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "scripts/kit_traps.py", str(tmp_path / "nope.md")],
        cwd=REPO, capture_output=True, text=True,
    )
    assert "template UNKNOWN" in result.stdout, result.stdout
    assert "no template kit at" in result.stdout


def test_the_fork_is_current_against_a_reachable_template():
    """Item 14's acceptance, and it SKIPS rather than passes when it cannot
    run — a comparison against a template that is not on this machine is not
    a clean bill of health."""
    kt = _kit_traps()
    template = kt.SIBLING_TEMPLATE
    if not template.exists():
        pytest.skip(f"no template checkout at {template} to compare against")

    fork_n, template_n, missing = kt.compare(
        (REPO / ".claude" / "CLAUDE.md").read_text(), template.read_text())
    names = [kt.key(m) for m in missing]

    # Items 18 and 19 add their own traps later in this same drop. Named
    # individually so the exemption cannot quietly cover a third.
    pending = {"a verify verdict is metering evidence, never sole authorisat",
               "a proxied robots.txt is not your robots.txt (1.6.44 item 19;"}
    unexplained = [n for n in names
                   if not any(n.startswith(p[:40]) for p in pending)]
    assert unexplained == [], (
        f"fork {fork_n} / template {template_n}; missing and unaccounted "
        f"for: {unexplained}"
    )
