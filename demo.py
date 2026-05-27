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
# ====================== PROFESSIONAL UI CSS ======================
st.markdown("""
<style>

/* ===== MAIN APP ===== */
.stApp {
    background-color: #f4f6f9;
    color: #1e293b;
}

/* ===== MAIN CONTAINER ===== */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1rem;
    max-width: 1400px;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #cbd5e1;
}

[data-testid="stSidebar"] * {
    color: white;
}

/* ===== HEADER ===== */
.header-box {
    background: linear-gradient(135deg, #1d4ed8, #0f172a);
    padding: 30px;
    border-radius: 20px;
    margin-bottom: 25px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.18);
}

.header-box h1 {
    color: white;
    margin-bottom: 8px;
    font-size: 38px;
    font-weight: 700;
}

.header-box h4 {
    color: #dbeafe;
    margin-top: 0;
    font-weight: 400;
}

.small-text {
    color: #cbd5e1;
    font-size: 14px;
    margin-top: 10px;
}

/* ===== TOP METRICS ===== */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e2e8f0;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

/* ===== STATION CARD ===== */
.station-card {
    background: white;
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 24px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
    transition: 0.2s ease;
}

.station-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

/* ===== STATION TITLE ===== */
.station-title {
    font-size: 26px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 22px;
    padding-bottom: 12px;
    border-bottom: 2px solid #eff6ff;
}

/* ===== EQUIPMENT BOX ===== */
.metric-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px;
    text-align: center;
    margin-bottom: 14px;
    transition: all 0.2s ease;
}

.metric-box:hover {
    border-color: #3b82f6;
    background: #eff6ff;
}

/* ===== EQUIPMENT LABEL ===== */
.metric-label {
    font-size: 13px;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 8px;
}

/* ===== EQUIPMENT VALUE ===== */
.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #0f172a;
}

/* ===== INPUT BOX ===== */
.stTextInput input {
    background-color: white !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 0.65rem !important;
}

.stTextInput input:focus {
    border: 1px solid #2563eb !important;
    box-shadow: 0 0 0 1px #2563eb !important;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.55rem 1rem;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #1d4ed8;
    transform: translateY(-1px);
}

/* ===== DIVIDER ===== */
hr {
    border-color: #e2e8f0;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 10px;
}

/* ===== DATAFRAME ===== */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

/* ===== MOBILE RESPONSIVE ===== */
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
