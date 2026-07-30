"""
Local demo — runs the whole scoring flow on tiny SYNTHETIC data, with NO
database and NO downloads required. Start here.

This proves the GIS engine + scoring work end to end, using only Shapely.
Once this makes sense, move to the PostGIS path (see README, Phase 1+).

Run:  python scripts/demo_local.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shapely.geometry import Point, Polygon  # noqa: E402
from floodscope.spatial import FloodIndex     # noqa: E402
from floodscope.scoring import score          # noqa: E402


def make_synthetic_zones():
    """A pretend riverside: Zone 3 hugging the 'river', Zone 2 around it.

    Coordinates are in pretend metres (as if EPSG:27700). The river runs
    vertically at x=100; Zone 3 is the strip 90<x<110, Zone 2 is 70<x<130.
    """
    zone3 = Polygon([(90, 0), (110, 0), (110, 200), (90, 200)])
    zone2 = Polygon([(70, 0), (130, 0), (130, 200), (70, 200)])
    return [(3, zone3), (2, zone2)]


def main():
    zones = make_synthetic_zones()
    index = FloodIndex(zones)

    properties = {
        "AA1 1AA": Point(100, 100),   # right on the river -> Zone 3
        "BB2 2BB": Point(120, 100),   # in the Zone 2 strip, near Zone 3
        "CC3 3CC": Point(300, 100),   # far away -> Zone 1 (low)
        "DD4 4DD": Point(135, 50),    # just outside Zone 2, close-ish to Zone 3
    }

    print(f"{'postcode':10} {'zone':>4} {'dist_m':>8} {'composite':>10}  band")
    print("-" * 46)
    for pc, pt in properties.items():
        zone = index.highest_zone_at(pt)
        dist = index.nearest_high_risk_distance(pt)
        r = score(zone, dist)
        zone_s = "1" if zone is None else str(zone)
        dist_s = "-" if dist is None else f"{dist:.1f}"
        print(f"{pc:10} {zone_s:>4} {dist_s:>8} {r.composite:>10}  {r.band}")


if __name__ == "__main__":
    main()
