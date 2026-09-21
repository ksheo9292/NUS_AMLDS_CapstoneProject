# Capstone Part 3 Machine Learning

## Folder structure

```text
part3_machine_learning/
|-- data/
|-- notebooks/
|-- models/
|-- mlflow/
|-- deployment/
|-- recommendation_system/
|-- monitoring/
|-- responsible_ai_report.pdf
|-- basic_train.py
|-- requirements.txt
`-- README.md
```

## Easiest way to run the project

Open a terminal inside the `part3_machine_learning` folder.

### Step 1 Create the Python environment

```bash
python -m venv .venv
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

### Step 2 Install the packages

```bash
pip install -r requirements.txt
```

### Step 3 Run the basic training script

```bash
python basic_train.py
```

This creates the trained model files and result CSV files inside `models/`.

### Step 4 Run the recommendation system

```bash
python recommendation_system/recommend.py
```

### Step 5 Run monitoring

```bash
python monitoring/monitor.py
```

The monitoring status is saved as `monitoring/monitoring_result.json`.

### Step 6 Record experiments with MLflow

```bash
python mlflow/mlflow_example.py
```

### Step 7 Start the API

```bash
uvicorn deployment.app:app --reload
```

Open `http://127.0.0.1:8000/docs` to test the prediction endpoint.


## Deliverables covered

- Two classification algorithms
- Two regression algorithms
- Classification and regression metrics
- K-means clustering
- Basic association rules with lift
- Basic neural network
- LIME explainability example
- MLflow experiment tracking
- Traffic-time recommendation system
- FastAPI deployment mock-up
- Monitoring with PASS or ALERT


