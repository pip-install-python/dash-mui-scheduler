"""
Visitor Analytics Tracker
Tracks visitor information including device type, bot detection, and geolocation

The ledger this writes is what `lib/traffic_report` rolls up and POSTs to
2plot.ai every hour, so the fields here are the network's raw material: an
accurate client IP (visitors are keyed on it) and a country code both come
from request headers, not from the socket peer.
"""
import json
import os
from pathlib import Path
from datetime import datetime
import requests
from functools import lru_cache

# Keep the ledger bounded: it is rewritten whole on every hit, and only the
# last couple of days ever feed a rollup. Env-tunable for a persistent disk.
MAX_VISITS = int(os.getenv("TRAFFIC_ANALYTICS_MAX_VISITS", "20000"))


def resolve_client_ip(headers, fallback=None):
    """The visitor's real address behind Cloudflare / Render's proxy.

    `remote_addr` / `request.client.host` is the PROXY in production — using
    it collapses every visitor into one (IP, user-agent) key and geolocates
    the datacenter. Prefer `CF-Connecting-IP`, then the first hop of
    `X-Forwarded-For` (the client; later entries are proxies).

    `headers` is any case-insensitive or plain mapping of request headers.
    """
    try:
        get = headers.get
    except AttributeError:
        return fallback
    cf = (get("CF-Connecting-IP") or get("cf-connecting-ip") or "").strip()
    if cf:
        return cf
    xff = (get("X-Forwarded-For") or get("x-forwarded-for") or "").strip()
    if xff:
        first = xff.split(",")[0].strip()
        if first:
            return first
    real = (get("X-Real-IP") or get("x-real-ip") or "").strip()
    return real or fallback


def resolve_country(headers):
    """Two-letter country from the edge (`CF-IPCountry`), or None.

    Free and accurate behind Cloudflare, and it saves the per-IP geolocation
    HTTP call in the request path. XX (unknown) and T1 (Tor) are not places.
    """
    try:
        get = headers.get
    except AttributeError:
        return None
    cc = (get("CF-IPCountry") or get("cf-ipcountry") or "").strip().upper()
    return cc if len(cc) == 2 and cc not in ("XX", "T1") else None


class AnalyticsTracker:
    """Track visitor analytics to JSON file.

    TRAFFIC_ANALYTICS_FILE env overrides the ledger path (tests seed a temp
    file; deployments can point at a persistent disk). the analytics log
    reads the same resolution, so readers always see what
    this tracker writes.
    """

    def __init__(self, data_file=None):
        self.data_file = Path(data_file or os.getenv("TRAFFIC_ANALYTICS_FILE") or "visitor_analytics.json")
        # An unusable ledger path must NEVER crash the boot. This module is
        # imported at the top of run.py, so an exception here kills every
        # worker before a port is bound and the platform loops the deploy
        # forever — which is exactly what happened when TRAFFIC_ANALYTICS_FILE
        # pointed at /var/data before the disk was attached. Analytics is an
        # accessory; the site serving is the product.
        self._disabled = False
        try:
            self._ensure_file_exists()
        except Exception as exc:
            self._disabled = True
            print(f"[analytics] ledger {self.data_file} is not writable "
                  f"({exc!r}) — visitor tracking DISABLED. Fix "
                  "TRAFFIC_ANALYTICS_FILE (attach the disk it points at, or "
                  "unset it) to re-enable; nothing else is affected.")

    def _ensure_file_exists(self):
        """Create the analytics file (and its directory) if missing."""
        if not self.data_file.exists():
            # A persistent-disk path like /var/data/… may not exist yet on
            # first boot — create the directory rather than failing on it.
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            self.data_file.write_text(json.dumps({
                "visits": [],
                "stats": {
                    "desktop": 0,
                    "mobile": 0,
                    "tablet": 0,
                    "bot": 0,
                    "total": 0
                }
            }, indent=2))

    def detect_device_type(self, user_agent):
        """Detect device type from user agent string."""
        if not user_agent:
            return "desktop"

        user_agent = user_agent.lower()

        # Check for bots first
        if self.is_bot(user_agent):
            return "bot"

        # Check for mobile
        if any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']):
            return "mobile"

        # Check for tablet
        if any(tablet in user_agent for tablet in ['ipad', 'tablet', 'kindle']):
            return "tablet"

        return "desktop"

    def is_bot(self, user_agent):
        """Check if user agent is a bot."""
        if not user_agent:
            return False

        bot_patterns = [
            'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget',
            'python-requests', 'gptbot', 'anthropic', 'claude',
            'googlebot', 'bingbot', 'slurp', 'duckduckbot',
            'perplexitybot', 'chatgpt'
        ]

        return any(pattern in user_agent.lower() for pattern in bot_patterns)

    def detect_bot_type(self, user_agent):
        """Detect the type of bot from user agent."""
        if not user_agent:
            return "unknown"

        user_agent = user_agent.lower()

        # AI Training bots
        training_bots = ['gptbot', 'anthropic-ai', 'claude-web', 'ccbot', 'google-extended', 'facebookbot']
        if any(bot in user_agent for bot in training_bots):
            return "training"

        # AI Search bots
        search_bots = ['chatgpt-user', 'claudebot', 'perplexitybot', 'youbot']
        if any(bot in user_agent for bot in search_bots):
            return "search"

        # Traditional search bots
        traditional_bots = ['googlebot', 'bingbot', 'slurp', 'duckduckbot', 'yandex', 'baidu']
        if any(bot in user_agent for bot in traditional_bots):
            return "traditional"

        return "unknown"

    @lru_cache(maxsize=1000)
    def get_geolocation(self, ip_address):
        """Get geolocation data from IP address using ip-api.com (free service)."""
        # Tests and CI must never depend on a third-party geo API being up.
        if os.getenv("ANALYTICS_GEO_LOOKUP", "1") == "0":
            return None

        # Skip local/private IPs
        if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
            return None

        # Skip private IP ranges
        if ip_address.startswith(('10.', '172.', '192.168.', 'fe80:', 'fc00:', 'fd00:')):
            return None

        try:
            # Use ip-api.com free API (no key required, 45 requests/minute limit)
            response = requests.get(
                f'http://ip-api.com/json/{ip_address}',
                timeout=2  # Short timeout to avoid slowing down requests
            )

            if response.status_code == 200:
                data = response.json()

                # Check if request was successful
                if data.get('status') == 'success':
                    return {
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'region': data.get('regionName'),
                        'city': data.get('city'),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone')
                    }
        except Exception as e:
            # Silently fail - geolocation is optional
            print(f"Geolocation failed for {ip_address}: {e}")
            pass

        return None

    def track_visit(self, path, user_agent, ip_address=None, auth_name=None,
                    country=None):
        """Track a visitor. auth_name (the verified Clerk display name, when the
        caller resolved one) stamps the hit as authenticated. country is the
        edge-supplied CF-IPCountry code, when the request carried one."""
        # Ledger unusable at boot (see __init__) → tracking is off, not broken.
        if self._disabled:
            return

        # The network's internal-traffic contract: hub health sweeps, CI smoke
        # batteries and satellite-to-satellite calls identify themselves with
        # INTERNAL_UA_TOKEN in the User-Agent. Dropped at WRITE time — before
        # device detection and before bot classification — so machinery talking
        # to itself never reaches the ledger the hourly rollup is built from.
        from lib.constants import INTERNAL_UA_TOKEN
        if user_agent and INTERNAL_UA_TOKEN.lower() in user_agent.lower():
            return

        # /healthz is a liveness probe, never a visit.
        if path.startswith('/healthz'):
            return

        # Skip internal Dash paths and static assets
        skip_paths = [
            '.css', '.js', '.png', '.jpg', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot',
            '_dash', '_reload-hash', 'favicon', '/_dash-update-component',
            '/_dash-layout', '/_dash-dependencies', '/_dash-component-suites',
            '/assets/', '[]'  # Also skip malformed paths
        ]
        if any(skip in path for skip in skip_paths):
            return

        # Only track valid paths that start with /
        if not path or not path.startswith('/') or path.startswith('//'):
            return

        device_type = self.detect_device_type(user_agent)

        visit_data = {
            "timestamp": datetime.now().isoformat(),
            "path": path,
            "device_type": device_type,
            "user_agent": user_agent or "Unknown",
        }

        # Add bot type if it's a bot
        if device_type == "bot":
            visit_data["bot_type"] = self.detect_bot_type(user_agent)

        # Stamp verified signed-in visitors (None = anonymous; never guessed)
        if auth_name:
            visit_data["auth"] = True
            visit_data["auth_name"] = str(auth_name)[:60]

        # Country from the edge is free, instant and authoritative — when it is
        # present skip the ip-api lookup entirely (an HTTP call in the request
        # path, rate-limited to 45/min).
        if country:
            visit_data["country"] = country

        if ip_address:
            visit_data["ip_address"] = ip_address

            if not country:
                # Try to get geolocation
                geo_data = self.get_geolocation(ip_address)
                if geo_data:
                    visit_data["location"] = geo_data

        # Load existing data
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
        except Exception:
            data = {"visits": [], "stats": {"desktop": 0, "mobile": 0, "tablet": 0, "bot": 0, "total": 0}}

        # Add visit
        data["visits"].append(visit_data)

        # Trim the oldest hits — the file is rewritten whole on every request,
        # so an unbounded list makes every page view slower forever. Stats are
        # cumulative counters and survive the trim.
        if MAX_VISITS > 0 and len(data["visits"]) > MAX_VISITS:
            data["visits"] = data["visits"][-MAX_VISITS:]

        # Update stats
        data["stats"][device_type] = data["stats"].get(device_type, 0) + 1
        data["stats"]["total"] = data["stats"].get("total", 0) + 1

        # Save data
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)


# Global tracker instance
tracker = AnalyticsTracker()
