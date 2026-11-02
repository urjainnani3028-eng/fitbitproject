"""Tests for the PCA + K-Means pipeline used in app.py."""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from tests.test_data import DATA_PATH, FEATURES


def build_pipeline():
    df = pd.read_csv(DATA_PATH).dropna()
    X = df[FEATURES].fillna(0)
    scaler = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)
    pca = PCA(n_components=2).fit(X_scaled)
    X_pca = pca.transform(X_scaled)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(X_pca)
    return df, scaler, pca, kmeans, X_pca


def test_pca_outputs_two_components():
    _, _, _, _, X_pca = build_pipeline()
    assert X_pca.shape[1] == 2


def test_kmeans_finds_three_clusters():
    _, _, _, kmeans, _ = build_pipeline()
    assert len(np.unique(kmeans.labels_)) == 3


def test_clustering_is_reproducible():
    _, _, _, k1, _ = build_pipeline()
    _, _, _, k2, _ = build_pipeline()
    assert np.array_equal(k1.labels_, k2.labels_)


def test_prediction_for_new_user():
    _, scaler, pca, kmeans, _ = build_pipeline()
    user = pd.DataFrame([[8000, 5.0, 5.0, 2200, 1.5, 1.0, 2.0, 0.0, 40, 25, 200, 800]], columns=FEATURES)
    cluster = kmeans.predict(pca.transform(scaler.transform(user)))[0]
    assert cluster in (0, 1, 2)

