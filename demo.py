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
# ====================== CUSTOM CSS ======================
st.markdown("""
<style>

/* Main App Background */
.stApp {
    background-color: #0f1117;
    color: #f1f5f9;
}

/* Main Container */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #000000;
    border-right: 1px solid #262730;
}

[data-testid="stSidebar"] * {
    color: #ffffff;
}

/* Header */
.header-box {
    background: linear-gradient(135deg, #000000, #1e293b);
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 20px;
    border: 1px solid #2d3748;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.4);
}

.header-box h1 {
    color: #ffffff;
    margin-bottom: 5px;
}

.header-box h4 {
    color: #cbd5e1;
    margin-top: 0;
}

.small-text {
    color: #94a3b8;
    font-size: 13px;
}

/* Station Card */
.station-card {
    background: #161b22;
    border: 1px solid #30363d;
    padding: 22px;
    border-radius: 16px;
    margin-bottom: 22px;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.35);
}

/* Station Title */
.station-title {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 18px;
    border-bottom: 1px solid #30363d;
    padding-bottom: 10px;
}

/* Metric Boxes */
.metric-box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    margin-bottom: 12px;
    transition: 0.2s ease-in-out;
}

.metric-box:hover {
    border: 1px solid #58a6ff;
    transform: translateY(-2px);
}

/* Metric Label */
.metric-label {
    font-size: 13px;
    color: #94a3b8;
    margin-bottom: 8px;
    font-weight: 600;
}

/* Metric Value */
.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
}

/* Search Box */
.stTextInput input {
    background-color: #161b22 !important;
    color: white !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
}

/* Buttons */
.stButton > button {
    background-color: #21262d;
    color: white;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 0.5rem 1rem;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #30363d;
    border: 1px solid #58a6ff;
    color: #58a6ff;
}

/* Metrics */
[data-testid="metric-container"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    padding: 15px;
    border-radius: 14px;
}

/* Expander */
.streamlit-expanderHeader {
    background-color: #161b22;
    border-radius: 10px;
    color: white;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Divider */
hr {
    border-color: #30363d;
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
    total_equipment = len(df.columns) - 1

    col1, col2 = st.columns(2)

    with col1:
        st.metric("📍 Total Stations", total_stations)

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
