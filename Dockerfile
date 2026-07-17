# dash-mui-scheduler docs — production image (Render docker runtime).
#
# NO node toolchain: the dash_mui_scheduler component bundle + generated Python
# wrappers are COMMITTED to git (dash_mui_scheduler/*.min.js + *.py), and
# setup.py only reads package.json — so `pip install -e .` works without npm.
# TRADE-OFF: changes under src/lib/components require a local `npm run build`
# and committing the regenerated artifacts (the image no longer self-builds).
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

# Python deps. vendor/ must be in place BEFORE the install — requirements.txt
# references vendored sdists (dash_clerk_auth) by path.
COPY requirements.txt .
COPY vendor/ ./vendor/
RUN pip install --no-cache-dir -r requirements.txt

# dash-improve-my-llms 2.0 is not on PyPI yet — install the vendored sdist.
RUN pip install --no-cache-dir "vendor/dash_improve_my_llms-2.0.0.tar.gz"

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
