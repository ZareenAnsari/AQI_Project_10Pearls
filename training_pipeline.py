import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)

import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

FEATURE_FILE = "karachi_aqi_final_features.csv"

MODEL_DIR = "models"

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "karachi_aqi_model.pkl"
)


# ============================================================
# 1. CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# 2. LOAD FEATURE DATA
# ============================================================

print("Loading feature data...")

df = pd.read_csv(
    FEATURE_FILE
)

print(f"Loaded {len(df)} rows")


# ============================================================
# 3. CONVERT DATE
# ============================================================

df["date"] = pd.to_datetime(
    df["date"]
)


# ============================================================
# 4. REMOVE MISSING VALUES
# ============================================================

df = df.dropna().reset_index(drop=True)


# ============================================================
# 5. SELECT FEATURES
# ============================================================

FEATURES = [
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
# 6. CREATE X AND y
# ============================================================

X = df[FEATURES]

y = df["target_aqi"]


print("\nFeature shape:")
print(X.shape)

print("\nTarget shape:")
print(y.shape)


# ============================================================
# 7. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ============================================================
# 8. TRAIN RANDOM FOREST
# ============================================================

print("\nTraining Random Forest...")

rf_model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

rf_model.fit(
    X_train,
    y_train
)


# ============================================================
# 9. PREDICTION
# ============================================================

predictions = rf_model.predict(
    X_test
)


# ============================================================
# 10. EVALUATION
# ============================================================

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

mae = mean_absolute_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)


print("\n================================")
print("MODEL RESULTS")
print("================================")

print(f"RMSE: {rmse:.4f}")
print(f"MAE : {mae:.4f}")
print(f"R²  : {r2:.4f}")


# ============================================================
# 11. SAVE MODEL
# ============================================================

joblib.dump(
    rf_model,
    MODEL_FILE
)


print("\n================================")
print("TRAINING COMPLETED")
print("================================")

print(f"Model saved to: {MODEL_FILE}")