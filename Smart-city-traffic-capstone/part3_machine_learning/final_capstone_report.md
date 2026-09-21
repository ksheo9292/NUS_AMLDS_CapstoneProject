# Part 3 Final Capstone Report

## Project overview

This project develops a beginner-friendly intelligent mobility solution using the processed Metro Interstate Traffic Volume dataset. The work includes classification, regression, clustering, association rules, a basic neural network, LIME explainability, MLflow experiment tracking, a recommendation system, an API deployment mock-up and model monitoring.

No accident dataset was supplied. Therefore, the classification task uses the assignment's proxy label. A record is labelled high risk when High or Severe congestion occurs together with severe or low-visibility weather. This result demonstrates the classification process only and is not a real accident-prediction model.

## Supervised machine learning

The models use temperature, rain, snow, cloud cover, holiday and weekend indicators, weather-risk indicators, and cyclical hour and weekday features. The first 80% of the data is used for training and the final 20% is used for testing so that later records are not used to predict earlier records.

Two classification algorithms were compared. Logistic Regression achieved accuracy 0.936, precision 0.679, recall 0.981, F1 0.802 and ROC AUC 0.969. The Random Forest Classifier performed better, with accuracy 0.977, precision 0.887, recall 0.952, F1 0.918 and ROC AUC 0.993.

Two regression algorithms were also compared. Linear Regression achieved MAE 844.9 vehicles per hour and R-squared 0.699. The Random Forest Regressor performed better, with MAE 301.2 and R-squared 0.925. The random forest was selected as the main traffic-volume model.

## Unsupervised learning

K-means divided the traffic records into four groups. The lowest-volume cluster averaged about 1,025 vehicles per hour. Two higher-volume clusters averaged about 4,165 and 4,823 vehicles per hour. The remaining cluster contained severe-weather records and averaged about 3,074 vehicles per hour.

The strongest association rule was Morning peak to Severe congestion, with confidence 58.5% and lift 2.34. Midday to High congestion had confidence 58.3% and lift 2.33. Night to Low congestion had confidence 56.2% and lift 2.25. Lift greater than 1 means the relationship occurs more often than expected from the overall congestion rate.

## Neural network and explainability

A basic neural network with two hidden layers containing 32 and 16 units was trained to predict traffic volume. It achieved MAE 752.1 and R-squared 0.750. This was better than the linear baseline but weaker than the random forest.

LIME is included in the notebook to explain one neural-network prediction. It changes the selected record slightly, observes how the prediction changes and creates a simple local explanation. A LIME explanation describes one prediction only and should not be interpreted as a global causal result.

## Advanced AI technique and MLOps

MLflow records the model name, MAE and R-squared for the regression experiments. The results are saved in `mlflow/mlruns`. This creates a simple experiment history that can be reviewed later.

A FastAPI mock-up loads the selected random-forest model and exposes a `/predict` endpoint. The API accepts hour, weekday and weather-related inputs and returns predicted traffic volume.

## Recommendation system

The dataset represents one corridor, so the system recommends travel time rather than an alternative route. For the clear weekday example, the three lowest historical traffic periods were 02:00-03:00, 03:00-04:00 and 01:00-02:00. These statistically quiet periods may not be practical for every traveller, so a real system should include user constraints.

## Monitoring

The monitoring example compares model error in the older period with the recent test period. The recent MAE was 301.2 compared with 190.8 in the older period, producing a ratio of 1.58. Because this exceeded the classroom threshold of 1.50, the system returned ALERT. An alert should lead to investigation and validation rather than automatic retraining.

## Conclusion

The Random Forest Regressor was the best demand-prediction model, while the Random Forest Classifier was the best proxy-risk model. K-means and association rules identified clear time and congestion patterns. The project demonstrates a complete but simple AI workflow. Before real-world use, the proxy label must be replaced, the model must be tested on additional roads and conditions, and human governance must be added.

