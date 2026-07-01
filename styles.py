APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 10%, rgba(124, 58, 237, 0.14), transparent 28%),
            radial-gradient(circle at 90% 18%, rgba(14, 165, 233, 0.12), transparent 24%),
            #f7f8fc;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #17142b 0%, #251c4d 56%, #17213c 100%);
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 2rem 2.2rem;
        margin-bottom: 1.3rem;
        border-radius: 28px;
        color: white;
        background: linear-gradient(135deg, #5b21b6 0%, #7c3aed 48%, #0284c7 100%);
        box-shadow: 0 22px 55px rgba(91, 33, 182, 0.22);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 240px;
        height: 240px;
        right: -80px;
        top: -90px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.13);
    }

    .hero-badge {
        display: inline-block;
        padding: 0.38rem 0.75rem;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(255,255,255,0.24);
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .hero h1 {
        margin: 0;
        font-size: clamp(2rem, 5vw, 3.45rem);
        line-height: 1.03;
        font-weight: 800;
    }

    .hero p {
        width: min(650px, 90%);
        margin: 0.75rem 0 0;
        color: rgba(255,255,255,0.88);
        font-size: 1rem;
        line-height: 1.65;
    }

    .stat-card {
        padding: 1.2rem 1.25rem;
        min-height: 118px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 22px;
        background: rgba(255, 255, 255, 0.82);
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.07);
        backdrop-filter: blur(14px);
    }

    .stat-label {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .stat-value {
        margin-top: 0.3rem;
        color: #111827;
        font-size: 2.25rem;
        font-weight: 800;
        line-height: 1;
    }

    .section-title {
        margin-top: 1.25rem;
        color: #111827;
        font-size: 1.15rem;
        font-weight: 800;
    }

    .task-card {
        padding: 1.05rem 1.1rem;
        margin: 0.45rem 0;
        border: 1px solid #e7e9f2;
        border-radius: 18px;
        background: rgba(255,255,255,0.92);
        box-shadow: 0 8px 24px rgba(15,23,42,0.055);
    }

    .task-title {
        margin-bottom: 0.45rem;
        color: #111827;
        font-weight: 750;
        font-size: 1rem;
    }

    .task-meta {
        color: #64748b;
        font-size: 0.82rem;
        line-height: 1.5;
    }

    .pill {
        display: inline-block;
        padding: 0.25rem 0.58rem;
        margin-right: 0.3rem;
        border-radius: 999px;
        background: #ede9fe;
        color: #6d28d9;
        font-size: 0.73rem;
        font-weight: 700;
    }

    .activity-card {
        padding: 1rem 1.15rem;
        margin-top: 0.7rem;
        border-left: 4px solid #7c3aed;
        border-radius: 14px;
        background: #f5f3ff;
        color: #4c1d95;
        font-size: 0.86rem;
    }

    .mode-chip {
        display: inline-block;
        padding: 0.35rem 0.65rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.18);
        font-size: 0.75rem;
        font-weight: 700;
    }

    .sidebar-logo {
        margin: 0.35rem 0 1.5rem;
        font-size: 1.55rem;
        font-weight: 800;
    }

    .sidebar-note {
        padding: 0.9rem;
        margin-top: 1rem;
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 15px;
        background: rgba(255,255,255,0.08);
        font-size: 0.82rem;
        line-height: 1.55;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 18px;
        background: rgba(255,255,255,0.82);
        box-shadow: 0 8px 24px rgba(15,23,42,0.045);
    }

    [data-testid="stChatInput"] {
        border-radius: 18px;
        box-shadow: 0 12px 34px rgba(15,23,42,0.08);
    }

    footer {
        visibility: hidden;
    }
</style>
"""


def inject_css(st) -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)
