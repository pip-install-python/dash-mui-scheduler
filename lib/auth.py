"""Optional Clerk authentication gate (dash-clerk-auth, vendored).

The integration is FULLY OPTIONAL: with no CLERK_* keys in the environment (or
the package missing) the app runs exactly as before — the package's dash hooks
no-op, no script/store is injected, no session machinery or routes register,
and Hall-of-Fame records stamp `observer: null` (anonymous). The single source
of truth for "is auth on" lives here; run.py (register/configure), the header
avatar chip, and the game's observer publisher all call `clerk_enabled()`.

Env vars (set all three to enable):
  CLERK_SECRET_KEY       sk_...   backend SDK key (never exposed to the client)
  CLERK_PUBLISHABLE_KEY  pk_...   embedded in the injected <script>
  CLERK_SIGN_IN_URL      https://<app>.clerk.accounts.dev/sign-in
REQUIRED in prod (run.py warns loudly when missing):
  SESSION_SECRET         signs the session + __dca_identity cookies — without it
                         the package falls back to a PUBLIC dev default string.
  CLERK_FRONTEND_API     https://<app>.clerk.accounts.dev — origin clerk.browser.js
                         is served from; read by the package straight from the env
                         (not gated here). Dev *.accounts.dev instances can derive
                         it from CLERK_SIGN_IN_URL, but production custom-domain
                         instances CANNOT (their Account Portal doesn't proxy
                         /npm/@clerk/clerk-js) — set it explicitly in prod.

NOTE: read keys at CALL time (not import time) — lib/backend's load_dotenv must
have run first, and tests blank env vars per-process.
"""
import os

# The app owner's Clerk account — the only signed-in user who sees the premium
# agent-model tier (lib/ai_brain.PREMIUM_MODELS) in the model selects. Checked
# CLIENTSIDE against the clerk-auth-store email (UI gating; the per-actor spend
# cap is the hard server-side bound). Env-overridable per deployment.
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "pipinstallpython@gmail.com")


def clerk_keys():
    return (os.getenv("CLERK_SECRET_KEY"),
            os.getenv("CLERK_PUBLISHABLE_KEY"),
            os.getenv("CLERK_SIGN_IN_URL"))


def clerk_enabled():
    """True only when all three CLERK_* env vars are set AND the package imports."""
    if not all(clerk_keys()):
        return False
    try:
        import dash_clerk_auth  # noqa: F401
        return True
    except Exception:
        return False


# Satellite origins the PRIMARY (2plot.ai) may redirect a user back to after a
# Clerk sign-in. The vendored dash_clerk_auth applies this list to Clerk.load()
# on the primary ONLY (gated on !isSatellite) — it is the whitelist that lets a
# satellite's signInForceRedirectUrl actually complete. A missing/malformed
# entry silently strands the user on the primary's home (the 2026-06 prod bug:
# two entries lacked a scheme, and 2plot.net was absent).
_DEFAULT_SATELLITE_ORIGINS = (
    "https://2plot.media", "https://www.2plot.media",
    "https://2plot.net",   "https://www.2plot.net",
    "https://2plot.xyz",   "https://www.2plot.xyz",
    "https://cast.2plot.net",
    "https://2plot.dev",   "https://2plot.me",
    "https://2plot.world", "https://2plot.shop",
    "https://muischeduler.2plot.dev",   # these docs
)


def allowed_redirect_origins():
    """Origins the primary Clerk instance may redirect back to after sign-in.

    Env-first via CLERK_ALLOWED_REDIRECT_ORIGINS (comma-separated) so a NEW
    satellite can be whitelisted without a redeploy; otherwise the galaxy
    default above. Bare hosts are coerced to https:// (a missing scheme is
    what silently dropped 2plot.world/2plot.shop in prod) and trailing slashes
    are stripped (Clerk matches on origin). De-duplicated, order preserved.
    """
    raw = os.getenv("CLERK_ALLOWED_REDIRECT_ORIGINS", "").strip()
    items = [x.strip() for x in raw.split(",") if x.strip()] if raw \
        else list(_DEFAULT_SATELLITE_ORIGINS)
    seen, out = set(), []
    for it in items:
        if not it.startswith(("http://", "https://")):
            it = "https://" + it
        it = it.rstrip("/")
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out


def identify_request_user(cookies):
    """Display name of the signed-in Clerk user for THIS request, or None.

    Reads the package's signed `__dca_identity` cookie (minted after a Clerk
    session verifies) — a cheap itsdangerous signature check, no Clerk
    roundtrip. Anonymous visitors, auth-off deployments, missing/blank
    SESSION_SECRET, and stale/tampered cookies all return None. Used by the
    analytics tracker to stamp authenticated visits for the /traffic log book.
    """
    if not clerk_enabled():
        return None
    secret = os.getenv("SESSION_SECRET") or ""
    token = (cookies or {}).get("__dca_identity")
    if not token or not secret:
        return None
    try:
        from dash_clerk_auth._identity_cookie import verify
        user = verify(token, secret, max_age=7 * 86400)
    except Exception:
        return None
    if not user:
        return None
    name = " ".join(x for x in (user.first_name, user.last_name) if x) or user.email or user.user_id
    return str(name)[:60]
