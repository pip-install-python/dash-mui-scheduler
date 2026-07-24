"""Satellite traffic reporter — POSTs this app's daily rollup to 2plot.ai.

2plot.ai is the analytics home for the whole 2plot network: its owner-only
`/traffic` dashboard charts every satellite side by side. Satellites feed it
by POSTing a signed daily rollup to `POST https://2plot.ai/api/satellite/traffic`
once an hour; re-POSTing the same `(app, date)` overwrites, so hourly reports
of *today* just firm the numbers up. The contract lives in the hub repo at
`docs/network/satellite-analytics.md` — this module implements the sender
side of it verbatim (v1 required fields + all v2 optional fields).

The rollup is derived from the same visitor ledger the tracker writes
(`lib/analytics_tracker`, `TRAFFIC_ANALYTICS_FILE`), using the HUB's own
definitions so the numbers compare across apps:

    human_hits/bot_hits  page hits (assets, /_dash, /healthz, llms/robots/
                         sitemap and /api are not page views and are excluded)
    visitors             unique (IP, user-agent) pairs, humans only
    sessions             visit groups split on 30-minute gaps
    median_session_s     median first→last span of MULTI-PAGE sessions only
                         (single-hit visits have no measurable duration and
                         are never padded in)
    pages                top 20 {path, hits}, humans only
    countries            top 20 {CC: hits}, humans only

Env:
    CROSS_APP_WEBHOOK_SECRET  shared HMAC secret. UNSET → the reporter is a
                              clean no-op (no thread, no network), matching
                              the Clerk-off pattern in this repo.
    SATELLITE_APP_KEY         network-directory key (default "scheduler")
    HUB_TRAFFIC_URL           override the hub endpoint (default 2plot.ai)
    TRAFFIC_REPORT_INTERVAL_S seconds between reports (default 3600)

Accuracy notes:
- A day with zero hits is NEVER posted. Render's filesystem is ephemeral, so
  a deploy wipes the ledger; posting the resulting zeros would overwrite good
  numbers already on the hub. Point `TRAFFIC_ANALYTICS_FILE` at a persistent
  disk (see render.yaml) to keep a day's numbers whole across deploys.
- Yesterday is re-posted alongside today until it falls out of the ledger, so
  a day that ended between reports still lands its final figures.
- Run ONE web worker (or one reporter): the ledger is a whole-file rewrite per
  hit, so concurrent workers lose updates.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import threading
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta

import requests

logger = logging.getLogger(__name__)

HUB_TRAFFIC_URL = os.environ.get(
    "HUB_TRAFFIC_URL", "https://2plot.ai/api/satellite/traffic")
APP_KEY = os.environ.get("SATELLITE_APP_KEY", "scheduler")

SESSION_GAP_MIN = 30          # the hub's session rule — keep it identical
_TIMEOUT = 10                 # seconds per POST
_STARTUP_DELAY_S = 90         # let the app finish booting before the first send

# Not page views. Mirrors the hub's own ledger filter (lib/traffic_insights)
# plus this app's machine endpoints, so "hits" means what a reader did.
_SKIP = ('.css', '.js', '.png', '.jpg', '.ico', '.svg', '.woff', '.ttf', '.eot',
         '_dash', '_reload-hash', 'favicon', '/assets/', '[]',
         '/healthz', '/llms.txt', '/llms.toon', '/sitemap', '/robots',
         '/api/', '/webhooks/')

_started = False
_start_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Rollup
# ---------------------------------------------------------------------------

def _ledger_path():
    from lib.analytics_tracker import tracker

    return tracker.data_file


def _load_visits():
    """Page-view hits from the ledger, each with a parsed `dt` and `vkey`."""
    try:
        with open(_ledger_path()) as f:
            raw = json.load(f).get("visits", [])
    except Exception:
        return []

    out = []
    for v in raw:
        path = v.get("path") or ""
        if not path.startswith("/") or any(s in path for s in _SKIP):
            continue
        try:
            dt = datetime.fromisoformat(v["timestamp"])
        except Exception:
            continue
        ua = hashlib.md5((v.get("user_agent") or "?").encode()).hexdigest()[:8]
        out.append({
            "dt": dt,
            "path": path,
            "is_bot": v.get("device_type") == "bot",
            "vkey": f"{v.get('ip_address') or '?'}|{ua}",
            "country": _country_of(v),
        })
    out.sort(key=lambda v: v["dt"])
    return out


def _country_of(visit):
    """Two-letter country code for a hit, or None.

    Prefers the edge-supplied code (`CF-IPCountry`, stamped by the tracker)
    and falls back to the geolocation lookup's country_code.
    """
    cc = visit.get("country")
    if not cc:
        cc = (visit.get("location") or {}).get("country_code")
    cc = (cc or "").strip().upper()
    # Cloudflare uses XX for unknown and T1 for Tor — neither is a place.
    return cc if len(cc) == 2 and cc not in ("XX", "T1") else None


def _median(values):
    values = sorted(values)
    n = len(values)
    if not n:
        return None
    mid = n // 2
    return values[mid] if n % 2 else (values[mid - 1] + values[mid]) / 2


def build_rollup(date=None, visits=None) -> dict:
    """The signed payload for one day. `date` is a `datetime.date`
    (default: today, the app's own local day — the hub only asks that we stay
    consistent). Returns the v1 fields always, v2 fields when derivable.
    """
    day = date or datetime.now().date()
    visits = [v for v in (visits if visits is not None else _load_visits())
              if v["dt"].date() == day]

    humans = [v for v in visits if not v["is_bot"]]
    rollup = {
        "app": APP_KEY,
        "date": day.strftime("%Y-%m-%d"),
        "human_hits": len(humans),
        "bot_hits": len(visits) - len(humans),
    }
    if not humans:
        return rollup

    # visitors + sessions (30-minute gap rule, humans only)
    by_visitor = defaultdict(list)
    for v in humans:
        by_visitor[v["vkey"]].append(v)

    gap = timedelta(minutes=SESSION_GAP_MIN)
    sessions = 0
    multi_page_spans = []
    for hits in by_visitor.values():
        group = [hits[0]]
        for h in hits[1:]:
            if h["dt"] - group[-1]["dt"] > gap:
                sessions += 1
                if len(group) > 1:
                    multi_page_spans.append(
                        (group[-1]["dt"] - group[0]["dt"]).total_seconds())
                group = [h]
            else:
                group.append(h)
        sessions += 1
        if len(group) > 1:
            multi_page_spans.append(
                (group[-1]["dt"] - group[0]["dt"]).total_seconds())

    rollup["visitors"] = len(by_visitor)
    rollup["sessions"] = sessions
    median = _median(multi_page_spans)
    if median is not None:
        rollup["median_session_s"] = round(median, 1)

    rollup["pages"] = [{"path": p, "hits": n} for p, n
                       in Counter(v["path"] for v in humans).most_common(20)]
    countries = Counter(v["country"] for v in humans if v["country"])
    if countries:
        rollup["countries"] = dict(countries.most_common(20))
    return rollup


# ---------------------------------------------------------------------------
# Send
# ---------------------------------------------------------------------------

def _secret():
    return os.environ.get("CROSS_APP_WEBHOOK_SECRET") or None


def post_rollup(rollup: dict) -> bool:
    """Sign and POST one rollup. Returns True on a 2xx. Never raises.

    Signature scheme is the network's shared one:
    `HMAC_SHA256(CROSS_APP_WEBHOOK_SECRET, f"{ts}." + raw_body)`, timestamp
    within ±300 s of the hub's clock.
    """
    secret = _secret()
    if not secret:
        return False
    body = json.dumps(rollup).encode()
    ts = str(int(time.time()))
    sig = hmac.new(secret.encode(), f"{ts}.".encode() + body,
                   hashlib.sha256).hexdigest()
    try:
        resp = requests.post(
            HUB_TRAFFIC_URL, data=body, timeout=_TIMEOUT,
            headers={"Content-Type": "application/json",
                     "X-AI-Canvas-Timestamp": ts,
                     "X-AI-Canvas-Signature": sig})
    except Exception as exc:
        logger.warning("[traffic-report] POST failed: %r", exc)
        return False
    if resp.status_code >= 300:
        logger.warning("[traffic-report] hub rejected %s (%s): %s",
                       rollup.get("date"), resp.status_code, resp.text[:200])
        return False
    logger.info("[traffic-report] sent %s · %s human / %s bot",
                rollup["date"], rollup["human_hits"], rollup["bot_hits"])
    return True


def report_now() -> list[dict]:
    """Report today (and yesterday, until it ages out of the ledger).

    A day with no hits at all is skipped: an empty ledger after a deploy must
    never overwrite numbers the hub already holds.
    """
    visits = _load_visits()
    today = datetime.now().date()
    sent = []
    for day in (today - timedelta(days=1), today):
        rollup = build_rollup(day, visits=visits)
        if not rollup["human_hits"] and not rollup["bot_hits"]:
            continue
        if post_rollup(rollup):
            sent.append(rollup)
    return sent


# ---------------------------------------------------------------------------
# Hourly loop
# ---------------------------------------------------------------------------

def _loop(interval_s: float, stop: threading.Event):
    if stop.wait(_STARTUP_DELAY_S):
        return
    while True:
        try:
            report_now()
        except Exception:                      # never kill the thread
            logger.exception("[traffic-report] cycle failed")
        if stop.wait(interval_s):
            return


def start_reporter() -> bool:
    """Start the hourly reporter thread. No-op (returns False) when
    CROSS_APP_WEBHOOK_SECRET is unset — so a local run or a deploy without
    the network secret costs nothing and touches no network.
    """
    global _started
    if not _secret():
        return False
    with _start_lock:
        if _started:
            return False
        _started = True
    interval = float(os.environ.get("TRAFFIC_REPORT_INTERVAL_S", "3600"))
    stop = threading.Event()
    threading.Thread(target=_loop, args=(interval, stop),
                     name="traffic-report", daemon=True).start()
    print(f"[traffic-report] reporting app='{APP_KEY}' to {HUB_TRAFFIC_URL} "
          f"every {int(interval)}s")
    return True


if __name__ == "__main__":       # manual check: python -m lib.traffic_report
    print(json.dumps(build_rollup(), indent=2))
