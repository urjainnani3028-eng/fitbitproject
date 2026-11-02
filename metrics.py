"""Prometheus metrics for the Fitbit clustering app.

Streamlit re-runs app.py on every interaction, but Python only imports this
module once per process, so the metrics below are created exactly once.

The /metrics endpoint is only started when the METRICS_PORT environment
variable is set (the Dockerfile sets it to 8000). That keeps local runs,
tests and Streamlit Community Cloud unaffected.
"""

import logging
import os
import threading

from prometheus_client import Counter, Gauge, Histogram, start_http_server

log = logging.getLogger(__name__)

APP_RUNS = Counter(
    "fitbit_app_runs_total",
    "Times the Streamlit script ran (page loads and widget interactions)",
)
PREDICTIONS = Counter(
    "fitbit_predictions_total",
    "Cluster predictions made, by activity level",
    ["level"],
)
PREDICTION_LATENCY = Histogram(
    "fitbit_prediction_latency_seconds",
    "Time taken to scale, project and classify one user input",
    buckets=(0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25),
)
TRAINING_SECONDS = Gauge(
    "fitbit_model_training_seconds",
    "Time the last PCA + K-Means training took",
)
DATASET_ROWS = Gauge(
    "fitbit_dataset_rows",
    "Rows in the training dataset",
)
CLUSTER_SIZE = Gauge(
    "fitbit_cluster_size",
    "Training rows assigned to each cluster",
    ["level"],
)

_lock = threading.Lock()
_started = False


def start_metrics_server():
    """Start the /metrics HTTP server once, if METRICS_PORT is set."""
    global _started
    port = int(os.environ.get("METRICS_PORT", "0"))
    if not port:
        return
    with _lock:
        if _started:
            return
        try:
            start_http_server(port)
            log.info("Prometheus metrics available on :%s/metrics", port)
        except OSError as exc:  # port already taken, e.g. after a hot reload
            log.warning("Could not start metrics server on %s: %s", port, exc)
        _started = True
