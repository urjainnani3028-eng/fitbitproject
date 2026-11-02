# 🏃 Fitbit Activity Clustering

![CI](https://github.com/urjainnani3028-eng/fitbitproject/actions/workflows/ci.yml/badge.svg)

A Streamlit app that groups Fitbit daily-activity data into activity levels using
**PCA** and **K-Means**, and lets you enter your own stats to see which group you fall into.

The project also shows a full DevOps workflow around the app: automated testing,
Docker, Kubernetes, Terraform, and monitoring with Prometheus and Grafana.

```
 git push ──▶ GitHub Actions ──▶ tests · lint · Terraform/K8s/PromQL checks
                    │            · deploy to a throwaway Kubernetes cluster
                    ▼
            GHCR image (amd64 + arm64)

 terraform apply ──▶ Kubernetes cluster
                      ├── namespace fitbit:     2 app pods + Service  (/metrics on :8000)
                      └── namespace monitoring: Prometheus ──scrapes──▶ app pods
                                                Grafana ◀── "Fitbit Activity Clustering" dashboard
```

## Tech stack

| Area | Tools |
|---|---|
| App | Python, Streamlit, scikit-learn (PCA + K-Means), pandas |
| Testing | pytest, Streamlit `AppTest`, ruff |
| CI/CD | GitHub Actions, Dependabot, GitHub Container Registry |
| Containers | Docker, Docker Compose |
| Orchestration | Kubernetes (Deployment with probes, rolling updates, resource limits) |
| Infrastructure as code | Terraform (Kubernetes + Helm providers) |
| Monitoring | Prometheus (custom app metrics, alert rules), Grafana (provisioned dashboard) |

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run with Docker

```bash
docker compose up -d --build
```

App: http://localhost:8501 · Metrics: http://localhost:8000/metrics

## Deploy to Kubernetes with Terraform (Prometheus + Grafana included)

Needs Docker Desktop with Kubernetes enabled, and Terraform.

```bash
docker compose build                 # the cluster uses this local image
kubectl config use-context docker-desktop
cd terraform
terraform init
terraform apply
terraform output next_steps          # port-forward commands
terraform output -raw grafana_admin_password
```

Then open Grafana (http://localhost:3000) and find the **Fitbit Activity Clustering** dashboard.

To deploy only the app, without Terraform or monitoring: `kubectl apply -f k8s/`.

To remove everything: `terraform destroy`.

## App metrics

| Metric | What it measures |
|---|---|
| `fitbit_predictions_total{level}` | Predictions made, by activity level |
| `fitbit_prediction_latency_seconds` | Time per prediction (histogram) |
| `fitbit_app_runs_total` | Page loads and interactions |
| `fitbit_model_training_seconds` | PCA + K-Means training time |
| `fitbit_dataset_rows`, `fitbit_cluster_size{level}` | Training data size and cluster split |

Alert rules: **FitbitAppDown**, **FitbitAppReplicasMissing**, **FitbitSlowPredictions**.

## Tests

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

## Continuous Integration

Every push and pull request to `main` runs the [CI workflow](.github/workflows/ci.yml):

| Job | What it does |
|---|---|
| **Lint** | Checks code with `ruff` and annotates problems inline on PRs |
| **Tests** | Runs `pytest` on Python 3.10, 3.11 and 3.12 with coverage, and uploads the reports |
| **Smoke test** | Starts the app and confirms the health and `/metrics` endpoints respond |
| **Infra** | `terraform fmt` + `validate`, `kubeconform` on the manifests, `promtool` on every alert rule and dashboard query |
| **Kubernetes** | Creates a kind cluster, deploys `k8s/`, waits for both replicas, and checks the Service |
| **Docker** | Builds the image, waits until it's healthy, and on `main` pushes an amd64 + arm64 image to GHCR |

## Project structure

```
app.py                 Streamlit app
metrics.py             Prometheus metrics
run.py                 Starts /metrics, then Streamlit (used in Docker/Kubernetes)
tests/                 Data, model, app and metrics tests
Dockerfile, docker-compose.yml
k8s/                   Namespace, Deployment, Service
terraform/             Deploys the app + kube-prometheus-stack to Kubernetes
monitoring/            Helm values (scrape config, alerts) and Grafana dashboard
scripts/               CI helper that extracts PromQL for promtool
.github/               CI workflow and Dependabot
```
