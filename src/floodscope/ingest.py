"""
Spatial data pipeline — ingest, transform, validate, publish.

This is the "develop and maintain spatial data pipelines" essential from the
job spec, end to end:

  ingest    read the EA flood-zone shapefile + the ONS postcode CSV
  transform reproject everything to British National Grid (EPSG:27700)
  validate  repair invalid geometries, drop empties
  publish   write to PostGIS with GeoPandas.to_postgis()

Run it:  python -m floodscope.ingest
(Requires the data files from data/README.md and a running PostGIS — see README.)
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from .config import TARGET_CRS, database_url

# --- point these at your downloaded files (see data/README.md) ---
FLOOD_ZONES_PATH = "data/flood_zones.shp"     # EA Flood Map for Planning (Zones 2 & 3)
POSTCODES_PATH = "data/postcodes.csv"         # ONS postcode directory (subset)
POSTCODE_COL = "pcds"
EAST_COL, NORTH_COL = "oseast1m", "osnrth1m"  # ONS BNG eastings/northings


def _validate(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Repair invalid geometries and drop anything empty/null."""
    gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notna()].copy()
    invalid = ~gdf.geometry.is_valid
    if invalid.any():
        gdf.loc[invalid, "geometry"] = gdf.loc[invalid, "geometry"].buffer(0)
    return gdf


def load_flood_zones() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(FLOOD_ZONES_PATH).to_crs(epsg=TARGET_CRS)
    # Expect a column identifying the zone; normalise it to an int 2 or 3.
    zone_col = next((c for c in gdf.columns if c.lower() in ("zone", "flood_zone")), None)
    if zone_col is None:
        raise ValueError("No zone column found in flood-zone data — check the source.")
    gdf["zone"] = gdf[zone_col].astype(int)
    gdf = _validate(gdf)
    return gdf[["zone", "geometry"]]


def load_postcodes() -> gpd.GeoDataFrame:
    df = pd.read_csv(POSTCODES_PATH)
    df = df.dropna(subset=[EAST_COL, NORTH_COL])
    geom = [Point(xy) for xy in zip(df[EAST_COL], df[NORTH_COL])]
    gdf = gpd.GeoDataFrame(
        {"postcode": df[POSTCODE_COL].str.upper()},
        geometry=geom,
        crs=TARGET_CRS,  # ONS eastings/northings are already BNG
    )
    return gdf.drop_duplicates("postcode")


def main():
    url = database_url()
    print("Loading flood zones…")
    zones = load_flood_zones()
    zones.to_postgis("flood_zones", url, if_exists="append", index=False)
    print(f"  -> {len(zones)} flood-zone polygons published")

    print("Loading postcodes…")
    pcs = load_postcodes()
    pcs.to_postgis("properties", url, if_exists="append", index=False)
    print(f"  -> {len(pcs)} postcodes published")
    print("Done. Remember the GiST indexes are created by db/schema.sql.")


if __name__ == "__main__":
    main()
