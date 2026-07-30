# FloodScope

A geospatial **flood-risk scoring service**: give it a postcode, it tells you the
Environment Agency flood zone, the distance to the nearest high-risk flood extent,
and a transparent risk score and band — the kind of location-based risk lookup an
insurance / reinsurance *risk & analytics* team runs against a book of properties.

Built with only open public data (Environment Agency flood zones, ONS postcodes).

---

## Why this project exists

It's a deliberate, honest way to turn "I've *scoped* PostGIS / APIs" into "I've
*built* them", while leading from genuine GIS strengths. Each part maps to a line
from the target job spec:

| Job requirement | Where it lives here | Your footing |
|---|---|---|
| Strong GIS — CRS, projections, geometry ops, spatial analysis | `spatial.py`, EPSG:27700 throughout | **Strength** |
| Python geospatial (GeoPandas, Shapely, PyProj) | `ingest.py`, `spatial.py` | **Strength** |
| Spatial data pipeline — ingest, transform, validate, publish | `ingest.py` | Learn by doing |
| Spatial database (PostGIS) + indexing | `db/schema.sql`, `db.py` | **Gap → close it here** |
| Production Python API, well-tested | `api.py`, `tests/` | Learn by doing |
| Web mapping (Leaflet) | `web/index.html` | Partial → make real |
| AI-assisted development, Git | how you build it | **Strength** |
| Insurance / risk domain | the whole use case | New → context |

Honest scope: this teaches you the *shape* of production geospatial engineering.
It is not a substitute for ArcGIS JS or TypeScript/Angular — those stay separate
gaps, and that's fine.

---

## Start here (no database, no downloads)

```bash
pip install shapely
python scripts/demo_local.py
```

This runs the GIS engine + scoring on synthetic data and prints a risk table.
Once it makes sense, move through the phases below.

---

## Build phases

**Phase 0 — Understand the core.** Read `scoring.py` and `spatial.py`, run the demo.
This is your home turf: point-in-polygon and nearest-distance in a metric CRS.

**Phase 1 — Stand up PostGIS.** `docker compose up db`, then load real data:
download the EA + ONS files (`data/README.md`), point `ingest.py` at them, and run
`python -m floodscope.ingest`. You've now built a spatial data pipeline.

**Phase 2 — Learn spatial SQL.** Open `db.py` and run the `ST_Contains` and KNN
(`<->`) queries by hand in `psql`. Watch what the GiST indexes do with `EXPLAIN`.

**Phase 3 — Run the API.** `uvicorn floodscope.api:app --reload`, then open
`/docs` and hit `GET /risk?postcode=...`. That's a production-style geospatial API.

**Phase 4 — Web map.** Open `web/index.html` next to the running API.

**Stretch — where the remaining job essentials live.** Dockerise fully
(`docker compose up --build`), add CI that runs `pytest`, then rebuild the
front-end in **React + TypeScript** to hit that exact essential. Add a raster
feature (elevation) if you want Rasterio exposure.

---

## Run the tests

```bash
pip install pytest
python -m pytest
```

The scoring tests need no database, so they run anywhere (and in CI).

---

## Layout

```
floodscope/
├─ src/floodscope/
│  ├─ scoring.py     transparent, rule-based risk score (fully tested)
│  ├─ spatial.py     Shapely GIS engine (point-in-zone, nearest distance)
│  ├─ ingest.py      GeoPandas pipeline → PostGIS
│  ├─ db.py          PostGIS spatial SQL (ST_Contains, KNN)
│  ├─ api.py         FastAPI service
│  └─ config.py
├─ db/schema.sql     PostGIS tables + GiST indexes
├─ scripts/demo_local.py   synthetic end-to-end demo (no DB)
├─ tests/            pytest
├─ web/index.html    minimal Leaflet front-end
├─ data/README.md    where to download the open datasets
├─ docker-compose.yml / Dockerfile
└─ requirements.txt
```

---

## A note on the score

The risk score is intentionally a **transparent weighted combination** of flood
zone and proximity — not a black box. If someone asks "why is this property High
risk?", the answer is a real sentence. That honesty is the point, in the code and
in the interview.

*Built by Isak Sam.*
