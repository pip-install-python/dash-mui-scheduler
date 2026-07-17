"""Drop-in Clerk *satellite* wiring for any 2plot.* Dash app.

The 2plot galaxy shares ONE Clerk app: 2plot.ai is the PRIMARY (hosts sign-in via
accounts.2plot.ai); every other 2plot.* domain is a SATELLITE. This wraps
dash-clerk-auth 0.9.0 and patches its three satellite gaps so a satellite can both
INITIALIZE and SIGN IN. Canonical runbook:
2plot_media/.claude/support_files/CLERK-SATELLITE-SETUP.md (this module is its Part 3).

Usage (order matters):

    from lib.clerk_satellite import register_clerk_satellite, clerk_is_enabled
    register_clerk_satellite(app_tag="2plot.xyz")      # BEFORE Dash(...)
    app = Dash(__name__, ...)
    if clerk_is_enabled():                              # AFTER Dash(...)
        from dash_clerk_auth import configure_app
        configure_app(app)
"""
import os

_REQUIRED = ("CLERK_SECRET_KEY", "CLERK_PUBLISHABLE_KEY", "CLERK_SIGN_IN_URL")


def clerk_is_enabled():
    """True only when the 3 required CLERK_* keys are set AND the package imports."""
    if not all(os.getenv(k) for k in _REQUIRED):
        return False
    try:
        import dash_clerk_auth  # noqa: F401
        return True
    except Exception:
        return False


def register_clerk_satellite(app_tag="2plot-satellite"):
    """Wire Clerk satellite auth + the 3 dash-clerk-auth 0.9.0 patches.
    No-op (returns False) if Clerk env is unset. MUST run BEFORE Dash() is built."""
    if not clerk_is_enabled():
        return False

    from dash_clerk_auth import register_clerk_auth

    pub = os.getenv("CLERK_PUBLISHABLE_KEY")
    sat_domain = (os.getenv("CLERK_SATELLITE_DOMAIN") or "").strip() or None
    sat_env = os.getenv("CLERK_IS_SATELLITE", "false").strip().lower() == "true"
    pk_live = (pub or "").startswith("pk_live_")

    # A pk_live key on a configured satellite domain IS a satellite, even if
    # CLERK_IS_SATELLITE was missed in the deploy env (prevents silently booting
    # in primary mode). Dev uses pk_test -> stays non-satellite.
    is_satellite = sat_env or (pk_live and bool(sat_domain))
    if is_satellite and not sat_domain:
        print(f"[{app_tag}] WARN satellite mode needs CLERK_SATELLITE_DOMAIN — "
              "booting PRIMARY; client sign-in will fail until it is set.")
        is_satellite = False

    register_clerk_auth(
        clerk_secret_key=os.getenv("CLERK_SECRET_KEY"),
        clerk_publishable_key=pub,
        clerk_sign_in_url=os.getenv("CLERK_SIGN_IN_URL"),
        session_secret=os.getenv("SESSION_SECRET"),
        backend="auto",
        headless=True,                     # avatar chip lives in the app header
        is_satellite=is_satellite,
        satellite_domain=sat_domain,
        clerk_frontend_api=(os.getenv("CLERK_FRONTEND_API") or None),
        sign_up_url=(os.getenv("CLERK_SIGN_UP_URL") or None),
    )

    if is_satellite and sat_domain:
        _patch_satellite_index(sat_domain)

    print(f"[{app_tag}] Clerk ENABLED (satellite={is_satellite}, "
          f"domain={sat_domain or '-'}, key={'live' if pk_live else 'test'}).")
    return is_satellite


def _patch_satellite_index(sat_domain):
    """Fix the 3 dash-clerk-auth 0.9.0 satellite gaps via a Dash index hook,
    registered AFTER the package's (so it sees the injected <script> tag)."""
    from dash import hooks

    # (2)+(3): the menu's Sign-in calls Clerk.openSignIn() (a modal on the CURRENT
    # domain) -> 403 on a satellite. Intercept the login-button click in the CAPTURE
    # phase (runs before the package's bubble listener; stopImmediatePropagation kills
    # it) and redirectToSignIn() to the primary, FORCING the return back to this
    # satellite page (deprecated redirectUrl is ignored by clerk-js@5, so without the
    # *ForceRedirectUrl props the primary dumps the user on ITS OWN home).
    signin_js = (
        "<script>(function(){"
        "document.addEventListener('click',function(e){"
        "var b=e.target&&e.target.closest?e.target.closest('#clerk-login-button'):null;"
        "if(b&&window.Clerk&&typeof window.Clerk.redirectToSignIn==='function'){"
        "e.stopImmediatePropagation();e.preventDefault();"
        "var u=window.location.origin+window.location.pathname;"
        "window.Clerk.redirectToSignIn({signInForceRedirectUrl:u,signUpForceRedirectUrl:u});}"
        "},true);})();</script>"
    )

    @hooks.index()
    def _clerk_satellite_fixups(index_string):
        needle = "data-clerk-publishable-key="
        # (1): clerk-js@5 reads `domain` from the script tag (a CONSTRUCTOR option),
        # NOT from Clerk.load() options. Stamp data-clerk-domain onto the package's tag
        # or load() throws "a satellite application needs to specify a domain".
        if needle in index_string and "data-clerk-domain=" not in index_string:
            index_string = index_string.replace(
                needle, f'data-clerk-domain="{sat_domain}" {needle}', 1)
        if "redirectToSignIn" not in index_string and "</body>" in index_string:
            index_string = index_string.replace("</body>", signin_js + "</body>", 1)
        return index_string
