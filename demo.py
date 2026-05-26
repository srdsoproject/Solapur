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
        # Using your actual secrets key
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        gc = gspread.authorize(creds)
        
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.worksheet(SHEET_NAME)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Failed to connect to Google Sheet: {str(e)}")
        st.info("🔧 Check: Secrets are saved correctly under [gcp_service_account]")
        return pd.DataFrame()

# ====================== MAIN PORTAL ======================
def main_portal():
    st.title("🚉 Solapur Division Operating Department")
    st.subheader("Equipment Inventory Portal")
    st.caption(f"Last Updated: {datetime.now().strftime('%d %B %Y, %H:%M')}")

    df = load_google_sheet()

    if df.empty:
        st.warning("Could not load data. Please verify your secrets and sheet sharing.")
        return

    # Sidebar Navigation
    page = st.sidebar.radio("Navigation", ["Dashboard", "All Stations", "Search"])

    if page == "Dashboard":
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Stations", len(df))
        with col2:
            st.metric("Equipment Types", len(df.columns) - 1)

        st.subheader("Preview")
        st.dataframe(df.head(10), use_container_width=True)

    elif page == "All Stations":
        st.subheader("Station-wise Equipment")
        search = st.text_input("🔍 Search Station", "")

        filtered_df = df
        if search:
            filtered_df = df[df['STATION'].astype(str).str.contains(search, case=False)]

        for _, row in filtered_df.iterrows():
            with st.expander(f"🚉 {row.get('STATION', 'Unknown Station')}", expanded=False):
                cols = st.columns(3)
                for i, col in enumerate([c for c in df.columns if c != "STATION"]):
                    with cols[i % 3]:
                        val = row.get(col, "")
                        st.metric(col, val if val != "" else "0")

    elif page == "Search":
        st.subheader("Search Records")
        term = st.text_input("Enter Station or Item")
        if term:
            result = df[df.astype(str).apply(lambda x: x.str.contains(term, case=False)).any(axis=1)]
            if not result.empty:
                st.dataframe(result, use_container_width=True)
            else:
                st.info("No matching records found.")

# ====================== RUN ======================
main_portal()
