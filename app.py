from utils.pdf_generator import generate_patient_pdf
import traceback
import hashlib
import streamlit as st
import matplotlib.pyplot as plt

from utils.patient import patient_information
from utils.pdf_reader import extract_pdf_text
from utils.preprocess import clean_text
from utils.analyzer import extract_parameters
from utils.charts import create_bar_chart, create_pie_chart
from utils.database import (
    save_patient_report,
    get_all_patient_reports,
    get_patient_report_by_id,
    create_user,
    user_exists,
    get_database_connection,
    reset_user_password
)
from llm.groq_service import analyze_report


# =====================================================
# Medical Normal Ranges
# =====================================================
NORMAL_RANGES = {
    "Hemoglobin": (13.0, 17.0),
    "WBC": (4000.0, 11000.0),
    "RBC": (4.5, 6.0),
    "Platelets": (150000.0, 450000.0),
    "Blood Sugar": (70.0, 126.0)
}


# =====================================================
# Safe Numeric Conversion
# =====================================================
def convert_to_number(value):
    """
    Safely convert extracted values such as:
    11.2
    "11.2"
    "13,200"
    "168 mg/dL"

    into float values.
    """

    if value is None:
        return None

    try:
        cleaned_value = str(value).replace(",", "").strip()

        number = ""
        decimal_found = False
        negative_found = False

        for character in cleaned_value:

            if character.isdigit():
                number += character

            elif character == "." and not decimal_found:
                number += character
                decimal_found = True

            elif character == "-" and not negative_found and not number:
                number += character
                negative_found = True

            elif number:
                break

        if number in ["", ".", "-", "-."]:
            return None

        return float(number)

    except (TypeError, ValueError):
        return None


# =====================================================
# Normalise Extracted Parameters
# =====================================================
def normalise_parameters(parameters):

    normalised = {}

    if not isinstance(parameters, dict):
        return normalised

    for parameter, value in parameters.items():

        numeric_value = convert_to_number(value)

        if numeric_value is not None:
            normalised[parameter] = numeric_value

    return normalised


# =====================================================
# Check Normal Ranges
# =====================================================
def check_normal_ranges_safe(parameters):

    results = {}

    for parameter, value in parameters.items():

        numeric_value = convert_to_number(value)

        if numeric_value is None:

            results[parameter] = {
                "Value": value,
                "Status": "Invalid"
            }

            continue

        if parameter not in NORMAL_RANGES:

            results[parameter] = {
                "Value": numeric_value,
                "Status": "Range not available"
            }

            continue

        minimum, maximum = NORMAL_RANGES[parameter]

        if numeric_value < minimum:
            status = "Low"

        elif numeric_value > maximum:
            status = "High"

        else:
            status = "Normal"

        results[parameter] = {
            "Value": numeric_value,
            "Status": status
        }

    return results


# =====================================================
# Disease Prediction
# =====================================================
def predict_disease_safe(parameters):

    diseases = []

    hemoglobin = convert_to_number(
        parameters.get("Hemoglobin")
    )

    blood_sugar = convert_to_number(
        parameters.get("Blood Sugar")
    )

    wbc = convert_to_number(
        parameters.get("WBC")
    )

    platelets = convert_to_number(
        parameters.get("Platelets")
    )

    if hemoglobin is not None and hemoglobin < 13.0:

        diseases.append(
            {
                "Disease": "Possible Anemia",
                "Probability": "90%"
            }
        )

    if blood_sugar is not None and blood_sugar > 126.0:

        diseases.append(
            {
                "Disease": "Possible Diabetes",
                "Probability": "95%"
            }
        )

    if wbc is not None and wbc > 11000.0:

        diseases.append(
            {
                "Disease": "Possible Infection",
                "Probability": "88%"
            }
        )

    if platelets is not None and platelets < 150000.0:

        diseases.append(
            {
                "Disease": "Possible Low Platelet Condition",
                "Probability": "85%"
            }
        )

    return diseases


# =====================================================
# Risk Factor Detection
# =====================================================
def detect_risk_factors_safe(range_results):

    risks = []

    hemoglobin_status = range_results.get(
        "Hemoglobin",
        {}
    ).get("Status")

    blood_sugar_status = range_results.get(
        "Blood Sugar",
        {}
    ).get("Status")

    wbc_status = range_results.get(
        "WBC",
        {}
    ).get("Status")

    platelets_status = range_results.get(
        "Platelets",
        {}
    ).get("Status")

    if hemoglobin_status == "Low":
        risks.append("🩸 Possible Anemia")

    if blood_sugar_status == "High":
        risks.append("🍬 Possible Diabetes")

    if wbc_status == "High":
        risks.append("🦠 Possible Infection")

    if platelets_status == "Low":
        risks.append(
            "🩹 Possible Low Platelet Condition"
        )

    return risks


# =====================================================
# Specialist Suggestion
# =====================================================
def suggest_specialists_safe(range_results):

    specialists = []

    hemoglobin_status = range_results.get(
        "Hemoglobin",
        {}
    ).get("Status")

    blood_sugar_status = range_results.get(
        "Blood Sugar",
        {}
    ).get("Status")

    wbc_status = range_results.get(
        "WBC",
        {}
    ).get("Status")

    platelets_status = range_results.get(
        "Platelets",
        {}
    ).get("Status")

    if hemoglobin_status == "Low":
        specialists.append("🩸 Hematologist")

    if blood_sugar_status == "High":
        specialists.append("🍬 Diabetologist")

    if wbc_status == "High":
        specialists.append("🩺 General Physician")

    if platelets_status == "Low":
        specialists.append("🩸 Hematologist")

    if not specialists:

        specialists.append(
            "✅ General Physician (Routine Check-up)"
        )

    return list(dict.fromkeys(specialists))


# =====================================================
# Dashboard Calculation
# =====================================================
def calculate_dashboard_safe(
    range_results,
    risk_factors
):

    total_parameters = len(range_results)

    normal_count = sum(
        1
        for result in range_results.values()
        if result.get("Status") == "Normal"
    )

    abnormal_count = sum(
        1
        for result in range_results.values()
        if result.get("Status") in ["Low", "High"]
    )

    return {
        "Total Parameters": total_parameters,
        "Normal": normal_count,
        "Abnormal": abnormal_count,
        "Risk Factors": len(risk_factors)
    }


# =====================================================
# Convert Results for Existing Pie Chart Function
# =====================================================
def prepare_chart_range_results(range_results):

    chart_results = {}

    for parameter, result in range_results.items():

        status = result.get("Status")

        if status == "Normal":
            chart_status = "🟢 Normal"

        elif status == "Low":
            chart_status = "🔴 Low"

        elif status == "High":
            chart_status = "🔴 High"

        else:
            chart_status = status

        chart_results[parameter] = {
            "Value": result.get("Value"),
            "Status": chart_status
        }

    return chart_results



# =====================================================
# Page Configuration
# =====================================================
# =====================================================
# Page Configuration
# =====================================================
from datetime import date, datetime

st.set_page_config(
    page_title="MedIntel AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="auto"
)
# ==========================================
# Login Session Setup
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =====================================================
# Session State
# =====================================================
if "navigation" not in st.session_state:
    st.session_state.navigation = "🏠 Dashboard"


# =====================================================
# Professional Global Styling
# =====================================================
st.markdown("""
<style>
:root {
    --primary: #0B4F6C;
    --secondary: #167D9A;
    --accent: #2FB5A8;
    --background: #F4F8FB;
    --surface: #FFFFFF;
    --text: #18323F;
    --muted: #607D8B;
    --border: #DCE8EE;
    --success: #16875B;
    --warning: #D97706;
    --danger: #C43E3E;
}

.stApp {
    background: linear-gradient(135deg, #F8FCFE 0%, #EDF6FA 100%);
}

.block-container {
    max-width: 1280px;
    padding-top: 1.35rem;
    padding-bottom: 3rem;
}

#MainMenu, footer {
    visibility: hidden;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07394F 0%, #0A607D 100%);
    border-right: none;
}

section[data-testid="stSidebar"] * {
    color: white;
}

section[data-testid="stSidebar"] .stRadio label {
    padding: 0.52rem 0.6rem;
    border-radius: 10px;
}

.sidebar-profile {
    padding: 16px;
    border-radius: 16px;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.18);
    margin-bottom: 16px;
}
.sidebar-profile h3 { margin: 0; color: white; }
.sidebar-profile p { margin: 5px 0; opacity: .88; }
.system-online {
    display: inline-block;
    margin-top: 7px;
    padding: 4px 9px;
    border-radius: 999px;
    background: rgba(38, 208, 124, .20);
    border: 1px solid rgba(124, 255, 187, .38);
    font-size: .82rem;
}

.hero {
    background: linear-gradient(135deg, #0B4F6C 0%, #167D9A 62%, #2FB5A8 100%);
    padding: 30px 34px;
    border-radius: 22px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 14px 34px rgba(11, 79, 108, 0.22);
}
.hero-grid {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}
.hero h1 { margin: 0; font-size: 2.25rem; font-weight: 800; }
.hero p { margin: 8px 0 0; opacity: .92; font-size: 1rem; }
.hero-date {
    min-width: 190px;
    text-align: right;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.20);
    padding: 12px 15px;
    border-radius: 14px;
}

.section-title {
    color: #0B4F6C;
    font-size: 1.35rem;
    font-weight: 750;
    margin: 0 0 .9rem;
}

.stat-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(36, 83, 105, .08);
    min-height: 126px;
}
.stat-card .label { color: #607D8B; font-weight: 650; font-size: .95rem; }
.stat-card .value { color: #0B4F6C; font-size: 2rem; font-weight: 850; margin-top: 8px; }
.stat-card .hint { color: #7B919B; font-size: .82rem; margin-top: 4px; }
.stat-card.green { border-top: 4px solid #1A9B68; }
.stat-card.blue { border-top: 4px solid #167D9A; }
.stat-card.orange { border-top: 4px solid #E58A18; }
.stat-card.purple { border-top: 4px solid #7157C7; }

.quick-card {
    background: linear-gradient(145deg, #FFFFFF, #F5FAFC);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
    min-height: 94px;
}

.patient-card {
    background: white;
    border: 1px solid var(--border);
    border-left: 5px solid #167D9A;
    border-radius: 16px;
    padding: 17px 18px;
    margin-bottom: 12px;
    box-shadow: 0 6px 18px rgba(36,83,105,.06);
}
.patient-card h4 { color: #0B4F6C; margin: 0 0 7px; }
.patient-card p { margin: 3px 0; color: #526D79; }
.badge {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 999px;
    background: #E8F6F3;
    color: #13745B;
    font-size: .8rem;
    font-weight: 700;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,.98);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 8px;
    box-shadow: 0 8px 24px rgba(36,83,105,.07);
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 7px 20px rgba(36,83,105,.08);
}
div[data-testid="stMetricLabel"] { color: #607D8B; font-weight: 650; }
div[data-testid="stMetricValue"] { color: #0B4F6C; font-size: 2rem; font-weight: 800; }

.stButton > button, .stDownloadButton > button {
    width: 100%; border: none; border-radius: 11px; padding: .68rem 1rem;
    font-weight: 700; background: linear-gradient(90deg,#0B4F6C,#167D9A);
    color: white; box-shadow: 0 6px 16px rgba(11,79,108,.20); transition: all .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px); box-shadow: 0 9px 20px rgba(11,79,108,.28); color: white;
}
input, textarea { border-radius: 10px !important; }
div[data-testid="stFileUploader"] {
    background: #FFFFFF; border: 2px dashed #8EC7D6; border-radius: 16px; padding: 12px;
}
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    border: 1px solid var(--border); border-radius: 14px; overflow: hidden;
}
div[data-testid="stAlert"] { border-radius: 12px; }
.footer-note {
    text-align: center; color: #6B7F89; font-size: .82rem; padding: 30px 10px 8px;
}
.footer-line { height: 1px; background: #DCE8EE; margin-bottom: 18px; }

/* Authentication page */
.auth-heading {
    text-align: center;
    padding: 22px 0 14px;
}
.auth-heading h1 {
    color: #0B4F6C;
    margin-bottom: 4px;
}
.auth-heading h3 {
    color: #526D79;
    margin: 0;
    font-weight: 650;
}
.auth-heading p {
    color: #718894;
    margin-top: 8px;
}
.auth-note {
    padding: 12px 14px;
    background: #EAF6F8;
    border: 1px solid #CBE5EB;
    border-radius: 12px;
    color: #315B69;
    font-size: .9rem;
}


/* =====================================================
   Responsive layout for tablets and mobile phones
   ===================================================== */
html, body, [data-testid="stAppViewContainer"], .stApp {
    max-width: 100%;
    overflow-x: hidden;
}

img, svg, canvas {
    max-width: 100% !important;
    height: auto;
}

[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stPlotlyChart"],
[data-testid="stImage"],
[data-testid="stPyplotGlobalUse"] {
    max-width: 100% !important;
    overflow-x: auto;
}

/* Tablet */
@media only screen and (max-width: 1024px) {
    .block-container {
        max-width: 100% !important;
        padding-top: 1rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
        padding-bottom: 2rem !important;
    }

    .hero {
        padding: 24px 24px !important;
        border-radius: 18px !important;
    }

    .hero h1 {
        font-size: 1.9rem !important;
    }

    .hero-date {
        min-width: 160px !important;
    }

    .stat-card {
        min-height: 116px !important;
        padding: 17px !important;
    }
}

/* Mobile */
@media only screen and (max-width: 768px) {
    .block-container {
        width: 100% !important;
        max-width: 100% !important;
        padding-top: 0.75rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        padding-bottom: 1.5rem !important;
    }

    /* Stack Streamlit columns vertically */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.75rem !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        flex: 1 1 100% !important;
        width: 100% !important;
        min-width: 100% !important;
    }

    /* Hero section */
    .hero {
        padding: 20px 18px !important;
        margin-bottom: 16px !important;
        border-radius: 16px !important;
    }

    .hero-grid {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 14px !important;
    }

    .hero h1 {
        font-size: 1.65rem !important;
        line-height: 1.2 !important;
    }

    .hero p {
        font-size: 0.92rem !important;
        line-height: 1.5 !important;
    }

    .hero-date {
        width: 100% !important;
        min-width: 0 !important;
        text-align: left !important;
        padding: 10px 12px !important;
        box-sizing: border-box !important;
    }

    /* Authentication */
    .auth-heading {
        padding: 8px 4px 10px !important;
    }

    .auth-heading h1 {
        font-size: 1.75rem !important;
    }

    .auth-heading h3 {
        font-size: 1.05rem !important;
        line-height: 1.35 !important;
    }

    .auth-heading p {
        font-size: 0.88rem !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        width: 100% !important;
        max-width: 100% !important;
        padding: 5px !important;
        border-radius: 14px !important;
        box-sizing: border-box !important;
    }

    /* Mobile authentication navigation: show full Login / Sign Up / Forgot Password names */
    div[data-testid="stRadio"] {
        width: 100% !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: 1fr !important;
        width: 100% !important;
        gap: 0.55rem !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        display: flex !important;
        width: 100% !important;
        min-height: 44px !important;
        margin: 0 !important;
        padding: 0.65rem 0.8rem !important;
        align-items: center !important;
        border: 1px solid #CBE0E8 !important;
        border-radius: 10px !important;
        background: #F8FCFE !important;
        box-sizing: border-box !important;
        overflow: visible !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: auto !important;
        max-width: none !important;
        margin: 0 0 0 0.35rem !important;
        color: #18323F !important;
        font-size: 0.94rem !important;
        line-height: 1.25 !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #167D9A !important;
        background: #E8F6F8 !important;
    }

    /* Cards */
    .stat-card,
    .quick-card,
    .patient-card,
    .sidebar-profile {
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

    .stat-card {
        min-height: auto !important;
        padding: 16px !important;
    }

    .stat-card .value {
        font-size: 1.7rem !important;
    }

    .quick-card {
        min-height: auto !important;
        padding: 14px !important;
    }

    .patient-card {
        padding: 15px !important;
    }

    .section-title {
        font-size: 1.18rem !important;
        line-height: 1.35 !important;
    }

    /* Inputs and buttons */
    .stButton > button,
    .stDownloadButton > button,
    button[kind="primary"],
    button[kind="secondary"] {
        width: 100% !important;
        min-height: 44px !important;
        white-space: normal !important;
    }

    input,
    textarea,
    [data-baseweb="select"] > div {
        font-size: 16px !important;
    }

    div[data-testid="stFileUploader"] {
        padding: 8px !important;
    }

    div[data-testid="stMetric"] {
        padding: 14px !important;
        min-height: auto !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
    }

    /* Tabs remain usable on narrow screens */
    button[data-baseweb="tab"] {
        white-space: nowrap !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        font-size: 0.88rem !important;
    }

    div[data-baseweb="tab-list"] {
        overflow-x: auto !important;
        scrollbar-width: thin;
    }

    /* Tables and charts */
    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        overflow-x: auto !important;
        border-radius: 10px !important;
    }

    /* Sidebar opens as an overlay and uses a sensible width */
    section[data-testid="stSidebar"] {
        min-width: 270px !important;
        max-width: 82vw !important;
    }

    section[data-testid="stSidebar"] > div {
        width: 100% !important;
    }

    .footer-note {
        font-size: 0.76rem !important;
        padding: 22px 4px 6px !important;
    }
}

/* Small phones */
@media only screen and (max-width: 480px) {
    .block-container {
        padding-left: 0.55rem !important;
        padding-right: 0.55rem !important;
    }

    .hero {
        padding: 17px 15px !important;
    }

    .hero h1 {
        font-size: 1.45rem !important;
    }

    .auth-heading {
        display: block !important;
        width: 100% !important;
        text-align: center !important;
    }

    .auth-heading h1 {
        display: block !important;
        visibility: visible !important;
        font-size: 1.55rem !important;
        line-height: 1.2 !important;
        margin: 0 0 0.35rem !important;
    }

    .auth-heading h3,
    .auth-heading p {
        display: block !important;
        visibility: visible !important;
    }

    .stat-card .label,
    .stat-card .hint,
    .quick-card,
    .patient-card p {
        font-size: 0.85rem !important;
    }

    .patient-card h4 {
        font-size: 1rem !important;
    }
}

</style>
""", unsafe_allow_html=True)
# ==========================================
# Authentication Helpers
# ==========================================
def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def authenticate_registered_user(username, password):
    connection = None
    cursor = None

    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, full_name, username, email, password
            FROM users
            WHERE username = %s OR email = %s
            LIMIT 1
            """,
            (username, username)
        )
        user = cursor.fetchone()

        if not user:
            return None

        stored_password = str(user.get("password", ""))
        entered_hash = hash_password(password)

        # Supports newly hashed passwords and any earlier plain-text test users.
        if stored_password == entered_hash or stored_password == password:
            return user

        return None

    except Exception as error:
        print(f"Login error: {error}")
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ==========================================
# Professional Login and Sign-Up Page
# ==========================================
def show_authentication_page():
    st.markdown(
        """
        <div class="auth-heading">
            <h1>🩺 MedIntel AI</h1>
            <h3>AI-Powered Medical Report Analyzer</h3>
            <p>Secure • Fast • AI-Powered Healthcare Analytics</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1, 1.35, 1])

    with center:
        with st.container(border=True):
            auth_mode = st.radio(
                "Account access",
                ["🔐 Login", "📝 Sign Up", "🔑 Forgot Password"],
                horizontal=True,
                label_visibility="collapsed",
                key="auth_mode"
            )

            if auth_mode == "🔐 Login":
                st.markdown(
                    "<h2 style='text-align:center;color:#0B4F6C;'>Welcome Back 👋</h2>",
                    unsafe_allow_html=True
                )
                st.caption("Sign in with your username or email to continue.")

                with st.form("login_form"):
                    login_username = st.text_input(
                        "👤 Username or Email",
                        placeholder="Enter username or email"
                    )
                    login_password = st.text_input(
                        "🔒 Password",
                        type="password",
                        placeholder="Enter password"
                    )
                    remember_me = st.checkbox("Remember me")
                    login_button = st.form_submit_button(
                        "🔐 Login",
                        type="primary",
                        use_container_width=True
                    )

                if login_button:
                    login_username = login_username.strip()

                    if not login_username or not login_password:
                        st.warning("Please enter your username/email and password.")
                    elif login_username == "admin" and login_password == "admin123":
                        st.session_state.logged_in = True
                        st.session_state.user_name = "Administrator"
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        user = authenticate_registered_user(
                            login_username,
                            login_password
                        )

                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user_name = user.get(
                                "full_name",
                                user.get("username", "User")
                            )
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid username/email or password.")

                st.markdown(
                    """
                    <div class="auth-note">
                        <strong>Demo administrator account</strong><br>
                        Username: admin<br>
                        Password: admin123
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif auth_mode == "📝 Sign Up":
                st.markdown(
                    "<h2 style='text-align:center;color:#0B4F6C;'>Create Account 📝</h2>",
                    unsafe_allow_html=True
                )
                st.caption("Register securely to access MedIntel AI.")

                with st.form("signup_form", clear_on_submit=False):
                    full_name = st.text_input(
                        "👤 Full Name",
                        placeholder="Enter your full name"
                    )
                    signup_username = st.text_input(
                        "🪪 Username",
                        placeholder="Choose a username"
                    )
                    email = st.text_input(
                        "✉️ Email",
                        placeholder="Enter your email address"
                    )
                    signup_password = st.text_input(
                        "🔒 Password",
                        type="password",
                        placeholder="Create a password"
                    )
                    confirm_password = st.text_input(
                        "🔒 Confirm Password",
                        type="password",
                        placeholder="Re-enter your password"
                    )
                    accept_terms = st.checkbox(
                        "I agree to use this educational healthcare platform responsibly."
                    )
                    signup_button = st.form_submit_button(
                        "✅ Create Account",
                        type="primary",
                        use_container_width=True
                    )

                if signup_button:
                    full_name = full_name.strip()
                    signup_username = signup_username.strip()
                    email = email.strip().lower()

                    if not all([
                        full_name, signup_username, email,
                        signup_password, confirm_password
                    ]):
                        st.warning("Please complete all required fields.")
                    elif " " in signup_username:
                        st.warning("Username must not contain spaces.")
                    elif len(signup_username) < 3:
                        st.warning("Username must contain at least 3 characters.")
                    elif "@" not in email or "." not in email.split("@")[-1]:
                        st.warning("Please enter a valid email address.")
                    elif len(signup_password) < 6:
                        st.warning("Password must contain at least 6 characters.")
                    elif signup_password != confirm_password:
                        st.warning("Passwords do not match.")
                    elif not accept_terms:
                        st.warning("Please accept the responsible-use agreement.")
                    elif user_exists(signup_username, email):
                        st.error("That username or email is already registered.")
                    else:
                        created = create_user(
                            full_name,
                            signup_username,
                            email,
                            hash_password(signup_password)
                        )

                        if created:
                            st.success(
                                "Account created successfully! Select Login and use your new credentials."
                            )
                        else:
                            st.error(
                                "The account could not be created. Please check the database connection."
                            )


            else:
                st.markdown("<h2 style='text-align:center;color:#0B4F6C;'>Reset Password 🔑</h2>", unsafe_allow_html=True)
                st.caption("Enter your registered username or email and create a new password.")
                with st.form("forgot_password_form"):
                    reset_username = st.text_input("👤 Username or Email")
                    new_password = st.text_input("🔒 New Password", type="password")
                    confirm_new_password = st.text_input("🔒 Confirm New Password", type="password")
                    reset_button = st.form_submit_button("🔑 Reset Password", use_container_width=True)
                if reset_button:
                    if new_password != confirm_new_password:
                        st.error("Passwords do not match.")
                    else:
                        ok = reset_user_password(reset_username.strip(), hash_password(new_password))
                        if ok:
                            st.success("Password reset successfully! Please login.")
                        else:
                            st.error("User not found.")

            st.divider()
            st.caption("© 2026 MedIntel AI • Educational demonstration platform")


# ==========================================
# Show Authentication Before Application
# ==========================================
if not st.session_state.logged_in:
    show_authentication_page()
    st.stop()

# =====================================================
# Reusable UI Components
# =====================================================
def render_hero(title, subtitle):
    today_text = date.today().strftime("%d %B %Y")
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-grid">
                <div>
                    <h1>🩺 {title}</h1>
                    <p>{subtitle}</p>
                </div>
                <div class="hero-date">
                    <strong>Welcome back 👋</strong><br>
                    <span>{today_text}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_footer():
    st.markdown(
        """
        <div class="footer-note">
            <div class="footer-line"></div>
            <strong>MedIntel AI v1.0</strong><br>
            Developed with Python, Streamlit, Groq AI and MySQL<br>
            © 2026 MedIntel AI · Educational demonstration only<br>
            Not a substitute for professional medical advice.
        </div>
        """,
        unsafe_allow_html=True
    )


def stat_card(label, value, hint, css_class, icon):
    st.markdown(
        f"""
        <div class="stat-card {css_class}">
            <div class="label">{icon} {label}</div>
            <div class="value">{value}</div>
            <div class="hint">{hint}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def go_to(page_name):
    st.session_state.next_page = page_name
    st.rerun()


if "next_page" in st.session_state:
    st.session_state.navigation = st.session_state.next_page
    del st.session_state.next_page


# =====================================================
# Logout Helper
# =====================================================
def logout_user():
    """Clear the current login session and return to the login page."""
    st.session_state.clear()
    st.session_state.logged_in = False


# =====================================================
# Sidebar Navigation
# =====================================================
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-profile">
            <h3>🩺 MedIntel AI</h3>
            <p>Healthcare Analytics Platform</p>
            <p><strong>{st.session_state.get("user_name", "Administrator")}</strong></p>
            <span class="system-online">● System Online</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📤 New Analysis",
            "📋 Patient History",
            "ℹ️ About Project"
        ],
        key="navigation",
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("### Core Modules")
    st.markdown(
        """
        - PDF report extraction
        - Clinical parameter analysis
        - Risk and condition prediction
        - Groq-powered AI insights
        - MySQL patient history
        - Downloadable PDF reports
        """
    )
    st.info("Version 1.0 · Interview demonstration build")

    st.button(
        "🚪 Logout",
        key="logout_button",
        use_container_width=True,
        on_click=logout_user
    )
    

    


# =====================================================
# Dashboard Page
# =====================================================
if page == "🏠 Dashboard":
    render_hero(
        "MedIntel AI",
        "Healthcare analytics dashboard for faster, clearer and structured medical-report review."
    )

    try:
        dashboard_reports = get_all_patient_reports() or []
    except Exception:
        dashboard_reports = []

    total_reports = len(dashboard_reports)
    unique_patients = len({
        str(item.get("phone", "")).strip()
        for item in dashboard_reports
        if str(item.get("phone", "")).strip()
    })
    today_iso = date.today().isoformat()
    reports_today = sum(
        1 for item in dashboard_reports
        if str(item.get("report_date", ""))[:10] == today_iso
        or str(item.get("created_at", ""))[:10] == today_iso
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Saved Reports", total_reports, "Reports stored securely", "blue", "📄")
    with c2:
        stat_card("Total Patients", unique_patients, "Unique patient records", "green", "👥")
    with c3:
        stat_card("Reports Today", reports_today, "Analysed or added today", "orange", "📅")
    with c4:
        stat_card("System Status", "Online", "All core modules available", "purple", "✅")

    st.write("")
    st.markdown('<div class="section-title">Quick Actions</div>', unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.markdown('<div class="quick-card"><strong>📤 New Analysis</strong><br><span style="color:#6B7F89">Upload and analyse a report</span></div>', unsafe_allow_html=True)
        if st.button("Start Analysis", key="quick_new"):
            go_to("📤 New Analysis")
    with q2:
        st.markdown('<div class="quick-card"><strong>📋 Patient History</strong><br><span style="color:#6B7F89">Review saved patient records</span></div>', unsafe_allow_html=True)
        if st.button("Open History", key="quick_history"):
            go_to("📋 Patient History")
    with q3:
        st.markdown('<div class="quick-card"><strong>📄 Reports</strong><br><span style="color:#6B7F89">Download from patient history</span></div>', unsafe_allow_html=True)
        if st.button("View Reports", key="quick_reports"):
            go_to("📋 Patient History")
    with q4:
        st.markdown('<div class="quick-card"><strong>ℹ️ Project</strong><br><span style="color:#6B7F89">View workflow and capabilities</span></div>', unsafe_allow_html=True)
        if st.button("About Project", key="quick_about"):
            go_to("ℹ️ About Project")

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="section-title">Platform Overview</div>', unsafe_allow_html=True)
        st.write(
            "MedIntel AI extracts important medical values from uploaded PDF reports, "
            "checks normal ranges, detects risk factors, predicts possible conditions, "
            "recommends specialists and generates a clear AI-assisted explanation."
        )
        st.success("Choose **New Analysis** to analyse a report, or open **Patient History** to review saved records.")

    if dashboard_reports:
        st.write("")
        with st.container(border=True):
            st.markdown('<div class="section-title">Recent Reports</div>', unsafe_allow_html=True)
            st.dataframe(dashboard_reports[:5], use_container_width=True, hide_index=True)

    render_footer()


# =====================================================
# New Analysis Page
# =====================================================
elif page == "📤 New Analysis":
    render_hero(
        "New Medical Analysis",
        "Enter patient information, upload a PDF report and generate structured clinical insights."
    )

    with st.container(border=True):
        st.markdown('<div class="section-title">👤 Patient Information</div>', unsafe_allow_html=True)
        patient = patient_information()

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="section-title">📤 Upload Medical Report</div>', unsafe_allow_html=True)
        st.caption("Supported format: text-based PDF medical reports")
        uploaded_file = st.file_uploader(
            "Choose a medical report",
            type=["pdf"],
            label_visibility="collapsed"
        )

    if uploaded_file is not None:
        st.success("✅ Report uploaded successfully")
        file_col1, file_col2, file_col3 = st.columns(3)
        file_col1.metric("File Name", uploaded_file.name)
        file_col2.metric("File Type", uploaded_file.type or "PDF")
        file_col3.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")

        try:
            extracted_text = extract_pdf_text(uploaded_file)
            cleaned_text = clean_text(extracted_text)

            if not cleaned_text:
                st.warning("No readable text was found in the uploaded PDF.")
            else:
                with st.expander("📄 View Extracted Report Text"):
                    st.text_area("Report Text", cleaned_text, height=260, label_visibility="collapsed")

                raw_parameters = extract_parameters(cleaned_text)
                parameters = normalise_parameters(raw_parameters)
                range_results = check_normal_ranges_safe(parameters)
                risk_factors = detect_risk_factors_safe(range_results)
                specialists = suggest_specialists_safe(range_results)
                predicted_diseases = predict_disease_safe(parameters)
                dashboard = calculate_dashboard_safe(range_results, risk_factors)

                st.write("")
                st.markdown('<div class="section-title">📊 Clinical Overview</div>', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("📋 Parameters", dashboard["Total Parameters"])
                col2.metric("🟢 Normal", dashboard["Normal"])
                col3.metric("🔴 Abnormal", dashboard["Abnormal"])
                col4.metric("⚠️ Risks", dashboard["Risk Factors"])

                if parameters:
                    st.write("")
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "🧪 Parameters", "📈 Visualisation", "⚠️ Clinical Findings", "🧠 AI Analysis"
                    ])

                    with tab1:
                        analysis_table = []
                        for parameter, result in range_results.items():
                            status = result.get("Status", "Unknown")
                            icon = "🟢" if status == "Normal" else "🔴" if status in ["Low", "High"] else "⚪"
                            analysis_table.append({
                                "Parameter": parameter,
                                "Value": result.get("Value"),
                                "Status": f"{icon} {status}"
                            })
                        st.dataframe(analysis_table, use_container_width=True, hide_index=True)

                    with tab2:
                        chart_col1, chart_col2 = st.columns([1.35, 1])
                        with chart_col1:
                            st.markdown("#### Parameter Values")
                            try:
                                bar_chart = create_bar_chart(parameters)
                                bar_chart.set_size_inches(6, 3.8)
                                bar_chart.tight_layout()
                                st.pyplot(bar_chart, use_container_width=True)
                                plt.close(bar_chart)
                            except Exception as chart_error:
                                st.warning(f"Bar chart could not be displayed: {chart_error}")
                        with chart_col2:
                            st.markdown("#### Normal vs Abnormal")
                            try:
                                chart_range_results = prepare_chart_range_results(range_results)
                                pie_chart = create_pie_chart(chart_range_results)
                                pie_chart.set_size_inches(4, 3.8)
                                pie_chart.tight_layout()
                                st.pyplot(pie_chart, use_container_width=True)
                                plt.close(pie_chart)
                            except Exception as chart_error:
                                st.warning(f"Pie chart could not be displayed: {chart_error}")

                    with tab3:
                        finding_col1, finding_col2 = st.columns(2)
                        with finding_col1:
                            st.markdown("#### Risk Factors")
                            if risk_factors:
                                for risk in risk_factors:
                                    st.warning(risk)
                            else:
                                st.success("No major risk factors detected.")
                        with finding_col2:
                            st.markdown("#### Suggested Specialist")
                            for specialist in specialists:
                                st.info(specialist)

                        st.markdown("#### Preliminary Condition Prediction")
                        st.caption("These results are preliminary and are not a confirmed diagnosis.")
                        if predicted_diseases:
                            st.dataframe(
                                [{"Predicted Condition": d.get("Disease"), "Probability": d.get("Probability")} for d in predicted_diseases],
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.success("No major conditions predicted from the extracted parameters.")

                    with tab4:
                        st.markdown("#### Generate AI Medical Insights")
                        st.caption("The report is saved to MySQL after successful AI analysis.")

                        if st.button("🧠 Analyse Report with AI", type="primary"):
                            patient_name = str(patient.get("Patient Name", "")).strip()
                            age = patient.get("Age")
                            gender = patient.get("Gender")
                            phone = str(patient.get("Phone", "")).strip()
                            report_type = patient.get("Report Type")
                            report_date = patient.get("Report Date")

                            if not patient_name:
                                st.warning("Please enter the patient name before analysis.")
                            elif not phone:
                                st.warning("Please enter the patient phone number before analysis.")
                            elif not phone.isdigit() or len(phone) != 10:
                                st.warning("Please enter a valid 10-digit phone number.")
                            else:
                                progress = st.progress(0, text="Preparing medical report...")
                                progress.progress(20, text="Extracting clinical parameters...")
                                progress.progress(45, text="Checking normal ranges and risks...")
                                progress.progress(70, text="Generating Groq AI insights...")

                                with st.spinner("AI is analysing the medical report..."):
                                    analysis = analyze_report(cleaned_text)

                                progress.progress(100, text="Analysis complete")

                                if analysis:
                                    st.success("✅ Analysis completed successfully")
                                    with st.container(border=True):
                                        st.markdown('<div class="section-title">🧠 AI Medical Summary</div>', unsafe_allow_html=True)
                                        st.markdown(analysis)
                                    st.warning(
                                        "This AI-generated analysis is for informational purposes only. "
                                        "Consult a qualified medical professional."
                                    )

                                    saved = save_patient_report(
                                        patient_name=patient_name,
                                        age=age,
                                        gender=gender,
                                        phone=phone,
                                        report_type=report_type,
                                        report_date=report_date,
                                        extracted_text=cleaned_text,
                                        ai_analysis=analysis
                                    )
                                    if saved:
                                        st.success("✅ Patient report saved to MySQL")
                                    else:
                                        st.error("Analysis completed, but the report could not be saved.")
                                else:
                                    st.error("AI analysis could not be generated.")
                else:
                    st.warning("No supported medical parameters were found in this report.")

        except Exception as error:
            st.error(f"Error processing report: {error}")
            with st.expander("Technical error details"):
                st.code(traceback.format_exc(), language="text")

    render_footer()


# =====================================================
# Patient History Page
# =====================================================
elif page == "📋 Patient History":
    render_hero(
        "Patient History",
        "Search, review and download previously analysed patient reports."
    )

    with st.container(border=True):
        search_patient = st.text_input(
            "Search patient",
            placeholder="Enter patient name or phone number"
        )

    try:
        reports = get_all_patient_reports() or []
        if search_patient:
            search_text = search_patient.lower().strip()
            reports = [
                report for report in reports
                if search_text in str(report.get("patient_name", "")).lower()
                or search_text in str(report.get("phone", "")).lower()
            ]

        if reports:
            st.write("")
            st.markdown('<div class="section-title">Patient Records</div>', unsafe_allow_html=True)
            st.caption("Select a patient card below, then use the report selector to open the complete record.")

            card_columns = st.columns(2)
            for index, report in enumerate(reports[:6]):
                with card_columns[index % 2]:
                    st.markdown(
                        f"""
                        <div class="patient-card">
                            <h4>👤 {report.get('patient_name', 'Unknown Patient')}</h4>
                            <p><strong>Report:</strong> {report.get('report_type', 'Medical Report')}</p>
                            <p><strong>Date:</strong> {str(report.get('report_date', 'Not available'))}</p>
                            <p><strong>Phone:</strong> {report.get('phone', 'Not available')}</p>
                            <span class="badge">Saved Record</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.write("")
            select_col1, select_col2 = st.columns([1, 3])
            select_col1.metric("Matching Reports", len(reports))
            selected_id = select_col2.selectbox(
                "Select Patient Report",
                [report["id"] for report in reports],
                format_func=lambda report_id: next(
                    (f"#{item['id']} · {item.get('patient_name', 'Unknown')} · {item.get('phone', '')}" for item in reports if item["id"] == report_id),
                    str(report_id)
                )
            )

            with st.expander("View complete report table"):
                st.dataframe(reports, use_container_width=True, hide_index=True)

            selected_report = get_patient_report_by_id(selected_id)
            if selected_report:
                st.write("")
                with st.container(border=True):
                    st.markdown('<div class="section-title">📄 Selected Patient Report</div>', unsafe_allow_html=True)
                    info1, info2, info3, info4 = st.columns(4)
                    info1.metric("Patient", selected_report.get("patient_name", "—"))
                    info2.metric("Age", selected_report.get("age", "—"))
                    info3.metric("Gender", selected_report.get("gender", "—"))
                    info4.metric("Phone", selected_report.get("phone", "—"))

                    history_tab1, history_tab2 = st.tabs(["📄 Extracted Report", "🧠 AI Medical Analysis"])
                    with history_tab1:
                        st.text_area(
                            "Saved Report",
                            selected_report.get("extracted_text", ""),
                            height=260,
                            disabled=True,
                            label_visibility="collapsed"
                        )
                    with history_tab2:
                        ai_analysis = selected_report.get("ai_analysis", "")
                        if ai_analysis:
                            st.markdown(ai_analysis)
                        else:
                            st.info("No AI analysis is available for this report.")

                    try:
                        pdf_data = generate_patient_pdf(selected_report)
                        st.download_button(
                            label="⬇️ Download Full Patient Report as PDF",
                            data=pdf_data,
                            file_name=f"{selected_report.get('patient_name', 'patient')}_medical_report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as pdf_error:
                        st.error(f"PDF generation error: {pdf_error}")
            else:
                st.info("Selected report could not be loaded.")
        else:
            st.info("No matching patient reports were found.")

    except Exception as error:
        st.error(f"Error loading patient history: {error}")

    render_footer()


# =====================================================
# About Page
# =====================================================
else:
    render_hero(
        "About MedIntel AI",
        "Project overview, workflow, capabilities and responsible-use limitations."
    )

    left, right = st.columns([1.25, 1])
    with left:
        with st.container(border=True):
            st.markdown('<div class="section-title">Project Overview</div>', unsafe_allow_html=True)
            st.write(
                "MedIntel AI is an AI-powered medical report analysis system designed to "
                "convert complex clinical reports into structured and understandable insights."
            )
            st.markdown(
                """
                **Main capabilities**
                - Extract text from PDF medical reports
                - Identify supported clinical parameters
                - Compare results with normal ranges
                - Detect possible risks and conditions
                - Recommend an appropriate specialist
                - Generate Groq-powered medical explanations
                - Store and retrieve patient history using MySQL
                - Export a complete patient report as PDF
                """
            )

    with right:
        with st.container(border=True):
            st.markdown('<div class="section-title">System Workflow</div>', unsafe_allow_html=True)
            st.markdown(
                """
                **1.** Enter patient details  
                **2.** Upload a medical report PDF  
                **3.** Extract and clean report text  
                **4.** Detect clinical parameters  
                **5.** Analyse ranges and risks  
                **6.** Generate AI insights  
                **7.** Save results to MySQL  
                **8.** Review or download report history
                """
            )

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="section-title">Technology Used</div>', unsafe_allow_html=True)
        tech1, tech2, tech3, tech4 = st.columns(4)
        tech1.metric("Frontend", "Streamlit")
        tech2.metric("Backend", "Python")
        tech3.metric("AI", "Groq")
        tech4.metric("Database", "MySQL")

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="section-title">Important Disclaimer</div>', unsafe_allow_html=True)
        st.warning(
            "MedIntel AI is an educational project. Its predictions and AI-generated text "
            "must not be treated as a confirmed diagnosis or a replacement for a licensed doctor."
        )

    render_footer()
