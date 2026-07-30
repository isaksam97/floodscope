"""
FastAPI service — the "production-quality geospatial service and API" the
job spec asks for.

Run it:  uvicorn floodscope.api:app --reload
Docs:    http://localhost:8000/docs   (auto-generated OpenAPI — free with FastAPI)

Endpoints:
  GET /health            -> liveness check
  GET /risk?postcode=..  -> flood-risk score for a postcode
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .db import lookup_postcode_risk
from .scoring import score

app = FastAPI(
    title="FloodScope",
    version="0.1.0",
    description="Geospatial flood-risk scoring for property/insurance use cases.",
)

# web/index.html is opened as a local file or served from a different port
# than this API, so the browser sends it as a cross-origin request.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


class RiskResponse(BaseModel):
    postcode: str
    zone: int | None
    distance_m: float | None
    composite: float
    band: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/risk", response_model=RiskResponse)
def risk(postcode: str = Query(..., min_length=5, max_length=8, examples=["SE5 7UD"])):
    row = lookup_postcode_risk(postcode)
    if row is None:
        raise HTTPException(status_code=404, detail="postcode not loaded")
    zone, distance_m = row
    result = score(zone, distance_m)
    return RiskResponse(
        postcode=postcode.strip().upper(),
        zone=result.zone,
        distance_m=result.distance_m,
        composite=result.composite,
        band=result.band,
    )
