"""Clerk webhook receiver — POST /webhooks/clerk (ported from SailsBoard
services/webhooks/clerk.py, observability-only: this app has no credits
system, so a verified event lands as a structured log line + a bounded
JSONL event log instead of a heartbeat note / signup grant).

Clerk signs webhooks with Svix. The three required headers are
svix-id / svix-timestamp / svix-signature; the signing secret is
CLERK_WEBHOOK_SECRET (Clerk Dashboard → Webhooks → reveal signing secret).
The handler FAIL-CLOSES: no secret → every request is rejected loudly
rather than silently swallowing events.

Dashboard subscription (keep to these six — over-subscribing just adds
noise; unknown types are tolerated and land as a generic note):
  user.created · user.updated · user.deleted
  session.created · session.ended · session.revoked
Skip email.created (fires for every verification email) and
organization.* (no Clerk organizations here).
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

# Event types we know how to describe nicely. Anything else still flows
# through as a generic note (handy while wiring up the subscription).
_DESCRIPTIONS: dict[str, str] = {
    "user.created": "new observer signed up",
    "user.updated": "observer updated their profile",
    "user.deleted": "observer removed their account",
    "session.created": "observer signed in",
    "session.ended": "observer signed out",
    "session.revoked": "session revoked",
    "email.created": "email sent",
    "organization.membership.created": "org membership added",
    "organization.membership.deleted": "org membership removed",
}

_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "clerk_events.jsonl")
_LOG_KEEP = 500          # most-recent events kept when the log is compacted
_LOG_COMPACT_AT = 1000   # compact once the line count passes this


def _secret() -> str | None:
    return os.environ.get("CLERK_WEBHOOK_SECRET") or None


def verify_and_handle(payload: bytes, headers: dict[str, str]) -> dict[str, Any]:
    """Verify a Clerk webhook payload and record an observability event.

    Returns a small dict with ``ok`` (bool) and either ``kind`` on success
    or ``reason`` on failure. Never raises — the caller returns the dict
    as the HTTP response body (200 on ok, 400 otherwise).
    """
    secret = _secret()
    if not secret:
        # Fail loudly on a misconfigured deploy instead of silently swallowing
        # events — but keep the HTTP body generic (operators read the log).
        logger.warning("Clerk webhook rejected: CLERK_WEBHOOK_SECRET not set")
        return {"ok": False, "reason": "webhook not configured"}

    try:
        from svix.webhooks import Webhook, WebhookVerificationError
    except ImportError:
        logger.warning("Clerk webhook rejected: svix not installed")
        return {"ok": False, "reason": "webhook not configured"}

    # Svix wants case-insensitive header access; lower-case a copy so we
    # don't care what the WSGI/ASGI layer did to the casing.
    lc_headers = {k.lower(): v for k, v in headers.items()}
    svix_headers = {
        "svix-id": lc_headers.get("svix-id", ""),
        "svix-timestamp": lc_headers.get("svix-timestamp", ""),
        "svix-signature": lc_headers.get("svix-signature", ""),
    }
    if not all(svix_headers.values()):
        return {"ok": False, "reason": "missing svix-* headers"}

    try:
        wh = Webhook(secret)
        event = wh.verify(payload, svix_headers)
    except WebhookVerificationError as exc:
        logger.warning("Clerk webhook signature rejected: %s", exc)
        return {"ok": False, "reason": "invalid signature"}
    except Exception:  # noqa: BLE001 — never escalate
        logger.exception("Clerk webhook verify crashed")
        return {"ok": False, "reason": "verification failed"}

    # Past this point the event is AUTHENTIC — an odd payload shape must still
    # be ACKed with 200 (a 4xx/5xx would just make Clerk retry an event we
    # can't parse), so the whole parse/record section honors "never raises".
    try:
        kind = (event or {}).get("type", "unknown") if isinstance(event, dict) else "unknown"
        data = event.get("data") if isinstance(event, dict) else {}
        data = data if isinstance(data, dict) else {}

        # Clerk keeps the user id in different places per event type —
        # session.* events carry `user_id`, user.* events carry `id`.
        user_id = str(
            data.get("user_id")
            or data.get("id")
            or (data.get("user_data") or {}).get("id")
            or "?"
        )
        email = _pluck_email(data)

        nice = _DESCRIPTIONS.get(kind, kind)
        note = f"clerk · {nice}"
        if email:
            note += f" · {email}"
        elif user_id and user_id != "?":
            note += f" · {user_id[:12]}"
        logger.info(note)
        _record({"ts": time.time(), "kind": kind, "user_id": user_id,
                 "email": email, "note": note})
        # A brand-new 2plot.ai signer gets a matching cross-app wallet + the
        # idempotent $10 welcome grant on piratesbargain.com (the shop + AI-spend
        # hub). Fire-and-forget: the two apps run SEPARATE Clerk instances, so we
        # can only fund a wallet keyed by lowercased email — it reconciles to a
        # real piratesbargain account when the user later signs in there.
        if kind == "user.created" and email:
            _provision_piratesbargain_wallet(email, (data.get("username") or None))
        return {"ok": True, "kind": kind, "user_id": user_id, "email": email}
    except Exception:  # noqa: BLE001
        logger.exception("Clerk webhook post-verification handling crashed")
        return {"ok": True, "kind": "unknown"}


def _pluck_email(data: dict) -> str | None:
    """Pull a primary email out of a Clerk payload without blowing up."""
    emails = data.get("email_addresses") or []
    if emails and isinstance(emails, list):
        primary_id = data.get("primary_email_address_id")
        for e in emails:
            if e.get("id") == primary_id and e.get("email_address"):
                return e["email_address"]
        first = emails[0]
        if isinstance(first, dict) and first.get("email_address"):
            return first["email_address"]
    if data.get("email_address"):
        return data["email_address"]
    return None


def _provision_piratesbargain_wallet(email: str, handle: str | None) -> None:
    """Fund the new signer's cross-app wallet by email on piratesbargain.com.

    POSTs to SailsBoard's existing ``/api/satellite/balance`` receiver, which
    auto-provisions a wallet keyed by lowercased email and fires the idempotent
    1200-credit ($10) signup grant (``credits.ensure_signup_grant`` — deduped by
    a ``signup:<key>`` sentinel, so retries and a missed call self-heal on the
    user's first piratesbargain visit). Best-effort by design: a downstream
    outage must NOT fail the Clerk webhook (the caller still returns 200).

    No-op without ``CROSS_APP_WEBHOOK_SECRET`` (same shared HMAC secret both
    deployments use) — an unconfigured deploy simply skips provisioning, matching
    the app's fail-open posture for optional cross-app plumbing.
    """
    secret = os.environ.get("CROSS_APP_WEBHOOK_SECRET")
    if not secret:
        return
    import hashlib
    import hmac

    base = (os.getenv("PIRATESBARGAIN_API_URL") or "https://piratesbargain.com").rstrip("/")
    body = json.dumps(
        {"email": email.strip().lower(), "handle": handle or email, "source": "2plot.ai-signup"},
        separators=(",", ":"),
    ).encode()
    ts = str(int(time.time()))
    sig = hmac.new(secret.encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    try:
        import requests

        requests.post(
            base + "/api/satellite/balance",
            data=body,
            timeout=8,
            headers={
                "Content-Type": "application/json",
                # satellite.py's header names (X-AI-Canvas-*), not the 2plot ones.
                "X-AI-Canvas-Timestamp": ts,
                "X-AI-Canvas-Signature": sig,
            },
        )
    except Exception:  # noqa: BLE001 — provisioning is best-effort; never escalate
        logger.warning("piratesbargain signup provision failed for %s", email, exc_info=True)


def _record(entry: dict) -> None:
    """Append to the bounded JSONL event log (best-effort, never raises)."""
    try:
        with open(_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
        # cheap compaction: only stat/rewrite once the file grows
        if os.path.getsize(_LOG_PATH) > 256 * 1024:
            with open(_LOG_PATH) as f:
                lines = f.readlines()
            if len(lines) > _LOG_COMPACT_AT:
                with open(_LOG_PATH, "w") as f:
                    f.writelines(lines[-_LOG_KEEP:])
    except Exception:
        logger.exception("clerk event log write failed")


# --------------------------------------------------------------------------
# Route registration (both backends). The handler fail-closes without the
# secret, so registering unconditionally is safe — a stray POST just gets a
# 400. svix missing → skip registration with a notice (degrade, don't crash).
# --------------------------------------------------------------------------
class _BodyReplayMiddleware:
    """Cache the request body and hand downstream a replayable ``receive``.

    Dash's FastAPI ``DashMiddleware`` can pre-read the request body while
    forwarding the original (now-drained) ``receive`` — a downstream
    ``await request.body()`` would then block forever. Replaying the cached
    body fixes that (ported from SailsBoard services/api/_fastapi.py).
    Body-carrying methods only: GETs (incl. SSE) pass through untouched so
    they still observe real http.disconnect messages.
    """

    _BODY_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http" or scope.get("method") not in self._BODY_METHODS:
            await self.app(scope, receive, send)
            return
        body = b""
        while True:
            message = await receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                if not message.get("more_body", False):
                    break
            else:  # http.disconnect, etc.
                break

        async def replay_receive() -> dict:
            return {"type": "http.request", "body": body, "more_body": False}

        await self.app(scope, replay_receive, send)


def register_webhook(app, backend: str) -> None:
    try:
        from svix.webhooks import Webhook  # noqa: F401
    except ImportError:
        print("[clerk-webhook] svix not installed — POST /webhooks/clerk NOT registered")
        return

    server = app.server
    if backend == "quart":
        # Quart needs its own async route + request proxy (the Starlette branch
        # is fastapi-only and the flask proxy is unbound under Quart).
        from quart import jsonify, request

        @server.post("/webhooks/clerk")
        async def _clerk_webhook():  # pragma: no cover — quart runtime
            result = verify_and_handle(await request.get_data(), dict(request.headers))
            return jsonify(result), (200 if result.get("ok") else 400)
    elif backend == "fastapi":
        from starlette.requests import Request
        from starlette.responses import JSONResponse

        # added after Dash init → runs FIRST inbound, wraps Dash's middleware
        server.add_middleware(_BodyReplayMiddleware)

        @server.post("/webhooks/clerk")
        async def _clerk_webhook(request: Request):  # pragma: no cover — fastapi runtime
            body = await request.body()
            result = verify_and_handle(body, dict(request.headers))
            return JSONResponse(result, status_code=200 if result.get("ok") else 400)
    else:
        from flask import jsonify, request

        @server.post("/webhooks/clerk")
        def _clerk_webhook():
            result = verify_and_handle(request.get_data(), dict(request.headers))
            return jsonify(result), (200 if result.get("ok") else 400)

    print("[clerk-webhook] POST /webhooks/clerk registered (%s)" % backend)
