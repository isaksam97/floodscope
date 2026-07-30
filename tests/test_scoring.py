"""Tests for the scoring logic — no database needed, so CI can run them anywhere."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from floodscope.scoring import score, proximity_score, band  # noqa: E402


def test_zone3_on_extent_is_high():
    r = score(zone=3, distance_m=0.0)
    assert r.band == "High"
    assert r.composite == 1.0


def test_zone1_far_away_is_low():
    r = score(zone=1, distance_m=5000.0)
    assert r.band == "Low"
    assert r.composite < 0.33


def test_proximity_decays_to_zero_at_limit():
    assert proximity_score(0.0) == 1.0
    assert proximity_score(2000.0) == 0.0
    assert proximity_score(5000.0) == 0.0
    assert 0.4 < proximity_score(1000.0) < 0.6


def test_missing_zone_defaults_to_low_baseline():
    r = score(zone=None, distance_m=None)
    assert r.zone_score == 0.1
    assert r.band == "Low"


def test_bands_are_monotonic():
    assert band(0.1) == "Low"
    assert band(0.5) == "Medium"
    assert band(0.9) == "High"
