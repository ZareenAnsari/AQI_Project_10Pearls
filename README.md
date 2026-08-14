##  Karachi AQI Prediction System

A machine learning app that predicts and forecasts Air Quality Index (AQI) for Karachi. It's built around a Random Forest model, with Hopsworks handling the feature store and model registry, FastAPI serving predictions, and Streamlit as the frontend.

I built this to get hands-on with a full ML pipeline — not just training a model in a notebook, but actually wiring up a feature store, versioning the model, exposing it through an API, and putting a real UI on top of it.

##  What it does
- 3-Day Forecast tab — pulls the latest environmental data automatically and shows a 3-day AQI forecast with daily cards, a trend chart, and a health advisory.
- What-If Simulator tab — lets you manually punch in pollutant levels, weather conditions, and time features to see what the model predicts for a custom scenario.
- Health alerts that change based on the predicted AQI band (Good → Hazardous), using the standard AQI category thresholds.

---

##  Project Overview

Air pollution is a major environmental and public-health concern. The purpose of this project is to develop an intelligent system that can:

- Process air-quality and environmental data
- Perform automated data preprocessing
- Engineer relevant features
- Train and evaluate machine-learning models
- Predict AQI
- Explain predictions using SHAP
- Classify AQI into health-risk categories
- Generate hazard/health alerts
- Visualize results through an interactive Streamlit dashboard
- Automate feature engineering and model training using GitHub Actions

---

##  Known limitations

The forecast depends on how fresh the feature store data is — if the upstream data source lags, forecasts can be stale.
Currently only trained/tuned for Karachi; feature ranges (e.g. dust, aerosol optical depth) wouldn't generalize well to a very different climate without retraining.
No authentication on the FastAPI endpoints — fine for a local/demo setup, not production-ready as-is.

##  Objectives

The main objectives of the project are:

1. Develop an automated AQI prediction pipeline.
2. Perform data preprocessing and feature engineering.
3. Train and compare machine-learning models.
4. Select and save the best-performing model.
5. Generate accurate AQI predictions.
6. Explain model predictions using SHAP.
7. Identify the major features contributing to AQI changes.
8. Generate AQI health and hazard alerts.
9. Provide an interactive visualization dashboard.
10. Automate ML workflows using GitHub Actions.

---

##  System Architecture

```text
                    AQI / Environmental Data
                              │
                              ▼
                    ┌───────────────────┐
                    │ Data Preprocessing│
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Feature Engineering│
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ ML Model Training │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Model Evaluation  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   Best ML Model   │
                    └─────────┬─────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
             AQI          SHAP          Health
          Prediction   Explanation       Alert
                │             │             │
                └─────────────┼─────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Streamlit Dashboard│
                    └───────────────────┘
