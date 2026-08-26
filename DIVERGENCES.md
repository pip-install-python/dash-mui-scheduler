# Divergences from the template

Every DELIBERATE difference between this repo and
dash-documentation-boilerplate, with its reason. This file is the
boundary between design and drift:

- Template syncs read this file FIRST and must not "restore" anything
  recorded here.
- A difference not recorded here is treated as drift and will be
  synced away.
- Record the divergence in the SAME commit that creates it — one
  line: what differs, why, and what the template would otherwise do.
- An empty list is a statement too: it means this repo intends to
  match the template exactly.

## This repo's divergences

1. **This repo is a component LIBRARY as well as a docs site.** It
   carries `src/lib/components/` (React), `package.json`,
   `webpack.config.js`, the committed bundle and generated wrappers
   under `dash_mui_scheduler/`, and a third workflow —
   `.github/workflows/release.yml`, a tag-driven PyPI publish over
   OIDC trusted publishing (`RELEASING.md`). The template documents
   components it does not ship, so it has no equivalent for any of
   this. A sync must not read these as drift, and `release.yml` is a
   third encoding of the interpreter — `tests/test_python_version.py`
   pins it alongside `ci.yml` and `cd.yml`.

2. **Render's DOCKER runtime, so `render.yaml` declares no
   `PYTHON_VERSION`.** The template deploys on Render's native
   `runtime: python`, where `PYTHON_VERSION` is the platform's
   interpreter declaration and must agree with the image. This
   service is `runtime: docker`: Render ignores `PYTHON_VERSION`
   entirely, so declaring one would add a second, INERT Python that
   nothing enforces and nothing serves — precisely the drift spec
   1.6.27 item 5 exists to prevent, with no way for the battery to
   see it. The image IS the runtime declaration here, and
   `tests/test_python_version.py::test_render_yaml_leaves_the_python_to_the_image`
   inverts the template's render.yaml pin to keep it that way. If
   this service ever moves to the native runtime, that pin fails on
   purpose and says what to do.

3. **The Dockerfile's `HEALTHCHECK` is a python-urllib probe, not
   the template's `curl`.** This image installs no apt packages at
   all — no node toolchain (the bundle is committed) and therefore
   no curl — so the template's block would need an apt layer added
   to run one probe. Same contract: `${PORT:-8598}` defaulted at the
   point of use, and `docker inspect` reports a real verdict, which
   is what ci.yml's health-verdict step asserts.

4. **This site has no `home.md`.** `pages/home.py` is a hand-written
   DMC landing page, and the root machine-lane prose is the
   `llms_doc=` string in `run.py`. Spec 1.6.22-27 item 4's two-lane
   pin therefore reads `run.py` where upstream reads
   `pages/home.py` — same contract (whatever the docs lane
   substitutes, the home lane substitutes too), different file.
   `run.py`'s `llms_doc` runs through `lib.versions.substitute_versions`
   for exactly that reason.

5. **`block_ai_training=False` — this host does not disallow the AI
   training crawlers.** Most satellites run `True`. These are
   MIT-licensed component docs whose whole point is being read; the
   robots artifact therefore carries no training-bucket `Disallow`,
   and both batteries PIN the divergence rather than tolerate it
   (`scripts/network_smoke.py` and `scripts/smoke_live.py` fail if a
   `ClaudeBot` stanza ever appears). See `run.py`'s `configure_seo`
   call for the reasoning in full.

## Retired

- ~~**`dependabot.yml` runs no `npm` ecosystem.**~~ RETIRED
  2026-08-26. The reason was real and still holds — this repo has a
  genuine `package.json` (the template deleted its own), but the JS
  bundle is rebuilt and committed BY HAND, so a lockfile PR would
  arrive with no regenerated artifact and nothing in CI could
  validate it. It is retired as a *divergence* because template
  1.6.24 removed the pip ecosystem and ships no npm entry either, so
  this repo now carries `.github/dependabot.yml` byte-identical to
  the template and there is no difference left to record. Kept, not
  deleted: the template's own DIVERGENCES.md still cites
  "muischeduler's no-npm dependabot scope" as a live fleet
  precedent, and a sync that adds an npm ecosystem here would still
  be wrong.

## Byte-owned paths

Paths this fork owns byte-for-byte. The F3b fan-out never overwrites
a path listed here; everything else in the spec's `sync-verbatim`
block is the template's to update mechanically. Prose above explains
divergences; this block is the machine answer.

Repo-relative paths, one per line, `#` comments, no `..`; exactly one
block. An EMPTY block means "the template owns every sync-verbatim
path here" — present so the absence is a statement. When the block
exists it is authoritative; a fork without it gets the conservative
mention heuristic (over-flags, never restores).

Audited 2026-08-26 against the three specs' `sync-verbatim` blocks
(the three kit skills, `tests/test_claude_kit.py`,
`.github/dependabot.yml`, `tests/test_auth_demos.py`): every one of
those paths is byte-identical to template 1.6.27 here, and no
divergence above makes a byte-level claim on any of them. Divergence
1 names `release.yml` and divergence 2 names
`tests/test_python_version.py` — neither is a sync-verbatim path
(both are session-class by their specs), so neither becomes an
entry. The block is EMPTY by decision, not by omission.

```yaml byte-owned
```
