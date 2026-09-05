"""/terms and /privacy — the Legal section (1.6.44 item 15).

Two pages, one shape each: a SINGLE markdown string that is both what the
browser renders and what the machine lane is handed as ``llms_doc``. That is
the whole point of the shape — a site whose privacy page says one thing to a
reader and another to a crawler has two privacy policies, and only one of
them was reviewed.

The privacy text is GENERATED FROM THE MECHANISM, not from a template. Every
claim in it is a claim about code in this repository, and
``tests/test_legal_pages.py`` holds the two together: it reads a REAL visit
row out of the tracker and asserts every key in it is described here, so if
the tracker starts storing something this page does not mention, the test
goes red rather than the page going quietly false.

BUILT AFTER ITEM 16, deliberately. This page states what the tracker stores
*after* the address stopped being stored; a fork that builds 15 first writes
prose about a mechanism it does not have.
"""
from __future__ import annotations

import dash_mantine_components as dmc
from markdown2dash import Admonition, Divider, Image, create_parser

from lib.constants import (
    BASE_URL,
    DISCORD_URL,
    GITHUB_URL,
    PUBLISHER,
    SITE_SHORT_NAME,
)

TERMS_DESCRIPTION = (
    f"Terms of use for {SITE_SHORT_NAME}: what this site is, what it is not, "
    "and the terms the documentation, the component library and its code "
    "examples are offered under."
)
PRIVACY_DESCRIPTION = (
    f"What {SITE_SHORT_NAME} stores about a visit, what it does not store, "
    "and where the numbers go — described from the code that does it."
)


TERMS_DOC = f"""# Terms of Use

> {TERMS_DESCRIPTION}

## What this site is

{SITE_SHORT_NAME} is documentation, published by {PUBLISHER}. It describes a
component library for [Plotly Dash](https://dash.plotly.com/) that wraps the
MUI X Scheduler, and it is reference material: it is not advice, it is not a
service, and nothing on it is a commitment to keep any particular behaviour
working in your project.

## The documentation, the library, and the code in it

The prose and the code examples are published so you can read them, run them
and copy them. The source repository states the licence the code is offered
under, and that licence — not this page — is what governs your use of it:

- [{GITHUB_URL}]({GITHUB_URL})

Everything here is offered **as is**, without warranty of any kind. Running a
code example against your own data, in your own deployment, is your decision
and your responsibility.

## The components this library wraps

`{SITE_SHORT_NAME}` is a Dash wrapper. The scheduler and chart components it
renders come from MUI X, which has its own licence terms — the Community
components are MIT, and the Pro and Premium components require a licence from
MUI. Installing this package does not grant you one, and the examples on this
site that use Premium features run against a licence key held by this site
and not distributed with the package. Whether your use of the underlying MUI
components is licensed is between you and MUI.

## Accounts

Some pages can be gated behind a sign-in. An account exists so the site can
tell whether you may see a page; it is not a subscription and carries no
entitlement. Accounts may be ended at any time, by you or by us, and the
[Privacy](/privacy) page describes what is kept while one exists.

## Links to other sites

This site links to other sites in the 2plot network, to MUI, and to
third-party projects. Those sites have their own terms and their own privacy
practices, and this page does not speak for them.

## Changes

These terms change when the site does. The change history for the whole site,
including this page, is the [Changelog](/changelog) and the repository's
commit history — there is no separate archive of previous versions, because
the repository already is one.

## Contact

Questions about these terms: the [Discord]({DISCORD_URL}) or an issue on
[the repository]({GITHUB_URL}).
"""


PRIVACY_DOC = f"""# Privacy

> {PRIVACY_DESCRIPTION}

This page describes what the code in this repository actually does. Each
claim below corresponds to something readable in `lib/analytics_tracker.py`,
and the test suite holds the two together.

## What is stored about a visit

Every request that is not network machinery records one row:

- the **time** of the request;
- the **path** requested;
- a **device type** (desktop, mobile, tablet, bot);
- the **User-Agent** string your browser or client sent;
- a **visitor key** — a keyed one-way hash of your network address and
  User-Agent, truncated to sixteen characters, used to tell one visitor from
  another within the retention window;
- a **location**, if and only if the network edge in front of this site sent
  one (see below).

Crawler rows additionally carry the vendor identity the classifier
determined — which bot it was, which class of bot, and whether it verified
against the address ranges that vendor publishes.

## What is NOT stored

- **Your IP address.** It is read from the request so the site can tell one
  visitor from another, and so a crawler can be checked against the ranges
  its vendor publishes, and it is then reduced to the visitor key and
  discarded. It is not written to disk. (An operator running their own copy
  of this software can set `ANALYTICS_KEEP_CLIENT_IP=1` to keep it. This site
  does not.)
- **Anything from a third-party lookup service.** Earlier versions of this
  site sent visitor addresses to a geolocation API to turn them into a city.
  That code was REMOVED — not disabled — in release 1.6.44. This app makes no
  outbound request about you.
- **Cookies for analytics.** The visitor key is computed per request from
  what your client already sent. Nothing is stored in your browser to track
  you. Signing in sets a session cookie, which is what keeps you signed in.

## Where location comes from

From the network edge, or not at all. Cloudflare sits in front of this site
and adds headers describing where a request entered its network:
`CF-IPCountry` always, and `CF-IPCity`, `CF-Region`, `CF-IPLatitude` and
`CF-IPLongitude` when the zone is configured to send them. Whatever arrives
is stored; whatever does not is simply absent. There is no lookup and no
fallback to one.

You can see which of those headers this host is actually receiving — they are
listed in the `geo.headers_seen` field of
[{BASE_URL}/healthz]({BASE_URL}/healthz).

## Network machinery is counted nowhere

The 2plot network's own traffic — hourly health checks, post-deploy test
batteries, continuous integration — carries a marker in its User-Agent and is
dropped before anything is recorded, in both of this site's tables. It is not
in these numbers, by design.

## How long it is kept, and where it goes

Rows are pruned on a retention window and the visit table is capped in size.
A daily summary — counts by day, by page, by country, by crawler vendor — is
sent to the 2plot network hub. The summary carries no visitor keys, no
addresses and no User-Agent strings: it is counts.

## Signing in

Sign-in is handled by Clerk. What Clerk stores about an account is governed
by Clerk's own privacy policy. This site keeps the identifier it needs in
order to decide what you may see.

## Questions

The [Discord]({DISCORD_URL}), or an issue on
[the repository]({GITHUB_URL}).
"""


# The Legal pages share the docs renderer so they carry one typography with
# the rest of the site. A narrower directive set than pages/markdown.py's on
# purpose: `BlockExec`, `Kwargs`, `LlmsCopy`, `SC` and `TOC` all exist to
# serve component documentation, and a Legal page has no business executing
# code or rendering a prop table.
_parse = create_parser([Admonition(), Divider(), Image()])


def _render(markdown: str, page_id: str):
    """The docs renderer, one typography for the whole site.

    `parse()` returns a LIST, and it is splatted rather than nested — not a
    style choice: a list nested inside a children list renders the page EMPTY
    with a green suite (React #31; tests/test_layout_nesting.py pins it).
    """
    return dmc.Container(id=page_id, size="md", py="xl",
                         children=_parse(markdown))
