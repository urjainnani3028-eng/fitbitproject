import streamlit as st
import pandas as pd
import numpy as np
import time
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

import metrics

# -------------------------------------------
# 🎯 PAGE CONFIG
# -------------------------------------------
st.set_page_config(page_title="Fitbit Activity Clustering", layout="wide", page_icon="🏃")

metrics.start_metrics_server()
metrics.APP_RUNS.inc()

st.title("🏃 Fitbit Activity Clustering App (PCA + K-Means)")
st.write("""
This app uses **PCA (Principal Component Analysis)** and **K-Means Clustering**  
to group Fitbit activity data into different activity-level clusters.  
You can also input your own daily stats to see **which cluster you belong to**.
""")

# -------------------------------------------
# 📂 LOAD TRAINING DATA & TRAIN MODEL
# -------------------------------------------
@st.cache_data
def load_and_train():
    start = time.perf_counter()
    # Load your Fitbit dataset
    df = pd.read_csv("dailyActivity_merged.csv")
    df = df.drop(columns=['Id', 'ActivityDate'], errors='ignore')
    df = df.dropna()

    # Select relevant numeric features
    features = [
        'TotalSteps', 'TotalDistance', 'TrackerDistance', 'Calories',
        'VeryActiveDistance', 'ModeratelyActiveDistance', 'LightActiveDistance',
        'SedentaryActiveDistance', 'VeryActiveMinutes', 'FairlyActiveMinutes',
        'LightlyActiveMinutes', 'SedentaryMinutes'
    ]

    X = df[features].fillna(0)

    # Scale the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA reduction
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    # Train KMeans
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(X_pca)
    df['cluster'] = kmeans.labels_

    metrics.TRAINING_SECONDS.set(time.perf_counter() - start)
    metrics.DATASET_ROWS.set(len(df))

    return df, features, scaler, pca, kmeans, X_pca


def label_clusters(df):
    """K-Means numbers clusters arbitrarily, so name them by average steps.

    Returns a dict like {cluster_id: "sedentary" | "moderate" | "active"}.
    """
    order = df.groupby("cluster")["TotalSteps"].mean().sort_values().index
    return dict(zip(order, ["sedentary", "moderate", "active"]))


df, features, scaler, pca, kmeans, X_pca = load_and_train()
cluster_names = label_clusters(df)
for cluster_id, level in cluster_names.items():
    metrics.CLUSTER_SIZE.labels(level=level).set(int((df["cluster"] == cluster_id).sum()))

# -------------------------------------------
# 📊 CLUSTER VISUALIZATION
# -------------------------------------------
st.subheader("📈 Trained Data Cluster Visualization")
fig, ax = plt.subplots(figsize=(8,6))
sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=df['cluster'], palette='Set2', s=80, ax=ax)
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.title("Clusters Found in Fitbit Data (PCA Projection)")
st.pyplot(fig)

# Show cluster averages
st.subheader("📋 Cluster Feature Averages")
cluster_profile = df.groupby('cluster')[features].mean().round(2)
st.dataframe(cluster_profile)

# -------------------------------------------
# 🧩 USER INPUT SECTION
# -------------------------------------------
st.subheader("🧠 Predict Your Cluster")

st.markdown("Enter your daily Fitbit stats below to see which cluster you belong to.")

with st.form("user_input_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        TotalSteps = st.number_input("Total Steps", min_value=0, value=8000)
        TotalDistance = st.number_input("Total Distance (miles)", min_value=0.0, value=5.0)
        TrackerDistance = st.number_input("Tracker Distance (miles)", min_value=0.0, value=5.0)
        Calories = st.number_input("Calories Burned", min_value=0, value=2200)

    with col2:
        VeryActiveDistance = st.number_input("Very Active Distance", min_value=0.0, value=1.5)
        ModeratelyActiveDistance = st.number_input("Moderately Active Distance", min_value=0.0, value=1.0)
        LightActiveDistance = st.number_input("Light Active Distance", min_value=0.0, value=2.0)
        SedentaryActiveDistance = st.number_input("Sedentary Active Distance", min_value=0.0, value=0.0)

    with col3:
        VeryActiveMinutes = st.number_input("Very Active Minutes", min_value=0, value=40)
        FairlyActiveMinutes = st.number_input("Fairly Active Minutes", min_value=0, value=25)
        LightlyActiveMinutes = st.number_input("Lightly Active Minutes", min_value=0, value=200)
        SedentaryMinutes = st.number_input("Sedentary Minutes", min_value=0, value=800)

    submitted = st.form_submit_button("🔍 Predict My Cluster")

# -------------------------------------------
# 🧮 CLUSTER PREDICTION
# -------------------------------------------
if submitted:
    # Create a dataframe from user input
    user_input = np.array([[TotalSteps, TotalDistance, TrackerDistance, Calories,
                            VeryActiveDistance, ModeratelyActiveDistance, LightActiveDistance,
                            SedentaryActiveDistance, VeryActiveMinutes, FairlyActiveMinutes,
                            LightlyActiveMinutes, SedentaryMinutes]])

    # Scale + PCA transform
    with metrics.PREDICTION_LATENCY.time():
        user_input = pd.DataFrame(user_input, columns=features)
        user_scaled = scaler.transform(user_input)
        user_pca = pca.transform(user_scaled)
        user_cluster = kmeans.predict(user_pca)[0]

    # Display result
    st.success(f"✅ You belong to **Cluster {user_cluster}**")

    # Interpretation
    st.subheader("📋 Cluster Interpretation")
    user_level = cluster_names[user_cluster]
    metrics.PREDICTIONS.labels(level=user_level).inc()
    if user_level == "active":
        st.markdown(f"""
        ### 🏃 Cluster {user_cluster}: Highly Active Users
        - High total steps and calorie burn  
        - Very low sedentary minutes  
        - Excellent overall activity level! 💪
        """)
    elif user_level == "moderate":
        st.markdown(f"""
        ### ⚖️ Cluster {user_cluster}: Moderately Active Users
        - Balanced active and sedentary time  
        - Moderate step count and activity minutes  
        - Good lifestyle, but room for improvement 👍
        """)
    else:
        st.markdown(f"""
        ### 🪑 Cluster {user_cluster}: Sedentary Users
        - Low step count and active minutes  
        - High sedentary time  
        - Try adding short walks or workouts to boost activity 🚶
        """)

    # -------------------------------------------
    # 📍 VISUALIZE USER POINT ON PCA CLUSTER MAP
    # -------------------------------------------
    st.subheader("📍 Your Position on the Cluster Map")

    fig2, ax2 = plt.subplots(figsize=(8,6))
    sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=df['cluster'], palette='Set2', s=70, alpha=0.8, ax=ax2)
    ax2.scatter(user_pca[:, 0], user_pca[:, 1], c='red', s=200, marker='X', edgecolor='black', label='You')
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.title("Your Location Among Activity Clusters")
    plt.legend()
    st.pyplot(fig2)
