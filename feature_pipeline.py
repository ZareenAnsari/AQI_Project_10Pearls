import os
import requests
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/air_quality_historical.csv"
OUTPUT_FILE = "karachi_aqi_final_features.csv"

LATITUDE = 24.8607
LONGITUDE = 67.0011


# ============================================================
# 1. LOAD AQI DATA
# ============================================================

print("Loading AQI data...")

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df)} rows")


# ============================================================
# 2. RENAME COLUMNS
# ============================================================

df = df.rename(columns={
    "us_aqi": "aqi",
    "pm2_5": "pm25",
    "carbon_monoxide": "co",
    "nitrogen_dioxide": "no2",
    "sulphur_dioxide": "so2",
    "ozone": "o3"
})


# ============================================================
# 3. CONVERT DATE
# ============================================================

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values("date").reset_index(drop=True)


# ============================================================
# 4. TIME FEATURES
# ============================================================

df["hour"] = df["date"].dt.hour
df["day"] = df["date"].dt.day
df["month"] = df["date"].dt.month
df["weekday"] = df["date"].dt.weekday


# ============================================================
# 5. AQI CHANGE RATE
# ============================================================

df["aqi_change_rate"] = df["aqi"].diff()


# ============================================================
# 6. AQI LAG FEATURES
# ============================================================

df["aqi_lag_1"] = df["aqi"].shift(1)

df["aqi_lag_7"] = df["aqi"].shift(7)


# ============================================================
# 7. TARGET AQI
# ============================================================

# Predict AQI 3 time steps ahead

df["target_aqi"] = df["aqi"].shift(-3)


# ============================================================
# 8. REMOVE INITIAL MISSING VALUES
# ============================================================

df = df.dropna().reset_index(drop=True)


# ============================================================
# 9. GET WEATHER DATA
# ============================================================

start_date = df["date"].min().strftime("%Y-%m-%d")
end_date = df["date"].max().strftime("%Y-%m-%d")

print("Fetching weather data...")

url = (
    "https://archive-api.open-meteo.com/v1/archive?"
    f"latitude={LATITUDE}"
    f"&longitude={LONGITUDE}"
    f"&start_date={start_date}"
    f"&end_date={end_date}"
    "&daily="
    "temperature_2m_mean,"
    "relative_humidity_2m_mean,"
    "wind_speed_10m_max,"
    "precipitation_sum"
    "&timezone=Asia/Karachi"
)

response = requests.get(url, timeout=60)

response.raise_for_status()

weather_data = response.json()


# ============================================================
# 10. CREATE WEATHER DATAFRAME
# ============================================================

weather_df = pd.DataFrame({

    "date": weather_data["daily"]["time"],

    "temperature":
        weather_data["daily"]["temperature_2m_mean"],

    "humidity":
        weather_data["daily"]["relative_humidity_2m_mean"],

    "wind_speed":
        weather_data["daily"]["wind_speed_10m_max"],

    "rain":
        weather_data["daily"]["precipitation_sum"]
})

weather_df["date"] = pd.to_datetime(weather_df["date"])


# ============================================================
# 11. MERGE AQI + WEATHER
# ============================================================

merged_df = pd.merge(
    df,
    weather_df,
    on="date",
    how="inner"
)


# ============================================================
# 12. REMOVE MISSING VALUES
# ============================================================

merged_df = merged_df.dropna().reset_index(drop=True)


# ============================================================
# 13. SAVE FINAL FEATURES
# ============================================================

merged_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 14. INFORMATION
# ============================================================

print("\nFeature pipeline completed successfully.")

print(f"Output file: {OUTPUT_FILE}")

print(f"Rows: {len(merged_df)}")

print("\nColumns:")
print(merged_df.columns.tolist())

print("\nShape:")
print(merged_df.shape)