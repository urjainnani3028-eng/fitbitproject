# 🏃 Fitbit Activity Clustering

![CI](https://github.com/urjainnani3028-eng/fitbitproject/actions/workflows/ci.yml/badge.svg)

A Streamlit app that groups Fitbit daily-activity data into activity levels using
**PCA** and **K-Means**, and lets you enter your own stats to see which group you fall into.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run with Docker

```bash
docker build -t fitbit-app .
docker run -d -p 8501:8501 --name fitbit fitbit-app
```

Or with Docker Compose:

```bash
docker compose up -d --build
```

Then open http://localhost:8501.

Every push to `main` also publishes the image to GitHub Container Registry:

```bash
docker run -p 8501:8501 ghcr.io/urjainnani3028-eng/fitbitproject:latest
```

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
| **Smoke test** | Starts the Streamlit server and confirms it responds on its health endpoint |
| **Docker** | Builds the image, runs it until Docker reports it healthy, and on `main` pushes it to GHCR |

The tests cover three layers: data quality of `dailyActivity_merged.csv`, the PCA + K-Means
pipeline, and the app itself end to end using Streamlit's `AppTest`.

Dependabot keeps `requirements.txt` and the workflow's actions up to date.
