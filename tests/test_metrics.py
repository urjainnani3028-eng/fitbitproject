"""Checks that the app exposes the Prometheus metrics the Grafana dashboard uses."""

import socket
import urllib.request

from prometheus_client import REGISTRY

import metrics
from tests.test_app import _predict, run_app


def _value(name, **labels):
    return REGISTRY.get_sample_value(name, labels) or 0.0


def test_page_load_is_counted():
    before = _value("fitbit_app_runs_total")
    run_app()
    assert _value("fitbit_app_runs_total") > before


def test_training_metrics_are_set():
    run_app()
    assert _value("fitbit_dataset_rows") > 0
    sizes = [_value("fitbit_cluster_size", level=lvl) for lvl in ("active", "moderate", "sedentary")]
    assert all(size > 0 for size in sizes)
    assert sum(sizes) == _value("fitbit_dataset_rows")


def test_prediction_is_counted_by_level():
    before = _value("fitbit_predictions_total", level="active")
    latency_before = _value("fitbit_prediction_latency_seconds_count")
    at = run_app()
    _predict(at, steps=20000, very_active=120, sedentary=600)
    assert _value("fitbit_predictions_total", level="active") == before + 1
    assert _value("fitbit_prediction_latency_seconds_count") == latency_before + 1


def test_metrics_endpoint_serves_metrics(monkeypatch):
    with socket.socket() as s:  # find a free port
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    monkeypatch.setenv("METRICS_PORT", str(port))
    monkeypatch.setattr(metrics, "_started", False)
    metrics.start_metrics_server()
    body = urllib.request.urlopen(f"http://127.0.0.1:{port}/metrics", timeout=5).read().decode()
    assert "fitbit_predictions_total" in body
    assert "fitbit_app_runs_total" in body
