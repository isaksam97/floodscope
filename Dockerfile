FROM python:3.12-slim
# GDAL/GEOS system libs for geopandas/shapely
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin libgdal-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["uvicorn", "floodscope.api:app", "--host", "0.0.0.0", "--port", "8000"]
