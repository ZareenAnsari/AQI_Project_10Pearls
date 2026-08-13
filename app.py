import os
import glob
import pickle
import joblib
import requests
import pandas as pd
from datetime import datetime, timedelta

import hopsworks
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

HOPSWORKS_API_KEY = os.getenv("HOPSWORKS_API_KEY")
HOPSWORKS_PROJECT = os.getenv("HOPSWORKS_PROJECT")

if not HOPSWORKS_API_KEY:
    raise RuntimeError("HOPSWORKS_API_KEY is not set in .env")

if not HOPSWORKS_PROJECT:
    raise RuntimeError("HOPSWORKS_PROJECT is not set in .env")

# Karachi coordinates - used for live forecast calls.
# Move these to .env too if you want the app to be city-agnostic later.
CITY_LAT = float(os.getenv("CITY_LAT", "24.8607"))
CITY_LON = float(os.getenv("CITY_LON", "67.0011"))


# ============================================================
# 2. FASTAPI APP
# ============================================================

app = FastAPI(
    title="Karachi AQI Prediction API",
    description="AQI prediction API using a model registered in Hopsworks",
    version="1.1.0"
)


# ============================================================
# 3. AQI INPUT MODEL (manual "what-if" prediction)
# ============================================================

class AQIInput(BaseModel):

    pm10: float
    pm25: float
    co: float
    no2: float
    so2: float
    o3: float

    aerosol_optical_depth: float
    dust: float
    uv_index: float

    aqi: float
    european_aqi: float

    hour: int
    day: int
    month: int
    weekday: int

    aqi_change_rate: float
    aqi_lag_1: float
    aqi_lag_7: float

    temperature: float
    humidity: float
    wind_speed: float
    rain: float


# ============================================================
# 4. FEATURE ORDER (must match training exactly)
# ============================================================

FEATURE_ORDER = [
    "pm10",
    "pm25",
    "co",
    "no2",
    "so2",
    "o3",
    "aerosol_optical_depth",
    "dust",
    "uv_index",
    "aqi",
    "european_aqi",
    "hour",
    "day",
    "month",
    "weekday",
    "aqi_change_rate",
    "aqi_lag_1",
    "aqi_lag_7",
    "temperature",
    "humidity",
    "wind_speed",
    "rain"
]


# ============================================================
# 5. GLOBAL STATE
# ============================================================

model = None
model_name = "aqi_random_forest"
model_version = 1

hopsworks_project = None
feature_store = None


# ============================================================
# 6. LOAD MODEL FROM HOPSWORKS
# ============================================================

def load_model_from_hopsworks():

    global model, hopsworks_project, feature_store

    print("Connecting to Hopsworks...")

    hopsworks_project = hopsworks.login(
        api_key_value=HOPSWORKS_API_KEY,
        project=HOPSWORKS_PROJECT
    )

    print(f"Connected to Hopsworks project: {hopsworks_project.name}")

    feature_store = hopsworks_project.get_feature_store()

    mr = hopsworks_project.get_model_registry()

    print(f"Looking for model: {model_name} (version {model_version})")

    registered_model = mr.get_model(
        name=model_name,
        version=model_version
    )

    model_directory = registered_model.download()

    print(f"Model downloaded to: {model_directory}")

    model_files = []
    for extension in ["*.pkl", "*.pickle", "*.joblib"]:
        model_files.extend(
            glob.glob(os.path.join(model_directory, "**", extension), recursive=True)
        )

    if not model_files:
        raise FileNotFoundError(
            f"No .pkl, .pickle, or .joblib model file found in: {model_directory}"
        )

    model_file = model_files[0]
    print(f"Loading model file: {model_file}")

    try:
        model = joblib.load(model_file)
    except Exception:
        with open(model_file, "rb") as f:
            model = pickle.load(f)

    print("AQI model loaded successfully!")
    print(f"Model type: {type(model)}")

    return model


try:
    load_model_from_hopsworks()
except Exception as e:
    print("ERROR: Could not load AQI model.")
    print(str(e))
    model = None


# ============================================================
# 7. HELPER — get recent AQI history from the Feature Store
#    (used to seed aqi_lag_1 / aqi_lag_7 / aqi_change_rate)
# ============================================================

def get_recent_aqi_history(n_days: int = 8) -> pd.DataFrame:
    """
    Reads the most recent rows from the Hopsworks feature group so we
    have real (not guessed) values to build lag features from.
    """

    if feature_store is None:
        raise RuntimeError("Feature store is not connected.")

    feature_group = feature_store.get_feature_group(
        name="karachi_aqi_features",
        version=1
    )

    df = feature_group.read()

    if "date" not in df.columns:
        raise RuntimeError("Feature group is missing a 'date' column.")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    return df.tail(n_days).reset_index(drop=True)


# ============================================================
# 8. HELPER — fetch live 3-day forecast (pollutants + weather)
#    from Open-Meteo's FORECAST endpoints (not the archive ones
#    used for backfill). These give real, externally-sourced
#    future values instead of guessing them.
# ============================================================

def get_forecast_inputs(days: int = 3) -> pd.DataFrame:

    # --- Air quality forecast ---
    # NOTE: the air-quality API only supports &hourly=, there is no &daily=
    # option on this endpoint (unlike the general weather forecast API).
    # We request hourly values and aggregate to daily means ourselves.
    aq_url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={CITY_LAT}&longitude={CITY_LON}"
        "&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,"
        "sulphur_dioxide,ozone,aerosol_optical_depth,dust,"
        "uv_index,european_aqi,us_aqi"
        "&timezone=Asia/Karachi"
        f"&forecast_days={days}"
    )

    aq_resp = requests.get(aq_url, timeout=30)
    aq_resp.raise_for_status()
    aq_json = aq_resp.json()["hourly"]

    aq_hourly_df = pd.DataFrame({
        "datetime": pd.to_datetime(aq_json["time"]),
        "pm10": aq_json["pm10"],
        "pm25": aq_json["pm2_5"],
        "co": aq_json["carbon_monoxide"],
        "no2": aq_json["nitrogen_dioxide"],
        "so2": aq_json["sulphur_dioxide"],
        "o3": aq_json["ozone"],
        "aerosol_optical_depth": aq_json["aerosol_optical_depth"],
        "dust": aq_json["dust"],
        "uv_index": aq_json["uv_index"],
        "european_aqi": aq_json["european_aqi"],
        "aqi": aq_json["us_aqi"],
    })

    aq_hourly_df["date"] = aq_hourly_df["datetime"].dt.date
    aq_daily_df = aq_hourly_df.groupby("date").mean(numeric_only=True).reset_index()
    aq_daily_df["date"] = pd.to_datetime(aq_daily_df["date"])
    aq_daily_df = aq_daily_df.sort_values("date").head(days).reset_index(drop=True)

    # --- Weather forecast (this endpoint DOES support &daily=) ---
    weather_url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={CITY_LAT}&longitude={CITY_LON}"
        "&daily=temperature_2m_mean,relative_humidity_2m_mean,"
        "wind_speed_10m_max,precipitation_sum"
        "&timezone=Asia/Karachi"
        f"&forecast_days={days}"
    )

    weather_resp = requests.get(weather_url, timeout=30)
    weather_resp.raise_for_status()
    weather_data = weather_resp.json()["daily"]

    weather_df = pd.DataFrame({
        "date": pd.to_datetime(weather_data["time"]),
        "temperature": weather_data["temperature_2m_mean"],
        "humidity": weather_data["relative_humidity_2m_mean"],
        "wind_speed": weather_data["wind_speed_10m_max"],
        "rain": weather_data["precipitation_sum"],
    })

    forecast_df = pd.merge(aq_daily_df, weather_df, on="date", how="inner")

    forecast_df["hour"] = 12  # daily-resolution data; midday placeholder
    forecast_df["day"] = forecast_df["date"].dt.day
    forecast_df["month"] = forecast_df["date"].dt.month
    forecast_df["weekday"] = forecast_df["date"].dt.weekday

    return forecast_df


# ============================================================
# 9. HELPER — build one prediction row and run the model
# ============================================================

def predict_row(feature_dict: dict) -> float:

    missing = [f for f in FEATURE_ORDER if f not in feature_dict]
    if missing:
        raise HTTPException(
            status_code=500,
            detail={"message": "Missing engineered features", "missing_features": missing}
        )

    X = pd.DataFrame([[feature_dict[f] for f in FEATURE_ORDER]], columns=FEATURE_ORDER)

    if X.shape[1] != len(FEATURE_ORDER):
        raise HTTPException(
            status_code=500,
            detail=f"Expected {len(FEATURE_ORDER)} features, got {X.shape[1]}."
        )

    prediction = model.predict(X)
    return float(prediction[0])


# ============================================================
# 10. HOME / HEALTH
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Karachi AQI Prediction API is running",
        "model": model_name,
        "version": model_version,
        "model_loaded": model is not None
    }


@app.get("/health")
def health():
    if model is None:
        return {"status": "unhealthy", "model_loaded": False}
    return {
        "status": "healthy",
        "model_loaded": True,
        "model": model_name,
        "version": model_version
    }


# ============================================================
# 11. MANUAL "WHAT-IF" PREDICTION (unchanged behavior)
# ============================================================

@app.post("/predict")
def predict_aqi(input_data: AQIInput):

    try:
        if model is None:
            raise HTTPException(status_code=503, detail="AQI model is not loaded from Hopsworks.")

        try:
            data = input_data.model_dump()
        except AttributeError:
            data = input_data.dict()

        predicted_aqi = predict_row(data)

        return {
            "predicted_aqi": predicted_aqi,
            "model": model_name,
            "version": model_version
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Prediction error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 12. AUTOMATIC 3-DAY FORECAST
#     Loads real forecasted pollutant/weather inputs (Open-Meteo)
#     + real recent AQI history (Hopsworks Feature Store), and
#     recursively builds lag features so no user input is needed.
# ============================================================

@app.get("/forecast")
def forecast_aqi(days: int = 3):

    try:
        if model is None:
            raise HTTPException(status_code=503, detail="AQI model is not loaded from Hopsworks.")

        if days < 1 or days > 5:
            raise HTTPException(status_code=400, detail="days must be between 1 and 5.")

        # --- seed lag features from real history in the feature store ---
        history_df = get_recent_aqi_history(n_days=8)

        if history_df.empty:
            raise HTTPException(status_code=503, detail="No historical data available in feature store.")

        recent_aqi_values = history_df["aqi"].tolist()  # oldest -> newest

        # --- pull real forecasted inputs for the next N days ---
        forecast_df = get_forecast_inputs(days=days)

        results = []

        for _, row in forecast_df.iterrows():

            last_aqi = recent_aqi_values[-1]
            lag_1 = recent_aqi_values[-1]
            lag_7 = recent_aqi_values[-7] if len(recent_aqi_values) >= 7 else recent_aqi_values[0]
            change_rate = recent_aqi_values[-1] - recent_aqi_values[-2] if len(recent_aqi_values) >= 2 else 0.0

            feature_dict = {
                "pm10": row["pm10"],
                "pm25": row["pm25"],
                "co": row["co"],
                "no2": row["no2"],
                "so2": row["so2"],
                "o3": row["o3"],
                "aerosol_optical_depth": row["aerosol_optical_depth"],
                "dust": row["dust"],
                "uv_index": row["uv_index"],
                "aqi": last_aqi,
                "european_aqi": row["european_aqi"],
                "hour": row["hour"],
                "day": row["day"],
                "month": row["month"],
                "weekday": row["weekday"],
                "aqi_change_rate": change_rate,
                "aqi_lag_1": lag_1,
                "aqi_lag_7": lag_7,
                "temperature": row["temperature"],
                "humidity": row["humidity"],
                "wind_speed": row["wind_speed"],
                "rain": row["rain"],
            }

            predicted_aqi = predict_row(feature_dict)

            results.append({
                "date": row["date"].strftime("%Y-%m-%d"),
                "predicted_aqi": round(predicted_aqi, 2)
            })

            # feed this prediction back in as history for the next day's lags
            recent_aqi_values.append(predicted_aqi)

        return {
            "model": model_name,
            "version": model_version,
            "forecast": results
        }

    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Forecast data source error: {str(e)}")
    except Exception as e:
        print("Forecast error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))