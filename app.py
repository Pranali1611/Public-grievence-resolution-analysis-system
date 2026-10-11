from pathlib import Path
import base64
import io
import shutil
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modules import dashboard, department_analysis, efficiency_analysis, pending_analysis

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "Dept_stat_receipt_disposal_010112019.csv"
BACKUP_FILE = ROOT / "data" / "Dept_stat_receipt_disposal_backup.csv"
LOGO_FILE = ROOT / "assets" / "logo.jpg"

COL_NAME = department_analysis.COL_NAME
COL_RECEIVED = department_analysis.COL_RECEIVED
COL_DISPOSED = department_analysis.COL_DISPOSED
COL_PENDING = department_analysis.COL_PENDING
COL_RATE = efficiency_analysis.COL_RATE

DURATION_COLS = pending_analysis.DURATION_COLS
DURATION_LABELS = pending_analysis.DURATION_LABELS

REQUIRED_COLUMNS = [
    COL_NAME,
    COL_RECEIVED,
    COL_DISPOSED,
    COL_PENDING,
    DURATION_COLS[0],
    DURATION_COLS[1],
    DURATION_COLS[2],
    DURATION_COLS[3],
]

STATE_AND_UTS = {
    "Andaman & Nicobar", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
    "Union Territory of Chandigarh", "Chhattisgarh", "Union Territory of Dadra & Nagar Haveli",
    "Union Territory of Daman & Diu", "Gujarat", "Goa", "Himachal Pradesh", "Haryana",
    "Jharkhand", "Jammu and Kashmir", "Kerala", "Karnataka", "Union Territory of Lakshadweep",
    "Meghalaya", "Maharashtra", "Manipur", "Madhya Pradesh", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Puducherry", "Rajasthan", "Sikkim", "Telangana",
    "Tamil Nadu", "Tripura", "Uttarakhand", "Uttar Pradesh", "West Bengal", "Delhi",
}


def classify_entity(name: str) -> str:
    n = str(name).strip()
    if n in STATE_AND_UTS or "Union Territory" in n or "State" in n:
        return "State / Union Territory"
    return "Central Ministry / Department"


def get_logo_base64() -> str:
    if LOGO_FILE.exists():
        with open(LOGO_FILE, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


LOGO_B64 = get_logo_base64()

# Streamlit Page Config - strictly NO emojis & SEO Optimized
st.set_page_config(
    page_title="Public Grievance Resolution Analysis System | National Governance Analytics Portal",
    page_icon=str(LOGO_FILE) if LOGO_FILE.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://darpg.gov.in",
        "Report a bug": "https://cpgrams.gov.in",
        "About": """
        ### Public Grievance Resolution Analysis System
        Comprehensive monitoring and evaluation of public grievance receipts, disposals, and pending durations across Central Ministries, Departments, and State Administrations in India.
        Reporting Period: 01 January 2016 to 01 November 2019.
        """,
    },
)




# Comprehensive Styling: Light Cream Theme, Almarai Typography, High Contrast, Fully Mobile-Responsive
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Global Font and Light Cream Theme */
html, body, [class*="css"], .stApp {
    font-family: 'Almarai', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #FAF7F0 !important;
    color: #1A1816 !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}

/* Main Container */
.main .block-container {
    padding-top: 1.2rem;
    padding-bottom: 2.5rem;
    max-width: 1420px;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Almarai', sans-serif !important;
    font-weight: 700 !important;
    color: #1A1816 !important;
    letter-spacing: -0.015em;
    margin-top: 0;
}

p, span, label, div {
    color: #1A1816;
}

/* Top Header Banner with Logo */
.portal-header {
    background: #FFFFFF;
    border: 1px solid #E6DDCF;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 3px 16px rgba(45, 38, 30, 0.04);
}
.portal-header-flex {
    display: flex;
    align-items: center;
    gap: 20px;
}
.portal-logo-img {
    width: 76px;
    height: 76px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #D5C9B4;
    box-shadow: 0 4px 14px rgba(45, 38, 30, 0.08);
    background: #FAF7F0;
    flex-shrink: 0;
}
.portal-title {
    font-size: 26px;
    font-weight: 800;
    color: #1A1816;
    margin: 0 0 4px 0;
    line-height: 1.25;
}
.portal-subtitle {
    font-size: 13.5px;
    color: #4D453A;
    margin: 0 0 6px 0;
    line-height: 1.5;
    font-weight: 500;
}
.portal-meta-badge {
    display: inline-flex;
    align-items: center;
    background: #F3ECE0;
    color: #2D2721;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 16px;
    border: 1px solid #DCD0BC;
}

/* Hero Preset Bar Container */
.hero-preset-container {
    background: #FFFFFF;
    border: 1px solid #E2D7C4;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(45, 38, 30, 0.03);
}
.hero-preset-title {
    font-size: 13px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #635A4E;
    margin-bottom: 4px;
}
.hero-preset-sub {
    font-size: 12.5px;
    color: #7A7063;
    margin-bottom: 0px;
    line-height: 1.4;
}

/* Active Scope Notification Banner */
.active-scope-banner {
    background: #F8F3EA;
    border: 1px solid #DED3BF;
    border-left: 5px solid #1B5E43;
    border-radius: 6px;
    padding: 12px 18px;
    margin-top: 14px;
    margin-bottom: 18px;
    font-size: 13.5px;
    color: #1A1816;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    box-shadow: 0 2px 6px rgba(45, 38, 30, 0.03);
}
.active-scope-badge {
    font-size: 12px;
    font-weight: 700;
    color: #1B5E43;
    background: #E8F3ED;
    padding: 4px 10px;
    border-radius: 12px;
    border: 1px solid #C4DFD2;
    white-space: nowrap;
}

/* Sidebar Brand Header */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    background: #FFFFFF;
    border: 1px solid #DFD5C2;
    border-radius: 8px;
    margin-bottom: 18px;
    box-shadow: 0 2px 8px rgba(45, 38, 30, 0.03);
}
.sidebar-logo-img {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    object-fit: cover;
    border: 1.5px solid #D5C9B4;
    flex-shrink: 0;
}
.sidebar-brand-title {
    font-size: 14px;
    font-weight: 800;
    color: #1A1816;
    line-height: 1.2;
}
.sidebar-brand-sub {
    font-size: 11px;
    color: #6C6255;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* Metric Cards */
.custom-metric-card {
    background: #FFFFFF;
    border: 1px solid #E6DDCF;
    border-radius: 8px;
    padding: 18px 20px;
    box-shadow: 0 2px 10px rgba(45, 38, 30, 0.03);
    position: relative;
    overflow: hidden;
    margin-bottom: 16px;
    min-height: 125px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-sizing: border-box;
}
.custom-metric-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
}
.card-blue::before { background: #1B5E43; }
.card-green::before { background: #2A6F55; }
.card-red::before { background: #B84A39; }
.card-amber::before { background: #C4822B; }

.metric-label-text {
    font-size: 11.5px;
    font-weight: 700;
    color: #635A4E;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
    line-height: 1.2;
}
.metric-value-text {
    font-size: 28px;
    font-weight: 800;
    color: #1A1816;
    line-height: 1.15;
    margin-bottom: 4px;
    font-feature-settings: "tnum" 1;
}
.metric-sub-text {
    font-size: 12px;
    color: #5A5247;
    font-weight: 600;
    line-height: 1.35;
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background-color: #F4ECE0 !important;
    border-right: 1px solid #DFD5C2 !important;
}
[data-testid="stSidebar"] * {
    color: #1A1816 !important;
}
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    color: #1A1816 !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stCaption {
    color: #1A1816 !important;
    font-weight: 600 !important;
}

/* Unified Button Styling: Perfect Baseline Alignment and Uniform Dimensions */
.stButton > button,
button[data-testid="baseButton-primary"],
button[data-testid="baseButton-secondary"],
button[kind="primary"],
button[kind="secondary"] {
    min-height: 44px !important;
    height: 44px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    font-family: 'Almarai', 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    line-height: 1.2 !important;
    width: 100% !important;
    box-sizing: border-box !important;
    border-radius: 6px !important;
    transition: all 0.15s ease-in-out !important;
    padding: 8px 14px !important;
}

/* Primary (Active) Button Styling - Deep Forest Emerald */
button[data-testid="baseButton-primary"],
button[kind="primary"] {
    background-color: #1B5E43 !important;
    color: #FFFFFF !important;
    border: 1px solid #134632 !important;
    font-weight: 800 !important;
    box-shadow: 0 2px 8px rgba(27, 94, 67, 0.25) !important;
}
button[data-testid="baseButton-primary"]:hover,
button[kind="primary"]:hover {
    background-color: #144933 !important;
    border-color: #0E3626 !important;
    color: #FFFFFF !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(27, 94, 67, 0.3) !important;
}
button[data-testid="baseButton-primary"]:active,
button[kind="primary"]:active {
    background-color: #0E3626 !important;
    border-color: #0B2B1E !important;
    color: #FFFFFF !important;
    transform: translateY(0) !important;
}

/* Secondary (Inactive) Button Styling */
button[data-testid="baseButton-secondary"],
button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #1A1816 !important;
    border: 1px solid #D5C8B4 !important;
    box-shadow: 0 1px 4px rgba(45, 38, 30, 0.04) !important;
}
button[data-testid="baseButton-secondary"]:hover,
button[kind="secondary"]:hover {
    background-color: #ECE3D2 !important;
    border-color: #BAAB92 !important;
    color: #1A1816 !important;
    transform: translateY(-1px);
}
button[data-testid="baseButton-secondary"]:active,
button[kind="secondary"]:active {
    background-color: #1B5E43 !important;
    border-color: #134632 !important;
    color: #FFFFFF !important;
    transform: translateY(0);
}

/* Download Buttons */
.stDownloadButton > button {
    min-height: 44px !important;
    height: 44px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background-color: #1B5E43 !important;
    color: #FFFFFF !important;
    border: 1px solid #134632 !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    padding: 8px 16px !important;
    font-family: 'Almarai', sans-serif !important;
    font-size: 13.5px !important;
}
.stDownloadButton > button:hover {
    background-color: #144933 !important;
    color: #FFFFFF !important;
}

/* Polished Dropdowns & BaseWeb Select */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #D5C9B5 !important;
    border-radius: 6px !important;
    min-height: 42px !important;
}
div[data-baseweb="select"] > div:hover {
    border-color: #B5A893 !important;
}
div[data-baseweb="select"] * {
    color: #1A1816 !important;
}

/* Popover & Listbox options */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[role="listbox"],
[data-testid="stVirtualDropdown"] {
    background-color: #FFFFFF !important;
    border: 1px solid #D5C9B5 !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 24px rgba(45, 38, 30, 0.12) !important;
}

[data-baseweb="menu"] li,
[role="listbox"] li,
[role="option"] {
    background-color: #FFFFFF !important;
    color: #1A1816 !important;
    font-family: 'Almarai', sans-serif !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
}
[data-baseweb="menu"] li:hover,
[role="listbox"] li:hover,
[role="option"]:hover {
    background-color: #F4ECE0 !important;
    color: #1A1816 !important;
}
[aria-selected="true"] {
    background-color: #EFE5D4 !important;
    color: #1A1816 !important;
    font-weight: 700 !important;
}

/* Multiselect Tags */
[data-baseweb="tag"] {
    background-color: #F3ECE0 !important;
    border: 1px solid #D8CDBA !important;
    border-radius: 4px !important;
    padding: 3px 8px !important;
}
[data-baseweb="tag"] span {
    color: #1A1816 !important;
    font-size: 12.5px !important;
    font-weight: 600 !important;
}
[data-baseweb="tag"] svg {
    fill: #5A5247 !important;
}
[data-baseweb="tag"] svg:hover {
    fill: #B84A39 !important;
}

/* Dropdown Arrow / Search icons */
[data-baseweb="select"] svg {
    fill: #5A5247 !important;
}
[data-baseweb="select"] input {
    color: #1A1816 !important;
    font-family: 'Almarai', sans-serif !important;
    font-size: 13.5px !important;
}
[data-baseweb="select"] input::placeholder {
    color: #6C6255 !important;
}

/* Text Inputs */
[data-testid="stTextInput"] input {
    background-color: #FFFFFF !important;
    color: #1A1816 !important;
    border: 1px solid #D5C9B5 !important;
    border-radius: 6px !important;
    padding: 9px 12px !important;
}

/* Sliders */
[data-testid="stSlider"] div {
    color: #1A1816 !important;
}

/* Tabs: Smooth Horizontal Scrolling for Full Mobile Responsiveness */
div[data-testid="stTabs"] {
    margin-top: 8px;
    margin-bottom: 20px;
}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #F1E9DC;
    padding: 6px 8px;
    border-radius: 8px;
    border: 1px solid #E1D6C2;
    gap: 6px;
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch !important;
    scrollbar-width: thin !important;
}
div[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Almarai', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    color: #4D453A !important;
    background-color: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 9px 18px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
}
div[data-testid="stTabs"] button[role="tab"]:hover {
    color: #1A1816 !important;
    background-color: #E8DFC9 !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #1A1816 !important;
    font-weight: 800 !important;
    box-shadow: 0 2px 8px rgba(45, 38, 30, 0.08) !important;
    border: 1px solid #DCD0BC !important;
    border-bottom: 3px solid #1B5E43 !important;
}

/* Dataframe table */
[data-testid="stDataFrame"] {
    border: 1px solid #E2D7C4 !important;
    border-radius: 8px !important;
    background-color: #FFFFFF !important;
}

/* Card Header Block (Self-contained, strictly valid DOM) */
.card-header-block {
    background-color: #FFFFFF;
    border: 1px solid #E6DDCF;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(45, 38, 30, 0.03);
}
.analytical-card-header {
    font-size: 17px;
    font-weight: 800;
    color: #1A1816;
    margin-bottom: 4px;
    line-height: 1.25;
}
.analytical-card-sub {
    font-size: 13px;
    color: #635A4E;
    margin-bottom: 0px;
    font-weight: 500;
    line-height: 1.45;
}

/* Insights callout box */
.insights-box {
    background-color: #F7F2E7;
    border: 1px solid #E2D7C2;
    border-left: 4px solid #2A6F55;
    border-radius: 6px;
    padding: 16px 20px;
    margin-top: 14px;
    margin-bottom: 16px;
}
.insights-box ul {
    margin: 0;
    padding-left: 20px;
    color: #2D2721;
}
.insights-box li {
    margin-bottom: 8px;
    line-height: 1.6;
    font-size: 13.5px;
}

/* Operation Status Banners */
.status-success-banner {
    background: #E8F5EE;
    border: 1px solid #B8E0CA;
    border-left: 5px solid #1B5E43;
    border-radius: 6px;
    padding: 12px 18px;
    margin-bottom: 18px;
    font-size: 13.5px;
    color: #0E3626;
    font-weight: 600;
    box-shadow: 0 2px 6px rgba(27, 94, 67, 0.04);
}
.status-warning-banner {
    background: #FDF3E7;
    border: 1px solid #F5D3A8;
    border-left: 5px solid #C4822B;
    border-radius: 6px;
    padding: 12px 18px;
    margin-bottom: 18px;
    font-size: 13.5px;
    color: #633C06;
    font-weight: 600;
}
.status-error-banner {
    background: #FBF0EB;
    border: 1px solid #ECC1B7;
    border-left: 5px solid #B84A39;
    border-radius: 6px;
    padding: 12px 18px;
    margin-bottom: 18px;
    font-size: 13.5px;
    color: #722013;
    font-weight: 600;
}

/* Number inputs and file uploader */
div[data-testid="stNumberInput"] input {
    background-color: #FFFFFF !important;
    color: #1A1816 !important;
    border: 1px solid #D5C9B5 !important;
    border-radius: 6px !important;
    font-family: 'Almarai', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}
div[data-testid="stNumberInput"] button {
    background-color: #F8F3EA !important;
    border-color: #D5C9B5 !important;
    color: #1A1816 !important;
}
div[data-testid="stNumberInput"] button:hover {
    background-color: #EDE3D2 !important;
}
div[data-testid="stFileUploader"] section {
    background-color: #FAF7F0 !important;
    border: 2px dashed #D5C9B5 !important;
    border-radius: 8px !important;
}
div[data-testid="stFileUploader"] section:hover {
    border-color: #1B5E43 !important;
}

/* Data Studio Sub-Card */
.data-mgmt-card {
    background: #FFFFFF;
    border: 1px solid #E2D7C2;
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 18px;
    box-shadow: 0 2px 8px rgba(45, 38, 30, 0.03);
}
.data-mgmt-card-title {
    font-size: 16px;
    font-weight: 800;
    color: #1A1816;
    margin-bottom: 4px;
}
.data-mgmt-card-sub {
    font-size: 13px;
    color: #635A4E;
    margin-bottom: 16px;
    line-height: 1.5;
}
.preview-kpi-badge {
    background: #FFFFFF;
    border: 1px solid #DFD5C2;
    border-radius: 6px;
    padding: 10px 14px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(45, 38, 30, 0.03);
}
.preview-kpi-val {
    font-size: 18px;
    font-weight: 800;
    color: #1A1816;
}
.preview-kpi-lbl {
    font-size: 11px;
    font-weight: 700;
    color: #635A4E;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-top: 2px;
}

/* Filter Panel Card */
.filter-panel-card {
    background-color: #FFFFFF;
    border: 1px solid #E2D7C4;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(45, 38, 30, 0.03);
}
.filter-panel-title {
    font-size: 14px;
    font-weight: 800;
    color: #1A1816;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.filter-panel-sub {
    font-size: 12.5px;
    color: #635A4E;
    margin-bottom: 0px;
    line-height: 1.45;
}

/* ------------------------------------------------------------- */
/* RESPONSIVE MEDIA QUERIES FOR MOBILE AND TABLET SCREENS         */
/* ------------------------------------------------------------- */

/* Tablet Screens (<= 992px) */
@media (max-width: 992px) {
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .portal-header {
        padding: 16px 18px;
    }
    .portal-title {
        font-size: 22px;
    }
    .metric-value-text {
        font-size: 24px;
    }
}

/* Mobile Screens (<= 768px) */
@media (max-width: 768px) {
    .main .block-container {
        padding-top: 0.8rem;
        padding-bottom: 1.5rem;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }
    .portal-header {
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .portal-header-flex {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }
    .portal-logo-img {
        width: 56px;
        height: 56px;
    }
    .portal-title {
        font-size: 20px;
        line-height: 1.25;
    }
    .portal-subtitle {
        font-size: 12.5px;
        line-height: 1.45;
    }
    .portal-meta-badge {
        font-size: 11px;
        padding: 3px 10px;
    }
    .hero-preset-container {
        padding: 12px 14px;
    }
    .active-scope-banner {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
        padding: 10px 14px;
        font-size: 12.5px;
    }
    .custom-metric-card {
        padding: 14px 16px;
        min-height: auto;
        margin-bottom: 12px;
    }
    .metric-value-text {
        font-size: 22px;
    }
    .metric-label-text {
        font-size: 11px;
    }
    .metric-sub-text {
        font-size: 11.5px;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 4px;
        padding: 4px;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        font-size: 12.5px !important;
        padding: 7px 12px !important;
    }
    .stButton > button,
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-secondary"] {
        font-size: 12.5px !important;
        min-height: 40px !important;
        height: 40px !important;
        padding: 6px 10px !important;
    }
    .analytical-card-header {
        font-size: 15.5px;
    }
    .analytical-card-sub {
        font-size: 12px;
    }
    .insights-box {
        padding: 12px 14px;
        font-size: 12.5px;
    }
    .insights-box li {
        font-size: 12.5px;
        margin-bottom: 6px;
    }
}

/* Small Handhelds (<= 480px) */
@media (max-width: 480px) {
    .portal-title {
        font-size: 18px;
    }
    .metric-value-text {
        font-size: 20px;
    }
    .stButton > button {
        font-size: 12px !important;
    }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_data_mtime() -> float:
    try:
        return DATA_FILE.stat().st_mtime
    except Exception:
        return 0.0


@st.cache_data
def load_data(file_mtime: float) -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    df.columns = [str(c).strip() for c in df.columns]
    df[COL_NAME] = df[COL_NAME].astype(str).str.strip()
    num_cols = [COL_RECEIVED, COL_DISPOSED, COL_PENDING] + DURATION_COLS
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    return df


def save_dataset_to_csv(df: pd.DataFrame) -> bool:
    try:
        save_cols = [c for c in REQUIRED_COLUMNS if c in df.columns]
        save_df = df[save_cols].copy()
        save_df.to_csv(DATA_FILE, index=False)
        load_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving dataset to CSV: {e}")
        return False


def restore_dataset_from_backup() -> bool:
    try:
        if BACKUP_FILE.exists():
            import shutil
            shutil.copyfile(BACKUP_FILE, DATA_FILE)
            load_data.clear()
            return True
        return False
    except Exception as e:
        st.error(f"Error restoring backup: {e}")
        return False


try:
    data = load_data(get_data_mtime())
except Exception as err:
    st.error(f"Failed to load dataset: {err}")
    if BACKUP_FILE.exists():
        if st.button("Restore Default Dataset from Backup"):
            restore_dataset_from_backup()
            st.rerun()
    st.stop()

# National Grand Totals (Dynamically calculated based on the loaded dataset)
NAT_RECEIVED = int(data[COL_RECEIVED].sum()) if not data.empty else 0
NAT_DISPOSED = int(data[COL_DISPOSED].sum()) if not data.empty else 0
NAT_PENDING = int(data[COL_PENDING].sum()) if not data.empty else 0
NAT_RATE = round((NAT_DISPOSED / NAT_RECEIVED) * 100, 2) if NAT_RECEIVED > 0 else 0.0

# Session State Initialization
if "active_preset" not in st.session_state:
    st.session_state["active_preset"] = "all"
if "dept_filter" not in st.session_state:
    st.session_state["dept_filter"] = []
if "sort_filter" not in st.session_state:
    st.session_state["sort_filter"] = "Total Receipts"
if "top_slider" not in st.session_state:
    st.session_state["top_slider"] = 10


# Callback to set any preset and immediately synchronize all controls
def set_preset(preset_key: str):
    st.session_state["active_preset"] = preset_key
    st.session_state["dept_filter"] = []
    if preset_key == "all":
        st.session_state["sort_filter"] = "Total Receipts"
    elif preset_key == "top_backlog":
        st.session_state["sort_filter"] = "Pending Backlog"
    elif preset_key == "top_volume":
        st.session_state["sort_filter"] = "Total Receipts"
    elif preset_key == "top_disposal":
        st.session_state["sort_filter"] = "Disposal Rate"


# Sidebar - Filters & Synchronized Controls
with st.sidebar:
    if LOGO_B64:
        st.markdown(
            f"""
            <div class="sidebar-brand">
                <img src="data:image/jpeg;base64,{LOGO_B64}" class="sidebar-logo-img" alt="Emblem" />
                <div>
                    <div class="sidebar-brand-title">Public Grievance</div>
                    <div class="sidebar-brand-sub">Analytics Portal</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Controls and Filters")
    st.markdown("Customize rankings, department focus, and comparative views.")

    # Sidebar Quick Action Buttons with active highlighting
    st.markdown("**Quick Preset Views**")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.button(
            "National Overview",
            type="primary" if st.session_state["active_preset"] == "all" and not st.session_state.get("dept_filter") else "secondary",
            on_click=set_preset,
            args=("all",),
            key="sb_btn_reset",
            width="stretch",
            help="Show all 124 departments (National Overview)",
        )
    with p_col2:
        st.button(
            "Top Backlog",
            type="primary" if st.session_state["active_preset"] == "top_backlog" else "secondary",
            on_click=set_preset,
            args=("top_backlog",),
            key="sb_btn_backlog",
            width="stretch",
            help="Show top departments by pending backlog",
        )

    p_col3, p_col4 = st.columns(2)
    with p_col3:
        st.button(
            "Top Volume",
            type="primary" if st.session_state["active_preset"] == "top_volume" else "secondary",
            on_click=set_preset,
            args=("top_volume",),
            key="sb_btn_volume",
            width="stretch",
            help="Show top departments by grievance volume",
        )
    with p_col4:
        st.button(
            "Top Disposal",
            type="primary" if st.session_state["active_preset"] == "top_disposal" else "secondary",
            on_click=set_preset,
            args=("top_disposal",),
            key="sb_btn_disposal",
            width="stretch",
            help="Show top departments by disposal rate",
        )

    st.markdown("---")

    all_dept_list = sorted(data[COL_NAME].dropna().unique().tolist())
    if "dept_filter" in st.session_state:
        st.session_state["dept_filter"] = [
            d for d in st.session_state["dept_filter"] if d in all_dept_list
        ]

    selected_departments = st.multiselect(
        "Select Specific Departments",
        options=all_dept_list,
        key="dept_filter",
        placeholder=f"Showing all {len(data)} departments",
    )

    # When user interacts with multiselect, switch preset to custom
    if selected_departments and st.session_state["active_preset"] != "custom":
        st.session_state["active_preset"] = "custom"

    sort_options = ["Total Receipts", "Pending Backlog", "Disposal Rate", "Total Disposed"]
    sort_metric = st.selectbox(
        "Ranking Dimension",
        options=sort_options,
        key="sort_filter",
    )

    max_slider_val = max(5, min(50, len(data)))
    top_n = st.slider(
        "Number of Departments to Display",
        min_value=min(5, len(data)) if len(data) > 0 else 1,
        max_value=max_slider_val,
        step=5 if max_slider_val >= 10 else 1,
        key="top_slider",
    )

    st.markdown("---")
    st.markdown("**Dataset Synchronization**")
    st.caption(f"Master source: {len(data)} departments in official dataset")
    if st.button("Reload from CSV File", key="sb_btn_reload_disk", width="stretch"):
        load_data.clear()
        st.session_state["data_action_status"] = "Dataset re-read fresh from disk CSV."
        st.rerun()


# Determine active scope, title, and active dataset
active_preset = st.session_state.get("active_preset", "all")
current_sort = st.session_state.get("sort_filter", "Total Receipts")

# Build efficiency table for complete dataset
full_efficiency = efficiency_analysis.get_efficiency_table(data)
data_with_eff = data.copy()
data_with_eff[COL_RATE] = full_efficiency[COL_RATE]

# Dynamic Scope Resolution
if selected_departments:
    active_scope_df = data_with_eff[data_with_eff[COL_NAME].isin(selected_departments)].copy()
    active_scope_name = f"Custom Selection ({len(selected_departments)} Departments)"
    is_subset_view = True
elif active_preset == "top_backlog" or current_sort == "Pending Backlog":
    active_scope_df = data_with_eff.nlargest(top_n, COL_PENDING).copy()
    active_scope_name = f"Top {top_n} Departments by Largest Pending Backlog"
    is_subset_view = True
elif active_preset == "top_disposal" or current_sort == "Disposal Rate":
    active_scope_df = data_with_eff.nlargest(top_n, COL_RATE).copy()
    active_scope_name = f"Top {top_n} Departments by Highest Disposal Rate"
    is_subset_view = True
elif active_preset == "top_volume":
    active_scope_df = data_with_eff.nlargest(top_n, COL_RECEIVED).copy()
    active_scope_name = f"Top {top_n} Departments by Highest Grievance Volume"
    is_subset_view = True
elif current_sort == "Total Disposed":
    active_scope_df = data_with_eff.nlargest(top_n, COL_DISPOSED).copy()
    active_scope_name = f"Top {top_n} Departments by Highest Disposals"
    is_subset_view = True
else:
    active_scope_df = data_with_eff.copy()
    active_scope_name = f"National Overview (All {len(data)} Departments)"
    is_subset_view = False


# Calculate Metrics for the Active Scope
scope_received = int(active_scope_df[COL_RECEIVED].sum())
scope_disposed = int(active_scope_df[COL_DISPOSED].sum())
scope_pending = int(active_scope_df[COL_PENDING].sum())
scope_rate = round((scope_disposed / scope_received) * 100, 2) if scope_received > 0 else 0.0

pct_of_nat_pending = (scope_pending / NAT_PENDING * 100) if NAT_PENDING > 0 else 0.0
pct_of_nat_receipts = (scope_received / NAT_RECEIVED * 100) if NAT_RECEIVED > 0 else 0.0


# Header Section with Generated Logo and Semantic SEO H1
logo_html_snippet = (
    f'<img src="data:image/jpeg;base64,{LOGO_B64}" class="portal-logo-img" alt="Government Emblem - Public Grievance Resolution Analysis System" />'
    if LOGO_B64
    else ""
)

st.markdown(
    f"""
    <div class="portal-header">
        <div class="portal-header-flex">
            {logo_html_snippet}
            <div style="flex: 1;">
                <h1 class="portal-title">Public Grievance Resolution Analysis System</h1>
                <p class="portal-subtitle">
                    Comprehensive Analysis of Public Grievance Receipts, Disposals, and Pending Durations Across Central Ministries, Departments, and State Administrations
                </p>
                <div class="portal-meta-badge">
                    Reporting Period: 01 January 2016 to 01 November 2019 &nbsp;|&nbsp; Official Government Dataset
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Hero Quick Preset Buttons - Clean, Balanced & Vertically Aligned
st.markdown(
    """
    <div class="hero-preset-container">
        <div class="hero-preset-title">Active Analytics Views & Quick Filters</div>
        <div class="hero-preset-sub">Instantly filter and synchronize all charts, metrics, rankings, and deep-dive tables:</div>
    </div>
    """,
    unsafe_allow_html=True,
)

h_col1, h_col2, h_col3, h_col4 = st.columns(4)
with h_col1:
    st.button(
        "National Overview",
        type="primary" if active_preset == "all" and not selected_departments else "secondary",
        on_click=set_preset,
        args=("all",),
        key="hero_btn_all",
        width="stretch",
        help="View all 124 ministries and states nationwide (Reset active filters)",
    )
with h_col2:
    st.button(
        "Top Backlog",
        type="primary" if active_preset == "top_backlog" or current_sort == "Pending Backlog" else "secondary",
        on_click=set_preset,
        args=("top_backlog",),
        key="hero_btn_backlog",
        width="stretch",
        help="Focus on departments with the largest volume of unresolved grievances",
    )
with h_col3:
    st.button(
        "Top Volume",
        type="primary" if active_preset == "top_volume" else "secondary",
        on_click=set_preset,
        args=("top_volume",),
        key="hero_btn_volume",
        width="stretch",
        help="Focus on departments handling the highest total incoming grievance volume",
    )
with h_col4:
    st.button(
        "Top Disposal",
        type="primary" if active_preset == "top_disposal" or current_sort == "Disposal Rate" else "secondary",
        on_click=set_preset,
        args=("top_disposal",),
        key="hero_btn_disposal",
        width="stretch",
        help="Focus on departments with the highest resolution efficiency percentage",
    )

# Active Scope Notification Banner
scope_context_msg = (
    f"Active View: <b>{active_scope_name}</b> &nbsp;&bull;&nbsp; Representing <b>{pct_of_nat_pending:.1f}%</b> of National Backlog ({scope_pending:,} of {NAT_PENDING:,})"
    if is_subset_view
    else f"Active View: <b>National Overview</b> &nbsp;&bull;&nbsp; Aggregate Performance across all {len(data)} Government Departments & States"
)

st.markdown(
    f"""
    <div class="active-scope-banner">
        <div>{scope_context_msg}</div>
        <div class="active-scope-badge">
            Showing {len(active_scope_df)} Departments
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4 Key Performance Metrics (Dynamically updated according to active view)
metric_cols = st.columns(4)

with metric_cols[0]:
    sub_text_rec = (
        f"{pct_of_nat_receipts:.1f}% of national total ({NAT_RECEIVED:,})"
        if is_subset_view
        else f"Total registered grievances ({len(data)} departments)"
    )
    st.markdown(
        f"""
        <div class="custom-metric-card card-blue">
            <div class="metric-label-text">Total Receipts</div>
            <div class="metric-value-text">{scope_received:,}</div>
            <div class="metric-sub-text">{sub_text_rec}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with metric_cols[1]:
    sub_text_disp = (
        f"Resolved in active selection"
        if is_subset_view
        else "Successfully resolved nationwide"
    )
    st.markdown(
        f"""
        <div class="custom-metric-card card-green">
            <div class="metric-label-text">Total Disposed</div>
            <div class="metric-value-text">{scope_disposed:,}</div>
            <div class="metric-sub-text">{sub_text_disp}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with metric_cols[2]:
    sub_text_pend = (
        f"{pct_of_nat_pending:.1f}% of national backlog ({NAT_PENDING:,})"
        if is_subset_view
        else "Active national backlog as on 01.11.2019"
    )
    st.markdown(
        f"""
        <div class="custom-metric-card card-red">
            <div class="metric-label-text">Total Pending</div>
            <div class="metric-value-text">{scope_pending:,}</div>
            <div class="metric-sub-text">{sub_text_pend}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with metric_cols[3]:
    sub_text_rate = (
        f"Benchmark: {NAT_RATE:.2f}% National Avg"
        if is_subset_view
        else "National grievance resolution efficiency"
    )
    st.markdown(
        f"""
        <div class="custom-metric-card card-amber">
            <div class="metric-label-text">Disposal Rate</div>
            <div class="metric-value-text">{scope_rate:.2f}%</div>
            <div class="metric-sub-text">{sub_text_rate}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# Navigation Tabs - Strictly No Emojis
tab_overview, tab_exploration, tab_performance, tab_pending, tab_explorer, tab_records = st.tabs(
    [
        "Executive Overview",
        "Data Exploration",
        "Department Performance",
        "Pending Backlog Analysis",
        "Department Drill-Down",
        "Data Records & Management",
    ]
)

# Shared Plotly theme styling helper with high contrast and readable margins
def apply_cream_chart_theme(fig, height=500, left_margin=200):
    fig.update_layout(
        height=height,
        font=dict(family="Almarai, sans-serif", color="#1A1816", size=12),
        paper_bgcolor="#FAF7F0",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=left_margin, r=25, t=30, b=30),
        autosize=True,
        legend=dict(
            font=dict(color="#1A1816", size=12),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#E5DDCF",
            borderwidth=1,
        ),
    )
    fig.update_xaxes(
        automargin=True,
        showgrid=True,
        gridcolor="#EFE8DC",
        zerolinecolor="#DDD2BF",
        tickfont=dict(color="#1A1816", size=11),
        title_font=dict(color="#1A1816", size=12, family="Almarai"),
    )
    fig.update_yaxes(
        automargin=True,
        showgrid=False,
        tickfont=dict(color="#1A1816", size=11),
        title_font=dict(color="#1A1816", size=12, family="Almarai"),
    )
    return fig


# -----------------------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW (Dynamic reactive charts responding to all buttons)
# -----------------------------------------------------------------------------
with tab_overview:
    col_left, col_right = st.columns([1.35, 1.0])

    with col_left:
        # Determine chart focus and title based on active preset / ranking dimension
        if current_sort == "Pending Backlog" or active_preset == "top_backlog":
            chart_header_title = "Departments with Largest Pending Backlog"
            chart_header_sub = "Ranking departments by unresolved grievances vs. cases disposed"

            ranked_chart_data = (
                data_with_eff.nlargest(top_n, COL_PENDING).sort_values(COL_PENDING, ascending=True)
                if not selected_departments
                else active_scope_df.sort_values(COL_PENDING, ascending=True)
            )

            melted_chart = ranked_chart_data.melt(
                id_vars=COL_NAME,
                value_vars=[COL_PENDING, COL_DISPOSED],
                var_name="Category",
                value_name="Count",
            )
            melted_chart["Category"] = melted_chart["Category"].map(
                {COL_PENDING: "Pending Backlog", COL_DISPOSED: "Total Disposed"}
            )

            fig_overview_left = px.bar(
                melted_chart,
                x="Count",
                y=COL_NAME,
                color="Category",
                barmode="group",
                orientation="h",
                color_discrete_map={
                    "Pending Backlog": "#B84A39",
                    "Total Disposed": "#2A6F55",
                },
                labels={COL_NAME: "", "Count": "Number of Grievances"},
            )
            fig_overview_left.update_traces(
                marker_line_width=0,
                hovertemplate="<b>%{y}</b><br>%{data.name}: %{x:,.0f}<extra></extra>",
            )

        elif current_sort == "Disposal Rate" or active_preset == "top_disposal":
            chart_header_title = "Top Departments by Disposal Rate (%)"
            chart_header_sub = "Ranking departments with highest grievance resolution efficiency"

            ranked_chart_data = (
                data_with_eff.nlargest(top_n, COL_RATE).sort_values(COL_RATE, ascending=True)
                if not selected_departments
                else active_scope_df.sort_values(COL_RATE, ascending=True)
            )

            fig_overview_left = px.bar(
                ranked_chart_data,
                x=COL_RATE,
                y=COL_NAME,
                orientation="h",
                color=COL_RATE,
                color_continuous_scale=[(0.0, "#D89E47"), (1.0, "#2A6F55")],
                range_color=(0, 100),
                labels={COL_RATE: "Disposal Rate (%)", COL_NAME: ""},
                text=ranked_chart_data[COL_RATE].apply(lambda x: f"{x:.1f}%"),
            )
            fig_overview_left.update_traces(
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Disposal Rate: %{x:.2f}%<extra></extra>",
            )
            fig_overview_left.update_layout(coloraxis_showscale=False)

        else:
            chart_header_title = "Grievance Volume: Receipts vs. Disposals"
            chart_header_sub = "Comparative evaluation of total receipts and resolved cases"

            ranked_chart_data = (
                data_with_eff.nlargest(top_n, COL_RECEIVED).sort_values(COL_RECEIVED, ascending=True)
                if not selected_departments
                else active_scope_df.sort_values(COL_RECEIVED, ascending=True)
            )

            melted_chart = ranked_chart_data.melt(
                id_vars=COL_NAME,
                value_vars=[COL_RECEIVED, COL_DISPOSED],
                var_name="Category",
                value_name="Count",
            )
            melted_chart["Category"] = melted_chart["Category"].map(
                {COL_RECEIVED: "Total Receipts", COL_DISPOSED: "Total Disposed"}
            )

            fig_overview_left = px.bar(
                melted_chart,
                x="Count",
                y=COL_NAME,
                color="Category",
                barmode="group",
                orientation="h",
                color_discrete_map={
                    "Total Receipts": "#1B5E43",
                    "Total Disposed": "#2A6F55",
                },
                labels={COL_NAME: "", "Count": "Number of Grievances"},
            )
            fig_overview_left.update_traces(
                marker_line_width=0,
                hovertemplate="<b>%{y}</b><br>%{data.name}: %{x:,.0f}<extra></extra>",
            )

        st.markdown(
            f"""
            <div class="card-header-block">
                <div class="analytical-card-header">{chart_header_title}</div>
                <div class="analytical-card-sub">{chart_header_sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        apply_cream_chart_theme(fig_overview_left, height=max(480, top_n * 34), left_margin=200)
        st.plotly_chart(fig_overview_left, width="stretch")

    with col_right:
        st.markdown(
            """
            <div class="card-header-block">
                <div class="analytical-card-header">Pending Grievances by Duration</div>
                <div class="analytical-card-sub">Backlog distribution across elapsed duration brackets for active view</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        duration_totals = pd.DataFrame(
            {
                "Duration Bracket": DURATION_LABELS,
                "Pending Count": [int(active_scope_df[col].sum()) for col in DURATION_COLS],
            }
        )
        total_backlog_in_scope = duration_totals["Pending Count"].sum()
        duration_totals["Percentage"] = (
            ((duration_totals["Pending Count"] / total_backlog_in_scope) * 100).round(1)
            if total_backlog_in_scope > 0
            else 0.0
        )

        fig_duration = px.bar(
            duration_totals,
            x="Pending Count",
            y="Duration Bracket",
            orientation="h",
            text="Pending Count",
            color="Duration Bracket",
            color_discrete_sequence=["#B84A39", "#C4822B", "#5C7C8A", "#2A6F55"],
        )
        fig_duration.update_traces(
            showlegend=False,
            texttemplate="%{text:,.0f}",
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Pending: %{x:,.0f} (%{customdata[0]:.1f}%)<extra></extra>",
            customdata=duration_totals[["Percentage"]],
        )
        apply_cream_chart_theme(fig_duration, height=max(480, top_n * 34), left_margin=140)
        fig_duration.update_xaxes(showgrid=True)
        st.plotly_chart(fig_duration, width="stretch")

    # Dynamic Key Analytical Findings
    top_backlog_share = (
        (data.nlargest(min(10, len(data)), COL_PENDING)[COL_PENDING].sum() / NAT_PENDING * 100)
        if NAT_PENDING > 0
        else 0.0
    )
    pct_over_1y = (
        (data[DURATION_COLS[0]].sum() / NAT_PENDING * 100) if NAT_PENDING > 0 else 0.0
    )
    st.markdown(
        f"""
        <div class="card-header-block">
            <div class="analytical-card-header">Key Analytical Findings</div>
            <div class="analytical-card-sub">Official governance insights derived from grievance reporting data</div>
            <div class="insights-box">
                <ul>
                    <li><b>High Backlog Concentration:</b> The top {min(10, len(data))} backlog departments hold <b>{top_backlog_share:.1f}%</b> of the entire country's pending grievances.</li>
                    <li><b>Prolonged Backlog Severity:</b> Nationally, <b>{pct_over_1y:.1f}%</b> of unresolved cases ({data[DURATION_COLS[0]].sum():,}) have been pending for longer than 1 year.</li>
                    <li><b>Overall Resolution Efficiency:</b> Across all {len(data)} reporting departments and states, the aggregate disposal rate stands at <b>{NAT_RATE:.2f}%</b>, with leading central departments reaching over 95%.</li>
                    <li><b>Active View Impact:</b> Currently analyzing <b>{len(active_scope_df)} departments</b> holding <b>{scope_pending:,} pending grievances</b> with a group disposal rate of <b>{scope_rate:.2f}%</b>.</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# TAB 2: DATA EXPLORATION & MULTI-FILTERING STUDIO (Reference Layout)
# -----------------------------------------------------------------------------
with tab_exploration:
    st.markdown(
        """
        <div class="filter-panel-card">
            <div class="filter-panel-title">Interactive Filter Controls</div>
            <div class="filter-panel-sub">
                Filter grievance records by administrative category, specific department, resolution efficiency, or backlog scale. 
                Selecting any specific department isolates its data across the table, KPI metrics, and duration distribution.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        sel_cat = st.selectbox(
            "Administrative Category",
            options=["All Administrative Entities", "Central Ministries & Departments", "States & Union Territories"],
            key="filter_exp_category",
        )
    with f_col2:
        # Determine available departments according to category
        if sel_cat == "Central Ministries & Departments":
            avail_depts = [d for d in all_dept_list if classify_entity(d) == "Central Ministry / Department"]
        elif sel_cat == "States & Union Territories":
            avail_depts = [d for d in all_dept_list if classify_entity(d) == "State / Union Territory"]
        else:
            avail_depts = all_dept_list

        sel_depts = st.multiselect(
            "Ministry / Department / State",
            options=avail_depts,
            placeholder="Select entity (e.g. Railways, Finance...)",
            key="filter_exp_depts",
        )
    with f_col3:
        sel_eff = st.selectbox(
            "Resolution Efficiency Tier",
            options=["All Resolution Tiers", "High Efficiency (≥ 90%)", "Moderate Efficiency (70% - 90%)", "Needs Attention (< 70%)"],
            key="filter_exp_efficiency",
        )

    f_col4, f_col5, f_col6 = st.columns(3)
    with f_col4:
        sel_backlog = st.selectbox(
            "Backlog Severity Scale",
            options=["All Backlog Sizes", "Critical Backlog (> 10,000)", "High Backlog (5,000 - 10,000)", "Moderate Backlog (1,000 - 5,000)", "Low Backlog (< 1,000)"],
            key="filter_exp_backlog",
        )
    with f_col5:
        sel_volume = st.selectbox(
            "Grievance Volume Scale",
            options=["All Volume Scales", "Major Volume (> 50,000 Receipts)", "Medium Volume (10,000 - 50,000)", "Standard Volume (< 10,000)"],
            key="filter_exp_volume",
        )
    with f_col6:
        sel_aging = st.selectbox(
            "Dominant Aging Bracket",
            options=["All Aging Brackets", "Prolonged Backlog (> 1 Year dominates)", "Mid-term Aging (6-12 Months dominates)", "Recent Grievances (< 6 Months)"],
            key="filter_exp_aging",
        )

    # Filtering Logic Engine
    exp_filtered_df = data_with_eff.copy()

    # 1. Category filter
    if sel_cat == "Central Ministries & Departments":
        exp_filtered_df = exp_filtered_df[exp_filtered_df[COL_NAME].apply(classify_entity) == "Central Ministry / Department"]
    elif sel_cat == "States & Union Territories":
        exp_filtered_df = exp_filtered_df[exp_filtered_df[COL_NAME].apply(classify_entity) == "State / Union Territory"]

    # 2. Specific departments filter
    if sel_depts:
        exp_filtered_df = exp_filtered_df[exp_filtered_df[COL_NAME].isin(sel_depts)]

    # 3. Efficiency tier filter
    if sel_eff == "High Efficiency (≥ 90%)":
        exp_filtered_df = exp_filtered_df[exp_filtered_df[COL_RATE] >= 90.0]
    elif sel_eff == "Moderate Efficiency (70% - 90%)":
        exp_filtered_df = exp_filtered_df[(exp_filtered_df[COL_RATE] >= 70.0) & (exp_filtered_df[COL_RATE] < 90.0)]
    elif sel_eff == "Needs Attention (< 70%)":
        exp_filtered_df = exp_filtered_df[exp_filtered_df[COL_RATE] < 70.0]

    # 4. Backlog severity scale
    if sel_backlog == "Critical Backlog (> 10,000)":
        exp_filtered_df = exp_filtered_df[exp_filtered_df[COL_PENDING] > 10000]
    elif sel_backlog == "High Backlog (5,000 - 10,000)":
        exp_filtered_df = exp_filtered_df[(exp_filtered_df[COL_PENDING] >= 5000) & (exp_filtered_df[COL_PENDING] <= 10000)]
    elif sel_backlog == "Moderate Backlog (1,000 - 5,000)":
        exp_filtered_df = exp_filtered_df[(exp_filtered_df[COL_PENDING] >= 1000) & (exp_filtered_df[COL_PENDING] < 5000)]
    elif sel_backlog == "Low Backlog (< 1,000)":
        exp_filtered_df = exp_filtered_df[exp_filtered_df[COL_PENDING] < 1000]

    # 5. Volume scale
    if sel_volume == "Major Volume (> 50,000 Receipts)":
        exp_filtered_df = exp_filtered_df[exp_filtered_df[COL_RECEIVED] > 50000]
    elif sel_volume == "Medium Volume (10,000 - 50,000)":
        exp_filtered_df = exp_filtered_df[(exp_filtered_df[COL_RECEIVED] >= 10000) & (exp_filtered_df[COL_RECEIVED] <= 50000)]
    elif sel_volume == "Standard Volume (< 10,000)":
        exp_filtered_df = exp_filtered_df[exp_filtered_df[COL_RECEIVED] < 10000]

    # 6. Dominant aging bracket
    if sel_aging == "Prolonged Backlog (> 1 Year dominates)":
        exp_filtered_df = exp_filtered_df[exp_filtered_df[DURATION_COLS[0]] >= (exp_filtered_df[COL_PENDING] * 0.4)]
    elif sel_aging == "Mid-term Aging (6-12 Months dominates)":
        exp_filtered_df = exp_filtered_df[exp_filtered_df[DURATION_COLS[1]] >= (exp_filtered_df[COL_PENDING] * 0.3)]
    elif sel_aging == "Recent Grievances (< 6 Months)":
        exp_filtered_df = exp_filtered_df[(exp_filtered_df[DURATION_COLS[2]] + exp_filtered_df[DURATION_COLS[3]]) >= (exp_filtered_df[COL_PENDING] * 0.5)]

    def reset_exp_filters():
        st.session_state["filter_exp_category"] = "All Administrative Entities"
        st.session_state["filter_exp_depts"] = []
        st.session_state["filter_exp_efficiency"] = "All Resolution Tiers"
        st.session_state["filter_exp_backlog"] = "All Backlog Sizes"
        st.session_state["filter_exp_volume"] = "All Volume Scales"
        st.session_state["filter_exp_aging"] = "All Aging Brackets"

    btn_exp_c1, btn_exp_c2 = st.columns([1.2, 4.0])
    with btn_exp_c1:
        st.button("Clear All Filters", on_click=reset_exp_filters, key="btn_clear_exploration_filters", width="stretch")

    with btn_exp_c2:
        if len(exp_filtered_df) == len(data):
            st.caption(f"Displaying all {len(data)} reporting departments (Master national dataset)")
        else:
            active_filter_names = []
            if sel_cat != "All Administrative Entities": active_filter_names.append(sel_cat)
            if sel_depts: active_filter_names.append(f"{len(sel_depts)} Selected Entity(ies)")
            if sel_eff != "All Resolution Tiers": active_filter_names.append(sel_eff)
            if sel_backlog != "All Backlog Sizes": active_filter_names.append(sel_backlog)
            if sel_volume != "All Volume Scales": active_filter_names.append(sel_volume)
            if sel_aging != "All Aging Brackets": active_filter_names.append(sel_aging)
            st.caption(f"Active records subset: {len(exp_filtered_df)} of {len(data)} departments | Filter: {', '.join(active_filter_names)}")

    # 4 KPI Summary Metric Cards (Calculated dynamically for filtered subset)
    exp_count = len(exp_filtered_df)
    exp_received = int(exp_filtered_df[COL_RECEIVED].sum()) if not exp_filtered_df.empty else 0
    exp_disposed = int(exp_filtered_df[COL_DISPOSED].sum()) if not exp_filtered_df.empty else 0
    exp_pending = int(exp_filtered_df[COL_PENDING].sum()) if not exp_filtered_df.empty else 0
    exp_rate = round((exp_disposed / exp_received * 100), 2) if exp_received > 0 else 0.0

    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)

    with kpi_c1:
        pct_ent = (exp_count / len(data) * 100) if len(data) > 0 else 0.0
        st.markdown(
            f"""
            <div class="custom-metric-card card-blue">
                <div class="metric-label-text">Filtered Entities</div>
                <div class="metric-value-text">{exp_count:,}</div>
                <div class="metric-sub-text">Active records subset ({pct_ent:.1f}% of master)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_c2:
        pct_rec = (exp_received / NAT_RECEIVED * 100) if NAT_RECEIVED > 0 else 0.0
        st.markdown(
            f"""
            <div class="custom-metric-card card-green">
                <div class="metric-label-text">Total Receipts</div>
                <div class="metric-value-text">{exp_received:,}</div>
                <div class="metric-sub-text">{pct_rec:.1f}% of national grievance volume</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_c3:
        pct_pend = (exp_pending / NAT_PENDING * 100) if NAT_PENDING > 0 else 0.0
        st.markdown(
            f"""
            <div class="custom-metric-card card-red">
                <div class="metric-label-text">Total Disposed</div>
                <div class="metric-value-text">{exp_disposed:,}</div>
                <div class="metric-sub-text">{exp_pending:,} pending ({pct_pend:.1f}% backlog share)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi_c4:
        st.markdown(
            f"""
            <div class="custom-metric-card card-amber">
                <div class="metric-label-text">Resolution Rate</div>
                <div class="metric-value-text">{exp_rate:.2f}%</div>
                <div class="metric-sub-text">Benchmark: {NAT_RATE:.2f}% National Avg</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Side-by-Side 2-Column Split Layout (Matches SupplierPulse Reference Layout)
    col_left_tbl, col_right_vis = st.columns([1.42, 1.0])

    with col_left_tbl:
        st.markdown(
            """
            <div class="card-header-block">
                <div class="analytical-card-header">Departmental Records Explorer</div>
                <div class="analytical-card-sub">Exact grievance statistics for matching entities. Filtered records only.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tbl_search_c, tbl_dl_c = st.columns([1.5, 1.0])
        with tbl_search_c:
            exp_table_search = st.text_input(
                "Search within Results",
                placeholder="Filter entity by name...",
                key="exp_search_sub",
            )
        with tbl_dl_c:
            exp_csv_buf = io.StringIO()
            tbl_export = exp_filtered_df.copy()
            if exp_table_search:
                tbl_export = tbl_export[
                    tbl_export[COL_NAME].str.contains(exp_table_search, case=False, na=False)
                ]
            tbl_export.to_csv(exp_csv_buf, index=False)
            st.download_button(
                label="Export Filtered CSV",
                data=exp_csv_buf.getvalue(),
                file_name="filtered_grievance_records.csv",
                mime="text/csv",
                width="stretch",
                key="btn_exp_tbl_dl",
            )

        display_exp_tbl = exp_filtered_df.copy()
        if exp_table_search:
            display_exp_tbl = display_exp_tbl[
                display_exp_tbl[COL_NAME].str.contains(exp_table_search, case=False, na=False)
            ]

        display_exp_tbl = display_exp_tbl.sort_values(by=COL_RECEIVED, ascending=False).reset_index(drop=True)
        display_exp_tbl.index = display_exp_tbl.index + 1

        st.caption(f"Showing {len(display_exp_tbl)} records in active view")

        st.dataframe(
            display_exp_tbl,
            width="stretch",
            height=500,
            column_config={
                COL_NAME: st.column_config.TextColumn("Ministry / Department / State", width="large"),
                COL_RECEIVED: st.column_config.NumberColumn("Total Receipts", format="%d"),
                COL_DISPOSED: st.column_config.NumberColumn("Total Disposal", format="%d"),
                COL_PENDING: st.column_config.NumberColumn("Total Pending", format="%d"),
                DURATION_COLS[0]: st.column_config.NumberColumn("> 1 Year", format="%d"),
                DURATION_COLS[1]: st.column_config.NumberColumn("6 - 12 Months", format="%d"),
                DURATION_COLS[2]: st.column_config.NumberColumn("2 - 6 Months", format="%d"),
                DURATION_COLS[3]: st.column_config.NumberColumn("< 2 Months", format="%d"),
                COL_RATE: st.column_config.NumberColumn("Disposal Rate", format="%.2f%%"),
            },
        )

    with col_right_vis:
        st.markdown(
            """
            <div class="card-header-block">
                <div class="analytical-card-header">Distribution Overview</div>
                <div class="analytical-card-sub">Backlog Aging and Resolution Breakdown for Active Selection</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("##### Backlog Duration Breakdown")

        # Donut Chart for Filtered Duration Breakdown
        exp_dur_vals = [
            int(exp_filtered_df[DURATION_COLS[0]].sum()) if not exp_filtered_df.empty else 0,
            int(exp_filtered_df[DURATION_COLS[1]].sum()) if not exp_filtered_df.empty else 0,
            int(exp_filtered_df[DURATION_COLS[2]].sum()) if not exp_filtered_df.empty else 0,
            int(exp_filtered_df[DURATION_COLS[3]].sum()) if not exp_filtered_df.empty else 0,
        ]

        if sum(exp_dur_vals) > 0:
            fig_exp_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=DURATION_LABELS,
                        values=exp_dur_vals,
                        hole=0.52,
                        marker=dict(
                            colors=["#B84A39", "#D27B2E", "#DDB856", "#2A6F55"],
                            line=dict(color="#FAF7F0", width=2),
                        ),
                        textinfo="label+percent",
                        insidetextorientation="radial",
                    )
                ]
            )
            fig_exp_donut.update_layout(
                height=320,
                paper_bgcolor="#FAF7F0",
                font=dict(family="Almarai, sans-serif", color="#1A1816"),
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=10, family="Almarai"),
                ),
            )
            st.plotly_chart(fig_exp_donut, width="stretch")
        else:
            st.info("No pending backlog recorded for the active filtered selection.")

        # Resolution Progress Gauge
        st.markdown("##### Resolution Progress Gauge")
        fig_exp_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=round(exp_rate, 2),
                number={"suffix": "%", "font": {"family": "Almarai", "size": 34, "color": "#1A1816"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#1A1816", "tickwidth": 1},
                    "bar": {"color": "#1B5E43"},
                    "bgcolor": "#FFFFFF",
                    "borderwidth": 1,
                    "bordercolor": "#D5C9B5",
                    "steps": [
                        {"range": [0, 50], "color": "#F3D8D3"},
                        {"range": [50, 80], "color": "#F6EAD0"},
                        {"range": [80, 100], "color": "#D4E7DC"},
                    ],
                    "threshold": {
                        "line": {"color": "#1A1816", "width": 3},
                        "thickness": 0.75,
                        "value": NAT_RATE,
                    },
                },
            )
        )
        fig_exp_gauge.update_layout(
            height=250,
            paper_bgcolor="#FAF7F0",
            font=dict(family="Almarai, sans-serif", color="#1A1816"),
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig_exp_gauge, width="stretch")

        # Analytical Summary Box
        exp_p1y_val = exp_dur_vals[0]
        exp_p1y_pct = (exp_p1y_val / exp_pending * 100) if exp_pending > 0 else 0.0
        diff_nat = exp_rate - NAT_RATE
        perf_desc = f"{diff_nat:+.2f}% higher than" if diff_nat >= 0 else f"{abs(diff_nat):.2f}% below"

        st.markdown(
            f"""
            <div class="insights-box" style="margin-top: 10px;">
                <b>Active Subset Insights:</b> 
                Active selection covers <b>{exp_count} department(s)</b> with <b>{exp_received:,}</b> receipts and <b>{exp_disposed:,}</b> disposals. 
                The group disposal rate of <b>{exp_rate:.2f}%</b> is {perf_desc} the national average ({NAT_RATE:.2f}%). 
                Of <b>{exp_pending:,}</b> unresolved grievances, <b>{exp_p1y_val:,} ({exp_p1y_pct:.1f}%)</b> have been pending over 1 year.
            </div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------------
# TAB 3: DEPARTMENT PERFORMANCE
# -----------------------------------------------------------------------------
with tab_performance:
    st.markdown(
        """
        <div class="card-header-block">
            <div class="analytical-card-header">Department Efficiency and Disposal Rate Analysis</div>
            <div class="analytical-card-sub">Disposal Rate = (Total Disposed / Total Received) &times; 100. Higher percentage indicates greater resolution capacity.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t2_col1, t2_col2 = st.columns([1, 1])
    with t2_col1:
        perf_view_mode = st.radio(
            "Ranking View Focus",
            options=["Highest Disposal Rate (Top Performers)", "Lowest Disposal Rate (Need Improvement)"],
            horizontal=True,
        )

    if "Lowest" in perf_view_mode:
        ranked_performance = active_scope_df.nsmallest(top_n, COL_RATE).sort_values(
            COL_RATE, ascending=True
        )
    else:
        ranked_performance = active_scope_df.nlargest(top_n, COL_RATE).sort_values(
            COL_RATE, ascending=True
        )

    fig_rate = px.bar(
        ranked_performance,
        x=COL_RATE,
        y=COL_NAME,
        orientation="h",
        color=COL_RATE,
        color_continuous_scale=[
            (0.0, "#B84A39"),
            (0.5, "#D89E47"),
            (1.0, "#2A6F55"),
        ],
        range_color=(0, 100),
        labels={COL_RATE: "Disposal Rate (%)", COL_NAME: ""},
        text=ranked_performance[COL_RATE].apply(lambda x: f"{x:.1f}%"),
    )
    fig_rate.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Disposal Rate: %{x:.2f}%<extra></extra>",
    )
    fig_rate.update_layout(
        coloraxis_colorbar=dict(
            title="Rate %",
            thickness=12,
            len=0.7,
            tickfont=dict(color="#1A1816", size=10),
        )
    )
    apply_cream_chart_theme(fig_rate, height=max(420, top_n * 34), left_margin=200)
    st.plotly_chart(fig_rate, width="stretch")

    st.markdown("#### Complete Performance Table")
    display_perf = active_scope_df.sort_values(by=COL_RATE, ascending=False).reset_index(drop=True)
    display_perf.index = display_perf.index + 1

    st.dataframe(
        display_perf[[COL_NAME, COL_RECEIVED, COL_DISPOSED, COL_PENDING, COL_RATE]],
        width="stretch",
        height=380,
        column_config={
            COL_NAME: st.column_config.TextColumn("Ministry / Department / State", width="large"),
            COL_RECEIVED: st.column_config.NumberColumn("Total Received", format="%d"),
            COL_DISPOSED: st.column_config.NumberColumn("Total Disposed", format="%d"),
            COL_PENDING: st.column_config.NumberColumn("Total Pending", format="%d"),
            COL_RATE: st.column_config.NumberColumn("Disposal Rate", format="%.2f%%"),
        },
    )


# -----------------------------------------------------------------------------
# TAB 3: PENDING BACKLOG ANALYSIS
# -----------------------------------------------------------------------------
with tab_pending:
    st.markdown(
        """
        <div class="card-header-block">
            <div class="analytical-card-header">Unresolved Grievances by Department and Duration</div>
            <div class="analytical-card-sub">Identification of departments with the largest backlogs and aging profiles</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_backlog = active_scope_df.nlargest(top_n, COL_PENDING).sort_values(COL_PENDING, ascending=True)

    fig_backlog = px.bar(
        top_backlog,
        x=COL_PENDING,
        y=COL_NAME,
        orientation="h",
        color=COL_PENDING,
        color_continuous_scale=[
            (0.0, "#E2A76F"),
            (1.0, "#B84A39"),
        ],
        text=COL_PENDING,
        labels={COL_PENDING: "Pending Grievances", COL_NAME: ""},
    )
    fig_backlog.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Pending: %{x:,.0f}<extra></extra>",
    )
    fig_backlog.update_layout(
        coloraxis_colorbar=dict(
            title="Pending",
            thickness=12,
            len=0.7,
            tickfont=dict(color="#1A1816", size=10),
        )
    )
    apply_cream_chart_theme(fig_backlog, height=max(420, top_n * 34), left_margin=200)
    st.plotly_chart(fig_backlog, width="stretch")

    st.markdown("#### Stacked Duration Breakdown (Top Backlog Departments)")
    stacked_df = top_backlog[[COL_NAME] + DURATION_COLS].copy()
    stacked_melted = stacked_df.melt(
        id_vars=COL_NAME,
        value_vars=DURATION_COLS,
        var_name="Duration Category",
        value_name="Pending Count",
    )
    duration_rename = {
        DURATION_COLS[0]: "More Than 1 Year",
        DURATION_COLS[1]: "6 To 12 Months",
        DURATION_COLS[2]: "2 To 6 Months",
        DURATION_COLS[3]: "Less Than 2 Months",
    }
    stacked_melted["Duration Category"] = stacked_melted["Duration Category"].map(duration_rename)

    fig_stacked = px.bar(
        stacked_melted,
        x="Pending Count",
        y=COL_NAME,
        color="Duration Category",
        orientation="h",
        barmode="stack",
        color_discrete_map={
            "More Than 1 Year": "#B84A39",
            "6 To 12 Months": "#D27B2E",
            "2 To 6 Months": "#DDB856",
            "Less Than 2 Months": "#2A6F55",
        },
        labels={COL_NAME: "", "Pending Count": "Grievance Count"},
    )
    apply_cream_chart_theme(fig_stacked, height=max(420, top_n * 34), left_margin=200)
    st.plotly_chart(fig_stacked, width="stretch")

    st.markdown("#### Detailed Pending Breakdown Table")
    pending_table = pending_analysis.get_pending_analysis(active_scope_df)
    pending_table = pending_table.sort_values(by=COL_PENDING, ascending=False).reset_index(drop=True)
    pending_table.index = pending_table.index + 1

    st.dataframe(
        pending_table,
        width="stretch",
        height=360,
        column_config={
            COL_NAME: st.column_config.TextColumn("Ministry / Department / State", width="large"),
            COL_PENDING: st.column_config.NumberColumn("Total Pending", format="%d"),
            DURATION_COLS[0]: st.column_config.NumberColumn("> 1 Year", format="%d"),
            DURATION_COLS[1]: st.column_config.NumberColumn("6 - 12 Months", format="%d"),
            DURATION_COLS[2]: st.column_config.NumberColumn("2 - 6 Months", format="%d"),
            DURATION_COLS[3]: st.column_config.NumberColumn("< 2 Months", format="%d"),
        },
    )


# -----------------------------------------------------------------------------
# TAB 4: DEPARTMENT DRILL-DOWN EXPLORER
# -----------------------------------------------------------------------------
with tab_explorer:
    st.markdown(
        """
        <div class="card-header-block">
            <div class="analytical-card-header">Single Department Deep-Dive</div>
            <div class="analytical-card-sub">Select any Ministry, Department, or State to inspect individual metrics and duration composition</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not all_dept_list:
        st.info("No departments currently available in the dataset. You can add departments or restore the baseline in the Data Records & Management tab.")
    else:
        drill_dept = st.selectbox(
            "Choose Entity to Inspect",
            options=all_dept_list,
            index=0,
        )

        matching_rows = data[data[COL_NAME] == drill_dept]
    if not matching_rows.empty:
        dept_row = matching_rows.iloc[0]
        dept_receipts = int(dept_row[COL_RECEIVED])
        dept_disposed = int(dept_row[COL_DISPOSED])
        dept_pending = int(dept_row[COL_PENDING])
        dept_rate = (dept_disposed / dept_receipts * 100) if dept_receipts > 0 else 0.0

        st.markdown(f"### Performance Report: **{drill_dept}**")

        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
        d_col1.metric("Receipts", f"{dept_receipts:,}")
        d_col2.metric("Disposals", f"{dept_disposed:,}")
        d_col3.metric("Current Backlog", f"{dept_pending:,}")
        d_col4.metric(
            "Disposal Rate",
            f"{dept_rate:.2f}%",
            delta=f"{dept_rate - NAT_RATE:+.2f}% vs National Avg",
        )

        st.write("")
        drill_left, drill_right = st.columns(2)

        with drill_left:
            st.markdown("##### Backlog Duration Breakdown")
            dept_duration_vals = [int(dept_row[col]) for col in DURATION_COLS]
            if sum(dept_duration_vals) > 0:
                fig_donut = go.Figure(
                    data=[
                        go.Pie(
                            labels=DURATION_LABELS,
                            values=dept_duration_vals,
                            hole=0.48,
                            marker=dict(
                                colors=["#B84A39", "#D27B2E", "#DDB856", "#2A6F55"],
                                line=dict(color="#FAF7F0", width=2),
                            ),
                            textinfo="label+percent",
                            insidetextorientation="radial",
                        )
                    ]
                )
                fig_donut.update_layout(
                    height=360,
                    paper_bgcolor="#FAF7F0",
                    font=dict(family="Almarai, sans-serif", color="#1A1816"),
                    margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=False,
                )
                st.plotly_chart(fig_donut, width="stretch")
            else:
                st.info("No pending grievances recorded for this department.")

        with drill_right:
            st.markdown("##### Resolution Progress Gauge")
            fig_gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=round(dept_rate, 2),
                    number={"suffix": "%", "font": {"family": "Almarai", "size": 36, "color": "#1A1816"}},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#1A1816", "tickwidth": 1},
                        "bar": {"color": "#1B5E43"},
                        "bgcolor": "#FFFFFF",
                        "borderwidth": 1,
                        "bordercolor": "#D5C9B5",
                        "steps": [
                            {"range": [0, 50], "color": "#F3D8D3"},
                            {"range": [50, 80], "color": "#F6EAD0"},
                            {"range": [80, 100], "color": "#D4E7DC"},
                        ],
                        "threshold": {
                            "line": {"color": "#1A1816", "width": 3},
                            "thickness": 0.75,
                            "value": NAT_RATE,
                        },
                    },
                )
            )
            fig_gauge.update_layout(
                height=360,
                paper_bgcolor="#FAF7F0",
                font=dict(family="Almarai, sans-serif", color="#1A1816"),
                margin=dict(l=20, r=20, t=20, b=20),
            )
            st.plotly_chart(fig_gauge, width="stretch")

        # Department Analytical Summary
        p_1y = int(dept_row[DURATION_COLS[0]])
        pct_1y = (p_1y / dept_pending * 100) if dept_pending > 0 else 0.0
        status_text = "exceeds" if dept_rate >= NAT_RATE else "is below"

        st.markdown(
            f"""
            <div class="insights-box">
                <b>Department Performance Note:</b> 
                <b>{drill_dept}</b> has registered <b>{dept_receipts:,}</b> total grievances with a resolution rate of <b>{dept_rate:.2f}%</b>, which {status_text} the national benchmark of {NAT_RATE:.2f}%. 
                Of its <b>{dept_pending:,}</b> unresolved grievances, <b>{p_1y:,} ({pct_1y:.1f}%)</b> have been pending for longer than 1 year.
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# TAB 5: COMPREHENSIVE DATA RECORDS & MANAGEMENT STUDIO
# -----------------------------------------------------------------------------
with tab_records:
    # Notification Banner if an action was executed
    if "data_action_status" in st.session_state and st.session_state["data_action_status"]:
        st.markdown(
            f"""
            <div class="status-success-banner">
                <b>Database Update Applied:</b> {st.session_state.pop('data_action_status')}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="card-header-block">
            <div class="analytical-card-header">Departmental Grievance Data Studio & Master Records</div>
            <div class="analytical-card-sub">
                Explore master data records, export customized reports, or modify the dataset in real time. 
                Any department added, modified, or removed immediately synchronizes across all analytical charts, rankings, and KPI metrics.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sub_tab_browse, sub_tab_add, sub_tab_edit, sub_tab_remove, sub_tab_upload, sub_tab_backup = st.tabs(
        [
            "Master Records Table",
            "Add New Department",
            "Edit Existing Record",
            "Remove Department",
            "Upload CSV Dataset",
            "Backup and Restore",
        ]
    )

    # SUB-TAB 1: BROWSE & EXPORT MASTER RECORDS
    with sub_tab_browse:
        st.markdown(
            f"""
            <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
                <div class="preview-kpi-badge" style="flex: 1; min-width: 140px;">
                    <div class="preview-kpi-val">{len(data):,}</div>
                    <div class="preview-kpi-lbl">Total Departments</div>
                </div>
                <div class="preview-kpi-badge" style="flex: 1; min-width: 140px;">
                    <div class="preview-kpi-val">{NAT_RECEIVED:,}</div>
                    <div class="preview-kpi-lbl">Total Receipts</div>
                </div>
                <div class="preview-kpi-badge" style="flex: 1; min-width: 140px;">
                    <div class="preview-kpi-val">{NAT_DISPOSED:,}</div>
                    <div class="preview-kpi-lbl">Total Disposed</div>
                </div>
                <div class="preview-kpi-badge" style="flex: 1; min-width: 140px;">
                    <div class="preview-kpi-val">{NAT_PENDING:,}</div>
                    <div class="preview-kpi-lbl">Total Backlog</div>
                </div>
                <div class="preview-kpi-badge" style="flex: 1; min-width: 140px;">
                    <div class="preview-kpi-val">{NAT_RATE:.2f}%</div>
                    <div class="preview-kpi-lbl">Overall Resolution Rate</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        action_c1, action_c2, action_c3, action_c4 = st.columns([1.4, 0.9, 0.9, 0.8])

        with action_c1:
            search_query = st.text_input(
                "Search Department by Name",
                placeholder="Filter by ministry or state name...",
                key="table_search_input",
            )

        with action_c2:
            csv_filtered_buffer = io.StringIO()
            filtered_export = active_scope_df.copy()
            if search_query:
                filtered_export = filtered_export[
                    filtered_export[COL_NAME].str.contains(search_query, case=False, na=False)
                ]
            filtered_export.to_csv(csv_filtered_buffer, index=False)
            st.download_button(
                label="Download View (CSV)",
                data=csv_filtered_buffer.getvalue(),
                file_name="public_grievances_current_view.csv",
                mime="text/csv",
                width="stretch",
                key="btn_dl_view",
            )

        with action_c3:
            csv_full_buffer = io.StringIO()
            data_with_eff.to_csv(csv_full_buffer, index=False)
            st.download_button(
                label="Download Master CSV",
                data=csv_full_buffer.getvalue(),
                file_name="public_grievances_master_records.csv",
                mime="text/csv",
                width="stretch",
                key="btn_dl_master",
            )

        with action_c4:
            if st.button("Reload from Disk", width="stretch", key="btn_reload_table"):
                load_data.clear()
                st.session_state["data_action_status"] = "Dataset re-read fresh from disk CSV file."
                st.rerun()

        display_records = active_scope_df.copy()
        if search_query:
            display_records = display_records[
                display_records[COL_NAME].str.contains(search_query, case=False, na=False)
            ]

        display_records[COL_RATE] = (
            (display_records[COL_DISPOSED] / display_records[COL_RECEIVED].replace(0, float("nan"))) * 100
        ).fillna(0.0).round(2)

        display_records = display_records.sort_values(by=COL_RECEIVED, ascending=False).reset_index(drop=True)
        display_records.index = display_records.index + 1

        st.caption(f"Displaying {len(display_records)} records (out of {len(data)} total departments)")

        st.dataframe(
            display_records,
            width="stretch",
            height=500,
            column_config={
                COL_NAME: st.column_config.TextColumn("Ministry / Department / State", width="large"),
                COL_RECEIVED: st.column_config.NumberColumn("Total Receipts", format="%d"),
                COL_DISPOSED: st.column_config.NumberColumn("Total Disposal", format="%d"),
                COL_PENDING: st.column_config.NumberColumn("Total Pending", format="%d"),
                DURATION_COLS[0]: st.column_config.NumberColumn("Pending > 1 Year", format="%d"),
                DURATION_COLS[1]: st.column_config.NumberColumn("6 To 12 Months", format="%d"),
                DURATION_COLS[2]: st.column_config.NumberColumn("2 To 6 Months", format="%d"),
                DURATION_COLS[3]: st.column_config.NumberColumn("Less Than 2 Months", format="%d"),
                COL_RATE: st.column_config.NumberColumn("Disposal Rate (%)", format="%.2f%%"),
            },
        )

    # SUB-TAB 2: ADD NEW DEPARTMENT
    with sub_tab_add:
        st.markdown(
            """
            <div class="card-header-block">
                <div class="analytical-card-header">Register New Administrative Entity</div>
                <div class="analytical-card-sub">
                    Add a newly reporting Ministry, Department, or State. The record is permanently saved to the CSV dataset 
                    and all dashboard charts, Pareto distributions, and rankings instantly reflect the new data.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("form_add_department", clear_on_submit=False):
            new_name = st.text_input(
                "Ministry / Department / State Name *",
                placeholder="e.g. Ministry of Renewable Energy, National Informatics Centre, Goa",
            )

            col_vol1, col_vol2 = st.columns(2)
            with col_vol1:
                new_received = st.number_input(
                    "Total Grievance Receipts *",
                    min_value=0,
                    value=10000,
                    step=500,
                    help="Total number of grievances received during reporting period",
                )
            with col_vol2:
                new_disposed = st.number_input(
                    "Total Grievances Disposed *",
                    min_value=0,
                    value=9200,
                    step=500,
                    help="Total number of grievances resolved and closed",
                )

            st.markdown("**Backlog Aging Breakdown by Duration**")
            bp1, bp2, bp3, bp4 = st.columns(4)
            with bp1:
                new_p1y = bp1.number_input("Pending > 1 Year", min_value=0, value=200, step=20)
            with bp2:
                new_p6m = bp2.number_input("6 To 12 Months", min_value=0, value=250, step=20)
            with bp3:
                new_p2m = bp3.number_input("2 To 6 Months", min_value=0, value=200, step=20)
            with bp4:
                new_pl2m = bp4.number_input("Less Than 2 Months", min_value=0, value=150, step=20)

            calc_pending_add = int(new_p1y + new_p6m + new_p2m + new_pl2m)
            calc_rate_add = round((new_disposed / new_received * 100), 2) if new_received > 0 else 0.0

            st.markdown(
                f"""
                <div style="display: flex; gap: 14px; margin: 12px 0 16px 0; background: #FFFFFF; padding: 12px 16px; border: 1px solid #DFD5C2; border-radius: 6px;">
                    <div><b>Calculated Total Pending:</b> <span style="color: #B84A39; font-weight: 700;">{calc_pending_add:,}</span></div>
                    <div>&bull;</div>
                    <div><b>Calculated Disposal Rate:</b> <span style="color: #1B5E43; font-weight: 700;">{calc_rate_add:.2f}%</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            submit_add = st.form_submit_button("Add Department to Master Dataset", type="primary")

        if submit_add:
            clean_name = new_name.strip()
            existing_names_lower = [str(x).strip().lower() for x in data[COL_NAME].dropna()]
            if not clean_name:
                st.error("Department name cannot be blank. Please enter a valid entity name.")
            elif clean_name.lower() in existing_names_lower:
                st.error(f"A record for '{clean_name}' already exists in the dataset. Use the 'Edit Existing Record' tab to update its figures.")
            else:
                new_record = {
                    COL_NAME: clean_name,
                    COL_RECEIVED: int(new_received),
                    COL_DISPOSED: int(new_disposed),
                    COL_PENDING: int(calc_pending_add),
                    DURATION_COLS[0]: int(new_p1y),
                    DURATION_COLS[1]: int(new_p6m),
                    DURATION_COLS[2]: int(new_p2m),
                    DURATION_COLS[3]: int(new_pl2m),
                }
                updated_dataset = pd.concat([data, pd.DataFrame([new_record])], ignore_index=True)
                if save_dataset_to_csv(updated_dataset):
                    st.session_state["data_action_status"] = f"Department '{clean_name}' successfully added! Total reporting departments is now {len(updated_dataset)}."
                    st.rerun()

    # SUB-TAB 3: EDIT EXISTING RECORD
    with sub_tab_edit:
        st.markdown(
            """
            <div class="card-header-block">
                <div class="analytical-card-header">Modify Existing Department Statistics</div>
                <div class="analytical-card-sub">
                    Select any Ministry or Department to update its receipt, disposal, or pending breakdown figures. 
                    Changes are committed directly to disk and update all visualizations immediately.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not all_dept_list:
            st.info("No departments currently in the dataset.")
        else:
            selected_edit_dept = st.selectbox(
                "Select Department to Update",
                options=all_dept_list,
                key="sel_dept_to_edit",
            )

            edit_row = data[data[COL_NAME] == selected_edit_dept].iloc[0]

            with st.form("form_edit_department"):
                upd_name = st.text_input(
                    "Department Name",
                    value=str(edit_row[COL_NAME]),
                )

                ec_col1, ec_col2 = st.columns(2)
                with ec_col1:
                    upd_received = st.number_input(
                        "Total Grievance Receipts",
                        min_value=0,
                        value=int(edit_row[COL_RECEIVED]),
                        step=500,
                    )
                with ec_col2:
                    upd_disposed = st.number_input(
                        "Total Grievances Disposed",
                        min_value=0,
                        value=int(edit_row[COL_DISPOSED]),
                        step=500,
                    )

                st.markdown("**Pending Duration Breakdown**")
                ep1, ep2, ep3, ep4 = st.columns(4)
                with ep1:
                    upd_p1y = ep1.number_input("Pending > 1 Year", min_value=0, value=int(edit_row[DURATION_COLS[0]]), step=10)
                with ep2:
                    upd_p6m = ep2.number_input("6 To 12 Months", min_value=0, value=int(edit_row[DURATION_COLS[1]]), step=10)
                with ep3:
                    upd_p2m = ep3.number_input("2 To 6 Months", min_value=0, value=int(edit_row[DURATION_COLS[2]]), step=10)
                with ep4:
                    upd_pl2m = ep4.number_input("Less Than 2 Months", min_value=0, value=int(edit_row[DURATION_COLS[3]]), step=10)

                calc_pending_edit = int(upd_p1y + upd_p6m + upd_p2m + upd_pl2m)
                calc_rate_edit = round((upd_disposed / upd_received * 100), 2) if upd_received > 0 else 0.0

                st.markdown(
                    f"""
                    <div style="display: flex; gap: 14px; margin: 12px 0 16px 0; background: #FFFFFF; padding: 12px 16px; border: 1px solid #DFD5C2; border-radius: 6px;">
                        <div><b>Calculated Total Pending:</b> <span style="color: #B84A39; font-weight: 700;">{calc_pending_edit:,}</span></div>
                        <div>&bull;</div>
                        <div><b>Calculated Disposal Rate:</b> <span style="color: #1B5E43; font-weight: 700;">{calc_rate_edit:.2f}%</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                submit_edit = st.form_submit_button("Save Changes to Department", type="primary")

            if submit_edit:
                clean_upd_name = upd_name.strip()
                if not clean_upd_name:
                    st.error("Department name cannot be blank.")
                else:
                    match_indices = data[data[COL_NAME] == selected_edit_dept].index
                    if not match_indices.empty:
                        target_idx = match_indices[0]
                        updated_dataset = data.copy()
                        updated_dataset.at[target_idx, COL_NAME] = clean_upd_name
                        updated_dataset.at[target_idx, COL_RECEIVED] = int(upd_received)
                        updated_dataset.at[target_idx, COL_DISPOSED] = int(upd_disposed)
                        updated_dataset.at[target_idx, COL_PENDING] = int(calc_pending_edit)
                        updated_dataset.at[target_idx, DURATION_COLS[0]] = int(upd_p1y)
                        updated_dataset.at[target_idx, DURATION_COLS[1]] = int(upd_p6m)
                        updated_dataset.at[target_idx, DURATION_COLS[2]] = int(upd_p2m)
                        updated_dataset.at[target_idx, DURATION_COLS[3]] = int(upd_pl2m)

                        if save_dataset_to_csv(updated_dataset):
                            st.session_state["data_action_status"] = f"Department '{clean_upd_name}' updated successfully. All graphs reflect the updated figures."
                            st.rerun()

    # SUB-TAB 4: REMOVE DEPARTMENT
    with sub_tab_remove:
        st.markdown(
            """
            <div class="card-header-block">
                <div class="analytical-card-header">Remove Administrative Entity</div>
                <div class="analytical-card-sub">
                    Select a department or state to permanently remove from the active dataset. 
                    All national totals, benchmarks, and departmental rankings will immediately recalculate for the remaining entities.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not all_dept_list:
            st.info("No departments currently in dataset to delete.")
        else:
            del_selected_dept = st.selectbox(
                "Select Department to Remove",
                options=all_dept_list,
                key="sel_dept_to_delete",
            )

            del_match = data[data[COL_NAME] == del_selected_dept]
            if not del_match.empty:
                del_row = del_match.iloc[0]
                d_rec = int(del_row[COL_RECEIVED])
                d_disp = int(del_row[COL_DISPOSED])
                d_pend = int(del_row[COL_PENDING])
                d_rate = (d_disp / d_rec * 100) if d_rec > 0 else 0.0

                st.markdown(
                    f"""
                    <div style="background: #FFFFFF; border: 1px solid #ECC1B7; border-left: 4px solid #B84A39; border-radius: 6px; padding: 16px 20px; margin-bottom: 16px;">
                        <div style="font-weight: 800; font-size: 15px; color: #1A1816; margin-bottom: 8px;">{del_selected_dept}</div>
                        <div style="font-size: 13px; color: #4D453A; line-height: 1.6;">
                            <b>Receipts:</b> {d_rec:,} &nbsp;|&nbsp; 
                            <b>Disposals:</b> {d_disp:,} &nbsp;|&nbsp; 
                            <b>Pending Backlog:</b> {d_pend:,} &nbsp;|&nbsp; 
                            <b>Disposal Rate:</b> {d_rate:.2f}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(f"Permanently Delete '{del_selected_dept}'", key="btn_confirm_delete", type="primary"):
                    updated_dataset = data[data[COL_NAME] != del_selected_dept].copy()
                    if save_dataset_to_csv(updated_dataset):
                        if "dept_filter" in st.session_state and del_selected_dept in st.session_state["dept_filter"]:
                            st.session_state["dept_filter"].remove(del_selected_dept)
                        st.session_state["data_action_status"] = f"Department '{del_selected_dept}' was permanently deleted. Remaining departments: {len(updated_dataset)}."
                        st.rerun()

    # SUB-TAB 5: UPLOAD CSV DATASET
    with sub_tab_upload:
        st.markdown(
            """
            <div class="card-header-block">
                <div class="analytical-card-header">Upload Replacement CSV Dataset</div>
                <div class="analytical-card-sub">
                    Upload a complete CSV file to replace or update the active dataset. 
                    The uploaded CSV must include the standard 8 columns. Before applying, the system verifies the schema and provides a preview.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded_csv_file = st.file_uploader(
            "Select CSV File",
            type=["csv"],
            key="fu_csv_replacement",
            help="File must contain the 8 standard columns used in public grievance reporting",
        )

        if uploaded_csv_file is not None:
            try:
                up_df = pd.read_csv(uploaded_csv_file)
                up_df.columns = [str(c).strip() for c in up_df.columns]
                missing_cols = [c for c in REQUIRED_COLUMNS if c not in up_df.columns]

                if missing_cols:
                    st.markdown(
                        f"""
                        <div class="status-error-banner">
                            <b>Validation Failed:</b> The uploaded CSV is missing {len(missing_cols)} required columns:<br>
                            <code>{', '.join(missing_cols)}</code>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    # Clean numeric columns
                    for col in [COL_RECEIVED, COL_DISPOSED, COL_PENDING] + DURATION_COLS:
                        up_df[col] = pd.to_numeric(up_df[col], errors="coerce").fillna(0).astype(int)

                    st.markdown(
                        f"""
                        <div class="status-success-banner">
                            <b>Dataset Validated:</b> Found {len(up_df)} departments with all required columns. Review preview below before applying.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.dataframe(up_df.head(5), width="stretch")

                    if st.button("Apply and Overwrite Master Dataset", type="primary", key="btn_apply_up_csv"):
                        # Save safety backup of current data
                        safety_backup_path = ROOT / "data" / "Dept_stat_receipt_disposal_pre_upload_backup.csv"
                        try:
                            shutil.copyfile(DATA_FILE, safety_backup_path)
                        except Exception:
                            pass

                        if save_dataset_to_csv(up_df):
                            st.session_state["dept_filter"] = []
                            st.session_state["active_preset"] = "all"
                            st.session_state["data_action_status"] = f"Replacement dataset applied! Loaded {len(up_df)} departments across all graphs."
                            st.rerun()

            except Exception as e:
                st.error(f"Error reading uploaded CSV file: {e}")

    # SUB-TAB 6: BACKUP & RESTORE
    with sub_tab_backup:
        st.markdown(
            """
            <div class="card-header-block">
                <div class="analytical-card-header">Dataset Backup and Master Baseline Restore</div>
                <div class="analytical-card-sub">
                    The portal maintains an immutable master backup of the official 124-department government report. 
                    If you have added, edited, or removed data and wish to return to the original dataset, you can reset anytime with one click.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        b_c1, b_c2 = st.columns(2)
        with b_c1:
            st.markdown(
                f"""
                <div class="preview-kpi-badge">
                    <div class="preview-kpi-val">{len(data)} Departments</div>
                    <div class="preview-kpi-lbl">Currently Active Dataset</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with b_c2:
            st.markdown(
                f"""
                <div class="preview-kpi-badge">
                    <div class="preview-kpi-val">124 Departments</div>
                    <div class="preview-kpi-lbl">Master Golden Backup Available</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        rst_col1, rst_col2 = st.columns([1.2, 1.0])
        with rst_col1:
            if st.button("Restore Original 124-Department Baseline", type="primary", key="btn_restore_golden_master"):
                if restore_dataset_from_backup():
                    st.session_state["dept_filter"] = []
                    st.session_state["active_preset"] = "all"
                    st.session_state["data_action_status"] = "Master baseline dataset (124 departments) successfully restored from backup! All dashboard views reset."
                    st.rerun()
                else:
                    st.error("Backup file could not be found.")

        with rst_col2:
            if BACKUP_FILE.exists():
                with open(BACKUP_FILE, "r", encoding="utf-8") as bf:
                    golden_csv_content = bf.read()
                st.download_button(
                    label="Download Original Baseline CSV",
                    data=golden_csv_content,
                    file_name="Dept_stat_receipt_disposal_original_124.csv",
                    mime="text/csv",
                    key="btn_dl_golden",
                )
