import streamlit as st
import requests
import pandas as pd
import textwrap


def html(content):
    lines = [line.strip() for line in content.strip("\n").splitlines()]
    return "\n".join(lines)

st.set_page_config(
    page_title="Karachi AQI Prediction System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FastAPI and Streamlit.
API_URL = "http://127.0.0.1:8000"


st.markdown(
    """
    <style>

    .stApp {
        background: #f8fafc;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* HERO */

    .hero {
        background: linear-gradient(
            135deg,
            #0f766e 0%,
            #0e7490 45%,
            #2563eb 100%
        );

        border-radius: 24px;
        padding: 2.4rem 2.7rem;
        margin-bottom: 1.6rem;

        color: white;

        box-shadow:
            0 12px 35px rgba(15, 118, 110, 0.20);
    }

    .hero-title {
        font-size: 2.35rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.45rem;
    }

    .hero-subtitle {
        font-size: 1.02rem;
        line-height: 1.6;
        opacity: 0.92;
        max-width: 850px;
        margin: 0;
    }

    .hero-badge {
        display: inline-block;
        margin-top: 1.1rem;
        padding: 0.4rem 0.85rem;
        border-radius: 999px;

        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.25);

        font-size: 0.78rem;
        font-weight: 700;
    }

    /* SECTION HEADINGS */

    .section-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 0.4rem;
        margin-bottom: 0.25rem;
    }

    .section-description {
        color: #64748b;
        font-size: 0.92rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    /* DASHBOARD INFO CARDS */

    .info-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.05rem 1.15rem;

        box-shadow: 0 3px 12px rgba(15,23,42,0.04);

        min-height: 105px;
    }

    .info-label {
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    .info-value {
        color: #0f172a;
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 0.3rem;
    }

    .info-description {
        color: #94a3b8;
        font-size: 0.75rem;
        margin-top: 0.2rem;
    }

    /* FORECAST CARDS*/

    .forecast-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 20px;

        padding: 1.45rem 1.2rem;

        min-height: 185px;

        text-align: center;

        box-shadow:
            0 5px 18px rgba(15,23,42,0.05);

        transition: transform 0.2s ease;
    }

    .forecast-card:hover {
        transform: translateY(-3px);
    }

    .forecast-date {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    .forecast-day {
        color: #0f172a;
        font-size: 1.05rem;
        font-weight: 800;
        margin-top: 0.15rem;
    }

    .forecast-aqi {
        color: #0f172a;
        font-size: 2.35rem;
        font-weight: 850;
        margin-top: 0.65rem;
        line-height: 1;
    }

    .forecast-category {
        margin-top: 0.6rem;
        font-size: 0.78rem;
        font-weight: 800;
        color: #475569;
    }

    .forecast-indicator {
        margin: 0.75rem auto 0 auto;
        height: 5px;
        width: 65px;
        border-radius: 999px;
        background: #facc15;
    }

    /* AQI RESULT */

    .aqi-result {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 22px;

        padding: 2rem;

        text-align: center;

        box-shadow:
            0 8px 25px rgba(15,23,42,0.06);
    }

    .aqi-result-label {
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }

    .aqi-result-number {
        color: #0f172a;
        font-size: 3.4rem;
        font-weight: 900;
        line-height: 1.1;
        margin-top: 0.45rem;
    }

    .aqi-result-category {
        color: #475569;
        font-size: 1rem;
        font-weight: 700;
        margin-top: 0.3rem;
    }

    /* HEALTH ALERT */

    .health-card {
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-top: 0.6rem;
        border: 1px solid #e2e8f0;
        background: white;
    }

    .health-title {
        font-size: 1rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }

    .health-text {
        color: #64748b;
        font-size: 0.88rem;
        line-height: 1.5;
    }

    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    .sidebar-brand {
        font-size: 1.35rem;
        font-weight: 850;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }

    .sidebar-subtitle {
        color: #64748b;
        font-size: 0.78rem;
        margin-bottom: 1.4rem;
    }

    .sidebar-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 0.8rem 0.9rem;
        margin-bottom: 0.6rem;
    }

    .sidebar-card-title {
        color: #334155;
        font-size: 0.78rem;
        font-weight: 800;
    }

    .sidebar-card-value {
        color: #64748b;
        font-size: 0.76rem;
        margin-top: 0.2rem;
    }

    /* TABS */

    button[data-baseweb="tab"] {
        font-size: 0.95rem;
        font-weight: 750;
        padding: 0.8rem 1.2rem;
    }

    /* BUTTONS */

    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 11px;
        min-height: 2.7rem;
        font-weight: 750;
        border: 1px solid #cbd5e1;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        border-color: #0f766e;
    }

    /* INPUTS */

    div[data-baseweb="input"] {
        border-radius: 10px;
    }

    /* FORM SECTION */

    .form-section {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 1.15rem 1.25rem;
        margin-bottom: 1rem;
    }

    .form-section-title {
        font-size: 1rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.75rem;
    }

    /* FOOTER */

    .footer {
        text-align: center;
        padding: 1.8rem 1rem 0.5rem 1rem;
        color: #94a3b8;
        font-size: 0.78rem;
    }

    /* MOBILE */

    @media (max-width: 768px) {

        .hero {
            padding: 1.7rem;
        }

        .hero-title {
            font-size: 1.8rem;
        }

        .hero-subtitle {
            font-size: 0.9rem;
        }

        .forecast-card {
            margin-bottom: 0.7rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)

def get_aqi_category(aqi):

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


def get_aqi_emoji(aqi):

    if aqi <= 50:
        return ""

    elif aqi <= 100:
        return ""

    elif aqi <= 150:
        return ""

    elif aqi <= 200:
        return ""

    elif aqi <= 300:
        return ""

    else:
        return ""


def get_aqi_color(aqi):

    if aqi <= 50:
        return "#22c55e"

    elif aqi <= 100:
        return "#eab308"

    elif aqi <= 150:
        return "#f97316"

    elif aqi <= 200:
        return "#ef4444"

    elif aqi <= 300:
        return "#9333ea"

    else:
        return "#7f1d1d"


def render_health_alert(predicted_aqi):

    category = get_aqi_category(predicted_aqi)

    if predicted_aqi <= 50:

        title = f" Good Air Quality"
        text = "Air quality is considered good."

    elif predicted_aqi <= 100:

        title = f" Moderate Air Quality"
        text = (
            "Air quality is acceptable. "
            "Unusually sensitive individuals may experience minor effects."
        )

    elif predicted_aqi <= 150:

        title = f" Unhealthy for Sensitive Groups"
        text = (
            "Sensitive individuals should consider reducing "
            "prolonged outdoor exposure."
        )

    elif predicted_aqi <= 200:

        title = f" Unhealthy Air Quality"
        text = (
            "Everyone may begin to experience health effects."
        )

    elif predicted_aqi <= 300:

        title = f" Very Unhealthy Air Quality"
        text = (
            "Health alert: the risk of health effects "
            "is increased for everyone."
        )

    else:

        title = f" Hazardous Air Quality"
        text = (
            "Health emergency conditions. "
            "Avoid prolonged outdoor exposure."
        )

    st.markdown(
        html(f"""
        <div class="health-card">

            <div class="health-title">
                 AQI Health Alert — {category}
            </div>

            <div class="health-text">
                <b>{title}</b><br>
                {text}
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )

# HERO HEADER

st.markdown(
    """
    <div class="hero">
         <b class="hero-title">Karachi Air Quality Index</b><br>
        <span class="hero-subtitle">
            AI-powered AQI prediction and 3-day air-quality forecasting
            using Random Forest, Hopsworks and FastAPI.
        </span><br>
        <span class="hero-badge">
            ● AI Prediction System &nbsp; • &nbsp; Karachi
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

# SIDEBAR

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand"> Karachi AQI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'AI-powered environmental monitoring system'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-card">
            <div class="sidebar-card-title"> Prediction Model</div>
            <div class="sidebar-card-value">Random Forest</div>
        </div>

        <div class="sidebar-card">
            <div class="sidebar-card-title"> Backend</div>
            <div class="sidebar-card-value">FastAPI</div>
        </div>

        <div class="sidebar-card">
            <div class="sidebar-card-title"> Feature Store</div>
            <div class="sidebar-card-value">Hopsworks</div>
        </div>

        <div class="sidebar-card">
            <div class="sidebar-card-title"> Model Registry</div>
            <div class="sidebar-card-value">Hopsworks</div>
        </div>

        <div class="sidebar-card">
            <div class="sidebar-card-title"> Frontend</div>
            <div class="sidebar-card-value">Streamlit</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("###  System Features")

    st.caption(" Automatic 3-Day Forecast")
    st.caption(" Manual What-If Simulation")
    st.caption(" AQI Health Alerts")
    st.caption(" AQI Trend Visualization")
    st.caption(" Prediction Details")

    st.divider()

    st.markdown("###  API Status")

    try:

        health_response = requests.get(
            f"{API_URL}/health",
            timeout=5
        )

        if health_response.status_code == 200:

            health_data = health_response.json()

            if health_data.get("model_loaded"):

                st.success(" API Online")

            else:

                st.warning(" API Online — Model not loaded")

        else:

            st.error(" API Error")

    except Exception:

        st.error(" API Offline")

    st.divider()

    st.caption(
        "Forecast mode automatically retrieves environmental "
        "features. What-If mode allows manual scenario testing."
    )

# TOP DASHBOARD METADATA

info1, info2, info3, info4 = st.columns(4)

with info1:

    st.markdown(
        """
        <div class="info-card">
            <div class="info-label">Location</div>
            <div class="info-value"> Karachi</div>
            <div class="info-description">Pakistan</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with info2:

    st.markdown(
        """
        <div class="info-card">
            <div class="info-label">Forecast Horizon</div>
            <div class="info-value"> 3 Days</div>
            <div class="info-description">Automatic forecast</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with info3:

    st.markdown(
        """
        <div class="info-card">
            <div class="info-label">ML Model</div>
            <div class="info-value"> Random Forest</div>
            <div class="info-description">Hopsworks registry</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with info4:

    st.markdown(
        """
        <div class="info-card">
            <div class="info-label">Data Pipeline</div>
            <div class="info-value">☁️ Hopsworks</div>
            <div class="info-description">Feature store</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")

# TABS

tab_forecast, tab_whatif = st.tabs(
    [
        "  3-Day Forecast",
        "  What-If Simulator"
    ]
)

# TAB 1 — AUTOMATIC FORECAST

with tab_forecast:

    st.markdown(
        '<div class="section-title">'
        ' Automatic 3-Day AQI Forecast'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Generate an AQI forecast using live forecasted environmental '
        'conditions and recent feature-store history.'
        '</div>',
        unsafe_allow_html=True
    )

    refresh_col1, refresh_col2 = st.columns([1, 5])

    with refresh_col1:

        refresh_forecast = st.button(
            " Refresh Forecast",
            use_container_width=True
        )

    if "run_forecast" not in st.session_state:

        st.session_state["run_forecast"] = True

    if refresh_forecast:

        st.session_state["run_forecast"] = True

    if st.session_state["run_forecast"]:

        with st.spinner(
            "Fetching environmental data and generating forecast..."
        ):

            try:

                response = requests.get(
                    f"{API_URL}/forecast",
                    params={"days": 3},
                    timeout=60
                )

                if response.status_code == 200:

                    result = response.json()

                    forecast = result.get(
                        "forecast",
                        []
                    )

                    if not forecast:

                        st.error(
                            "The API returned an empty forecast."
                        )

                    else:

                        df = pd.DataFrame(forecast)

                        st.success(
                            "Forecast generated successfully using "
                            "the latest available data."
                        )

                        st.write("")

                        # FORECAST SUMMARY

                        st.markdown(
                            '<div class="section-title">'
                            ' Forecast Overview'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        aqi_values = [
                            float(day["predicted_aqi"])
                            for day in forecast
                        ]

                        average_aqi = sum(aqi_values) / len(aqi_values)
                        highest_aqi = max(aqi_values)
                        lowest_aqi = min(aqi_values)

                        s1, s2, s3, s4 = st.columns(4)

                        with s1:

                            st.metric(
                                "Average AQI",
                                f"{average_aqi:.2f}"
                            )

                        with s2:

                            st.metric(
                                "Highest AQI",
                                f"{highest_aqi:.2f}"
                            )

                        with s3:

                            st.metric(
                                "Lowest AQI",
                                f"{lowest_aqi:.2f}"
                            )

                        with s4:

                            st.metric(
                                "Overall Category",
                                get_aqi_category(average_aqi)
                            )

                        st.write("")

                        # DAILY FORECAST CARDS

                        st.markdown(
                            '<div class="section-title">'
                            ' Daily Forecast'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        cols = st.columns(
                            len(forecast)
                        )

                        for index, (col, day) in enumerate(
                            zip(cols, forecast)
                        ):

                            aqi_value = float(
                                day["predicted_aqi"]
                            )

                            category = get_aqi_category(
                                aqi_value
                            )

                            aqi_color = get_aqi_color(
                                aqi_value
                            )

                            date_value = pd.to_datetime(
                                day["date"]
                            )

                            if index == 0:
                                day_label = "Today"
                            elif index == 1:
                                day_label = "Tomorrow"
                            else:
                                day_label = date_value.strftime("%A")

                            with col:

                                # NOTE: wrapped with html() so the deep
                                st.markdown(
                                    html(f"""
                                    <div class="forecast-card">
                                        <div class="forecast-date">
                                            {date_value.strftime("%d %b %Y")}
                                        </div>
                                        <div class="forecast-day">
                                            {day_label}
                                        </div>
                                        <div class="forecast-aqi">
                                             {aqi_value:.2f}
                                        </div>
                                        <div class="forecast-category">
                                            {category}
                                        </div>
                                        <div
                                            class="forecast-indicator"
                                            style="background:{aqi_color};"
                                        ></div>
                                    </div>
                                    """),
                                    unsafe_allow_html=True
                                )

                        st.write("")

                        # TREND CHART

                        st.markdown(
                            '<div class="section-title">'
                            ' AQI Forecast Trend'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            '<div class="section-description">'
                            'Predicted AQI values across the next three days.'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        chart_df = df[
                            [
                                "date",
                                "predicted_aqi"
                            ]
                        ].copy()

                        chart_df["date"] = pd.to_datetime(
                            chart_df["date"]
                        )

                        chart_df = chart_df.set_index(
                            "date"
                        )

                        st.line_chart(
                            chart_df,
                            y="predicted_aqi",
                            use_container_width=True,
                            height=330
                        )

                        st.write("")

                        # NEAREST FORECAST

                        nearest_aqi = float(
                            forecast[0]["predicted_aqi"]
                        )

                        st.markdown(
                            '<div class="section-title">'
                            ' Nearest Forecast'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        n1, n2, n3 = st.columns(3)

                        with n1:

                            st.metric(
                                "Forecast Date",
                                forecast[0]["date"]
                            )

                        with n2:

                            st.metric(
                                "Predicted AQI",
                                f"{nearest_aqi:.2f}"
                            )

                        with n3:

                            st.metric(
                                "Category",
                                get_aqi_category(
                                    nearest_aqi
                                )
                            )

                        st.write("")

                        render_health_alert(nearest_aqi)

                        st.write("")

                else:

                    st.error(
                        f"FastAPI returned status code "
                        f"{response.status_code}"
                    )

                    try:

                        st.json(
                            response.json()
                        )

                    except Exception:

                        st.write(
                            response.text
                        )

            except requests.exceptions.ConnectionError:

                st.error(
                    " Could not connect to FastAPI."
                )

                st.info(
                    "Make sure Uvicorn is running on port 8000 "
                    "inside the Codespace."
                )

            except requests.exceptions.Timeout:

                st.error(
                    " The forecast request timed out."
                )

            except requests.exceptions.RequestException as e:

                st.error(
                    f" Request error: {str(e)}"
                )

            except Exception as e:

                st.error(
                    f" Unexpected error: {str(e)}"
                )

# TAB 2 — WHAT-IF SIMULATOR

with tab_whatif:

    st.markdown(
        '<div class="section-title">'
        ' Manual What-If Simulator'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Modify environmental conditions manually and observe how '
        'the trained Random Forest model responds.'
        '</div>',
        unsafe_allow_html=True
    )

    # INPUT FORM

    with st.form(
        "aqi_prediction_form"
    ):

        # POLLUTANTS

        st.markdown(
            '<div class="form-section-title">'
            ' Pollutant Conditions'
            '</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

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

        with col2:

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

        with col3:

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

            uv_index = st.number_input(
                "UV Index",
                value=5.0,
                min_value=0.0
            )

        st.divider()

        # AQI + TIME

        st.markdown(
            '<div class="form-section-title">'
            ' AQI & Time Features'
            '</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

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

        with col2:

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

        with col3:

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

        st.divider()

        # HISTORY + WEATHER

        st.markdown(
            '<div class="form-section-title">'
            ' Weather & AQI History'
            '</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            aqi_change_rate = st.number_input(
                "AQI Change Rate",
                value=0.0
            )

            aqi_lag_1 = st.number_input(
                "AQI Lag 1",
                value=70.0,
                min_value=0.0
            )

        with col2:

            aqi_lag_7 = st.number_input(
                "AQI Lag 7",
                value=65.0,
                min_value=0.0
            )

            temperature = st.number_input(
                "Temperature",
                value=32.0
            )

        with col3:

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

        st.write("")

        predict_button = st.form_submit_button(
            "  Predict AQI",
            use_container_width=True
        )

    # MANUAL PREDICTION

    if predict_button:

        payload = {

            "pm10": pm10,
            "pm25": pm25,
            "co": co,
            "no2": no2,
            "so2": so2,
            "o3": o3,

            "aerosol_optical_depth":
                aerosol_optical_depth,

            "dust":
                dust,

            "uv_index":
                uv_index,

            "aqi":
                aqi,

            "european_aqi":
                european_aqi,

            "hour":
                int(hour),

            "day":
                int(day),

            "month":
                int(month),

            "weekday":
                int(weekday),

            "aqi_change_rate":
                aqi_change_rate,

            "aqi_lag_1":
                aqi_lag_1,

            "aqi_lag_7":
                aqi_lag_7,

            "temperature":
                temperature,

            "humidity":
                humidity,

            "wind_speed":
                wind_speed,

            "rain":
                rain
        }

        with st.spinner(
            " Running Random Forest prediction..."
        ):

            try:

                response = requests.post(
                    f"{API_URL}/predict",
                    json=payload,
                    timeout=60
                )

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

                    category = get_aqi_category(
                        predicted_aqi
                    )


                    aqi_color = get_aqi_color(
                        predicted_aqi
                    )

                    st.success(
                        "Prediction completed successfully."
                    )

                    st.write("")

                    # RESULT

                    st.markdown(
                        '<div class="section-title">'
                        ' Prediction Result'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        html(f"""
                        <div class="aqi-result">
                            <div class="aqi-result-label">
                                Predicted Air Quality Index
                            </div>
                            <div
                                class="aqi-result-number"
                                style="color:{aqi_color};"
                            >
                                 {predicted_aqi:.2f}
                            </div>
                            <div class="aqi-result-category">
                                {category}
                            </div>
                        </div>
                        """),
                        unsafe_allow_html=True
                    )

                    st.write("")

                    # MODEL METRICS

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

                    # CLASSIFICATION

                    st.write("")

                    st.markdown(
                        '<div class="section-title">'
                        ' AQI Classification'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    if predicted_aqi <= 50:

                        st.success(
                            f" **{category}** — "
                            f"AQI {predicted_aqi:.2f}"
                        )

                    elif predicted_aqi <= 100:

                        st.info(
                            f" **{category}** — "
                            f"AQI {predicted_aqi:.2f}"
                        )

                    elif predicted_aqi <= 150:

                        st.warning(
                            f" **{category}** — "
                            f"AQI {predicted_aqi:.2f}"
                        )

                    else:

                        st.error(
                            f" **{category}** — "
                            f"AQI {predicted_aqi:.2f}"
                        )


                    st.write("")

                    render_health_alert(
                        predicted_aqi
                    )

                    st.write("")


                else:

                    st.error(
                        f"FastAPI returned status code "
                        f"{response.status_code}"
                    )

                    try:

                        st.json(
                            response.json()
                        )

                    except Exception:

                        st.write(
                            response.text
                        )

            except requests.exceptions.ConnectionError:

                st.error(
                    " Could not connect to FastAPI."
                )

                st.info(
                    "Make sure Uvicorn is running on port 8000."
                )

            except requests.exceptions.Timeout:

                st.error(
                    " Prediction request timed out."
                )

            except requests.exceptions.RequestException as e:

                st.error(
                    f" Request error: {str(e)}"
                )

            except Exception as e:

                st.error(
                    f" Unexpected error: {str(e)}"
                )

# FOOTER
st.divider()

st.markdown(
    """
    <div class="footer">
         <b>Karachi AQI Prediction System</b>
        <br>
        Random Forest &nbsp;•&nbsp;
        FastAPI &nbsp;•&nbsp;
        Hopsworks Feature Store &nbsp;•&nbsp;
        Hopsworks Model Registry &nbsp;•&nbsp;
        Streamlit
        <br><br>
        AI-powered environmental prediction for Karachi
    </div>
    """,
    unsafe_allow_html=True
)