import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import folium
from streamlit_folium import st_folium

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Solapur Division Equipment Inventory Management System",
    page_icon="🚉",
    layout="wide"
)

# ====================== STYLING ENGINE ======================
st.markdown("""
<style>
/* App Canvas Setup */
.stApp {
    background-color: #f8fafc;
    color: #0f172a;
}

html, body, [class*="css"] {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

.block-container {
    padding-top: 2rem;
    max-width: 1500px;
}

/* Sidebar Override */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    box-shadow: 4px 0 10px rgba(0,0,0,0.05);
}
[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

/* Header Component */
.header-box {
    background: linear-gradient(135deg, #1e3a8a 0%, #0369a1 100%);
    padding: 35px;
    border-radius: 16px;
    margin-bottom: 30px;
    box-shadow: 0 10px 25px rgba(30, 58, 138, 0.15);
    border-left: 8px solid #38bdf8;
}
.header-box h1 {
    color: #ffffff !important;
    font-size: 36px;
    font-weight: 800;
    margin: 0 0 10px 0;
    letter-spacing: -0.5px;
}
.header-box h4 {
    color: #e0f2fe !important;
    font-weight: 400;
    margin: 0;
    opacity: 0.9;
}

/* Metrics Displays */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
[data-testid="metric-container"] label {
    color: #475569 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}
[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #1e3a8a !important;
    font-size: 32px !important;
    font-weight: 800 !important;
}

/* Data Presentation Cards */
.station-card-wrapper {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}
.station-title-strip {
    font-size: 22px;
    font-weight: 700;
    color: #1e3a8a !important;
    border-bottom: 2px solid #f1f5f9;
    padding-bottom: 12px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
}

/* Inventory Item Grid Elements */
.metric-box {
    background: #fdfdfd;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.01);
    height: 100%;
}
.metric-box.active-assets {
    border-left: 4px solid #2563eb;
}
.metric-box.zero-assets {
    border-left: 4px solid #cbd5e1;
    background: #f8fafc;
}
.metric-label {
    color: #64748b !important;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.metric-value {
    color: #0f172a !important;
    font-size: 26px;
    font-weight: 800;
}
.metric-value.zero {
    color: #94a3b8 !important;
}

/* Interactive Components styling */
.stButton > button {
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    transition: all 0.2s;
}
</style>
""", unsafe_allow_html=True)

# ====================== LOGIN SERVICE ======================
def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.write("")
        st.write("")
        st.markdown("""
        <div style="background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
            <h2 style="text-align: center; margin-bottom: 5px; color: #1e3a8a;">🚉 Solapur Division</h2>
            <p style="text-align: center; color: #64748b; margin-bottom: 30px;">Safety Branch - Inventory Portal Access</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("User ID")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Secure Sign In", use_container_width=True) #  Fixed line
            
            if submit:
                try:
                    if username == st.secrets["APP_USERNAME"] and password == st.secrets["APP_PASSWORD"]:
                        st.session_state.authenticated = True
                        st.success("✅ Access Authorized.")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Credentials Provided.")
                except KeyError:
                    st.error("🔑 Configuration secrets missing from server execution context.")
    return False

if not login():
    st.stop()

# ====================== DATA PIPELINE ======================
SHEET_ID = st.secrets["SHEET_ID"]
SHEET_NAME = st.secrets["SHEET_NAME"]

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
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error("🚨 Interface Link Exception (Google Sheets Connection Refused)")
        st.exception(e)
        return pd.DataFrame()

# ====================== MAIN SYSTEM APPLICATION ======================
def main_portal():
    # --- Data Fetching ---
    df = load_google_sheet()
    
    if df.empty:
        st.warning("⚠️ Application connected successfully, but target matrix returns an empty frame.")
        return

    # --- Header Banner ---
    st.markdown(f"""
    <div class="header-box">
        <h1>🚉 Solapur Division Equipment Inventory Management System</h1>
        <h4>An initiative by Safety Branch, Solapur Division, Central Railway</h4>
    </div>
    """, unsafe_allow_html=True)

    # --- Control Sidebar ---
    st.sidebar.markdown("### 👤 Operator Console")
    st.sidebar.caption("System Status: Online / Encrypted")
    
    if st.sidebar.button("🔄 Force Clear Cache & Sync", use_container_width=True):
        load_google_sheet.clear()
        st.rerun()
        
    if st.sidebar.button("🚪 Terminate Session (Logout)", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    # --- Calculations & Dynamic KPI Ribbon ---
    total_stations = len(df)
    exclude_cols = ["STATION", "LATITUDE", "LONGITUDE"]
    equipment_columns = [col for col in df.columns if col not in exclude_cols]
    
    # Calculate operational values cleanly converting strings/nan values safely
    numeric_df = df[equipment_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
    aggregate_physical_assets = int(numeric_df.sum().sum())

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("🚏 Monitored Locations", f"{total_stations} Stations")
    with m_col2:
        st.metric("🛠 Tracked Equipment Categories", f"{len(equipment_columns)} Classes")
    with m_col3:
        st.metric("📦 Deployed Physical Assets", f"{aggregate_physical_assets:,} Units")

    st.write("")

    # --- GIS Map Integration Layer ---
    if "LATITUDE" in df.columns and "LONGITUDE" in df.columns:
        with st.expander("🗺️ Division GIS Spatial Mapping View", expanded=True):
            # Calculate mean coordinates safely for standard view bounding setup
            map_lat = pd.to_numeric(df["LATITUDE"], errors='coerce').dropna().mean()
            map_lon = pd.to_numeric(df["LONGITUDE"], errors='coerce').dropna().mean()
            
            if not pd.isna(map_lat) and not pd.isna(map_lon):
                m = folium.Map(location=[map_lat, map_lon], zoom_start=8, tiles="OpenStreetMap")
                
                for _, row in df.iterrows():
                    try:
                        lat = float(row["LATITUDE"])
                        lon = float(row["LONGITUDE"])
                        if not (pd.isna(lat) or pd.isna(lon)):
                            station_title = row.get("STATION", "Unknown Node")
                            
                            # Interactive pop-up payload design for infrastructure overview
                            html_popup = f"""
                            <div style='font-family:sans-serif; min-width:160px;'>
                                <h4 style='margin:0 0 5px 0; color:#1e3a8a;'>🚉 {station_title}</h4>
                                <hr style='margin:5px 0; border:1px solid #e2e8f0;'>
                                <p style='margin:0; font-size:12px; color:#475569;'>
                                    Total Monitored Types: <b>{len(equipment_columns)}</b>
                                </p>
                            </div>
                            """
                            folium.Marker(
                                [lat, lon],
                                popup=folium.Popup(html_popup, max_width=250),
                                tooltip=f"Station: {station_title}",
                                icon=folium.Icon(color="blue", icon="train", prefix="fa")
                            ).add_to(m)
                    except (ValueError, TypeError):
                        continue
                st_folium(m, width="100%", height=380, returned_objects=[])
            else:
                st.info("💡 Map initialization deferred: Population coordinates are non-numeric or unpopulated.")

    # --- Filter & Operational Search ---
    search_col, export_col = st.columns([3, 1])
    with search_col:
        search = st.text_input(
            "🔎 Station Filter Engine",
            placeholder="Type station name to filter records instantly..."
        )
    
    filtered_df = df.copy()
    if search:
        filtered_df = df[df["STATION"].astype(str).str.contains(search, case=False, na=False)]

    with export_col:
        st.write("")
        st.write("")
        # Clean export data frame extraction payload
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Report Data (.CSV)",
            data=csv_data,
            file_name=f"Solapur_Safety_Inventory_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    if filtered_df.empty:
        st.info("ℹ️ No operational records or stations match criteria selection.")
        return

    # --- Station Grid Presentation Loop ---
    for _, row in filtered_df.iterrows():
        station_name = row.get("STATION", "Unknown Base Point")
        
        # Safe structural separation using Streamlit containers instead of trailing custom divs
        with st.container():
            st.markdown(f"""
            <div class="station-title-strip">
                🚉 System Node: &nbsp;<b>{station_name}</b>
            </div>
            """, unsafe_allow_html=True)
            
            cols = st.columns(4)
            for i, col in enumerate(equipment_columns):
                raw_val = row.get(col, 0)
                
                # Normalization optimization
                try:
                    if raw_val == "" or pd.isna(raw_val):
                        value = 0
                    else:
                        value = int(float(raw_val))
                except (ValueError, TypeError):
                    value = raw_val # Fallback if text data is stored intentionally
                
                box_class = "zero-assets" if value == 0 else "active-assets"
                val_class = "zero" if value == 0 else "active"
                
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="metric-box {box_class}">
                        <div class="metric-label">{col}</div>
                        <div class="metric-value {val_class}">{value}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-bottom:35px;'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main_portal()
