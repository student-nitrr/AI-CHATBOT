APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: #f6f7fb; color: #172033; }
    [data-testid="stSidebar"] { background: #111827; border-right: 1px solid #263244; }
    [data-testid="stSidebar"] * { color: #e5eaf3; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { padding: .48rem .65rem; border-radius: 10px; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: #263244; }

    /* Keep text readable inside the light provider selectbox on the dark sidebar. */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #ffffff !important;
        border-color: #d7deea !important;
    }
    /* Force the selected provider label (e.g. Auto Mode) to use dark,
       fully opaque text. Streamlit/BaseWeb can apply its own muted value colour. */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-baseweb="select"] input,
    [data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"],
    [data-testid="stSidebar"] [data-baseweb="select"] [aria-selected="true"],
    [data-testid="stSidebar"] [data-baseweb="select"] div[class*="singleValue"] {
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] div[class*="singleValue"] {
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="popover"],
    [data-testid="stSidebar"] [data-baseweb="popover"] * {
        color: #172033 !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] p {
        color: inherit !important;
    }
    .block-container { max-width: 1220px; padding-top: 2.1rem; padding-bottom: 3rem; }
    .brand-lockup { display:flex; align-items:center; gap:.75rem; padding:.6rem 0 1rem; }
    .brand-mark { width:42px; height:42px; display:grid; place-items:center; border-radius:14px; background:linear-gradient(135deg,#8b5cf6,#38bdf8); color:white; font-size:1.5rem; font-weight:800; }
    .brand-name { font:800 1.15rem 'Manrope',sans-serif; color:#fff; }
    .brand-caption,.side-label { color:#94a3b8!important; font-size:.65rem; letter-spacing:.14em; font-weight:800; }
    .side-label { margin:.5rem 0 .45rem; }
    .sidebar-tip { margin-top:1.4rem; padding:.9rem; border:1px solid #334155; border-radius:13px; background:#1e293b; color:#cbd5e1; font-size:.8rem; line-height:1.6; }
    .page-heading { margin:.2rem 0 1.5rem; }
    .eyebrow { color:#7c3aed; font-size:.7rem; font-weight:800; letter-spacing:.15em; margin-bottom:.45rem; }
    .page-heading h1 { font:800 clamp(1.8rem,4vw,2.55rem) 'Manrope',sans-serif; color:#172033; letter-spacing:-.045em; margin:0; }
    .page-heading p { color:#64748b; margin:.45rem 0 0; font-size:.98rem; }
    .metric-card { padding:1.15rem 1.25rem; min-height:140px; border:1px solid #e7eaf1; border-radius:18px; background:white; box-shadow:0 8px 24px rgba(15,23,42,.045); }
    .metric-top { display:flex; justify-content:space-between; align-items:center; color:#64748b; font-size:.7rem; font-weight:800; letter-spacing:.08em; }
    .metric-icon { display:grid; place-items:center; width:32px; height:32px; border-radius:10px; background:#f1edff; color:#7c3aed; font-size:1.1rem; }
    .metric-number { color:#172033; font:800 2.2rem 'Manrope',sans-serif; margin-top:.6rem; line-height:1; }
    .metric-hint { color:#94a3b8; font-size:.78rem; margin-top:.4rem; }
    .progress-panel { margin:1rem 0 1.8rem; padding:1rem 1.2rem; background:white; border:1px solid #e7eaf1; border-radius:16px; }
    .progress-copy { display:flex; justify-content:space-between; color:#475569; font-size:.85rem; margin-bottom:.6rem; }
    .progress-copy strong { color:#7c3aed; }
    .progress-track { height:8px; border-radius:99px; background:#eeeaf8; overflow:hidden; }
    .progress-fill { height:100%; border-radius:99px; background:linear-gradient(90deg,#8b5cf6,#38bdf8); }
    .section-heading { color:#172033; font:800 1.15rem 'Manrope',sans-serif; margin:1.5rem 0 .8rem; }
    .feature-card { min-height:150px; padding:1.25rem; background:white; border:1px solid #e7eaf1; border-radius:18px; }
    .feature-icon { color:#7c3aed; font-size:1.5rem; }
    .feature-card h3 { color:#172033; font:800 1.05rem 'Manrope',sans-serif; margin:.45rem 0 .3rem; }
    .feature-card p { color:#64748b; font-size:.87rem; margin:0; line-height:1.55; }
    .chat-intro { color:#64748b; font-size:.85rem; margin:-.7rem 0 1rem; }
    .online-dot { display:inline-block; width:8px; height:8px; background:#22c55e; border-radius:50%; margin-right:.4rem; }
    [data-testid="stChatMessage"] { background:white; border:1px solid #e8ebf2; border-radius:17px; padding:.8rem 1rem; box-shadow:0 5px 18px rgba(15,23,42,.035); }
    [data-testid="stChatInput"] { border-radius:16px; }
    .activity-panel { margin:.5rem 0 1rem; padding:.8rem 1rem; border:1px solid #e9ddff; border-radius:13px; background:#faf8ff; color:#5b21b6; font-size:.82rem; }
    .activity-heading { font-weight:800; margin-bottom:.35rem; }
    .activity-heading span { color:#8b7aa9; font-weight:500; margin-left:.35rem; }
    .activity-panel ul { margin:.25rem 0 0; padding-left:1.15rem; }
    .task-row { display:flex; justify-content:space-between; align-items:center; gap:1rem; padding:1rem 1.1rem; margin:.4rem 0; background:white; border:1px solid #e7eaf1; border-radius:15px; }
    .task-name { color:#172033; font-weight:800; font-size:.95rem; }
    .task-sub { color:#94a3b8; font-size:.76rem; margin-top:.3rem; }
    .task-tags { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:.35rem; }
    .tag { padding:.25rem .55rem; border-radius:99px; font-size:.68rem; font-weight:800; white-space:nowrap; }
    .tag.high { background:#fff1f2; color:#be123c; }
    .tag.medium { background:#fff7ed; color:#c2410c; }
    .tag.low { background:#eff6ff; color:#1d4ed8; }
    .tag.pending { background:#f3e8ff; color:#7e22ce; }
    .tag.completed { background:#dcfce7; color:#15803d; }
    .workflow-step { display:flex; gap:1rem; align-items:flex-start; padding:1rem; margin:.55rem 0; background:white; border:1px solid #e7eaf1; border-radius:15px; }
    .workflow-step > span { color:#8b5cf6; font:800 1.05rem 'Manrope',sans-serif; }
    .workflow-step strong { color:#172033; }
    .workflow-step p { color:#64748b; margin:.2rem 0 0; font-size:.88rem; }
    .stButton > button { border-radius:11px; font-weight:700; border-color:#e2e8f0; }
    .stButton > button[kind="primary"] { background:#7c3aed; border-color:#7c3aed; }
    .app-footer { text-align:center; color:#94a3b8; font-size:.72rem; padding:2rem 0 .5rem; }
    footer { visibility:hidden; }
    @media (max-width: 700px) { .block-container { padding:1.1rem 1rem 2rem; } .task-row { align-items:flex-start; flex-direction:column; } .task-tags { justify-content:flex-start; } }
</style>
"""


def inject_css(st) -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)
