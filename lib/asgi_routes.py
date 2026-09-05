"""
FastAPI showcase routes for the documentation boilerplate.

The AI/LLM surfaces (``/llms.txt``, ``/<page>/llms.txt``, ``/robots.txt``,
``/sitemap.xml``) are mounted by ``dash-improve-my-llms`` 2.0 directly —
the package detects the FastAPI backend and registers its own router.
This module only carries the **showcase** surfaces that demonstrate
first-class OpenAPI integration under Dash 4.1+'s FastAPI backend:

- ``/healthz``       — liveness probe
- ``/api/backend``   — active backend info
- ``/api/pages``     — registered Dash pages, sortable list

These show up in Swagger UI at ``/docs`` and ReDoc at ``/redoc`` because
each route declares a Pydantic ``response_model``.
"""
from __future__ import annotations

from typing import List, Optional

import dash
from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Pydantic models — these power the OpenAPI schema at /docs
# ---------------------------------------------------------------------------


class BackendInfoModel(BaseModel):
    name: str = Field(..., description="Active backend identifier")
    label: str = Field(..., description="Human-readable backend label")
    is_async: bool = Field(..., description="True for ASGI backends (fastapi, quart)")
    description: str


class PageSummary(BaseModel):
    name: str
    path: str
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None


class PageListResponse(BaseModel):
    backend: str
    count: int
    pages: List[PageSummary]


class HealthResponse(BaseModel):
    """The probe contract, identical on every backend.

    ``lib.health.health_payload`` is the single source — this model only
    types it for Swagger. It used to be built independently here, which is
    how a FastAPI deployment silently lacked ``build``: cd.yml's build-match
    wait polls /healthz for exactly that field, so it would have fallen into
    the "predates the build field" warning path forever, verifying whichever
    release happened to be serving — the muicharts defect the wait was
    written to prevent, reintroduced per-backend.
    """

    # ADDITIVE KEYS ARE KEPT (1.6.44 item 20, and the reason is item 1).
    # A pydantic response_model DROPS every field it does not declare, in
    # SILENCE. That is how `llms_version` — item 1's rider, whose entire
    # purpose is to stop the resolved package version being self-reported —
    # was present on the Flask lane and absent from this one on the template
    # for two days. The template's production runs Flask, so nothing there
    # said so; THIS HOST RUNS FASTAPI, so on this host it is the only lane
    # that answers and the key would simply never have existed.
    #
    # Two defences, because either alone has already failed in the fleet:
    # the known keys are declared below (so Swagger still documents them),
    # and `extra="allow"` keeps whatever health_payload adds NEXT without
    # anyone remembering to come back here. A model that silently narrows
    # the payload is the "two lanes are different documents" trap wearing a
    # type annotation.
    model_config = ConfigDict(extra="allow")

    ok: bool = True
    backend: str
    dash_version: str
    # The serving interpreter (platform.python_version()) — required, not
    # Optional: every process has one, and an absent field is exactly the
    # invisibility that lets an image and its declaration drift apart
    # (ops-seat finding, 2026-08-25).
    python: str
    # Optional because they are environment-dependent, not backend-dependent:
    # `build` is RENDER_GIT_COMMIT (absent off Render), `app` is the
    # satellite key, `geo` needs dash-improve-my-llms >= 2.7.0.
    build: Optional[str] = None
    app: Optional[str] = None
    geo: Optional[dict] = None
    # The resolved dash-improve-my-llms version (item 1's rider) and the
    # ledger block (item 20). `llms_version` is Optional because
    # health_payload OMITS it when the import itself fails, which is the
    # finding rather than a default worth inventing.
    llms_version: Optional[str] = None
    ledger: Optional[dict] = None


# ---------------------------------------------------------------------------
# Router factories
# ---------------------------------------------------------------------------


def build_api_router(app, backend_info) -> APIRouter:
    """Native FastAPI showcase routes — populate /docs and /redoc."""
    router = APIRouter(prefix="/api", tags=["showcase"])

    @router.get("/backend", response_model=BackendInfoModel, summary="Active backend")
    def get_backend() -> BackendInfoModel:
        return BackendInfoModel(
            name=backend_info.name,
            label=backend_info.label,
            is_async=backend_info.is_async,
            description=backend_info.description,
        )

    @router.get(
        "/pages",
        response_model=PageListResponse,
        summary="Registered Dash pages",
    )
    def list_pages() -> PageListResponse:
        pages: List[PageSummary] = []
        for p in dash.page_registry.values():
            pages.append(PageSummary(
                name=p.get("name"),
                path=p.get("path"),
                title=p.get("title"),
                description=p.get("description"),
                icon=p.get("icon"),
            ))
        return PageListResponse(
            backend=backend_info.name,
            count=len(pages),
            pages=sorted(pages, key=lambda x: x.path),
        )

    return router


def build_health_router() -> APIRouter:
    router = APIRouter(tags=["health"])

    @router.get("/healthz", response_model=HealthResponse, summary="Liveness probe")
    def healthz(request: Request) -> HealthResponse:
        from lib.health import health_payload

        # Shared with the flask build so the two can never disagree about
        # what a healthy response says — including the `build` field the CD
        # SHA-wait keys off. Built PER REQUEST: `geo` reports live state and
        # this route is mounted long before any geo configuration runs.
        #
        # THIS request's headers go with it. geo's `resolved` reads the
        # country header off the caller, and the Flask-context fallback
        # inside health_payload can never see a Starlette request — the lane
        # this app actually runs in production would have answered "no
        # request context" forever.
        return HealthResponse(**health_payload("fastapi", headers=request.headers))

    return router


def register_asgi_routes(app, backend_info) -> None:
    """Mount the showcase FastAPI routers on ``app.server``.

    These must be registered **before** ``add_llms_routes(app)`` so that
    the package's catch-all ``/<page>/llms.txt`` matcher does not shadow
    ``/healthz`` or ``/api/*``.
    """
    server: FastAPI = app.server  # type: ignore[assignment]
    server.include_router(build_health_router())
    server.include_router(build_api_router(app, backend_info))
