"""Very basic Part 3 training script.

Run this file first:
    python basic_train.py
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


# 1. File locations
project_folder = Path(__file__).parent
data_file = project_folder / "data" / "traffic_processed.csv"
model_folder = project_folder / "models"
model_folder.mkdir(exist_ok=True)


# 2. Load the data
data = pd.read_csv(data_file)


# 3. Create the proxy accident-risk label required by the assignment
high_congestion = data["congestion_category"].isin(["High", "Severe"])
risky_weather = (data["is_severe_weather"] == 1) | (data["is_low_visibility"] == 1)
data["high_risk"] = (high_congestion & risky_weather).astype(int)


# 4. Select simple numerical features
features = [
    "temp_celsius",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "is_holiday",
    "is_weekend",
    "is_low_visibility",
    "is_severe_weather",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
]

X = data[features]
y_classification = data["high_risk"]
y_regression = data["traffic_volume"]


# 5. Use the first 80% for training and the last 20% for testing
split_row = int(len(data) * 0.80)
X_train = X.iloc[:split_row]
X_test = X.iloc[split_row:]
y_class_train = y_classification.iloc[:split_row]
y_class_test = y_classification.iloc[split_row:]
y_reg_train = y_regression.iloc[:split_row]
y_reg_test = y_regression.iloc[split_row:]


# 6. Classification model 1 - Logistic Regression
logistic_model = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
)
logistic_model.fit(X_train, y_class_train)
logistic_prediction = logistic_model.predict(X_test)
logistic_probability = logistic_model.predict_proba(X_test)[:, 1]


# 7. Classification model 2 - Random Forest
forest_classifier = RandomForestClassifier(
    n_estimators=80,
    max_depth=12,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)
forest_classifier.fit(X_train, y_class_train)
forest_class_prediction = forest_classifier.predict(X_test)
forest_class_probability = forest_classifier.predict_proba(X_test)[:, 1]


# 8. Regression model 1 - Linear Regression
linear_model = LinearRegression()
linear_model.fit(X_train, y_reg_train)
linear_prediction = linear_model.predict(X_test)


# 9. Regression model 2 - Random Forest
forest_regression = RandomForestRegressor(
    n_estimators=80,
    max_depth=14,
    random_state=42,
    n_jobs=-1,
)
forest_regression.fit(X_train, y_reg_train)
forest_regression_prediction = forest_regression.predict(X_test)


# 10. Neural network for traffic-volume prediction
neural_model = make_pipeline(
    StandardScaler(),
    MLPRegressor(
        hidden_layer_sizes=(32, 16),
        max_iter=200,
        early_stopping=True,
        tol=0.01,
        random_state=42,
    ),
)
neural_model.fit(X_train, y_reg_train)
neural_prediction = neural_model.predict(X_test)


# 11. K-means clustering
cluster_columns = ["hour_sin", "hour_cos", "traffic_volume", "is_severe_weather"]
cluster_data = data[cluster_columns]
cluster_model = make_pipeline(StandardScaler(), KMeans(n_clusters=4, n_init=10, random_state=42))
data["cluster"] = cluster_model.fit_predict(cluster_data)

cluster_summary = data.groupby("cluster").agg(
    records=("traffic_volume", "size"),
    average_hour=("hour", "mean"),
    average_traffic=("traffic_volume", "mean"),
    severe_weather_rate=("is_severe_weather", "mean"),
)
cluster_summary.to_csv(model_folder / "cluster_summary.csv")


# 12. Very simple association rules: time period -> congestion category
def get_time_period(hour):
    if 6 <= hour < 10:
        return "Morning peak"
    if 10 <= hour < 16:
        return "Midday"
    if 16 <= hour < 20:
        return "Evening peak"
    return "Night"


data["time_period"] = data["hour"].apply(get_time_period)
rules = []

for time_period in data["time_period"].unique():
    for congestion in ["Low", "Medium", "High", "Severe"]:
        condition_a = data["time_period"] == time_period
        condition_b = data["congestion_category"] == congestion
        support = (condition_a & condition_b).mean()
        confidence = (condition_a & condition_b).sum() / condition_a.sum()
        probability_b = condition_b.mean()
        lift = confidence / probability_b

        rules.append(
            {
                "rule": f"{time_period} -> {congestion} congestion",
                "support": support,
                "confidence": confidence,
                "lift": lift,
            }
        )

rules_table = pd.DataFrame(rules).sort_values("lift", ascending=False)
rules_table.head(10).to_csv(model_folder / "association_rules.csv", index=False)


# 13. Save the evaluation results
classification_results = pd.DataFrame(
    [
        {
            "model": "Logistic Regression",
            "accuracy": accuracy_score(y_class_test, logistic_prediction),
            "precision": precision_score(y_class_test, logistic_prediction, zero_division=0),
            "recall": recall_score(y_class_test, logistic_prediction, zero_division=0),
            "f1": f1_score(y_class_test, logistic_prediction, zero_division=0),
            "roc_auc": roc_auc_score(y_class_test, logistic_probability),
        },
        {
            "model": "Random Forest Classifier",
            "accuracy": accuracy_score(y_class_test, forest_class_prediction),
            "precision": precision_score(y_class_test, forest_class_prediction, zero_division=0),
            "recall": recall_score(y_class_test, forest_class_prediction, zero_division=0),
            "f1": f1_score(y_class_test, forest_class_prediction, zero_division=0),
            "roc_auc": roc_auc_score(y_class_test, forest_class_probability),
        },
    ]
)

regression_results = pd.DataFrame(
    [
        {
            "model": "Linear Regression",
            "mae": mean_absolute_error(y_reg_test, linear_prediction),
            "r2": r2_score(y_reg_test, linear_prediction),
        },
        {
            "model": "Random Forest Regressor",
            "mae": mean_absolute_error(y_reg_test, forest_regression_prediction),
            "r2": r2_score(y_reg_test, forest_regression_prediction),
        },
        {
            "model": "Basic Neural Network",
            "mae": mean_absolute_error(y_reg_test, neural_prediction),
            "r2": r2_score(y_reg_test, neural_prediction),
        },
    ]
)

classification_results.to_csv(model_folder / "classification_results.csv", index=False)
regression_results.to_csv(model_folder / "regression_results.csv", index=False)


# 14. Save the trained models
joblib.dump(logistic_model, model_folder / "logistic_classifier.joblib", compress=3)
joblib.dump(forest_classifier, model_folder / "random_forest_classifier.joblib", compress=3)
joblib.dump(linear_model, model_folder / "linear_regression.joblib", compress=3)
joblib.dump(forest_regression, model_folder / "traffic_regression_model.joblib", compress=3)
joblib.dump(neural_model, model_folder / "neural_network_model.joblib", compress=3)
joblib.dump(cluster_model, model_folder / "kmeans_model.joblib", compress=3)


# 15. Save information required by other folders
project_information = {
    "features": features,
    "training_rows": split_row,
    "testing_rows": len(data) - split_row,
    "proxy_high_risk_rate": float(data["high_risk"].mean()),
}

with open(model_folder / "project_information.json", "w", encoding="utf-8") as file:
    json.dump(project_information, file, indent=2)


print("Training completed.")
print("The models and result files are inside the models folder.")
