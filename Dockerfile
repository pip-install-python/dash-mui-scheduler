# dash-mui-scheduler docs — production image (Render docker runtime).
#
# NO node toolchain: the dash_mui_scheduler component bundle + generated Python
# wrappers are COMMITTED to git (dash_mui_scheduler/*.min.js + *.py), and
# setup.py only reads package.json — so `pip install -e .` works without npm.
# TRADE-OFF: changes under src/lib/components require a local `npm run build`
# and committing the regenerated artifacts (the image no longer self-builds).
FROM python:3.14-slim

# PYTHONUNBUFFERED is load-bearing: without it Python block-buffers stdout to
# the pipe and NONE of the boot diagnostics (bulletin wired/off, traffic
# reporter state, backend banner) ever reach Render's log stream.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

# Python deps. vendor/ MUST be copied BEFORE the requirements install —
# requirements.txt installs dash_clerk_auth from ./vendor/ by path (it is not
# on PyPI). Get the order wrong and pip reports the missing path as a SOFT
# WARNING, then dies seconds later on an OSError that reads like a registry
# outage (emojimart's image died on exactly this). A vendor/ that resolves to
# an EMPTY directory is worse still: it installs nothing, silently — which is
# why CI asserts the clerk version and imports the package inside the built
# image rather than trusting this layer.
#
# CACHE SEMANTICS (the round-2 fleet lesson, found by pannellum 2026-08-22):
# this layer re-runs ONLY when vendor/ or requirements.txt bytes change. A
# `>=` floor can NEVER pull a newer release through a cache hit — a code-only
# commit rebuilds the app layers below while pip silently keeps whatever
# version the image was first built with. Ship every dependency upgrade as a
# floor bump in requirements.txt (grep the NUMBER — it also lives in run.py's
# boot floor and in both CI gates): the bump IS the cache bust, and the boot
# floor turns a stale image from a silent downgrade into a loud refusal to
# start.
COPY vendor/ ./vendor/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# markdown2dash 0.1.2 pins gunicorn>=21.2,<22 — stuck on two request-smuggling
# CVEs against our gunicorn>=23 floor. --no-deps dodges the pin; its real
# dependencies (mistune, frontmatter, pydantic) are in requirements.txt. CI
# asserts gunicorn>=23 INSIDE this image to keep the dodge honest.
RUN pip install --no-cache-dir --no-deps markdown2dash==0.1.2

COPY . .
RUN pip install --no-cache-dir -e .

# Production target is the FASTAPI backend (websocket callbacks, /healthz,
# OpenAPI). Render injects PORT and ignores EXPOSE; env vars come from
# render.yaml / the dashboard (NEVER bake .env — see .dockerignore).
ENV DASH_BACKEND=fastapi
EXPOSE 8598

# The websocket-callback transport is disabled app-side (run.py turns off the
# FastAPI backend's websocket capability — no WS route is registered). Keep
# --ws websockets-sansio anyway: if WS callbacks are ever re-enabled, uvicorn's
# default 'auto' selects the legacy websockets protocol (concurrent-send assert
# crash). Do NOT swap this for gunicorn+UvicornWorker (deprecated upstream +
# cannot set the ws protocol).
CMD ["sh", "-c", "uvicorn run:server --host 0.0.0.0 --port ${PORT:-8598} --workers ${WEB_WORKERS:-2} --ws websockets-sansio --timeout-graceful-shutdown 10"]
