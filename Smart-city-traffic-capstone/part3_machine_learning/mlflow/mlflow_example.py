"""Basic MLflow example using the result CSV files."""

import os
from pathlib import Path

import mlflow
import pandas as pd


project_folder = Path(__file__).resolve().parents[1]
result_file = project_folder / "models" / "regression_results.csv"
tracking_folder = Path(__file__).parent / "mlruns"

os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
mlflow.set_tracking_uri(tracking_folder.resolve().as_uri())
mlflow.set_experiment("basic_traffic_project")

results = pd.read_csv(result_file)

for _, row in results.iterrows():
    with mlflow.start_run(run_name=row["model"]):
        mlflow.log_param("model_name", row["model"])
        mlflow.log_metric("mae", row["mae"])
        mlflow.log_metric("r2", row["r2"])

print("MLflow results saved inside mlflow/mlruns.")

