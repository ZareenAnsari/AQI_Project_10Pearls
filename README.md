# Karachi AQI Prediction System

A machine learning app that predicts and forecasts Air Quality Index (AQI) for Karachi. Built around a Random Forest model, with Hopsworks handling the feature store and model registry, FastAPI serving predictions, and Streamlit as the frontend.

I built this to get hands-on with a full ML pipeline not just training a model in a notebook, but actually wiring up a feature store, versioning the model, exposing it through an API, and putting a real UI on top of it.

**Submitted by:** Zareen Ansari
**Program:** 10Pearls Shine Internship Program
**Institution:** 10Pearls Pakistan

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement & Objectives](#problem-statement--objectives)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Data & Feature Engineering](#data--feature-engineering)
- [Model & Methodology](#model--methodology)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [API Reference](#api-reference)
- [Results & Evaluation](#results--evaluation)
- [Screenshots](#screenshots)
- [Limitations](#limitations)
- [Implemented](#implemented)
- [Author](#author)

---

## Overview

Air pollution is a persistent problem in Karachi, and reliable, easy-to-read AQI information isn't always available in a timely way. This project is a small end-to-end ML system that predicts the current and near-future Air Quality Index based on pollutant concentrations, weather variables, and time-based features. It supports both an automatic 3-day forecast and a manual "what-if" mode where you can test custom scenarios.

## Problem Statement & Objectives

There's a need for a lightweight, self-contained system that can 
- (a) predict AQI from a given set of environmental readings, and 
- (b) forecast AQI a few days ahead using recent trends without requiring the user to understand the model underneath.

Goals for this project:

- Collect and engineer relevant pollutant, weather, and time-based features for AQI prediction.
- Train and evaluate multiple models and best model was Random Forest Regressor.
- Version and serve the trained model using a feature store / model registry (Hopsworks).
- Expose the model through a REST API (FastAPI) with prediction and forecast endpoints.
- Build an interactive frontend (Streamlit) for both automatic forecasting and manual scenario testing.
- Evaluate accuracy and usability, and document limitations honestly rather than overselling the result.

## Features

- **3-Day Forecast tab** : pulls the latest environmental data automatically and shows a 3-day AQI forecast with daily cards, a trend chart, and a health advisory.
- **What-If Simulator tab** : lets you manually enter pollutant levels, weather conditions, and time features to see what the model predicts for a custom scenario.
- Health alerts that change based on the predicted AQI band (Good → Hazardous), using standard AQI category thresholds.

## Tech Stack

| Layer | Tool |
|---|---|
| Model | Random Forest (scikit-learn) |
| Feature Store & Model Registry | Hopsworks |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Data source |  Zenodo.org, Aqicn.org |

## System Architecture

The system follows a standard ML-serving pipeline with four main components:

```
Environmental data source
        │
        ▼
Hopsworks Feature Store  ──►  Model training  ──►  Hopsworks Model Registry
                                                                  │
                                                                  ▼
                                                        FastAPI (/predict, /forecast, /health)
                                                                  │
                                                                  ▼
                                                        Streamlit UI (this repo)
```

Data flows one direction at inference time: the Streamlit app never talks to Hopsworks directly. Every read and prediction goes through the FastAPI layer, which keeps the frontend simple and keeps credentials off the client.

## Data & Feature Engineering

**Data source:** Zenodo.org, Aqicn.org

**Features used:**

| Category | Features |
|---|---|
| Pollutants | PM10, PM2.5, CO, NO2, SO2, O3 |
| Atmospheric | Aerosol Optical Depth, Dust, UV Index |
| AQI context | Current AQI, European AQI |
| Time features | Hour, Day, Month, Weekday |
| History / trend | AQI Change Rate, AQI Lag 1, AQI Lag 7 |
| Weather | Temperature, Humidity, Wind Speed, Rain |


## Model & Methodology

Random Forest regression was chosen because it handles non-linear relationships between pollutants and AQI reasonably well, needs relatively little feature scaling, and is robust to the kind of noisy readings you get from environmental sensors.

| Model | RMSE | MAE | R² |
|---|---:|---:|---:|
| Ridge Regression | 28.1912 | 22.4450 | 0.1029 |
| Random Forest | 24.1779 | 17.2996 | 0.3402 |
| XGBoost | 25.0515 | 17.4762 | 0.2916 |
| LSTM | 30.3105 | 23.8073 | -0.0002 | Random Forest was best among these models.

**Training pipeline:** Features are engineered and written to the Hopsworks Feature Store. The Random Forest model is trained on this feature set and, once evaluated, registered to the Hopsworks Model Registry along with its version number, so the serving layer always pulls a known, reproducible model rather than whatever's sitting in a local file.

**Hyperparameters:** max_depth=20, n_estimators=300, random_state=42, gridsearchcv=5.

## Project Structure

```
.
├── streamlit_app.py        # frontend
├── app.py/                     # FastAPI backend (endpoints, model loading)
├── pipelines/                # feature engineering / training pipeline
├── requirements.txt
└── README.md
```


## Setup & Installation

This assumes FastAPI and Streamlit run side by side — e.g. in a GitHub Codespace or two terminal tabs locally.

1. Clone the repo and install dependencies:
   ```bash
   git clone https://github.com/ZareenAnsari/AQI_Project_10Pearls
   cd AQI_Project_10Pearls
   pip install -r requirements.txt
   ```

2. Add your Hopsworks API key to a `.env` file (make sure this file is in `.gitignore` and never committed):
   ```

3. Start the backend:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

4. In a separate terminal, start the frontend:
   ```bash
   streamlit run streamlit_app.py
   ```

5. Open the URL Streamlit prints (usually `http://localhost:8501`).

## API Reference

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Reports API status and whether the model loaded successfully |
| `/forecast?days=3` | GET | Returns a multi-day AQI forecast |
| `/predict` | POST | Accepts a JSON payload of features and returns a single AQI prediction |

Example `/predict` payload:
```json
{
  "pm10": 45.0,
  "pm25": 30.0,
  "co": 0.5,
  "no2": 20.0,
  "so2": 5.0,
  "o3": 30.0,
  "aerosol_optical_depth": 0.3,
  "dust": 0.2,
  "uv_index": 5.0,
  "aqi": 70.0,
  "european_aqi": 70.0,
  "hour": 12,
  "day": 11,
  "month": 8,
  "weekday": 2,
  "aqi_change_rate": 0.0,
  "aqi_lag_1": 70.0,
  "aqi_lag_7": 65.0,
  "temperature": 32.0,
  "humidity": 50.0,
  "wind_speed": 10.0,
  "rain": 0.0
}
```

## Results & Evaluation

| Metric | Value |
|---|---|
| Mean Absolute Error (MAE) | 17.299552 |
| Root Mean Squared Error (RMSE) | 24.177871 |
| R² Score | 0.340159 |


## Screenshots

[Add screenshots of the Forecast tab and What-If tab here. On GitHub you can drag-and-drop images directly into the README editor, or reference them like:]

```markdown
![Forecast tab](docs/screenshots/forecast.png)
![What-If simulator](docs/screenshots/whatif.png)
```

## Limitations

- The forecast depends on how fresh the feature store data is — if the upstream data source lags, forecasts can be stale.
- Currently trained/tuned for Karachi specifically; feature ranges (e.g. dust, aerosol optical depth).
- No authentication on the FastAPI endpoints fine for a local/demo setup, not production-ready as-is.

## Implemented

- Automate retraining on a schedule instead of manually re-running the pipeline.
- Compare Random Forest against gradient-boosted models (XGBoost/LightGBM).
- Cache forecast results so repeated refreshes don't always hit the feature store.
- Extend the forecast horizon beyond 3 days and validate accuracy at longer horizons.


## Author

Zareen Ansari — [zareenansari918@gmail.com / (https://www.linkedin.com/in/zareenansari/)]

##  Complete System Architecture

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
