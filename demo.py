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

# ====================== LOGIN FUNCTION ======================

def login():

    # Session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # If already logged in
    if st.session_state.authenticated:
        return True

    st.title("🔐 Login Required")

    username = st.text_input("User ID")
    password = st.text_input("Password", type="password")

    login_button = st.button("Login")

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
        🔧 Please verify:
        1. Secrets are correctly added
        2. Google Sheet is shared with service account
        3. SHEET_ID and SHEET_NAME are correct
        """)

        return pd.DataFrame()

# ====================== MAIN PORTAL ======================

def main_portal():

    st.title("🚉 Solapur Division Operating Department")

    st.subheader("Equipment Inventory Portal")

    st.caption(
        f"Last Updated: {datetime.now().strftime('%d %B %Y, %H:%M')}"
    )

    # ====================== SIDEBAR ======================

    st.sidebar.success("✅ Logged In")

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "All Stations", "Search"]
    )

    # ====================== LOAD DATA ======================

    df = load_google_sheet()

    if df.empty:
        st.warning("⚠️ No data available.")
        return

    # ====================== DASHBOARD ======================

    if page == "Dashboard":

        st.subheader("Dashboard Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Stations",
                len(df)
            )

        with col2:
            st.metric(
                "Equipment Types",
                len(df.columns) - 1
            )

        st.divider()

        st.subheader("Preview Data")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

    # ====================== ALL STATIONS ======================

    elif page == "All Stations":

        st.subheader("📍 Station-wise Equipment")

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

        for _, row in filtered_df.iterrows():

            station_name = row.get(
                "STATION",
                "Unknown Station"
            )

            with st.expander(f"🚉 {station_name}"):

                equipment_columns = [
                    col for col in df.columns
                    if col != "STATION"
                ]

                cols = st.columns(3)

                for i, col in enumerate(equipment_columns):

                    value = row.get(col, "")

                    if value == "" or pd.isna(value):
                        value = 0

                    with cols[i % 3]:

                        st.metric(
                            label=col,
                            value=value
                        )

    # ====================== SEARCH ======================

    elif page == "Search":

        st.subheader("🔎 Search Records")

        term = st.text_input(
            "Enter Station or Equipment Name"
        )

        if term:

            result = df[
                df.astype(str)
                .apply(
                    lambda x: x.str.contains(
                        term,
                        case=False,
                        na=False
                    )
                )
                .any(axis=1)
            ]

            if not result.empty:

                st.success(
                    f"Found {len(result)} matching record(s)."
                )

                st.dataframe(
                    result,
                    use_container_width=True
                )

            else:
                st.info("No matching records found.")

# ====================== RUN APP ======================

if __name__ == "__main__":
    main_portal()
