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
/* Smooth Viewport Entrance Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes statusPulse {
    0% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.2); }
    70% { box-shadow: 0 0 0 6px rgba(37, 99, 235, 0); }
    100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
}

/* App Canvas Setup & Light Theme Reinforcement */
.stApp {
    background-color: #f8fafc;
    color: #0f172a;
}

html, body, [class*="css"] {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    padding-top: 1.5rem;
    max-width: 1550px;
    animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* Sidebar Styling Override */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    box-shadow: 4px 0 15px rgba(0,0,0,0.08);
}
[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

/* Enterprise Header Component */
.header-box {
    background: linear-gradient(135deg, #1e3a8a 0%, #0369a1 100%);
    padding: 30px 40px;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(30, 58, 138, 0.12);
    border-left: 6px solid #38bdf8;
    position: relative;
    overflow: hidden;
}
.header-box::before {
    content: '';
    position: absolute;
    top: 0; right: 0; bottom: 0; left: 0;
    background: linear-gradient(45deg, transparent 60%, rgba(255,255,255,0.06) 100%);
    pointer-events: none;
}
.header-box h1 {
    color: #ffffff !important;
    font-size: 34px;
    font-weight: 800;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.header-box h4 {
    color: #bae6fd !important;
    font-weight: 400;
    margin: 0;
    letter-spacing: 0.2px;
}

/* Native Metrics Override */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
}
[data-testid="metric-container"] label {
    color: #475569 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #1e3a8a !important;
    font-size: 30px !important;
    font-weight: 800 !important;
}

/* Station Structural Wrapper Card */
.rail-station-wrapper {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 25px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.02);
    transition: border-color 0.25s ease;
}
.rail-station-wrapper:hover {
    border-color: #cbd5e1;
}
.station-title-strip {
    font-size: 20px;
    font-weight: 700;
    color: #1e3a8a !important;
    border-bottom: 2px solid #f1f5f9;
    padding-bottom: 10px;
    margin-bottom: 18px;
}

/* Interactive Dynamic Grid Elements */
.metric-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px;
    text-align: center;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
}
.metric-box.active-assets {
    border-top: 4px solid #2563eb;
    background: #f8fafc;
}
.metric-box.active-assets:hover {
    transform: scale(1.03);
    background: #eff6ff;
    border-top-color: #1d4ed8;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
}
.metric-box.zero-assets {
    border-top: 4px solid #94a3b8;
    background: #ffffff;
    opacity: 0.75;
}
.metric-box.zero-assets:hover {
    opacity: 1.0;
    background: #f8fafc;
}
.metric-label {
    color: #64748b !important;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
    min-height: 32px;
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
    font-weight: 600;
}

/* Form Panel Adjustments */
.stButton > button {
    border-radius: 6px;
    font-weight: 600;
    transition: all 0.2s ease;
}
</style>
""", unsafe_allow_html=True)

# ====================== LOGIN SERVICE ======================
def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.write("")
        st.write("")
        st.markdown("""
        <div style="background: white; padding: 35px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.04); border: 1px solid #e2e8f0; text-align: center;">
            <h2 style="margin: 0 0 5px 0; color: #1e3a8a; font-weight:800;">🚉 Solapur Division</h2>
            <p style="color: #64748b; margin: 0 0 5px 0; font-size:14px; font-weight:500;">Safety Branch - Equipment Asset Tracking Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Operator User ID")
            password = st.text_input("Security Access Password", type="password")
            submit = st.form_submit_button("Secure Log In", use_container_width=True)
            
            if submit:
                try:
                    if username == st.secrets["APP_USERNAME"] and password == st.secrets["APP_PASSWORD"]:
                        st.session_state.authenticated = True
                        st.success("Authorization confirmed.")
                        st.rerun()
                    else:
                        st.error("❌ Invalid User ID or Password credential.")
                except KeyError:
                    st.error("🔑 Context configuration parameters are missing.")
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
        st.error("🚨 Interface Pipeline Error: Connection to secure cloud asset data matrix rejected.")
        st.exception(e)
        return pd.DataFrame()

# ====================== MAIN PORTAL APPLICATION ======================
def main_portal():
    df = load_google_sheet()
    
    if df.empty:
        st.warning("⚠️ Connected to repository data frame, but no asset rows found inside target sheet.")
        return

    # --- Header Banner Component ---
    st.markdown(f"""
    <div class="header-box">
        <h1>🚉 Solapur Division Equipment Inventory Management System</h1>
        <h4>An initiative by Safety Branch, Solapur Division, Central Railway</h4>
    </div>
    """, unsafe_allow_html=True)

    # --- Sidebar Console Operations ---
    st.sidebar.markdown("### 🖥️ Controller Desk")
    st.sidebar.caption("Security Context: Authenticated")
    st.sidebar.write("")
    
    if st.sidebar.button("🔄 Clear System Cache & Sync", use_container_width=True):
        load_google_sheet.clear()
        st.rerun()
        
    if st.sidebar.button("🚪 Terminate Session (Logout)", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    # --- Calculations & Dynamic KPI Summary Section ---
    total_stations = len(df)
    exclude_cols = ["STATION", "LATITUDE", "LONGITUDE"]
    equipment_columns = [col for col in df.columns if col not in exclude_cols]
    
    numeric_df = df[equipment_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
    aggregate_physical_assets = int(numeric_df.sum().sum())

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("🚏 Active Monitored Nodes", f"{total_stations} Locations")
    with m_col2:
        st.metric("🛠 Categorized Equipment Lines", f"{len(equipment_columns)} Asset Types")
    with m_col3:
        st.metric("📦 Gross Physical Units Deployed", f"{aggregate_physical_assets:,} Elements")

    st.write("")

    # --- GIS Map Integration Panel ---
    if "LATITUDE" in df.columns and "LONGITUDE" in df.columns:
        with st.expander("🗺️ Division GIS Spatial Mapping Overview", expanded=True):
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
                            
                            html_popup = f"""
                            <div style='font-family:sans-serif; min-width:150px;'>
                                <h5 style='margin:0 0 4px 0; color:#1e3a8a;'>🚉 {station_title}</h5>
                                <div style='border-bottom:1px solid #e2e8f0; margin-bottom:6px;'></div>
                                <span style='font-size:11px; color:#475569;'>Equipment Classes tracked here: <b>{len(equipment_columns)}</b></span>
                            </div>
                            """
                            folium.Marker(
                                [lat, lon],
                                popup=folium.Popup(html_popup, max_width=250),
                                tooltip=f"Node: {station_title}",
                                icon=folium.Icon(color="blue", icon="train", prefix="fa")
                            ).add_to(m)
                    except (ValueError, TypeError):
                        continue
                st_folium(m, width="100%", height=360, returned_objects=[])
            else:
                st.info("💡 GIS Visual Map skipped: Target coordinates evaluate to Null/NaN.")

    # --- Search Filter & Export Configuration Engine ---
    search_col, export_col = st.columns([3, 1])
    with search_col:
        search = st.text_input(
            "🔍 Operational Node Filter Engine",
            placeholder="Search matching station names or cabins..."
        )
    
    filtered_df = df.copy()
    if search:
        filtered_df = df[df["STATION"].astype(str).str.contains(search, case=False, na=False)]

    with export_col:
        st.write("")
        st.write("")
        csv_payload = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Filtered Report (.CSV)",
            data=csv_payload,
            file_name=f"CR_Solapur_Safety_Audit_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    if filtered_df.empty:
        st.info("ℹ️ No active railway infrastructure records match the current filter query.")
        return

    # --- Station Grid Loops ---
    for _, row in filtered_df.iterrows():
        station_name = row.get("STATION", "Unknown Base Station")
        
        st.markdown(f"""
        <div class="rail-station-wrapper">
            <div class="station-title-strip">
                🚉 Station / Node context: <b>{station_name}</b>
            </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(4)
        for i, col in enumerate(equipment_columns):
            raw_val = row.get(col, 0)
            
            try:
                if raw_val == "" or pd.isna(raw_val):
                    value = 0
                else:
                    value = int(float(raw_val))
            except (ValueError, TypeError):
                value = raw_val
            
            box_style = "zero-assets" if value == 0 else "active-assets"
            val_style = "zero" if value == 0 else "active"
            
            with cols[i % 4]:
                st.markdown(f"""
                <div class="metric-box {box_style}">
                    <div class="metric-label">{col}</div>
                    <div class="metric-value {val_style}">{value}</div>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main_portal()
