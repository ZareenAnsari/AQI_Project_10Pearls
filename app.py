import os
import glob
import pickle
import joblib
import pandas as pd
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


# ============================================================
# 2. FASTAPI APP
# ============================================================

app = FastAPI(
    title="Karachi AQI Prediction API",
    description="AQI prediction API using Random Forest model registered in Hopsworks",
    version="1.0.0"
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
# 5. GLOBAL MODEL VARIABLES
# ============================================================

model = None
model_name = "aqi_random_forest"
model_version = 1


# ============================================================
# 6. LOAD MODEL FROM HOPSWORKS
# ============================================================

def load_model_from_hopsworks():

    global model

    print("Connecting to Hopsworks...")

    project = hopsworks.login(
        api_key_value=HOPSWORKS_API_KEY,
        project=HOPSWORKS_PROJECT
    )

    print(f"Connected to Hopsworks project: {project.name}")

    # Get Model Registry
    mr = project.get_model_registry()

    print(f"Looking for model: {model_name}")
    print(f"Version: {model_version}")

    # Get registered model
    registered_model = mr.get_model(
        name=model_name,
        version=model_version
    )

    print(f"Model found: {registered_model.name}")
    print(f"Model version: {registered_model.version}")

    # Download model artifacts
    model_directory = registered_model.download()

    print(f"Model downloaded to: {model_directory}")

    # --------------------------------------------------------
    # Find model files
    # --------------------------------------------------------

    model_files = []

    extensions = [
        "*.pkl",
        "*.pickle",
        "*.joblib"
    ]

    for extension in extensions:
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
            f"No .pkl, .pickle, or .joblib model file found in: "
            f"{model_directory}"
        )

    print("Model files found:")

    for file in model_files:
        print(f" - {file}")

    # --------------------------------------------------------
    # Load first model file
    # --------------------------------------------------------

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


# ============================================================
# 7. LOAD MODEL WHEN APPLICATION STARTS
# ============================================================

try:

    load_model_from_hopsworks()

except Exception as e:

    print("ERROR: Could not load AQI model.")
    print(str(e))

    # Keep API running so the error can be seen through endpoints.
    model = None


# ============================================================
# 8. HOME ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Karachi AQI Prediction API is running",
        "model": model_name,
        "version": model_version,
        "model_loaded": model is not None
    }


# ============================================================
# 9. HEALTH CHECK
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
        "model": model_name,
        "version": model_version
    }


# ============================================================
# 10. AQI PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
def predict_aqi(input_data: AQIInput):

    try:

        # ----------------------------------------------------
        # Check model
        # ----------------------------------------------------

        if model is None:

            raise HTTPException(
                status_code=503,
                detail="AQI model is not loaded from Hopsworks."
            )

        # ----------------------------------------------------
        # Convert Pydantic object to dictionary
        # ----------------------------------------------------

        try:

            data = input_data.model_dump()

        except AttributeError:

            # Compatibility with Pydantic v1
            data = input_data.dict()

        # ----------------------------------------------------
        # Check all required features
        # ----------------------------------------------------

        missing_features = [
            feature
            for feature in FEATURE_ORDER
            if feature not in data
        ]

        if missing_features:

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Missing input features",
                    "missing_features": missing_features
                }
            )

        # ----------------------------------------------------
        # Create DataFrame
        # ----------------------------------------------------

        X = pd.DataFrame(
            [
                [
                    data[feature]
                    for feature in FEATURE_ORDER
                ]
            ],
            columns=FEATURE_ORDER
        )

        # ----------------------------------------------------
        # Verify number of features
        # ----------------------------------------------------

        if X.shape[1] != 22:

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Expected 22 features, "
                    f"but received {X.shape[1]}."
                )
            )

        print("Input features:")
        print(X)

        # ----------------------------------------------------
        # Make prediction
        # ----------------------------------------------------

        prediction = model.predict(X)

        predicted_aqi = float(prediction[0])

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return {
            "predicted_aqi": predicted_aqi,
            "model": model_name,
            "version": model_version
        }

    except HTTPException:
        raise

    except Exception as e:

        print("Prediction error:")
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )