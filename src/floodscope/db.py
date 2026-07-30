"""
Database access — the PRODUCTION path, using PostGIS.

This is where you learn spatial SQL. The two queries below are the exact
PostGIS equivalents of the Shapely operations in spatial.py:

  * highest zone containing a point  -> ST_Contains
  * nearest Zone-3 distance          -> ST_Distance + KNN (<->) with a GiST index

Both rely on the GiST spatial indexes created in db/schema.sql. Without
those indexes these queries would do a full table scan; with them, PostGIS
prunes to a handful of candidate polygons first. That's "efficient spatial
querying and indexing" from the job spec, made concrete.
"""

from sqlalchemy import create_engine, text
from .config import database_url

_engine = None


def engine():
    global _engine
    if _engine is None:
        _engine = create_engine(database_url(), future=True)
    return _engine


# Highest flood zone whose polygon contains the property point.
_ZONE_SQL = text(
    """
    SELECT max(fz.zone) AS zone
    FROM properties p
    JOIN flood_zones fz ON ST_Contains(fz.geom, p.geom)
    WHERE p.postcode = :postcode
    """
)

# Distance (metres) from the property to the nearest Zone-3 extent.
# The "ORDER BY geom <-> geom LIMIT 1" pattern is a KNN query: with a GiST
# index it walks the tree instead of scanning every polygon.
_DIST_SQL = text(
    """
    SELECT ST_Distance(p.geom, fz.geom) AS distance_m
    FROM properties p
    CROSS JOIN LATERAL (
        SELECT geom
        FROM flood_zones
        WHERE zone = 3
        ORDER BY geom <-> p.geom
        LIMIT 1
    ) fz
    WHERE p.postcode = :postcode
    """
)


def lookup_postcode_risk(postcode: str):
    """Return (zone, distance_m) for a postcode, or None if it isn't loaded."""
    postcode = postcode.strip().upper()
    with engine().connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM properties WHERE postcode = :pc"),
            {"pc": postcode},
        ).first()
        if exists is None:
            return None
        zone = conn.execute(_ZONE_SQL, {"postcode": postcode}).scalar()
        dist = conn.execute(_DIST_SQL, {"postcode": postcode}).scalar()
        return (zone, None if dist is None else float(dist))
