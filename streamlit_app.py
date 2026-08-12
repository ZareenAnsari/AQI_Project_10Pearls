import streamlit as st
import requests


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AQI Prediction System",
    page_icon="🌍",
    layout="wide"
)


# ============================================================
# FASTAPI URL
# ============================================================

# Your deployed FastAPI prediction endpoint
API_URL = "http://127.0.0.1:8000/predict"


# ============================================================
# HELPER FUNCTION - AQI CATEGORY
# ============================================================

def get_aqi_category(aqi):
    """
    Return AQI category based on predicted AQI.
    """

    if aqi <= 50:
        return "Good"

    elif aqi <= 100:
        return "Moderate"

    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"

    elif aqi <= 200:
        return "Unhealthy"

    elif aqi <= 300:
        return "Very Unhealthy"

    else:
        return "Hazardous"


# ============================================================
# TITLE
# ============================================================

st.title("🌍 Air Quality Index Prediction System")

st.write(
    "Enter the required environmental and AQI-related values "
    "to predict the Air Quality Index using the Random Forest model."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ System Information")

    st.write("**Prediction Model:** Random Forest")

    st.write("**Backend:** FastAPI")

    st.write("**Model Registry:** Hopsworks")

    st.write("**Frontend:** Streamlit")

    st.divider()

    st.caption(
        "The prediction request is sent to the deployed "
        "FastAPI `/predict` endpoint."
    )


# ============================================================
# INPUT FORM
# ============================================================

with st.form("aqi_prediction_form"):

    st.subheader("🌫️ Air Quality Features")

    col1, col2, col3 = st.columns(3)

    # ========================================================
    # COLUMN 1
    # ========================================================

    with col1:

        pm10 = st.number_input(
            "PM10",
            value=45.0,
            min_value=0.0
        )

        pm25 = st.number_input(
            "PM2.5",
            value=30.0,
            min_value=0.0
        )

        co = st.number_input(
            "CO",
            value=0.5,
            min_value=0.0
        )

        no2 = st.number_input(
            "NO2",
            value=20.0,
            min_value=0.0
        )

        so2 = st.number_input(
            "SO2",
            value=5.0,
            min_value=0.0
        )

        o3 = st.number_input(
            "O3",
            value=30.0,
            min_value=0.0
        )

        aerosol_optical_depth = st.number_input(
            "Aerosol Optical Depth",
            value=0.3,
            min_value=0.0
        )

        dust = st.number_input(
            "Dust",
            value=0.2,
            min_value=0.0
        )


    # ========================================================
    # COLUMN 2
    # ========================================================

    with col2:

        uv_index = st.number_input(
            "UV Index",
            value=5.0,
            min_value=0.0
        )

        aqi = st.number_input(
            "Current AQI",
            value=70.0,
            min_value=0.0
        )

        european_aqi = st.number_input(
            "European AQI",
            value=70.0,
            min_value=0.0
        )

        hour = st.number_input(
            "Hour",
            min_value=0,
            max_value=23,
            value=12,
            step=1
        )

        day = st.number_input(
            "Day",
            min_value=1,
            max_value=31,
            value=11,
            step=1
        )

        month = st.number_input(
            "Month",
            min_value=1,
            max_value=12,
            value=8,
            step=1
        )

        weekday = st.number_input(
            "Weekday",
            min_value=0,
            max_value=6,
            value=2,
            step=1
        )


    # ========================================================
    # COLUMN 3
    # ========================================================

    with col3:

        aqi_change_rate = st.number_input(
            "AQI Change Rate",
            value=0.0
        )

        aqi_lag_1 = st.number_input(
            "AQI Lag 1",
            value=70.0,
            min_value=0.0
        )

        aqi_lag_7 = st.number_input(
            "AQI Lag 7",
            value=65.0,
            min_value=0.0
        )

        temperature = st.number_input(
            "Temperature",
            value=32.0
        )

        humidity = st.number_input(
            "Humidity",
            value=50.0,
            min_value=0.0,
            max_value=100.0
        )

        wind_speed = st.number_input(
            "Wind Speed",
            value=10.0,
            min_value=0.0
        )

        rain = st.number_input(
            "Rain",
            value=0.0,
            min_value=0.0
        )


    # ========================================================
    # SUBMIT BUTTON
    # ========================================================

    st.divider()

    predict_button = st.form_submit_button(
        "🔮 Predict AQI",
        use_container_width=True
    )


# ============================================================
# PREDICTION
# ============================================================

if predict_button:

    # ========================================================
    # CREATE REQUEST PAYLOAD
    # ========================================================

    payload = {
        "pm10": pm10,
        "pm25": pm25,
        "co": co,
        "no2": no2,
        "so2": so2,
        "o3": o3,
        "aerosol_optical_depth": aerosol_optical_depth,
        "dust": dust,
        "uv_index": uv_index,
        "aqi": aqi,
        "european_aqi": european_aqi,
        "hour": hour,
        "day": day,
        "month": month,
        "weekday": weekday,
        "aqi_change_rate": aqi_change_rate,
        "aqi_lag_1": aqi_lag_1,
        "aqi_lag_7": aqi_lag_7,
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "rain": rain
    }


    # ========================================================
    # SEND REQUEST TO FASTAPI
    # ========================================================

    with st.spinner("🔄 Predicting AQI..."):

        try:

            response = requests.post(
                API_URL,
                json=payload,
                timeout=60
            )


            # =================================================
            # SUCCESSFUL RESPONSE
            # =================================================

            if response.status_code == 200:

                result = response.json()

                predicted_aqi = float(
                    result["predicted_aqi"]
                )

                model_name = result.get(
                    "model",
                    "Random Forest"
                )

                model_version = result.get(
                    "version",
                    "Unknown"
                )


                # =============================================
                # SUCCESS MESSAGE
                # =============================================

                st.success(
                    "✅ Prediction completed successfully!"
                )

                st.divider()


                # =============================================
                # RESULT METRICS
                # =============================================

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Predicted AQI",
                        f"{predicted_aqi:.2f}"
                    )

                with col2:

                    st.metric(
                        "Model",
                        model_name
                    )

                with col3:

                    st.metric(
                        "Model Version",
                        str(model_version)
                    )


                # =============================================
                # AQI CATEGORY
                # =============================================

                category = get_aqi_category(
                    predicted_aqi
                )

                st.subheader("📊 AQI Classification")

                st.info(
                    f"Predicted AQI: **{predicted_aqi:.2f}**\n\n"
                    f"Category: **{category}**"
                )


                # =============================================
                # HEALTH / HAZARD ALERT
                # =============================================

                st.subheader("🚦 AQI Health Alert")


                if predicted_aqi <= 50:

                    st.success(
                        f"🟢 GOOD — Predicted AQI is "
                        f"{predicted_aqi:.2f}. "
                        "Air quality is considered good."
                    )


                elif predicted_aqi <= 100:

                    st.info(
                        f"🟡 MODERATE — Predicted AQI is "
                        f"{predicted_aqi:.2f}. "
                        "Air quality is acceptable, "
                        "although unusually sensitive people "
                        "may experience minor effects."
                    )


                elif predicted_aqi <= 150:

                    st.warning(
                        f"🟠 UNHEALTHY FOR SENSITIVE GROUPS — "
                        f"Predicted AQI is {predicted_aqi:.2f}. "
                        "Sensitive individuals should consider "
                        "reducing prolonged outdoor exposure."
                    )


                elif predicted_aqi <= 200:

                    st.error(
                        f"🔴 UNHEALTHY — Predicted AQI is "
                        f"{predicted_aqi:.2f}. "
                        "Everyone may begin to experience "
                        "health effects."
                    )


                elif predicted_aqi <= 300:

                    st.error(
                        f"🟣 VERY UNHEALTHY — Predicted AQI is "
                        f"{predicted_aqi:.2f}. "
                        "Health alert: the risk of health effects "
                        "is increased for everyone."
                    )


                else:

                    # =========================================
                    # HAZARDOUS ALERT
                    # =========================================

                    st.error(
                        f"🚨 HAZARDOUS AQI ALERT — "
                        f"Predicted AQI is {predicted_aqi:.2f}."
                    )

                    st.warning(
                        "⚠️ Health emergency conditions. "
                        "Avoid prolonged outdoor exposure and "
                        "follow local air-quality health guidance."
                    )


                # =============================================
                # INPUT SUMMARY
                # =============================================

                with st.expander(
                    "🔎 View Submitted Input Data"
                ):

                    st.json(payload)


            # =================================================
            # API ERROR
            # =================================================

            else:

                st.error(
                    f"❌ API returned status code "
                    f"{response.status_code}"
                )

                try:

                    error_data = response.json()

                    st.json(error_data)

                except Exception:

                    st.write(response.text)


        # ====================================================
        # CONNECTION ERROR
        # ====================================================

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Could not connect to the FastAPI server."
            )

            st.info(
                "Make sure your FastAPI/Uvicorn server is "
                "running on port 8000 and the port is publicly "
                "accessible in GitHub Codespaces."
            )


        # ====================================================
        # TIMEOUT
        # ====================================================

        except requests.exceptions.Timeout:

            st.error(
                "⏱️ The API request timed out."
            )

            st.info(
                "The FastAPI server or Hopsworks model "
                "may be taking too long to respond."
            )


        # ====================================================
        # OTHER ERRORS
        # ====================================================

        except requests.exceptions.RequestException as e:

            st.error(
                f"❌ Request error: {str(e)}"
            )


        except Exception as e:

            st.error(
                f"❌ Unexpected error: {str(e)}"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AQI Prediction System | "
    "Random Forest Model | "
    "FastAPI | "
    "Hopsworks Model Registry"
)