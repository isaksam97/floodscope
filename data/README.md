# Data sources — all open, all free, no login

Place the downloaded files in this `data/` folder and match the filenames at the
top of `src/floodscope/ingest.py`. None of this is confidential or employer data.

## 1. Flood zones — Environment Agency "Flood Map for Planning"
- **What:** Flood Zones 2 and 3 for England, as polygons.
- **Where:** DEFRA Data Services Platform / EA "Flood Map for Planning (Rivers and Sea) — Flood Zone 2 and Flood Zone 3".
- **Format:** Shapefile or GeoPackage, already in British National Grid (EPSG:27700).
- **Licence:** Open Government Licence (OGL).
- **Tip:** Download a single county or district first (e.g. clip to Gloucestershire or Greater London) so your first load is small and fast.

## 2. Postcodes — ONS Postcode Directory (ONSPD / NSPL)
- **What:** Every UK postcode with its BNG eastings/northings and lat/long.
- **Where:** ONS Open Geography Portal.
- **Format:** CSV. Use the `pcds`, `oseast1m`, `osnrth1m` columns.
- **Licence:** OGL (contains OS data © Crown copyright).
- **Tip:** Filter to the same area as your flood zones before loading.

## Optional extras (for later phases)
- OS Terrain 50 (elevation) — to add a height-above-nearest-drainage feature.
- OS Open Rivers — to score distance to watercourses as well as flood extents.

> You do **not** need any of this to try the project — run `python scripts/demo_local.py`
> first, which uses synthetic data and needs no downloads.
