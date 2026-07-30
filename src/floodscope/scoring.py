"""
Flood-risk scoring — deliberately transparent and rule-based.

This is the same design philosophy as a good insurance risk score: every
number here is one you can defend in a meeting. No black-box model, because
if an underwriter asks "why is this property High risk?" you need a real
answer. (This is also the honest framing that plays well in interviews.)

Inputs per property:
  - flood_zone: the EA Flood Zone the property sits in (1, 2, 3, or None)
  - distance_m: metres to the nearest high-risk (Zone 3) flood extent

EA Flood Zones (England):
  Zone 3 = HIGH   (>1% annual chance from rivers, or >0.5% from the sea)
  Zone 2 = MEDIUM (between 0.1% and 1%)
  Zone 1 = LOW    (<0.1%) — everything not in Zone 2 or 3
"""

from dataclasses import dataclass, asdict

# How dangerous each zone is, on a 0-1 scale. Tunable and explainable.
ZONE_SCORE = {3: 1.0, 2: 0.6, 1: 0.1, None: 0.1}

# Beyond this distance, being near a flood extent adds no extra risk.
PROXIMITY_LIMIT_M = 2000.0

# The two drivers of the composite score. They sum to 1.0.
WEIGHTS = {"zone": 0.7, "proximity": 0.3}


@dataclass
class RiskResult:
    zone: int | None
    distance_m: float | None
    zone_score: float
    proximity_score: float
    composite: float
    band: str

    def to_dict(self):
        return asdict(self)


def proximity_score(distance_m: float | None) -> float:
    """1.0 right on a flood extent, decaying linearly to 0.0 at the limit."""
    if distance_m is None:
        return 0.0
    return max(0.0, 1.0 - (distance_m / PROXIMITY_LIMIT_M))


def band(composite: float) -> str:
    if composite >= 0.66:
        return "High"
    if composite >= 0.33:
        return "Medium"
    return "Low"


def score(zone: int | None, distance_m: float | None) -> RiskResult:
    zs = ZONE_SCORE.get(zone, 0.1)
    ps = proximity_score(distance_m)
    composite = WEIGHTS["zone"] * zs + WEIGHTS["proximity"] * ps
    return RiskResult(
        zone=zone,
        distance_m=None if distance_m is None else round(distance_m, 1),
        zone_score=round(zs, 3),
        proximity_score=round(ps, 3),
        composite=round(composite, 3),
        band=band(composite),
    )
