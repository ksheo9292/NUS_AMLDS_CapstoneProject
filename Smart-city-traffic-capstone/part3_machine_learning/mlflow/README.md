# MLflow

Run the MLflow example from the main project folder:

```bash
python mlflow/mlflow_example.py
```

View the stored experiment:

```bash
MLFLOW_ALLOW_FILE_STORE=true mlflow ui --backend-store-uri ./mlflow/mlruns
```

