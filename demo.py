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

# ====================== SHEET CONFIG ======================

SHEET_ID = "1bEQ_o020l2rTmFRKvTjKHQSdrCp3N6BUEXIRybHDios"
SHEET_NAME = "OPTG"

# ====================== LOAD GOOGLE SHEET ======================

@st.cache_data(ttl=300)
def load_google_sheet():
    try:
        # Authenticate using Streamlit Secrets
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )

        # Authorize gspread
        gc = gspread.authorize(creds)

        # Open Google Sheet
        sh = gc.open_by_key(SHEET_ID)

        # Open worksheet
        worksheet = sh.worksheet(SHEET_NAME)

        # Get records
        data = worksheet.get_all_records()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Clean column names
        df.columns = df.columns.str.strip()

        return df

    except Exception as e:
        st.error(f"❌ Failed to connect to Google Sheet")
        st.exception(e)

        st.info("""
        🔧 Please verify:
        1. Secrets are correctly added in Streamlit
        2. Google Sheet is shared with service account email
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

    # Load data
    df = load_google_sheet()

    # If data not loaded
    if df.empty:
        st.warning("⚠️ No data available.")
        return

    # ====================== SIDEBAR ======================

    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "All Stations", "Search"]
    )

    # ====================== DASHBOARD ======================

    if page == "Dashboard":

        st.subheader("Dashboard Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="Total Stations",
                value=len(df)
            )

        with col2:
            st.metric(
                label="Equipment Types",
                value=len(df.columns) - 1
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

        # Filter stations
        if search:
            filtered_df = df[
                df["STATION"]
                .astype(str)
                .str.contains(search, case=False, na=False)
            ]

        if filtered_df.empty:
            st.info("No stations found.")
            return

        # Display stations
        for _, row in filtered_df.iterrows():

            station_name = row.get("STATION", "Unknown Station")

            with st.expander(f"🚉 {station_name}", expanded=False):

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

                st.success(f"Found {len(result)} matching record(s).")

                st.dataframe(
                    result,
                    use_container_width=True
                )

            else:
                st.info("No matching records found.")

# ====================== RUN APP ======================

if __name__ == "__main__":
    main_portal()
