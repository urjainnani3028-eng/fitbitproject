"""Start the Prometheus /metrics server, then Streamlit, in one process.

Streamlit only runs app.py when someone opens the page. Starting the metrics
server here means Prometheus can scrape a pod as soon as it starts, even
before its first visitor. Usage (any `streamlit run` options work):

    METRICS_PORT=8000 python run.py --server.port=8501
"""

import sys

from streamlit.web import cli as stcli

import metrics

if __name__ == "__main__":
    metrics.start_metrics_server()
    sys.argv = ["streamlit", "run", "app.py", *sys.argv[1:]]
    sys.exit(stcli.main())
