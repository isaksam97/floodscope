"""
Core spatial operations.

This module is the "GIS engine" in pure Shapely - the same two operations
you'd run in QGIS or PostGIS, done in code so you understand what they
actually do:

  1. Point-in-polygon  -> which flood zone is this property in?
  2. Nearest-distance  -> how far to the nearest high-risk flood extent?

In PRODUCTION (see db.py) these run inside PostGIS using ST_Contains and a
GiST-indexed KNN (<->) query. Here we mirror them with Shapely's STRtree,
which is the in-memory equivalent of a GiST spatial index - same idea:
don't test every polygon, use a tree to prune the search.

CRS note: all geometries are assumed to already be in a projected, metric
CRS (British National Grid, EPSG:27700). That's why distances come out in
real metres. Reprojection happens once, at ingest time (see ingest.py).
"""

from shapely.geometry import Point
from shapely.strtree import STRtree


class FloodIndex:
    """A tiny spatial index over flood-zone polygons.

    zones: list of (zone_int, shapely_polygon), all in EPSG:27700.

    Shapely 2.x STRtree returns integer indices into the geometry array it
    was built from, so we keep parallel lists and index back into them.
    """

    def __init__(self, zones):
        self.zones = list(zones)
        self._geoms = [poly for _, poly in self.zones]
        self._zone = [z for z, _ in self.zones]
        self._tree = STRtree(self._geoms) if self._geoms else None

        # High-risk (Zone 3) extents, indexed separately for proximity queries.
        self._high = [poly for z, poly in self.zones if z >= 3]
        self._high_tree = STRtree(self._high) if self._high else None

    def highest_zone_at(self, point: Point):
        """Point-in-polygon: the highest (worst) flood zone containing the point."""
        if self._tree is None:
            return None
        candidate_idx = self._tree.query(point)  # indices whose bbox may match
        hits = [self._zone[i] for i in candidate_idx if self._geoms[i].contains(point)]
        return max(hits) if hits else None

    def nearest_high_risk_distance(self, point: Point):
        """Metres to the nearest Zone 3 extent, or None if there are none."""
        if self._high_tree is None:
            return None
        idx = self._high_tree.nearest(point)  # integer index in Shapely 2.x
        return point.distance(self._high[idx])
