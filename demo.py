import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import folium
from streamlit_folium import st_folium

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Solapur Division Equipment & Infrastructure Management System",
    page_icon="🚉",
    layout="wide"
)

# ====================== STYLING ENGINE ======================
st.markdown("""
<style>
/* Smooth Viewport Entrance Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes glowGreen {
    0% { box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08), 0 0 0 0 rgba(34, 197, 94, 0.4); }
    50% { box-shadow: 0 6px 20px rgba(34, 197, 94, 0.35), 0 0 14px 4px rgba(34, 197, 94, 0.2); }
    100% { box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08), 0 0 0 0 rgba(34, 197, 94, 0); }
}

@keyframes glowRed {
    0% { box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08), 0 0 0 0 rgba(239, 68, 68, 0.4); }
    50% { box-shadow: 0 6px 20px rgba(239, 68, 68, 0.35), 0 0 14px 4px rgba(239, 68, 68, 0.2); }
    100% { box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08), 0 0 0 0 rgba(239, 68, 68, 0); }
}

/* App Canvas Setup & Theme Reinforcement */
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

/* Sidebar Light Green Theme Styling Override */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f0fdf4 0%, #dcfce7 100%);
    box-shadow: 4px 0 15px rgba(0,0,0,0.04);
    border-right: 1px solid #bbf7d0;
}
[data-testid="stSidebar"] h3 { color: #14532d !important; }
[data-testid="stSidebar"] caption, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
    color: #166534 !important;
}

/* Tab Component Styling Overrides */
button[data-baseweb="tab"] {
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
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

/* Structural Wrapper Card */
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
    padding: 16px 14px;
    text-align: center;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 6px;
}
.metric-box.active-assets { border-top: 4px solid #2563eb; background: #f8fafc; }
.metric-box.active-assets:hover { transform: scale(1.03); background: #eff6ff; border-top-color: #1d4ed8; }

/* Infrastructure layout specific card styling variant */
.metric-box.infra-asset { border-top: 4px solid #0284c7; background: #f0f9ff; }
.metric-box.infra-asset:hover { transform: scale(1.03); background: #e0f2fe; border-top-color: #0369a1; }

.metric-box.flag-green-glow {
    border-top: 4px solid #22c55e !important;
    background: #f0fdf4 !important;
    animation: glowGreen 2.5s infinite ease-in-out;
}
.metric-box.flag-green-glow:hover { transform: scale(1.03); background: #f0fdf4 !important; }

.metric-box.flag-red-glow {
    border-top: 4px solid #ef4444 !important;
    background: #fef2f2 !important;
    animation: glowRed 2.5s infinite ease-in-out;
}
.metric-box.flag-red-glow:hover { transform: scale(1.03); background: #fef2f2 !important; }

.metric-box.zero-assets { border-top: 4px solid #94a3b8; background: #ffffff; opacity: 0.75; }
.metric-box.zero-assets:hover { opacity: 1.0; background: #f8fafc; }

/* Unified Font Sizes for Label and Value */
.metric-label {
    color: #334155 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    text-transform: capitalize;
    letter-spacing: 0.2px;
    line-height: 1.3;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}
.metric-value { color: #1e3a8a !important; font-size: 18px !important; font-weight: 700 !important; margin: 0; }
.metric-value.zero { color: #94a3b8 !important; font-weight: 600; }

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
        st.markdown("""
        <div style="background: white; padding: 35px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.04); border: 1px solid #e2e8f0; text-align: center;">
            <h2 style="margin: 0 0 5px 0; color: #1e3a8a; font-weight:800;">🚉 Solapur Division</h2>
            <p style="color: #64748b; margin: 0; font-size:14px; font-weight:500;">Safety & Engineering Branch Asset Tracking Portal</p>
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
                        st.rerun()
                    else:
                        st.error("❌ Invalid User ID or Password credential.")
                except KeyError:
                    st.error("🔑 Context configuration parameters are missing.")
    return False

if not login():
    st.stop()

# ====================== DATA PIPELINE ENGINE ======================
@st.cache_data(ttl=0)
def load_secure_sheet(sheet_id_key, sheet_name_key):
    try:
        sheet_id = st.secrets[sheet_id_key]
        sheet_name = st.secrets[sheet_name_key]
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        worksheet = sh.worksheet(sheet_name)
        df = pd.DataFrame(worksheet.get_all_records())
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"🚨 Connection to Cloud Target matrix rejected for config mapping keys.")
        return pd.DataFrame()

# ====================== APPLICATION MAIN CORE ======================
def main_portal():
    # --- Header Banner Component ---
    st.markdown("""
    <div class="header-box">
        <h1>🚉 Solapur Division Infrastructure Management Dashboard</h1>
        <h4>Safety & Engineering Branch Operations Matrix — Central Railway</h4>
    </div>
    """, unsafe_allow_html=True)

    # --- Sidebar Console Operations ---
    st.sidebar.markdown("### 🖥️ Controller Desk")
    st.sidebar.caption("Security Status: Connected")
    
    if st.sidebar.button("🔄 Sync Global Sheets & Clear Cache", use_container_width=True):
        load_secure_sheet.clear()
        st.rerun()
    if st.sidebar.button("🚪 Terminate Session", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    # ====================== TABS ROUTER SETUP ======================
    tab1, tab2 = st.tabs(["📦 Equipment Inventory Matrix", "🛤️ Track Crossing Layouts"])

    # ---------------------------------------------------------------
    # TAB 1 (tab1): EQUIPMENT INVENTORY PORTAL
    # ---------------------------------------------------------------
    with tab1:
        df_eq = load_secure_sheet("SHEET_ID", "SHEET_NAME")
        if df_eq.empty:
            st.warning("⚠️ No active rows found inside Equipment Inventory database.")
        else:
            exclude_cols = ["STATION", "LATITUDE", "LONGITUDE"]
            equipment_columns = [col for col in df_eq.columns if col not in exclude_cols]
            
            # Summary KPI Cards
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            num_df = df_eq[equipment_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
            with kpi_col1: st.metric("🚏 Active Stations", f"{len(df_eq)} Locations")
            with kpi_col2: st.metric("🛠️ Categorized Asset Classes", f"{len(equipment_columns)} Types")
            with kpi_col3: st.metric("📦 Gross Physical Units", f"{int(num_df.sum().sum()):,} Elements")
            
            st.write("")
            
            # GIS Engine Map
            if "LATITUDE" in df_eq.columns and "LONGITUDE" in df_eq.columns:
                with st.expander("🗺️ Division GIS Spatial Mapping Overview", expanded=False):
                    map_lat = pd.to_numeric(df_eq["LATITUDE"], errors='coerce').dropna().mean()
                    map_lon = pd.to_numeric(df_eq["LONGITUDE"], errors='coerce').dropna().mean()
                    if not (pd.isna(map_lat) or pd.isna(map_lon)):
                        m = folium.Map(location=[map_lat, map_lon], zoom_start=8, tiles="OpenStreetMap")
                        for _, row in df_eq.iterrows():
                            try:
                                lat, lon = float(row["LATITUDE"]), float(row["LONGITUDE"])
                                if not (pd.isna(lat) or pd.isna(lon)):
                                    folium.Marker(
                                        [lat, lon],
                                        tooltip=f"Node: {row.get('STATION', 'Unknown')}",
                                        icon=folium.Icon(color="blue", icon="train", prefix="fa")
                                    ).add_to(m)
                            except: continue
                        st_folium(m, width="100%", height=320, returned_objects=[])

            # Filter Search
            search_eq = st.text_input("🔍 Operational Node Filter Engine", placeholder="Search stations or cabins...", key="search_eq")
            fil_df_eq = df_eq[df_eq["STATION"].astype(str).str.contains(search_eq, case=False, na=False)] if search_eq else df_eq

            # Grid View
            for _, row in fil_df_eq.iterrows():
                st.markdown(f'<div class="rail-station-wrapper"><div class="station-title-strip">🚉 Node: <b>{row.get("STATION", "Unknown")}</b></div>', unsafe_allow_html=True)
                cols = st.columns(4)
                for idx, col in enumerate(equipment_columns):
                    try:
                        raw = row.get(col, 0)
                        val = int(float(raw)) if raw != "" and not pd.isna(raw) else 0
                    except: val = raw
                    
                    box_style = "zero-assets" if val == 0 else "active-assets"
                    val_style = "zero" if val == 0 else "active"
                    
                    if val != 0:
                        col_clean = col.lower()
                        if "green" in col_clean and "flag" in col_clean: box_style += " flag-green-glow"
                        elif "red" in col_clean and "flag" in col_clean: box_style += " flag-red-glow"
                    
                    with cols[idx % 4]:
                        st.markdown(f'<div class="metric-box {box_style}"><div class="metric-label">{col}</div><div class="metric-value {val_style}">{val}</div></div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------------
    # TAB 2 (tab2): NEW TRACK CROSSINGS LAYOUT PORTAL (MIRRORED DESIGN)
    # ---------------------------------------------------------------
    with tab2:
        df_tr = load_secure_sheet("NEW_SHEET_ID", "NEW_SHEET_NAME")
        
        if df_tr.empty:
            st.warning("⚠️ No active infrastructure data row elements found inside target crossing layout sheet.")
        else:
            # Main identifiers used to formulate the strip headers
            header_identifiers = ["PXING NO.", "OPERATING STATION"]
            # Dynamically identify all detail columns (including added or modified headers automatically)
            detail_columns = [col for col in df_tr.columns if col not in header_identifiers]
            
            # Summary KPIs (Matched layout style)
            kpi_t1, kpi_t2, kpi_t3 = st.columns(3)
            with kpi_t1: st.metric("🛤️ Registered Infrastructure Nodes", f"{len(df_tr)} Crossings")
            with kpi_t2: 
                uniq_st = len(df_tr["OPERATING STATION"].dropna().unique()) if "OPERATING STATION" in df_tr.columns else 0
                st.metric("🚉 Controlled Operations Stations", f"{uniq_st} Main Hubs")
            with kpi_t3: 
                line_types = len(df_tr["LINE TYPE"].dropna().unique()) if "LINE TYPE" in df_tr.columns else 0
                st.metric("🛣️ Active Running Configurations", f"{line_types} Track Lines")
                
            st.write("")
            
            # Filter & Search Engine UI
            search_tr = st.text_input("🔍 Infrastructure Attribute Search Desk", placeholder="Filter by station, crossing number, jurisdiction...", key="search_tr")
            
            fil_df_tr = df_tr.copy()
            if search_tr:
                # Runs search filtration across all available table dimensions safely
                combined_mask = fil_df_tr.astype(str).apply(lambda row: row.str.contains(search_tr, case=False).any(), axis=1)
                fil_df_tr = fil_df_tr[combined_mask]

            # Mirrored Layout Cards Generation Loop
            for _, row in fil_df_tr.iterrows():
                pxing = row.get("PXING NO.", "N/A")
                station = row.get("OPERATING STATION", "Unknown Hub")
                
                # Dynamic Wrapper block header (Identical styling pattern)
                st.markdown(f"""
                <div class="rail-station-wrapper">
                    <div class="station-title-strip">
                        🛤️ Crossing Index: <b>{pxing}</b> &nbsp;|&nbsp; Station Context: <b>{station}</b>
                    </div>
                """, unsafe_allow_html=True)
                
                # Split row metadata cards into 4-column dynamic grid
                cols_tr = st.columns(4)
                for idx, col in enumerate(detail_columns):
                    val = row.get(col, "")
                    if val == "" or pd.isna(val):
                        val = "N/A"
                    
                    # Renders using the elegant corporate sky-blue styling card configuration
                    box_style = "infra-asset"
                    
                    with cols_tr[idx % 4]:
                        st.markdown(f"""
                        <div class="metric-box {box_style}">
                            <div class="metric-label">{col}</div>
                            <div class="metric-value">{val}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main_portal()
