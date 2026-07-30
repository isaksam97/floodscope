-- FloodScope PostGIS schema.
-- Run once against your database:  psql ... -f db/schema.sql
-- (docker-compose loads this automatically on first startup.)

CREATE EXTENSION IF NOT EXISTS postgis;

-- Flood zones: EA Flood Map for Planning, Zones 2 and 3, in British National Grid.
DROP TABLE IF EXISTS flood_zones;
CREATE TABLE flood_zones (
    id    serial PRIMARY KEY,
    zone  integer NOT NULL CHECK (zone IN (2, 3)),
    geom  geometry(MultiPolygon, 27700) NOT NULL
);

-- Properties, keyed by postcode, as BNG points.
DROP TABLE IF EXISTS properties;
CREATE TABLE properties (
    postcode text PRIMARY KEY,
    geom     geometry(Point, 27700) NOT NULL
);

-- The GiST spatial indexes. THESE are what make ST_Contains and the KNN
-- distance query fast instead of full table scans. This is the "efficient
-- spatial querying and indexing" line from the job spec.
CREATE INDEX IF NOT EXISTS flood_zones_geom_gix ON flood_zones USING GIST (geom);
CREATE INDEX IF NOT EXISTS properties_geom_gix  ON properties  USING GIST (geom);
