import os
import glob
import pickle
import joblib
import requests
import pandas as pd

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import hopsworks


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


# Karachi coordinates
CITY_LAT = float(os.getenv("CITY_LAT", "24.8607"))
CITY_LON = float(os.getenv("CITY_LON", "67.0011"))


# ============================================================
# 2. FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Karachi AQI Prediction API",
    description="AQI prediction API using Random Forest and Hopsworks",
    version="1.1.0"
)


# ============================================================
# 3. AQI INPUT MODEL
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
# 4. FEATURE ORDER
# IMPORTANT:
# This MUST exactly match the training pipeline.
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

MODEL_NAME = "aqi_random_forest"
MODEL_VERSION = 1

hopsworks_project = None
feature_store = None


# ============================================================
# 6. LOAD MODEL FROM HOPSWORKS
# ============================================================

def load_model_from_hopsworks():

    global model
    global hopsworks_project
    global feature_store

    print("=" * 60)
    print("Connecting to Hopsworks...")
    print("=" * 60)

    hopsworks_project = hopsworks.login(
        api_key_value=HOPSWORKS_API_KEY,
        project=HOPSWORKS_PROJECT
    )

    print(
        f"Connected to Hopsworks project: "
        f"{hopsworks_project.name}"
    )

    feature_store = hopsworks_project.get_feature_store()

    model_registry = hopsworks_project.get_model_registry()

    print(
        f"Looking for model: "
        f"{MODEL_NAME}, version {MODEL_VERSION}"
    )

    registered_model = model_registry.get_model(
        name=MODEL_NAME,
        version=MODEL_VERSION
    )

    model_directory = registered_model.download()

    print(
        f"Model downloaded to: "
        f"{model_directory}"
    )

    model_files = []

    for extension in [
        "*.pkl",
        "*.pickle",
        "*.joblib"
    ]:

        model_files.extend(
            glob.glob(
                os.path.join(
                    model_directory,
                    "**",
                    extension
                ),
                recursive=True
            )
        )

    if not model_files:

        raise FileNotFoundError(
            "No model file found in "
            f"{model_directory}"
        )

    model_file = model_files[0]

    print(
        f"Loading model file: "
        f"{model_file}"
    )

    try:

        model = joblib.load(model_file)

    except Exception:

        with open(model_file, "rb") as file:

            model = pickle.load(file)

    print("AQI model loaded successfully.")
    print(
        f"Model type: {type(model)}"
    )

    return model


# ============================================================
# LOAD MODEL
# ============================================================

try:

    load_model_from_hopsworks()

except Exception as e:

    print("=" * 60)
    print("ERROR: Could not load AQI model.")
    print(str(e))
    print("=" * 60)

    model = None


# ============================================================
# 7. GET RECENT AQI HISTORY
# ============================================================

def get_recent_aqi_history(
    n_days: int = 8
) -> pd.DataFrame:

    if feature_store is None:

        raise RuntimeError(
            "Feature store is not connected."
        )

    feature_group = feature_store.get_feature_group(
        name="karachi_aqi_features",
        version=1
    )

    df = feature_group.read()

    if df.empty:

        raise RuntimeError(
            "Feature group contains no data."
        )

    if "date" not in df.columns:

        raise RuntimeError(
            "Feature group is missing 'date' column."
        )

    if "aqi" not in df.columns:

        raise RuntimeError(
            "Feature group is missing 'aqi' column."
        )

    df["date"] = pd.to_datetime(
        df["date"]
    )

    df = (
        df
        .sort_values("date")
        .reset_index(drop=True)
    )

    return df.tail(
        n_days
    ).reset_index(drop=True)


# ============================================================
# 8. GET OPEN-METEO FORECAST
# ============================================================

def get_forecast_inputs(
    days: int = 3
) -> pd.DataFrame:

    # --------------------------------------------------------
    # AIR QUALITY FORECAST
    # --------------------------------------------------------

    air_quality_url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={CITY_LAT}"
        f"&longitude={CITY_LON}"
        "&hourly="
        "pm10,"
        "pm2_5,"
        "carbon_monoxide,"
        "nitrogen_dioxide,"
        "sulphur_dioxide,"
        "ozone,"
        "aerosol_optical_depth,"
        "dust,"
        "uv_index,"
        "european_aqi,"
        "us_aqi"
        "&timezone=Asia/Karachi"
        f"&forecast_days={days}"
    )

    air_response = requests.get(
        air_quality_url,
        timeout=30
    )

    air_response.raise_for_status()

    air_json = air_response.json()

    if "hourly" not in air_json:

        raise RuntimeError(
            "Invalid response from Open-Meteo air-quality API."
        )

    hourly = air_json["hourly"]

    air_df = pd.DataFrame({

        "datetime": pd.to_datetime(
            hourly["time"]
        ),

        "pm10": hourly["pm10"],

        "pm25": hourly["pm2_5"],

        "co": hourly["carbon_monoxide"],

        "no2": hourly["nitrogen_dioxide"],

        "so2": hourly["sulphur_dioxide"],

        "o3": hourly["ozone"],

        "aerosol_optical_depth":
            hourly["aerosol_optical_depth"],

        "dust": hourly["dust"],

        "uv_index": hourly["uv_index"],

        "european_aqi":
            hourly["european_aqi"],

        "aqi": hourly["us_aqi"]
    })

    air_df["date"] = (
        air_df["datetime"]
        .dt.date
    )

    air_daily_df = (
        air_df
        .groupby("date")
        .mean(numeric_only=True)
        .reset_index()
    )

    air_daily_df["date"] = pd.to_datetime(
        air_daily_df["date"]
    )

    air_daily_df = (
        air_daily_df
        .sort_values("date")
        .head(days)
        .reset_index(drop=True)
    )


    # --------------------------------------------------------
    # WEATHER FORECAST
    # --------------------------------------------------------

    weather_url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={CITY_LAT}"
        f"&longitude={CITY_LON}"
        "&daily="
        "temperature_2m_mean,"
        "relative_humidity_2m_mean,"
        "wind_speed_10m_max,"
        "precipitation_sum"
        "&timezone=Asia/Karachi"
        f"&forecast_days={days}"
    )

    weather_response = requests.get(
        weather_url,
        timeout=30
    )

    weather_response.raise_for_status()

    weather_json = weather_response.json()

    if "daily" not in weather_json:

        raise RuntimeError(
            "Invalid response from Open-Meteo weather API."
        )

    daily = weather_json["daily"]

    weather_df = pd.DataFrame({

        "date": pd.to_datetime(
            daily["time"]
        ),

        "temperature":
            daily["temperature_2m_mean"],

        "humidity":
            daily["relative_humidity_2m_mean"],

        "wind_speed":
            daily["wind_speed_10m_max"],

        "rain":
            daily["precipitation_sum"]
    })


    # --------------------------------------------------------
    # MERGE AIR + WEATHER
    # --------------------------------------------------------

    forecast_df = pd.merge(
        air_daily_df,
        weather_df,
        on="date",
        how="inner"
    )

    if forecast_df.empty:

        raise RuntimeError(
            "Could not merge air-quality and weather forecasts."
        )

    # Daily-resolution prediction
    forecast_df["hour"] = 12

    forecast_df["day"] = (
        forecast_df["date"].dt.day
    )

    forecast_df["month"] = (
        forecast_df["date"].dt.month
    )

    forecast_df["weekday"] = (
        forecast_df["date"].dt.weekday
    )

    return forecast_df


# ============================================================
# 9. RUN MODEL PREDICTION
# ============================================================

def predict_row(
    feature_dict: dict
) -> float:

    if model is None:

        raise HTTPException(
            status_code=503,
            detail="AQI model is not loaded."
        )

    missing_features = [
        feature
        for feature in FEATURE_ORDER
        if feature not in feature_dict
    ]

    if missing_features:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Missing engineered features.",
                "missing_features": missing_features
            }
        )

    X = pd.DataFrame(
        [
            [
                feature_dict[feature]
                for feature in FEATURE_ORDER
            ]
        ],
        columns=FEATURE_ORDER
    )

    # Ensure numeric values
    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    if X.isnull().any().any():

        raise HTTPException(
            status_code=400,
            detail="One or more input features are invalid."
        )

    prediction = model.predict(X)

    return float(
        prediction[0]
    )


# ============================================================
# 10. HOME
# ============================================================

@app.get("/")
def home():

    return {

        "message":
            "Karachi AQI Prediction API is running",

        "model":
            MODEL_NAME,

        "version":
            MODEL_VERSION,

        "model_loaded":
            model is not None
    }


# ============================================================
# 11. HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    if model is None:

        return {
            "status": "unhealthy",
            "model_loaded": False
        }

    return {

        "status": "healthy",

        "model_loaded": True,

        "model":
            MODEL_NAME,

        "version":
            MODEL_VERSION
    }


# ============================================================
# 12. MANUAL PREDICTION
# ============================================================

@app.post("/predict")
def predict_aqi(
    input_data: AQIInput
):

    if model is None:

        raise HTTPException(
            status_code=503,
            detail="AQI model is not loaded from Hopsworks."
        )

    try:

        try:
            data = input_data.model_dump()

        except AttributeError:
            data = input_data.dict()

        predicted_aqi = predict_row(
            data
        )

        return {

            "predicted_aqi":
                round(predicted_aqi, 2),

            "model":
                MODEL_NAME,

            "version":
                MODEL_VERSION
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            "Prediction error:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# 13. AUTOMATIC FORECAST
# ============================================================

@app.get("/forecast")
def forecast_aqi(
    days: int = 3
):

    if model is None:

        raise HTTPException(
            status_code=503,
            detail="AQI model is not loaded from Hopsworks."
        )

    if days < 1 or days > 5:

        raise HTTPException(
            status_code=400,
            detail="days must be between 1 and 5."
        )

    try:

        # ----------------------------------------------------
        # GET REAL AQI HISTORY
        # ----------------------------------------------------

        history_df = get_recent_aqi_history(
            n_days=8
        )

        if history_df.empty:

            raise HTTPException(
                status_code=503,
                detail="No historical AQI data available."
            )

        recent_aqi_values = (
            history_df["aqi"]
            .astype(float)
            .tolist()
        )


        # ----------------------------------------------------
        # GET FUTURE ENVIRONMENTAL CONDITIONS
        # ----------------------------------------------------

        forecast_df = get_forecast_inputs(
            days=days
        )

        if forecast_df.empty:

            raise HTTPException(
                status_code=503,
                detail="No forecast data available."
            )


        # ----------------------------------------------------
        # GENERATE FORECAST
        # ----------------------------------------------------

        results = []

        for _, row in forecast_df.iterrows():

            # Previous AQI
            lag_1 = recent_aqi_values[-1]

            # AQI seven observations back
            if len(recent_aqi_values) >= 7:

                lag_7 = recent_aqi_values[-7]

            else:

                lag_7 = recent_aqi_values[0]


            # AQI change
            if len(recent_aqi_values) >= 2:

                change_rate = (
                    recent_aqi_values[-1]
                    -
                    recent_aqi_values[-2]
                )

            else:

                change_rate = 0.0


            feature_dict = {

                "pm10":
                    row["pm10"],

                "pm25":
                    row["pm25"],

                "co":
                    row["co"],

                "no2":
                    row["no2"],

                "so2":
                    row["so2"],

                "o3":
                    row["o3"],

                "aerosol_optical_depth":
                    row["aerosol_optical_depth"],

                "dust":
                    row["dust"],

                "uv_index":
                    row["uv_index"],

                "aqi":
                    lag_1,

                "european_aqi":
                    row["european_aqi"],

                "hour":
                    int(row["hour"]),

                "day":
                    int(row["day"]),

                "month":
                    int(row["month"]),

                "weekday":
                    int(row["weekday"]),

                "aqi_change_rate":
                    change_rate,

                "aqi_lag_1":
                    lag_1,

                "aqi_lag_7":
                    lag_7,

                "temperature":
                    row["temperature"],

                "humidity":
                    row["humidity"],

                "wind_speed":
                    row["wind_speed"],

                "rain":
                    row["rain"]
            }


            predicted_aqi = predict_row(
                feature_dict
            )


            results.append({

                "date":
                    row["date"].strftime(
                        "%Y-%m-%d"
                    ),

                "predicted_aqi":
                    round(
                        predicted_aqi,
                        2
                    )
            })


            # Recursive forecasting:
            # today's prediction becomes
            # tomorrow's historical AQI

            recent_aqi_values.append(
                predicted_aqi
            )


        return {

            "model":
                MODEL_NAME,

            "version":
                MODEL_VERSION,

            "forecast":
                results
        }


    except HTTPException:

        raise

    except requests.exceptions.RequestException as e:

        raise HTTPException(
            status_code=502,
            detail=(
                "Forecast data source error: "
                f"{str(e)}"
            )
        )

    except Exception as e:

        print(
            "Forecast error:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )