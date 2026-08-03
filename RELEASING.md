# Releasing dash-mui-scheduler

Releases are tag-driven: push a `v*` tag and `.github/workflows/release.yml`
verifies the tag, runs the full CI matrix against the tagged commit, builds,
gates the artifacts, publishes to PyPI via OIDC trusted publishing, and opens a
GitHub Release. No PyPI token is stored anywhere.

## PyPI trusted publisher — configured

Added on 2026-08-03 to the existing project (0.1.0 was uploaded by hand on
2026-07-17). For the record, pypi.org → **dash-mui-scheduler** → Manage →
Publishing shows:

- Owner: `pip-install-python`
- Repository: `dash-mui-scheduler`
- Workflow name: `release.yml`
- Environment name: `pypi`

The repository name must keep matching letter-for-letter — OIDC claims do not
follow GitHub's rename redirects, so renaming the repo breaks publishing until
the publisher is re-added.

Optionally add a required reviewer on the `pypi` environment in the GitHub repo
settings to put a human approval gate between the tag and the upload.

## Cutting a release

1. The version lives in **package.json** (`setup.py` reads it; `pyproject.toml`
   carries only the build-system table). Bump it, and add a
   `## [x.y.z] - date` section to `CHANGELOG.md` — the workflow lifts that
   section into the GitHub Release notes and **refuses to release without it**.
2. The component bundle (`dash_mui_scheduler/*.min.js`) is committed to git; if
   `src/` changed, run `npm run build` and commit the regenerated artifacts in
   the same change.
3. Merge to `main`. The workflow runs from the tagged commit and refuses to
   publish a commit that is not an ancestor of `origin/main`, so tag only after
   the merge — and the tag must point at a commit that contains `release.yml`.
4. Tag and push:

   ```bash
   git tag v<version>          # must equal package.json's version — the
   git push origin v<version>  # workflow refuses a mismatch
   ```

5. Watch Actions → Release:
   - **verify** — tag/version parity, the commit is on `main`, the CHANGELOG
     section exists;
   - **ci** — the same matrix `cd.yml` runs before a deploy (lint, secretless
     pytest on both backends, the Docker image built, booted and smoke-tested),
     so a release can never ship something CI rejected;
   - **build** — wheel + sdist, `twine check`, the sdist proven to carry the
     bundle, then the wheel installed into a clean venv and asserted to report
     the tagged version and carry its JS dist. That last check runs from
     *outside* the checkout on purpose: a script fed to `python` on stdin puts
     the working directory at `sys.path[0]`, and the repo root holds
     `dash_mui_scheduler/` — run from there it would import the source tree and
     pass against a wheel that shipped nothing;
   - **publish** — environment `pypi`, OIDC, no stored token;
   - **github-release** — release created with the CHANGELOG section as notes.

## Dry run

Actions → Release → Run workflow with `dry_run: true` builds and gates
everything, then publishes to **TestPyPI** instead. (The upload step itself
needs a matching trusted publisher on test.pypi.org; the build and the gates run
regardless.) A manual run with `dry_run: false` fails deliberately rather than
reporting a green run that published nothing — releasing to PyPI is the tag's
job.
