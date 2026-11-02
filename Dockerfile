# ---- Fitbit Activity Clustering (Streamlit) ----
FROM python:3.11-slim

# Faster, quieter Python and pip inside containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MPLBACKEND=Agg

WORKDIR /app

# Install dependencies first so Docker can cache this layer
# (it only re-runs when requirements.txt changes)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the app and its dataset
COPY app.py dailyActivity_merged.csv ./

# Run as a non-root user for safety
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8501

# Docker marks the container "healthy" once Streamlit answers
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true"]
