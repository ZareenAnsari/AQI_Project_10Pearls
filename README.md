#  AQI Prediction System

An end-to-end **Air Quality Index (AQI) Prediction System** that uses machine learning, automated feature engineering, model training, explainable AI, and an interactive Streamlit dashboard to predict AQI and provide health-risk alerts.

The project is designed as an automated ML/MLOps pipeline using **GitHub Actions** for feature processing and model training.

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
