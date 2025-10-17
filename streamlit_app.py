import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
from scipy import stats
import io

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Scanner Data Analysis Platform",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'df_riil' not in st.session_state:
    st.session_state.df_riil = None
if 'df_ipr' not in st.session_state:
    st.session_state.df_ipr = None
if 'all_sheets' not in st.session_state:
    st.session_state.all_sheets = {}

# Login credentials
USERS = {
    "ahmad_rp.i": "Sasuke123@20072001",
    "mutiara_sa.i": "Bandung2025$",
    "natasya_fs.i": "Tasya1606@"
}

def login_page():
    """Display login page"""
    st.markdown("""
    <div style='text-align: center; padding: 50px 0;'>
        <h1 style='color: #1f77b4; font-size: 3em; margin-bottom: 0;'>Hello, Welcome.</h1>
        <h3 style='color: #666; font-size: 1.5em; margin-top: 10px;'>Analyze Scanner Data Platform</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.form_submit_button("Login", use_container_width=True):
                if username in USERS and USERS[username] == password:
                    st.session_state.authenticated = True
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid username or password!")
        
        # Add some styling
        st.markdown("""
        <div style='text-align: center; margin-top: 30px; color: #888;'>
            <p>Welcome to Scanner Data Analysis Platform</p>
            <p>Please enter your credentials to access the dashboard</p>
        </div>
        """, unsafe_allow_html=True)

def load_excel_sheets(uploaded_file):
    """
    Load all sheets from Excel file into a dictionary
    Returns: dict with sheet names as keys and dataframes as values
    """
    try:
        # First, get all sheet names
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        sheets_dict = {}
        loading_status = st.empty()
        
        # Load each sheet with appropriate headers
        for sheet_name in sheet_names:
            loading_status.info(f"Loading sheet: {sheet_name}...")
            
            # Determine header row based on sheet name
            if sheet_name.lower() == 'riil':
                # For 'Riil' sheet, start from row 3 (header=2)
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=2)
            elif sheet_name.lower() == 'ipr':
                # For 'IPR' sheet, use default header
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            else:
                # For other sheets, use default header (row 1)
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            
            sheets_dict[sheet_name] = df
        
        loading_status.success(f"Successfully loaded {len(sheets_dict)} sheets!")
        return sheets_dict
        
    except Exception as e:
        st.error(f"Error loading Excel sheets: {str(e)}")
        return None

def upload_page():
    """Enhanced upload page with multi-sheet support"""
    st.markdown("""
    <div style='text-align: center; padding: 30px 0;'>
        <h1 style='color: #1f77b4;'>Upload Your Data</h1>
        <p style='color: #666; font-size: 1.2em;'>Please upload your Excel file to begin analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Data Requirements")
        
        # Info about multiple sheets
        st.info("""
        **Your Excel file should contain the following sheets:**
        - **Main Data Sheet**: Contains Omzet Scanner Data
        - **Index Sheet**: Retail Scanner Index
        - **IPR Sheet**: Indeks Penjualan Riil
        
        **Required columns in main sheet:**
        - tahun (year)
        - bulan (month)
        - kategori (category)
        - subkategori (subcategory)
        - klasifikasi (classification SPE or Non-SPE)
        - total_expenditure (total expenditure)
        - total_quantity (total quantity)
        """)
        
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls'],
            help="Upload your scanner data Excel file with multiple sheets"
        )
        
        if uploaded_file is not None:
            try:
                # Load all sheets
                with st.spinner("Reading all sheets from your file..."):
                    sheets_dict = load_excel_sheets(uploaded_file)
                
                if sheets_dict:
                    # Display available sheets
                    st.success(f"File uploaded successfully!")
                    
                    # Simpan sheet Riil dan IPR ke session state
                    for sheet_name, sheet_df in sheets_dict.items():
                        if sheet_name.lower() == 'riil':
                            st.session_state.df_riil = sheet_df
                        elif sheet_name.lower() == 'ipr':
                            st.session_state.df_ipr = sheet_df
                    
                    # Peringatan jika sheet tidak ditemukan
                    if 'df_riil' not in st.session_state or st.session_state.df_riil is None:
                        st.warning("⚠️ Sheet 'Riil' tidak ditemukan. Tab Indeks Penjualan mungkin tidak berfungsi penuh.")
                    if 'df_ipr' not in st.session_state or st.session_state.df_ipr is None:
                        st.warning("⚠️ Sheet 'IPR' tidak ditemukan. Tab Indeks Penjualan mungkin tidak berfungsi penuh.")
                    
                    # Process main data sheet
                    df = sheets_dict[list(sheets_dict.keys())[0]].copy()
                    
                    # Clean and filter main data
                    df = df[(df['kategori'].notnull()) & 
                        (df['subkategori'].notnull()) & 
                        ~(df['subkategori'] == 'Alat Musik')]
                    
                    # Show main sheet preview
                    st.markdown(f"### Main Data Preview (Sheet: {list(sheets_dict.keys())[0]})")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # Validate required columns
                    df.columns = [c.strip().lower() for c in df.columns]
                    required_cols = ['tahun', 'bulan', 'kategori', 'subkategori', 
                                'klasifikasi', 'total_expenditure', 'total_quantity']
                    missing_cols = [col for col in required_cols if col not in df.columns]
                    
                    if missing_cols:
                        st.error(f"Missing required columns in main sheet: {missing_cols}")
                        st.info("Please ensure your main data sheet contains all required columns.")
                    else:
                        st.success("All required columns found in main sheet!")
                        
                        # Process the data
                        df = process_data(df)
                        
                        if st.button("Start Analysis", use_container_width=True):
                            # Store all dataframes in session state
                            st.session_state.df = df
                            st.session_state.all_sheets = sheets_dict
                        
                            st.session_state.file_uploaded = True
                            st.success("Data processed successfully! Redirecting to dashboard...")
                            st.rerun()
                            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.info("Please check your file format and try again.")
        
        # Logout button
        st.markdown("---")
        if st.button("Logout"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def process_data(df):
    """Process and validate the uploaded data"""
    # Ensure column names are consistent
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Ensure data types
    df['tahun'] = df['tahun'].astype(int)
    df['bulan'] = df['bulan'].astype(int)
    
    # Create date column
    df['date'] = pd.to_datetime(
        dict(year=df['tahun'], month=df['bulan'], day=1), errors='coerce'
    )
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['date'])
    
    # Create year_month column
    df['year_month'] = df['date'].dt.strftime('%Y-%m')
    
    return df

# Fungsi untuk menghitung indeks penjualan
def comparing_index(df, base_period='2022'):
    riil_data = 'df_riil' in st.session_state and st.session_state.df_riil is not None
    ipr_data = 'df_ipr' in st.session_state and st.session_state.df_ipr is not None
    if riil_data:
        scanner_index = st.session_state.df_riil
        scanner_index.rename(columns={'Periode': 'Kategori'}, inplace=True)
        scanner_index = scanner_index.dropna(subset=['Kategori'])
        df_long = scanner_index.melt(
            id_vars=['Kategori'],
            var_name='Periode',
            value_name='Omzet'
        )
        df_long['Periode'] = pd.to_datetime(df_long['Periode'], format='%b-%y', errors='coerce')
        df_long['Tahun'] = df_long['Periode'].dt.year
        df_long['Bulan'] = df_long['Periode'].dt.month
        # Base Year
        base_year = df_long[df_long['Tahun'] == int(base_period)]
        base_year_df = (
            base_year.groupby('Kategori', as_index=False)
            .agg({'Omzet': 'mean'})
            .rename(columns={'Omzet': 'Base_Year'})
        )
        # Retail Scanner Index
        df_index = pd.merge(
            df_long,
            base_year_df,
            on='Kategori',
            how='left'
        )
        df_index['Retail_Scanner_Index'] = round((df_index['Omzet'] / df_index['Base_Year']) * 100, 1)
        df_index = df_index.sort_values(['Periode']).reset_index(drop=True)
    if ipr_data:
        # IPR
        ipr = st.session_state.df_ipr
        ipr.rename(columns={"Indeks Penjualan Riil": 'Kategori'}, inplace=True)
        ipr_clean = ipr.loc[ipr.isna().any(axis=1), 'Kategori'].unique()
        ipr_clean = ipr[~ipr['Kategori'].isin(ipr_clean)]
        ipr_clean = ipr_clean.melt(
            id_vars=['Kategori'],
            var_name='Periode',
            value_name='Index'
        )
        ipr_clean['Periode'] = pd.to_datetime(ipr_clean['Periode'], format='%b-%y', errors='coerce')
        ipr_clean['Tahun'] = ipr_clean['Periode'].dt.year
        ipr_clean['Bulan'] = ipr_clean['Periode'].dt.month
        ipr_clean['Index'] = round(ipr_clean['Index'], 1)
    # Merged
    merged_df = (
        df_index
        .merge(
            ipr_clean,
            on=['Kategori', 'Periode'],   
            how='inner'                   
        )
        .rename(columns={
            'Retail_Scanner_Index': 'Scanner_index',
            'Index': 'IPR_index',
            'Tahun_x': 'Tahun',
            'Bulan_x': 'Bulan'
        })
        .loc[:, ['Kategori', 'Periode', 'Scanner_index', 'IPR_index', 'Tahun', 'Bulan']]
    )
    return merged_df

def main_dashboard():
    """Main dashboard with all analysis tabs"""
    df = st.session_state.df
    
    # Header with logout
    col1, col2 = st.columns([12, 1])
    with col1:
        st.markdown("""
        # :material/query_stats: Retail Scanner Index
        Dashboard Analisis Omzet Scanner Data
        """)
    with col2:
        if st.button("Logout", key="main_logout"):
            st.session_state.authenticated = False
            st.session_state.file_uploaded = False
            st.session_state.df = None
            st.rerun()
    
    # Sidebar untuk filter
    st.sidebar.header("Filter Data")
    
    # Filter tahun
    tahun_range = st.sidebar.slider(
        "Pilih Range Tahun",
        min_value=int(df['tahun'].min()),
        max_value=int(df['tahun'].max()),
        value=(int(df['tahun'].min()), int(df['tahun'].max()))
    )
    
    # Filter kategori
    selected_kategori = st.sidebar.multiselect(
        "Pilih Kategori",
        options=df['kategori'].unique(),
        default=df['kategori'].unique()
    )
    
    # Filter subkategori berdasarkan kategori terpilih
    available_subkategori = df[df['kategori'].isin(selected_kategori)]['subkategori'].unique()
    selected_subkategori = st.sidebar.multiselect(
        "Pilih Subkategori",
        options=available_subkategori,
        default=available_subkategori
    )
    
    # Filter klasifikasi berdasarkan subkategori terpilih
    available_klasifikasi = df[df['subkategori'].isin(selected_subkategori)]['klasifikasi'].unique()
    selected_klasifikasi = st.sidebar.multiselect(
        "Pilih Klasifikasi",
        options=available_klasifikasi,
        default=available_klasifikasi
    )

    # Apply filters
    df_filtered = df[
        (df['tahun'] >= tahun_range[0]) & 
        (df['tahun'] <= tahun_range[1]) &
        (df['kategori'].isin(selected_kategori)) &
        (df['subkategori'].isin(selected_subkategori)) &
        (df['klasifikasi'].isin(selected_klasifikasi))
    ]
    
    # Tab layout
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        " Overview", 
        " Indeks Penjualan",
        " Analisis Tren", 
        " Analisis Kategori",
        " Perbandingan YoY/MoM",
        " Forecasting",
        " Data Explorer"
    ])
    
    # Tab 1: Overview Dashboard
    with tab1:
        st.header("Overview Dashboard")
    
        # CSS untuk styling border putih elegan
        st.markdown("""
        <style>
        .metric-container {
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }
        
        .metric-container:hover {
            border: 2px solid rgba(255, 255, 255, 0.6);
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
        }
        
        .metric-container.clickable {
            cursor: pointer;
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        }
        
        .metric-container.clickable:hover {
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin-bottom: 5px;
            animation: fadeIn 0.5s ease-in;
        }
        
        .metric-label {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .metric-delta {
            font-size: 12px;
            color: #4ade80;
            font-weight: 500;
        }
        
        .metric-delta.negative {
            color: #f87171;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .flip-card {
            animation: flip 0.6s ease-in-out;
        }
        
        @keyframes flip {
            0% { transform: rotateY(0deg); }
            50% { transform: rotateY(90deg); }
            100% { transform: rotateY(0deg); }
        }
        
        .toggle-indicator {
            font-size: 10px;
            color: rgba(255, 255, 255, 0.5);
            margin-left: 10px;
        }
        
        .growth-type-selector {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .growth-badge {
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 11px;
            background: rgba(255, 255, 255, 0.1);
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .growth-badge:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .growth-badge.active {
            background: rgba(74, 222, 128, 0.2);
            border: 1px solid rgba(74, 222, 128, 0.5);
        }
        
        .switch-button {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 20px;
            padding: 2px 8px;
            font-size: 10px;
            color: rgba(255, 255, 255, 0.7);
            cursor: pointer;
            transition: all 0.3s;
            margin-left: auto;
        }
        
        .switch-button:hover {
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }
                    
        .stButton > button {
            margin-bottom: 0px;
            margin-top: -10px; /* tarik lebih dekat ke header */
        }

        </style>
        """, unsafe_allow_html=True)

        if 'show_spe_combined' not in st.session_state:
            st.session_state.show_spe_combined = False
        if 'show_categories' not in st.session_state:
            st.session_state.show_categories = False
        if 'growth_type' not in st.session_state:
            st.session_state.growth_type = 'yoy'

        # Row untuk tombol di atas
        btn_col1, btn_col2, btn_col3 = st.columns([3,3,6])  # atur lebar sesuai selera

        with btn_col1:
            if st.button("Toggle View", key="spe_toggle", help="Click to switch between SPE only and SPE & Non-SPE view"):
                st.session_state.show_spe_combined = not st.session_state.show_spe_combined

        with btn_col2:
            if st.button("Categories" if st.session_state.show_categories else "Subcategories", key="cat_toggle"):
                st.session_state.show_categories = not st.session_state.show_categories

        with btn_col3:
            if st.button("YoY" if st.session_state.growth_type == 'yoy' else "MoM", key="growth_toggle"):
                st.session_state.growth_type = 'mom' if st.session_state.growth_type == 'yoy' else 'yoy'

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)

        tahun_terbaru = df_filtered['tahun'].max()
        bulan_terbaru = df_filtered.loc[df_filtered['tahun'] == tahun_terbaru, 'bulan'].max()
        # Col 1
        total_omzet_mamin = df_filtered[
            (df_filtered['tahun'] == tahun_terbaru) &
            (df_filtered['bulan'] == bulan_terbaru) &
            (df_filtered['kategori'] == 'Makanan, minuman dan tembakau')
        ]['total_expenditure'].sum()
        # Col 2
        total_omzet_non_mamin = df_filtered[
            (df_filtered['tahun'] == tahun_terbaru) &
            (df_filtered['bulan'] == bulan_terbaru) &
            (df_filtered['kategori'].isin(['Barang Budaya dan Rekreasi', 'Barang Lainnya', 'Peralatan Informasi dan Komunikasi', 'Perlengkapan Rumah Tangga Lainnya', 'Suku Cadang dan Aksesoris']))
        ]['total_expenditure'].sum()
        # Col 3
        total_omzet_spe = df_filtered[
            (df_filtered['tahun'] == tahun_terbaru) &
            (df_filtered['bulan'] == bulan_terbaru) &
            (df_filtered['kategori'].isin(['Makanan, minuman dan tembakau', 'Barang Budaya dan Rekreasi', 
                                        'Barang Lainnya', 'Peralatan Informasi dan Komunikasi', 
                                        'Perlengkapan Rumah Tangga Lainnya', 'Suku Cadang dan Aksesoris'])) &
            (df_filtered['klasifikasi'] == 'SPE')
        ]['total_expenditure'].sum()
        
        total_omzet_non_spe = df_filtered[
            (df_filtered['tahun'] == tahun_terbaru) &
            (df_filtered['bulan'] == bulan_terbaru) &
            (df_filtered['kategori'].isin(['Makanan, minuman dan tembakau', 'Barang Budaya dan Rekreasi', 
                                        'Barang Lainnya', 'Peralatan Informasi dan Komunikasi', 
                                        'Perlengkapan Rumah Tangga Lainnya', 'Suku Cadang dan Aksesoris'])) &
            (df_filtered['klasifikasi'] == 'Non-SPE')
        ]['total_expenditure'].sum()
        
        total_omzet_combined = total_omzet_spe + total_omzet_non_spe
        # Col 4
        latest_period = (tahun_terbaru, bulan_terbaru)
        prev_year_period = (tahun_terbaru - 1, bulan_terbaru)
        if bulan_terbaru == 1:
            prev_month_period = (tahun_terbaru - 1, 12)
        else:
            prev_month_period = (tahun_terbaru, bulan_terbaru - 1)

        # Prepare dataframes for each period
        df_latest = df_filtered[(df_filtered['tahun'] == latest_period[0]) & (df_filtered['bulan'] == latest_period[1])]
        df_prev_year = df_filtered[(df_filtered['tahun'] == prev_year_period[0]) & (df_filtered['bulan'] == prev_year_period[1])]
        df_prev_month = df_filtered[(df_filtered['tahun'] == prev_month_period[0]) & (df_filtered['bulan'] == prev_month_period[1])]

        # Growth calculations for both categories and subcategories
        if st.session_state.show_categories:
            # Group by kategori
            latest_cat = df_latest.groupby('kategori')['total_expenditure'].sum()
            prev_year_cat = df_prev_year.groupby('kategori')['total_expenditure'].sum()
            prev_month_cat = df_prev_month.groupby('kategori')['total_expenditure'].sum()
            
            yoy_growth_cat = ((latest_cat - prev_year_cat) / prev_year_cat.replace(0, np.nan)) * 100
            mom_growth_cat = ((latest_cat - prev_month_cat) / prev_month_cat.replace(0, np.nan)) * 100
            
            if st.session_state.growth_type == 'yoy':
                if not yoy_growth_cat.dropna().empty:
                    best_cat = yoy_growth_cat.idxmax()
                    best_val = yoy_growth_cat.max()
                else:
                    best_cat = "-"
                    best_val = 0
            else:  # mom
                if not mom_growth_cat.dropna().empty:
                    best_cat = mom_growth_cat.idxmax()
                    best_val = mom_growth_cat.max()
                else:
                    best_cat = "-"
                    best_val = 0
        else:
            # Group by subkategori
            latest_sub = df_latest.groupby('subkategori')['total_expenditure'].sum()
            prev_year_sub = df_prev_year.groupby('subkategori')['total_expenditure'].sum()
            prev_month_sub = df_prev_month.groupby('subkategori')['total_expenditure'].sum()
            
            yoy_growth_sub = ((latest_sub - prev_year_sub) / prev_year_sub.replace(0, np.nan)) * 100
            mom_growth_sub = ((latest_sub - prev_month_sub) / prev_month_sub.replace(0, np.nan)) * 100
            
            if st.session_state.growth_type == 'yoy':
                if not yoy_growth_sub.dropna().empty:
                    best_cat = yoy_growth_sub.idxmax()
                    best_val = yoy_growth_sub.max()
                else:
                    best_cat = "-"
                    best_val = 0
            else:  # mom
                if not mom_growth_sub.dropna().empty:
                    best_cat = mom_growth_sub.idxmax()
                    best_val = mom_growth_sub.max()
                else:
                    best_cat = "-"
                    best_val = 0

        with col1: 
            # Mamin
            # YoY change calculation
            total_prev = df_filtered[
            (df_filtered['tahun'] == tahun_terbaru - 1) &
            (df_filtered['bulan'] == bulan_terbaru) &
            (df_filtered['kategori'] == 'Makanan, minuman dan tembakau')
            ]['total_expenditure'].sum()
            # MoM change calculation
            if bulan_terbaru == 1:
                prev_month = 12
                prev_year = tahun_terbaru - 1
            else:
                prev_month = bulan_terbaru - 1
                prev_year = tahun_terbaru
            total_prev_mom = df_filtered[
            (df_filtered['tahun'] == prev_year) &
            (df_filtered['bulan'] == prev_month) &
            (df_filtered['kategori'] == 'Makanan, minuman dan tembakau')
            ]['total_expenditure'].sum()

            if total_prev > 0:
                yoy_change = ((total_omzet_mamin - total_prev) / total_prev) * 100
            else:
                yoy_change = 0
            if total_prev_mom > 0:
                mom_change = ((total_omzet_mamin - total_prev_mom) / total_prev_mom) * 100
            else:
                mom_change = 0
            delta_class = "negative" if yoy_change < 0 else ""

            st.markdown(f"""
            <div class="metric-container">
            <div class="metric-label">Total Omzet Mamin</div>
            <div class="metric-value">Rp {total_omzet_mamin:,.0f}</div>
            <div class="metric-delta {delta_class}">{yoy_change:.2f}% YoY {mom_change:.2f}% MoM</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            # Non Mamin
            # YoY change calculation
            total_prev = df_filtered[
            (df_filtered['tahun'] == tahun_terbaru - 1) &
            (df_filtered['bulan'] == bulan_terbaru) &
            (df_filtered['kategori'].isin(['Barang Budaya dan Rekreasi', 'Barang Lainnya', 'Peralatan Informasi dan Komunikasi', 'Perlengkapan Rumah Tangga Lainnya', 'Suku Cadang dan Aksesoris']))
            ]['total_expenditure'].sum()
            # MoM change calculation
            if bulan_terbaru == 1:
                prev_month = 12
                prev_year = tahun_terbaru - 1
            else:
                prev_month = bulan_terbaru - 1
                prev_year = tahun_terbaru
            total_prev_mom = df_filtered[
            (df_filtered['tahun'] == prev_year) &
            (df_filtered['bulan'] == prev_month) &
            (df_filtered['kategori'].isin(['Barang Budaya dan Rekreasi', 'Barang Lainnya', 'Peralatan Informasi dan Komunikasi', 'Perlengkapan Rumah Tangga Lainnya', 'Suku Cadang dan Aksesoris']))
            ]['total_expenditure'].sum()

            if total_prev > 0:
                yoy_change = ((total_omzet_non_mamin - total_prev) / total_prev) * 100
            else:
                yoy_change = 0
            if total_prev_mom > 0:
                mom_change = ((total_omzet_non_mamin - total_prev_mom) / total_prev_mom) * 100
            else:
                mom_change = 0
            delta_class = "negative" if yoy_change < 0 else ""

            st.markdown(f"""
            <div class="metric-container">
            <div class="metric-label">Total Omzet Non-Mamin</div>
            <div class="metric-value">Rp {total_omzet_non_mamin:,.0f}</div>
            <div class="metric-delta {delta_class}">{yoy_change:.2f}% YoY {mom_change:.2f}% MoM</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            
            if not st.session_state.show_spe_combined:
                # Show SPE only
                total_prev = df_filtered[
                    (df_filtered['tahun'] == tahun_terbaru - 1) &
                    (df_filtered['bulan'] == bulan_terbaru) &
                    (df_filtered['kategori'].isin(['Makanan, minuman dan tembakau', 'Barang Budaya dan Rekreasi', 
                                                'Barang Lainnya', 'Peralatan Informasi dan Komunikasi', 
                                                'Perlengkapan Rumah Tangga Lainnya', 'Suku Cadang dan Aksesoris'])) &
                    (df_filtered['klasifikasi'] == 'SPE')
                ]['total_expenditure'].sum()
                
                if bulan_terbaru == 1:
                    prev_month = 12
                    prev_year = tahun_terbaru - 1
                else:
                    prev_month = bulan_terbaru - 1
                    prev_year = tahun_terbaru
                    
                total_prev_mom = df_filtered[
                    (df_filtered['tahun'] == prev_year) &
                    (df_filtered['bulan'] == prev_month) &
                    (df_filtered['kategori'].isin(['Makanan, minuman dan tembakau', 'Barang Budaya dan Rekreasi', 
                                                'Barang Lainnya', 'Peralatan Informasi dan Komunikasi', 
                                                'Perlengkapan Rumah Tangga Lainnya', 'Suku Cadang dan Aksesoris'])) &
                    (df_filtered['klasifikasi'] == 'SPE')
                ]['total_expenditure'].sum()
                
                yoy_change = ((total_omzet_spe - total_prev) / total_prev) * 100 if total_prev > 0 else 0
                mom_change = ((total_omzet_spe - total_prev_mom) / total_prev_mom) * 100 if total_prev_mom > 0 else 0
                delta_class = "negative" if yoy_change < 0 else ""
                
                st.markdown(f"""
                <div class="metric-container clickable flip-card">
                    <div class="metric-label">
                        Total Omzet (SPE Only)
                        <span class="toggle-indicator">⇄ Click to toggle</span>
                    </div>
                    <div class="metric-value">Rp {total_omzet_spe:,.0f}</div>
                    <div class="metric-delta {delta_class}">{yoy_change:.2f}% YoY {mom_change:.2f}% MoM</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Show SPE & Non-SPE combined with breakdown
                total_prev = df_filtered[
                    (df_filtered['tahun'] == tahun_terbaru - 1) &
                    (df_filtered['bulan'] == bulan_terbaru) &
                    (df_filtered['kategori'].isin(['Makanan, minuman dan tembakau', 'Barang Budaya dan Rekreasi', 
                                                'Barang Lainnya', 'Peralatan Informasi dan Komunikasi', 
                                                'Perlengkapan Rumah Tangga Lainnya', 'Suku Cadang dan Aksesoris']))
                ]['total_expenditure'].sum()
                
                if bulan_terbaru == 1:
                    prev_month = 12
                    prev_year = tahun_terbaru - 1
                else:
                    prev_month = bulan_terbaru - 1
                    prev_year = tahun_terbaru
                    
                total_prev_mom = df_filtered[
                    (df_filtered['tahun'] == prev_year) &
                    (df_filtered['bulan'] == prev_month) &
                    (df_filtered['kategori'].isin(['Makanan, minuman dan tembakau', 'Barang Budaya dan Rekreasi', 
                                                'Barang Lainnya', 'Peralatan Informasi dan Komunikasi', 
                                                'Perlengkapan Rumah Tangga Lainnya', 'Suku Cadang dan Aksesoris']))
                ]['total_expenditure'].sum()
                
                yoy_change = ((total_omzet_combined - total_prev) / total_prev) * 100 if total_prev > 0 else 0
                mom_change = ((total_omzet_combined - total_prev_mom) / total_prev_mom) * 100 if total_prev_mom > 0 else 0
                delta_class = "negative" if yoy_change < 0 else ""
                
                spe_percentage = (total_omzet_spe / total_omzet_combined * 100) if total_omzet_combined > 0 else 0
                
                st.markdown(f"""
                <div class="metric-container clickable flip-card">
                    <div class="metric-label">
                        Total Omzet (SPE & Non-SPE)
                        <span class="toggle-indicator">⇄ Click to toggle</span>
                    </div>
                    <div class="metric-value">Rp {total_omzet_combined:,.0f}</div>
                    <div class="metric-delta {delta_class}">{yoy_change:.2f}% YoY {mom_change:.2f}% MoM</div>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2);">
                        <div style="font-size: 11px; color: rgba(255,255,255,0.7);">
                            SPE: Rp {total_omzet_spe:,.0f} ({spe_percentage:.1f}%)<br>
                            Non-SPE: Rp {total_omzet_non_spe:,.0f} ({100-spe_percentage:.1f}%)
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:       
            delta_class = "negative" if best_val < 0 else ""
            level_text = "Category" if st.session_state.show_categories else "Sub-Category"
            growth_text = "YoY" if st.session_state.growth_type == 'yoy' else "MoM"
            
            # Truncate long names for better display
            display_name = best_cat[:30] + "..." if len(str(best_cat)) > 30 else best_cat
            
            st.markdown(f"""
            <div class="metric-container clickable">
                <div class="metric-label">
                    Best Growth {level_text}
                    <span class="toggle-indicator">⇄ Click toggles</span>
                </div>
                <div class="metric-value" style="font-size: 20px;">{display_name}</div>
                <div class="metric-delta {delta_class}" style="font-size: 14px;">
                    <strong>{best_val:.2f}% {growth_text}</strong>
                </div>
                <div class="growth-type-selector">
                    <span style="font-size: 10px; color: rgba(255,255,255,0.6);">
                        Viewing: {level_text} | {growth_text} Growth
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        # Time series overview
        # Group by date and category, then normalize each category
        df_ts_cat = df_filtered.groupby(['date', 'kategori'])['total_expenditure'].sum().reset_index()
        
        # Create normalized data for each category (base = first value for each category)
        df_normalized = df_ts_cat.copy()
        df_normalized['normalized_price'] = 1.0
        
        for kategori in df_filtered['kategori'].unique():
            mask = df_normalized['kategori'] == kategori
            kategori_data = df_normalized[mask].copy()
            if len(kategori_data) > 0:
                base_value = kategori_data['total_expenditure'].iloc[0]
                if base_value != 0:
                    df_normalized.loc[mask, 'normalized_price'] = kategori_data['total_expenditure'] / base_value
        
        # Create color palette for categories
        colors = [
                '#667eea',  # Soft blue-purple
                '#764ba2',  # Deep purple
                '#f093fb',  # Pink gradient
                '#f5576c',  # Coral red
                '#4facfe',  # Sky blue
                '#00f2fe',  # Cyan
                '#43e97b',  # Green gradient
                '#38f9d7',  # Turquoise
                '#ffecd2',  # Peach
                '#fcb69f',  # Orange gradient
                '#ff9a9e',  # Rose
                '#fecfef'   # Light pink
    ]
        
        fig = go.Figure()
        
        # Add trace for each category
        for i, kategori in enumerate(df_filtered['kategori'].unique()):
            kategori_data = df_normalized[df_normalized['kategori'] == kategori]
            
            fig.add_trace(go.Scatter(
                x=kategori_data['date'],
                y=kategori_data['normalized_price'],
                mode='lines+markers',
                name=kategori,
                line=dict(
                    color=colors[i % len(colors)], 
                    width=3,
                    shape='linear'
                ),
                marker=dict(
                    size=6,
                    color=colors[i % len(colors)],
                    line=dict(width=2, color='white'),
                    opacity=0.8,
                    symbol='circle'
                ),
                hovertemplate=f'<b style="color:{colors[i % len(colors)]}">{kategori}</b><br>' +
                            '<b>Date:</b> %{x}<br>' +
                            '<b>Normalized Price:</b> %{y:.2f}<br>' +
                            '<extra></extra>',
                hoverlabel=dict(
                    bgcolor=colors[i % len(colors)],
                    bordercolor='white',
                    font=dict(color='white', size=12)
                )
            ))
        
        fig.update_layout(
            title="Normalized Omzet Trends by Category",
            xaxis_title="Date",
            yaxis_title="Normalized Omzet",
            height=600,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Subcategory Performance by Category
        st.subheader("Normalized Omzet Trends by Sub-Category")
        categories = sorted(df_filtered['kategori'].unique())
        NUM_COLS = 4
        cols = st.columns(NUM_COLS)

        for i, kategori in enumerate(categories):
            df_cat = df_filtered[df_filtered['kategori'] == kategori].copy()
            df_sub_ts = (
                df_cat.groupby(['date', 'subkategori'])['total_expenditure']
                .sum()
                .reset_index()
            )

            # Normalisasi per subkategori
            normalized_list = []
            for subkat in df_cat['subkategori'].unique():
                df_subkat = df_sub_ts[df_sub_ts['subkategori'] == subkat].copy()
                if not df_subkat.empty:
                    base_val = df_subkat['total_expenditure'].iloc[0]
                    if base_val != 0:
                        df_subkat['normalized'] = df_subkat['total_expenditure'] / base_val
                        df_subkat['subkategori'] = subkat
                        normalized_list.append(df_subkat)
            if not normalized_list:
                continue

            df_norm = pd.concat(normalized_list)

            # Altair line chart
            chart = (
                alt.Chart(df_norm)
                .mark_line(strokeWidth=2.5)
                .encode(
                    alt.X("date:T", title="Date"),
                    alt.Y("normalized:Q", title="Price", scale=alt.Scale(zero=False)),
                    alt.Color("subkategori:N", legend=alt.Legend(orient="bottom")),
                    tooltip=["date:T", "subkategori:N", alt.Tooltip("normalized:Q", format=".2f")],
                )
                .properties(title=kategori, height=280)
                .configure_axis(
                    grid=True,
                    gridColor="rgba(255,255,255,0.08)",
                    labelColor="rgba(255,255,255,0.7)",
                    titleColor="rgba(255,255,255,0.7)"
                )
                .configure_title(
                    fontSize=12,
                    color="white",
                    anchor="middle"
                )
                .configure_legend(
                    labelColor="white",
                    title=None,
                    orient="bottom"
                )
            )

            # Masukkan ke container dengan border
            cell = cols[i % NUM_COLS].container(border=True)
            cell.altair_chart(chart, use_container_width=True)
    
    # Tab 2: Indeks Penjualan
    with tab2:
        # Calculate sales index
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            base_period = st.selectbox(
                "Pilih Periode Basis",
                options=['2022'],
                index=0
            )
        st.header("Analisis Indeks Penjualan Riil")
        df_index = comparing_index(df_filtered, base_period)
        # Ambil tahun awal dan akhir
        tahun_awal = df_index['Tahun'].min()
        tahun_akhir = df_index['Tahun'].max()
        # Ambil bulan awal dan bulan akhir (berdasarkan tahun terkait)
        bulan_awal = df_index[df_index['Tahun'] == tahun_awal]['Bulan'].min()
        bulan_akhir = df_index[df_index['Tahun'] == tahun_akhir]['Bulan'].max()
        st.subheader(f"Date: {bulan_awal:02d}/{tahun_awal} - {bulan_akhir:02d}/{tahun_akhir}")
        NUM_COLS = 3
        cols = st.columns(NUM_COLS)
        comodity_group = ['Makanan, Minuman, dan Tembakau', 'Barang Budaya & Rekreasi', 
                        'Barang Lainnya', 'Peralatan Informasi & Komunikasi', 
                        'Perlengkapan Rumah Tangga Lainnya', 'Suku Cadang & Aksesoris']

        for i, kategori in enumerate(comodity_group):
            # Filter data untuk kategori tertentu
            df_cat = df_index[df_index['Kategori'] == kategori].copy()
            # Buat kolom date dari Tahun dan Bulan
            df_cat['date'] = pd.to_datetime(df_cat['Tahun'].astype(str) + '-' + df_cat['Bulan'].astype(str).str.zfill(2) + '-01')
            # Hitung korelasi antara Scanner_index dan IPR_index
            correlation = df_cat['Scanner_index'].corr(df_cat['IPR_index'])
            # Reshape data untuk plotting
            df_plot = df_cat.melt(
                id_vars=['date'], 
                value_vars=['Scanner_index', 'IPR_index'],
                var_name='Tipe_Index',
                value_name='nilai_index'
            )
            # Rename untuk label yang lebih baik
            df_plot['Tipe_Index'] = df_plot['Tipe_Index'].replace({
                'Scanner_index': 'Scanner Index',
                'IPR_index': 'IPR Index'
            })
            
            # Line chart
            line_chart = (
                alt.Chart(df_plot.sort_values("date"))
                .mark_line(strokeWidth=2.5)
                .encode(
                    alt.X("date:T", title="Date", timeUnit="yearmonth", axis=alt.Axis(format='%Y', tickCount="year")),
                    alt.Y("nilai_index:Q", title="Index Value", scale=alt.Scale(zero=False)),
                    alt.Color("Tipe_Index:N", 
                            legend=alt.Legend(orient="bottom"),
                            scale=alt.Scale(scheme='category10')),
                    tooltip=[
                        alt.Tooltip("date:T", title="Date", format="%b %Y"),
                        alt.Tooltip("Tipe_Index:N", title="Type"),
                        alt.Tooltip("nilai_index:Q", title="Value", format=".2f")
                    ],
                )
            )
            
            # Tentukan warna berdasarkan nilai korelasi
            if correlation >= 0.8:
                corr_color = "#22c55e"  # Hijau - korelasi sangat kuat
                corr_label = "Sangat Kuat"
            elif correlation >= 0.6:
                corr_color = "#84cc16"  # Hijau muda - korelasi kuat
                corr_label = "Kuat"
            elif correlation >= 0.4:
                corr_color = "#eab308"  # Kuning - korelasi sedang
                corr_label = "Sedang"
            elif correlation >= 0.2:
                corr_color = "#f97316"  # Orange - korelasi lemah
                corr_label = "Lemah"
            else:
                corr_color = "#ef4444"  # Merah - korelasi sangat lemah
                corr_label = "Sangat Lemah"
            
            # Buat annotation untuk korelasi (kotak info di kanan atas)
            corr_text = alt.Chart(pd.DataFrame({
                'x': [df_plot['date'].max()],
                'y': [df_plot['nilai_index'].max()],
                'corr': [f'r = {correlation:.3f}'],
                'label': [corr_label]
            })).mark_text(
                align='right',
                baseline='top',
                dx=-10,
                dy=10,
                fontSize=11,
                fontWeight='bold',
                color=corr_color
            ).encode(
                x='x:T',
                y='y:Q',
                text='corr:N'
            )
            
            # Buat kotak background untuk korelasi
            corr_bg = alt.Chart(pd.DataFrame({
                'x': [df_plot['date'].max()],
                'y': [df_plot['nilai_index'].max()],
            })).mark_rect(
                align='right',
                baseline='top',
                dx=-80,
                dy=5,
                width=70,
                height=25,
                opacity=0.8,
                cornerRadius=5,
                color='#1e293b'
            ).encode(
                x='x:T',
                y='y:Q',
            )
            
            # Gabungkan semua layer
            chart = (
                (corr_bg + line_chart + corr_text)
                .properties(title=kategori, height=280)
                .configure_axis(
                    grid=True,
                    gridColor="rgba(255,255,255,0.08)",
                    labelColor="rgba(255,255,255,0.7)",
                    titleColor="rgba(255,255,255,0.7)"
                )
                .configure_title(
                    fontSize=12,
                    color="white",
                    anchor="middle"
                )
                .configure_legend(
                    labelColor="white",
                    title=None,
                    orient="bottom"
                )
                .configure_view(
                    strokeWidth=0
                )
            )
            
            # Masukkan ke container dengan border
            cell = cols[i % NUM_COLS].container(border=True)
            cell.altair_chart(chart, use_container_width=True)

        col1, col2, col3 = st.columns([1, 1, 3])
        komoditas_dict = {
                'Makanan, Minuman, dan Tembakau': [
                    'Bahan Makanan', 'Makanan Jadi', 'Minuman', 'Tembakau'
                ],
                'Barang Budaya & Rekreasi': [
                    'Alat Olahraga', 'Alat Tulis dan Gambar', 'Kertas, Karton, Cetakan', 'Mainan anak-anak'
                ],
                'Barang Lainnya': [
                    '*Sandang', 'Alas Kaki & Perlengkapannya', 'Farmasi', 'Kacamata, perhiasan, jam', 
                    'Kosmetik', 'Pakaian Jadi', 'Tas, dompet, koper dan ransel'
                ],
                'Peralatan Informasi & Komunikasi': [
                    'Elektronik (audio/video)'
                ],
                'Perlengkapan Rumah Tangga Lainnya': [
                    'Bahan Konstruksi dari Logam', 'Elektronik (selain audio/video)', 'Meubel', 'Perabotan Rumah Tangga'
                ],
                'Suku Cadang & Aksesoris': [
                    'Suku Cadang & Aksesoris Mobil'
                ]
            }
        with col1:
            group = st.selectbox(
                "Kelompok Komoditas",
                options=list(komoditas_dict.keys()),
                index=0
            )
        with col2:
            subgroup = st.selectbox(
                "Subkelompok Komoditas",
                options=komoditas_dict[group],
                index=0
            )
        with col3:
            # Correlation metric
            correlation = np.corrcoef(df_index['Scanner_index'][df_index['Kategori'] == subgroup], df_index['IPR_index'][df_index['Kategori'] == subgroup])[0, 1]
            st.metric("Korelasi dengan IPR", f"{correlation:.3f}")
        
        colorsTab2 = [
                "#267bdb",  
                '#f97316',  
    ]
        # Plot comparison
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_index['Periode'][df_index['Kategori'] == subgroup],
            y=df_index['IPR_index'][df_index['Kategori'] == subgroup],
            mode='lines+markers',
            name='IPR Index',
            line=dict(
                    color=colorsTab2[0], 
                    width=3,
                    shape='linear'
            ),
            marker=dict(
                    size=6,
                    color=colorsTab2[0],
                    line=dict(width=2, color='white'),
                    opacity=0.8,
                    symbol='circle'
            ),
            hovertemplate=f'<b style="color:{colorsTab2[0]}">{kategori}</b><br>' +
                            '<b>Date:</b> %{x}<br>' +
                            '<b>Indeks Penjualan Riil:</b> %{y:.2f}<br>' +
                            '<extra></extra>',
            hoverlabel=dict(
                    bgcolor=colorsTab2[0],
                    bordercolor='white',
                    font=dict(color='white', size=12)
            )
        ))

        fig.add_trace(go.Scatter(
            x=df_index['Periode'][df_index['Kategori'] == subgroup],
            y=df_index['Scanner_index'][df_index['Kategori'] == subgroup],
            mode='lines+markers',
            name='Scanner Index',
            line=dict(
                    color=colorsTab2[1], 
                    width=3,
                    shape='linear'
            ),
            marker=dict(
                    size=6,
                    color=colorsTab2[1],
                    line=dict(width=2, color='white'),
                    opacity=0.8,
                    symbol='circle'
            ),
            hovertemplate=f'<b style="color:{colorsTab2[1]}">{kategori}</b><br>' +
                            '<b>Date:</b> %{x}<br>' +
                            '<b>Scanner Data Index:</b> %{y:.2f}<br>' +
                            '<extra></extra>',
            hoverlabel=dict(
                    bgcolor=colorsTab2[1],
                    bordercolor='white',
                    font=dict(color='white', size=12)
            )
        ))
        
        fig.update_layout(
            title=f"Perbandingan Indeks Penjualan (Basis: {base_period})",
            xaxis_title="Periode",
            yaxis_title="Indeks",
            hovermode='x unified',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    # Tab 3: Trend Analysis
    with tab3:
        st.header("📄 Analisis Tren dan Musiman")
        st.info("Sedang dalam masa pengembangan..")
    
    with tab4:
        st.header("🏷️ Analisis per Kategori dan Subkategori")
        st.info("Sedang dalam masa pengembangan..")
    
    with tab5:
        st.header("📉 Analisis Pertumbuhan YoY dan MoM")
        st.info("Sedang dalam masa pengembangan..")
    
    with tab6:
        st.header("🎯 Forecasting dan Prediksi")
        st.info("Sedang dalam masa pengembangan..")
    
    with tab7:
        st.header("📋 Data Explorer")
        st.info("Sedang dalam masa pengembangan..")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Dashboard Analisis Indeks Penjualan Riil - Scanner Data</p>
        <p>Bank Indonesia | Statistik Sektor Riil</p>
    </div>
    """, unsafe_allow_html=True)

# Main application flow
def main():
    if not st.session_state.authenticated:
        login_page()
    elif not st.session_state.file_uploaded:
        upload_page()
    else:
        main_dashboard()

# Run the app
if __name__ == "__main__":
    main()