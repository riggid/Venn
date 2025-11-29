"""Analytics dashboard CSS styles matching the reference design."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Hide Streamlit header/decorative bar */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stHeader"] {display: none;}
[data-testid="stDecoration"] {display: none;}

/* Analytics dashboard dark background */
.stApp {
    background: #0a0e27;
}

/* Sidebar - darker blue */
[data-testid="stSidebar"] {
    background: #0f1629;
    border-right: 1px solid rgba(99, 102, 241, 0.15);
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e2e8f0 !important;
}

/* Hero title - analytics style */
.hero-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #ffffff;
    text-align: left;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}

.hero-subtitle {
    font-size: 1rem;
    color: #94a3b8;
    text-align: left;
    margin-bottom: 2rem;
    font-weight: 400;
}

/* Compass icon */
.compass-icon {
    font-size: 3rem;
    text-align: center;
    display: inline-block;
}

/* Feature cards - analytics card style */
.feature-card {
    background: #0f1629;
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 6px;
    padding: 1.5rem;
    transition: all 0.2s ease;
    height: 100%;
}

.feature-card:hover {
    border-color: rgba(99, 102, 241, 0.3);
    background: #151b2e;
}

.feature-card h3 {
    color: #ffffff;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.feature-card p {
    color: #94a3b8;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(90deg, 
        transparent 0%, 
        rgba(99, 102, 241, 0.2) 50%, 
        transparent 100%);
    margin: 2rem 0;
}

/* Buttons - indigo blue */
.stButton > button {
    background: #6366f1 !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.5rem 1.25rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: #4f46e5 !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3) !important;
}

/* Google sign-in button */
.google-signin-btn {
    display: inline-block;
    background: white;
    color: #1f2937;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    padding: 12px 24px;
    font-weight: 500;
    cursor: pointer;
    text-align: center;
    transition: all 0.2s ease;
    text-decoration: none;
    width: 100%;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.google-signin-btn:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    border-color: #d1d5db;
}

/* Input fields - dark analytics style */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: #0f1629 !important;
    border: 1px solid rgba(99, 102, 241, 0.15) !important;
    border-radius: 4px !important;
    color: #ffffff !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus-within,
.stNumberInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1) !important;
    background: #151b2e !important;
}

/* Text colors */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
}

p, span, div, label {
    color: #e2e8f0 !important;
}

/* Cards - analytics style */
.member-card,
.group-card,
.metric-card {
    background: #0f1629;
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 6px;
    padding: 1rem;
    margin: 0.5rem 0;
    transition: all 0.2s ease;
}

.member-card:hover,
.group-card:hover,
.metric-card:hover {
    border-color: rgba(99, 102, 241, 0.3);
    background: #151b2e;
}

/* Metric numbers - large analytics style */
.stat-number {
    font-size: 2.5rem;
    font-weight: 700;
    color: #6366f1;
    letter-spacing: -1px;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid rgba(99, 102, 241, 0.15) !important;
    color: #e2e8f0 !important;
    margin: 0.3rem 0 !important;
    transition: all 0.2s ease !important;
    border-radius: 4px !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99, 102, 241, 0.1) !important;
    border-color: rgba(99, 102, 241, 0.3) !important;
}

/* Info boxes - colored left borders */
.stInfo,
.stWarning,
.stSuccess,
.stError {
    border-radius: 4px !important;
    border-left: 3px solid !important;
}

.stInfo {
    border-left-color: #6366f1 !important;
    background: rgba(99, 102, 241, 0.08) !important;
}

.stWarning {
    border-left-color: #f59e0b !important;
    background: rgba(245, 158, 11, 0.08) !important;
}

.stSuccess {
    border-left-color: #10b981 !important;
    background: rgba(16, 185, 129, 0.08) !important;
}

.stError {
    border-left-color: #ef4444 !important;
    background: rgba(239, 68, 68, 0.08) !important;
}

/* Map container */
.map-container,
.stMap {
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid rgba(99, 102, 241, 0.15);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: #0f1629;
}

::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.3);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.5);
}

/* Expander styling */
.streamlit-expanderHeader {
    background: #0f1629 !important;
    border: 1px solid rgba(99, 102, 241, 0.15) !important;
    border-radius: 4px !important;
    color: #e2e8f0 !important;
}

.streamlit-expanderHeader:hover {
    border-color: rgba(99, 102, 241, 0.3) !important;
    background: #151b2e !important;
}

/* Tabs - analytics style */
.stTabs [data-baseweb="tab-list"] {
    background: #0f1629;
    border-radius: 4px;
    padding: 0.25rem;
    border: 1px solid rgba(99, 102, 241, 0.15);
}

.stTabs [data-baseweb="tab"] {
    color: #94a3b8 !important;
    border-radius: 3px;
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(99, 102, 241, 0.08) !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(99, 102, 241, 0.15) !important;
    color: #6366f1 !important;
}

/* Progress bars - indigo gradient */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
}

/* Selectbox and inputs */
.stSelectbox label,
.stNumberInput label,
.stTextInput label {
    color: #e2e8f0 !important;
}

/* Main content area */
.main .block-container {
    padding-top: 2rem;
}

/* Remove any default Streamlit styling */
.stApp > header {
    background-color: transparent;
}
</style>
"""
