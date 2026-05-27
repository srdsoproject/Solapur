import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Solapur Division Operating",
    page_icon="🚉",
    layout="wide"
)

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>

/* ================= ROOT VARIABLES ================= */

:root {

    --bg-color: #f3f6fb;
    --card-bg: #ffffff;
    --text-color: #0f172a;
    --secondary-text: #64748b;
    --border-color: #dbe2ea;

    --sidebar-bg: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    --header-bg: linear-gradient(135deg, #2563eb, #1e3a8a);

    --metric-bg: #f8fafc;
    --hover-bg: #eff6ff;

    --button-bg: #2563eb;
    --button-hover: #1d4ed8;

    --shadow: 0 4px 14px rgba(0,0,0,0.06);
}

/* ================= DARK MODE ================= */

@media (prefers-color-scheme: dark) {

    :root {

        --bg-color: #0e1117;
        --card-bg: #161b22;
        --text-color: #f1f5f9;
        --secondary-text: #94a3b8;
        --border-color: #2d3748;

        --sidebar-bg: linear-gradient(180deg, #020617 0%, #111827 100%);
        --header-bg: linear-gradient(135deg, #1e3a8a, #0f172a);

        --metric-bg: #1e293b;
        --hover-bg: #1d4ed8;

        --button-bg: #2563eb;
        --button-hover: #3b82f6;

        --shadow: 0 6px 18px rgba(0,0,0,0.35);
    }
}

/* ================= MAIN APP ================= */

.stApp {
    background-color: var(--bg-color);
    color: var(--text-color);
}

/* ================= CONTAINER ================= */

.block-container {
    padding-top: 1rem;
    max-width: 1450px;
}

/* ================= SIDEBAR ================= */

[data-testid="stSidebar"] {
    background: var(--sidebar-bg);
}

[data-testid="stSidebar"] * {
    color: white;
}

/* ================= HEADER ================= */

.header-box {

    background: var(--header-bg);
    padding: 30px;
    border-radius: 22px;

    margin-bottom: 24px;

    box-shadow: var(--shadow);
}

.header-box h1 {
    color: white;
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 8px;
}

.header-box h4 {
    color: #dbeafe;
    font-weight: 400;
}

.small-text {
    color: #cbd5e1;
    font-size: 14px;
}

/* ================= METRICS ================= */

[data-testid="metric-container"] {

    background: var(--card-bg);

    border: 1px solid var(--border-color);

    border-radius: 18px;

    padding: 18px;

    box-shadow: var(--shadow);
}

/* ================= STATION CARD ================= */

.station-card {

    background: var(--card-bg);

    border: 1px solid var(--border-color);

    border-radius: 22px;

    padding: 24px;

    margin-bottom: 24px;

    box-shadow: var(--shadow);

    transition: all 0.2s ease;
}

.station-card:hover {

    transform: translateY(-2px);

    box-shadow: 0 10px 24px rgba(0,0,0,0.12);
}

/* ================= STATION TITLE ================= */

.station-title {

    font-size: 26px;

    font-weight: 700;

    color: var(--text-color);

    border-bottom: 1px solid var(--border-color);

    padding-bottom: 12px;

    margin-bottom: 22px;
}

/* ================= EQUIPMENT BOX ================= */

.metric-box {

    background: var(--metric-bg);

    border: 1px solid var(--border-color);

    border-radius: 16px;

    padding: 18px;

    text-align: center;

    margin-bottom: 14px;

    transition: 0.2s ease;
}

.metric-box:hover {

    background: var(--hover-bg);

    border-color: #3b82f6;
}

/* ================= LABEL ================= */

.metric-label {

    color: var(--secondary-text);

    font-size: 13px;

    font-weight: 600;

    margin-bottom: 8px;
}

/* ================= VALUE ================= */

.metric-value {

    color: var(--text-color);

    font-size: 28px;

    font-weight: 700;
}

/* ================= INPUT ================= */

.stTextInput input {

    background-color: var(--card-bg) !important;

    color: var(--text-color) !important;

    border: 1px solid var(--border-color) !important;

    border-radius: 12px !important;
}

.stTextInput input:focus {

    border: 1px solid #3b82f6 !important;

    box-shadow: 0 0 0 1px #3b82f6 !important;
}

/* ================= BUTTON ================= */

.stButton > button {

    background: var(--button-bg);

    color: white;

    border: none;

    border-radius: 12px;

    font-weight: 600;

    transition: 0.2s ease;
}

.stButton > button:hover {

    background: var(--button-hover);

    transform: translateY(-1px);
}

/* ================= DIVIDER ================= */

hr {
    border-color: var(--border-color);
}

/* ================= MOBILE ================= */

@media (max-width: 768px) {

    .header-box h1 {
        font-size: 28px;
    }

    .station-title {
        font-size: 22px;
    }

    .metric-value {
        font-size: 22px;
    }
}

</style>
""", unsafe_allow_html=True)

# ====================== LOGIN FUNCTION ======================
def login():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔐 Login Required")

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown("### Solapur Division Operating Portal")

        username = st.text_input("User ID")
        password = st.text_input("Password", type="password")

        login_button = st.button(
            "Login",
            use_container_width=True
        )

        if login_button:

            secret_username = st.secrets["APP_USERNAME"]
            secret_password = st.secrets["APP_PASSWORD"]

            if username == secret_username and password == secret_password:
                st.session_state.authenticated = True
                st.success("✅ Login successful")
                st.rerun()

            else:
                st.error("❌ Invalid User ID or Password")

    return False

# ====================== AUTH CHECK ======================
if not login():
    st.stop()

# ====================== LOAD SECRET CONFIG ======================
SHEET_ID = st.secrets["SHEET_ID"]
SHEET_NAME = st.secrets["SHEET_NAME"]

# ====================== LOAD GOOGLE SHEET ======================
@st.cache_data(ttl=300)
def load_google_sheet():

    try:

        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )

        gc = gspread.authorize(creds)

        sh = gc.open_by_key(SHEET_ID)

        worksheet = sh.worksheet(SHEET_NAME)

        data = worksheet.get_all_records()

        df = pd.DataFrame(data)

        # Clean column names
        df.columns = df.columns.str.strip()

        return df

    except Exception as e:

        st.error("❌ Failed to connect to Google Sheet")
        st.exception(e)

        st.info("""
        Please verify:
        1. Secrets are correctly added
        2. Google Sheet is shared with service account
        3. SHEET_ID and SHEET_NAME are correct
        """)

        return pd.DataFrame()

# ====================== MAIN PORTAL ======================
def main_portal():

    # ====================== HEADER ======================
    st.markdown(f"""
    <div class="header-box">
        <h1>🚉 Solapur Division Operating Department</h1>
        <h4>Equipment Inventory Management System</h4>
        <div class="small-text">
            Last Updated: {datetime.now().strftime('%d %B %Y, %H:%M')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ====================== SIDEBAR ======================
    st.sidebar.success("✅ Logged In")

    if st.sidebar.button("🔄 Refresh Data"):
        load_google_sheet.clear()
        st.success("✅ Data refreshed successfully")
        st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

    # ====================== LOAD DATA ======================
    df = load_google_sheet()

    if df.empty:
        st.warning("⚠️ No data available.")
        return

    # ====================== TOP METRICS ======================
    total_stations = len(df)
    total_equipment = len(df.columns) - 2

    col1, col2 = st.columns(2)

    with col1:
        st.metric("🚏 Total Stations", total_stations)

    with col2:
        st.metric("🛠 Total Equipment Types", total_equipment)

    st.divider()

    # ====================== SEARCH ======================
    search = st.text_input(
        "🔍 Search Station",
        placeholder="Enter station name..."
    )

    filtered_df = df.copy()

    if search:
        filtered_df = df[
            df["STATION"]
            .astype(str)
            .str.contains(search, case=False, na=False)
        ]

    if filtered_df.empty:
        st.info("No stations found.")
        return

    # ====================== STATION VIEW ======================
    for _, row in filtered_df.iterrows():

        station_name = row.get(
            "STATION",
            "Unknown Station"
        )

        st.markdown(f"""
        <div class="station-card">
            <div class="station-title">
                🚉 {station_name}
            </div>
        """, unsafe_allow_html=True)

        equipment_columns = [
            col for col in df.columns
            if col != "STATION"
        ]

        cols = st.columns(4)

        for i, col in enumerate(equipment_columns):

            value = row.get(col, "")

            if value == "" or pd.isna(value):
                value = 0

            with cols[i % 4]:

                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">
                        {col}
                    </div>
                    <div class="metric-value">
                        {value}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ====================== RUN APP ======================
if __name__ == "__main__":
    main_portal()
