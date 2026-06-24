import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import streamlit as st

from frontend import _ai_widget
from frontend.client import (
    ai_recommend, create_restaurant, delete_restaurant, list_restaurants,
    login, register, update_account, update_restaurant,
)

st.set_page_config(page_title="FoodieLog", page_icon="🍽️", layout="wide")

# ── Global CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --accent:     #EA580C;
  --accent-bg:  #FFF7ED;
  --accent-mid: #FED7AA;
  --surface:    #FFFFFF;
  --border:     #E7E5E4;
  --text:       #1C1917;
  --muted:      #78716C;
  --r:          12px;
  --shadow:     0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
}

body, p, div, h1, h2, h3, h4, h5, h6,
input, textarea, button, label, select,
.stMarkdown, .stText, .stCaption {
  font-family: 'Inter', -apple-system, sans-serif !important;
}

.stApp { background: #FAFAF9 !important; }
.main .block-container { padding-top: 1.5rem; max-width: 1200px; }
[data-testid="block-container"] { background: transparent !important; }

section[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
  background: #FFFFFF !important;
  border-right: 1px solid var(--border) !important;
}

/* ── Login page (centered, single column) ── */
.login-logo { text-align: center; margin: 0.5rem 0 0.25rem; }
.login-logo img {
  width: 84px; height: 84px; object-fit: contain;
  border-radius: 20px;
  box-shadow: 0 6px 20px rgba(234,88,12,0.18);
}
.login-logo-emoji { font-size: 3.5rem; line-height: 1; }
.login-title {
  text-align: center; font-size: 1.9rem; font-weight: 800;
  letter-spacing: -0.02em; color: var(--text); margin: 0.6rem 0 0.15rem;
}
.login-title span { color: var(--accent); }
.login-sub {
  text-align: center; color: var(--muted); font-size: 0.9rem;
  margin-bottom: 1.5rem;
}
.demo-hint {
  text-align: center; color: var(--muted); font-size: 0.82rem;
  margin-top: 0.9rem;
}
.demo-hint code {
  background: var(--accent-bg); color: var(--accent);
  padding: 0.12rem 0.45rem; border-radius: 5px; font-size: 0.8rem;
}

/* Center & style the login tab bar */
[data-testid="stTabs"] [data-baseweb="tab-list"] { justify-content: center; gap: 0.5rem; }
[data-testid="stTabs"] [data-baseweb="tab"] {
  border-radius: 10px 10px 0 0;
  padding: 0.4rem 1.1rem;
}

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
  border: 1px solid var(--accent-mid);
  border-left: 4px solid var(--accent);
  border-radius: var(--r);
  padding: 1.25rem 2rem;
  margin-bottom: 1.5rem;
}
.hero h1 { margin: 0 0 0.2rem 0; font-size: 1.6rem; font-weight: 800; color: var(--text); }
.hero p  { margin: 0; color: var(--muted); font-size: 0.875rem; }

/* ── Metrics ── */
[data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 1rem 1.25rem !important;
  border-top: 3px solid var(--accent);
  box-shadow: var(--shadow);
}
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; font-weight: 600 !important;
  color: var(--muted) !important; text-transform: uppercase; letter-spacing: 0.06em; }
[data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800 !important;
  color: var(--accent) !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  overflow: hidden; box-shadow: var(--shadow);
}

/* ── Expanders ── */
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  background: var(--surface) !important;
  box-shadow: var(--shadow); margin-bottom: 0.75rem;
}

/* ── Buttons ── */
.stButton > button {
  border-radius: 8px !important;
  font-weight: 500 !important;
}
[data-testid="stFormSubmitButton"] > button {
  background: var(--accent) !important;
  color: white !important;
  border-color: var(--accent) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--accent) !important;
  border-bottom-color: var(--accent) !important;
  font-weight: 600 !important;
}

[data-testid="stAlert"] { border-radius: var(--r) !important; }
hr { border-color: var(--border) !important; }

/* ── Sidebar nav ── */
.sidebar-brand { display: flex; align-items: center; gap: 0.6rem; margin: 0.25rem 0 0.5rem; }
.sidebar-brand .sb-name { font-size: 1.2rem; font-weight: 800; color: var(--text); }
.sidebar-brand .sb-name span { color: var(--accent); }
.sidebar-user {
  display: flex; align-items: center; gap: 0.65rem;
  background: var(--accent-bg); border: 1px solid var(--accent-mid);
  border-radius: 12px; padding: 0.6rem 0.75rem; margin-bottom: 0.5rem;
}
.sidebar-user .su-avatar {
  width: 38px; height: 38px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #FB923C);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 1.05rem; flex-shrink: 0;
}
.sidebar-user .su-name { font-weight: 700; font-size: 0.9rem; color: var(--text); line-height: 1.1; }
.sidebar-user .su-role { font-size: 0.72rem; color: var(--accent); text-transform: capitalize; }
.sidebar-label { font-size: 0.7rem; font-weight: 700; color: var(--muted);
  text-transform: uppercase; letter-spacing: 0.08em; margin: 0.5rem 0 0.25rem 0.25rem; }

section[data-testid="stSidebar"] .stButton > button {
  text-align: left; justify-content: flex-start;
  border: none !important; background: transparent !important;
  font-weight: 600 !important; color: var(--text) !important;
  padding: 0.5rem 0.75rem !important; border-radius: 8px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--accent-bg) !important; color: var(--accent) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: var(--accent-bg) !important; color: var(--accent) !important;
  border-left: 3px solid var(--accent) !important;
}

/* ── Profile ── */
.profile-avatar-fallback {
  width: 130px; height: 130px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #FB923C);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 3.2rem; font-weight: 800; margin: 0 auto;
  box-shadow: 0 8px 24px rgba(234,88,12,0.25);
}
.profile-name { font-size: 1.5rem; font-weight: 800; text-align: center; margin-top: 0.85rem; color: var(--text); }
.profile-email { text-align: center; color: var(--muted); font-size: 0.9rem; margin-bottom: 0.4rem; }
.role-badge {
  display: inline-block; background: var(--accent-bg); color: var(--accent);
  padding: 0.2rem 0.8rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700;
  text-transform: capitalize;
}
.section-head { font-size: 1.5rem; font-weight: 800; color: var(--text); margin-bottom: 0.1rem; }
.section-sub { color: var(--muted); font-size: 0.88rem; margin-bottom: 1.25rem; }
</style>
""", unsafe_allow_html=True)

if st.session_state.get("theme") == "dark":
    st.markdown("""
<style>
:root {
  --bg: #16130F; --surface: #211D18; --surface2: #2A251F;
  --border: #3A332C; --text: #F5F1EB; --muted: #B8AFA4; --accent-bg: #2A1C12;
}
/* App shell */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main { background: #16130F !important; }
[data-testid="stHeader"] { background: #16130F !important; }
[data-testid="stToolbar"] { color: #B8AFA4 !important; }
.main .block-container, [data-testid="block-container"] { background: transparent !important; }

/* Sidebar */
section[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
  background: #211D18 !important; border-right: 1px solid #3A332C !important;
}

/* Text */
body, p, span, label, li, h1,h2,h3,h4,h5,h6,
.stMarkdown, .stMarkdown p, .section-head, .su-name, .sb-name,
[data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] p,
[data-testid="stMarkdownContainer"] p {
  color: #F5F1EB !important;
}
.section-sub, .sidebar-label, [data-testid="stMetricLabel"],
[data-testid="stCaptionContainer"], .stCaption, small { color: #B8AFA4 !important; }

/* Cards / surfaces */
[data-testid="stMetric"] { background: #211D18 !important; border-color: #3A332C !important; }
[data-testid="stExpander"] { background: #211D18 !important; border-color: #3A332C !important; }
[data-testid="stExpander"] summary { background: #211D18 !important; color: #F5F1EB !important; }
[data-testid="stExpander"] summary:hover { background: #2A251F !important; }
[data-testid="stMetricValue"] { color: #FB923C !important; }

/* Inputs / selects / textareas */
.stTextInput input, .stTextArea textarea, .stNumberInput input,
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"] {
  background: #16130F !important; color: #F5F1EB !important; border-color: #3A332C !important;
}
[data-baseweb="select"] > div, [data-baseweb="select"] div[role="button"] {
  background: #16130F !important; color: #F5F1EB !important; border-color: #3A332C !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
  background: #211D18 !important; color: #F5F1EB !important;
}
[role="option"] { background: #211D18 !important; color: #F5F1EB !important; }
[role="option"]:hover { background: #2A251F !important; }
/* multiselect chips */
[data-baseweb="tag"] { background: #2A1C12 !important; color: #FB923C !important; }

/* Slider track */
[data-testid="stSlider"] [data-baseweb="slider"] div { color: #F5F1EB !important; }

/* File uploader */
[data-testid="stFileUploaderDropzone"] { background: #16130F !important; border-color: #3A332C !important; }
[data-testid="stFileUploaderDropzone"] * { color: #B8AFA4 !important; }

/* Dataframe / data editor */
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {
  background: #211D18 !important; border-color: #3A332C !important;
}

/* Hero + sidebar user pill */
.hero { background: linear-gradient(135deg, #2A251F, #16130F) !important; border-color: #3A332C !important; }
.hero p { color: #B8AFA4 !important; }
.sidebar-user { background: rgba(234,88,12,0.16) !important; border-color: rgba(234,88,12,0.35) !important; }

/* Buttons */
hr { border-color: #3A332C !important; }
section[data-testid="stSidebar"] .stButton > button { color: #F5F1EB !important; }
.stButton > button:not([kind="primary"]) {
  background: #2A251F !important; color: #F5F1EB !important; border-color: #3A332C !important;
}

/* Tabs (login) */
[data-testid="stTabs"] [data-baseweb="tab"] { color: #B8AFA4 !important; }

/* Download / misc */
[data-testid="stDownloadButton"] button { background: #2A251F !important; color: #F5F1EB !important; border-color: #3A332C !important; }
</style>
""", unsafe_allow_html=True)

# ── Login page (shown when not authenticated) ─────────────────────────────────

if "token" not in st.session_state:
    _, mid, _ = st.columns([1, 1.3, 1])

    with mid:
        # Icon at the top (centered, small)
        logo = Path(__file__).parent / "assets" / "foodielog.png"
        if logo.exists():
            import base64
            _b64 = base64.b64encode(logo.read_bytes()).decode()
            st.markdown(
                f'<div class="login-logo"><img src="data:image/png;base64,{_b64}"/></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="login-logo"><span class="login-logo-emoji">🍽️</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="login-title">Foodie<span>Log</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Eat. Explore. Remember.</div>', unsafe_allow_html=True)

        tab_signin, tab_signup = st.tabs(["Sign In", "Create Account"])

        # ── Sign In ──
        with tab_signin:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@email.com", key="login_email")
                password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pw")
                submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please enter your email and password.")
                else:
                    try:
                        result = login(email.strip(), password)
                        st.session_state["token"] = result["access_token"]
                        st.session_state["user"] = result["user"]
                        st.rerun()
                    except Exception:
                        st.error("Invalid email or password.")

            st.markdown('<div class="demo-hint">Demo &nbsp;·&nbsp; <code>admin@foodielog.com</code> / <code>admin123</code></div>', unsafe_allow_html=True)

        # ── Create Account ──
        with tab_signup:
            with st.form("register_form"):
                reg_name = st.text_input("Full Name", placeholder="Alex Cohen", key="reg_name")
                reg_email = st.text_input("Email", placeholder="you@email.com", key="reg_email")
                reg_pw = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_pw")
                reg_pw2 = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_pw2")
                reg_submitted = st.form_submit_button("Create Account", use_container_width=True)

            if reg_submitted:
                if not (reg_name and reg_email and reg_pw):
                    st.error("Please fill in all fields.")
                elif reg_pw != reg_pw2:
                    st.error("Passwords don't match.")
                elif len(reg_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    try:
                        result = register(reg_name.strip(), reg_email.strip(), reg_pw)
                        st.session_state["token"] = result["access_token"]
                        st.session_state["user"] = result["user"]
                        st.rerun()
                    except ValueError as ve:
                        st.error(str(ve))
                    except Exception:
                        st.error("Could not create account. Check your details and try again.")

    st.stop()

# ── Main app (authenticated) ─────────────────────────────────────────────────

import base64

_AVATAR_DIR = Path(__file__).parent / "assets" / "avatars"
_AVATAR_DIR.mkdir(parents=True, exist_ok=True)


def _avatar_file(email: str) -> Path | None:
    safe = "".join(c if c.isalnum() else "_" for c in email)
    for ext in ("png", "jpg", "jpeg"):
        p = _AVATAR_DIR / f"{safe}.{ext}"
        if p.exists():
            return p
    return None


_PRICE_OPTS = ["—", "$", "$$", "$$$", "$$$$"]


def _price_to_int(label: str) -> int | None:
    return {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}.get(label)


def _price_to_label(value) -> str:
    try:
        return "$" * int(value)
    except (TypeError, ValueError):
        return ""


def _price_to_int_safe(value) -> int:
    """Map a stored price_level to its index in _PRICE_OPTS (0 = '—')."""
    try:
        v = int(value)
        return v if 1 <= v <= 4 else 0
    except (TypeError, ValueError):
        return 0


@st.cache_data(ttl=30)
def _load(token: str) -> list[dict]:
    return list_restaurants(token)


def refresh() -> None:
    _load.clear()
    st.rerun()


user = st.session_state.get("user", {})
user_name = user.get("name", "User")
user_email = user.get("email", "")
user_role = user.get("role", "user")
is_admin = user_role == "admin"
initials = (user_name[:1] or "U").upper()
token = st.session_state["token"]

# ── Load data ──
try:
    restaurants = _load(token)
except Exception as exc:
    st.error(
        "**Cannot reach the API.** Make sure the backend is running:\n\n"
        "```\nuv run uvicorn app.main:app --reload\n```\n\n"
        f"Error detail: `{exc}`"
    )
    st.stop()

df = pd.DataFrame(restaurants) if restaurants else pd.DataFrame(
    columns=["id", "name", "cuisine", "city", "rating", "status", "notes", "is_favorite"]
)

total = len(df)
visited = int((df["status"] == "Visited").sum()) if not df.empty else 0
want = total - visited
avg_rating = round(df["rating"].mean(), 1) if not df.empty and total > 0 else "—"

# ── Sidebar nav ──
NAV = [
    ("Dashboard", "🏠"),
    ("Restaurants", "🍽️"),
    ("Add & Manage", "➕"),
    ("Insights", "📊"),
    ("Profile", "👤"),
]
if "active_section" not in st.session_state:
    st.session_state.active_section = "Dashboard"

with st.sidebar:
    _logo = Path(__file__).parent / "assets" / "foodielog.png"
    if _logo.exists():
        c_logo, c_name = st.columns([1, 3])
        with c_logo:
            st.image(str(_logo), width=44)
        with c_name:
            st.markdown('<div class="sb-name" style="font-size:1.2rem;font-weight:800;margin-top:0.35rem;">Foodie<span style="color:#EA580C;">Log</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-brand"><span class="sb-name">🍽️ Foodie<span>Log</span></span></div>', unsafe_allow_html=True)

    _avatar = _avatar_file(user_email)
    if _avatar:
        ca, cb = st.columns([1, 3])
        with ca:
            st.image(str(_avatar), width=42)
        with cb:
            st.markdown(f'<div class="su-name" style="font-weight:700;margin-top:0.1rem;">{user_name}</div><div class="su-role" style="color:#EA580C;font-size:0.72rem;text-transform:capitalize;">{user_role}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="sidebar-user"><div class="su-avatar">{initials}</div>'
            f'<div><div class="su-name">{user_name}</div>'
            f'<div class="su-role">{user_role}</div></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="sidebar-label">Menu</div>', unsafe_allow_html=True)
    for label, icon in NAV:
        active = st.session_state.active_section == label
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.active_section = label
            st.rerun()

    st.divider()
    _dark = st.toggle("🌙 Dark mode", value=st.session_state.get("theme") == "dark")
    _new_theme = "dark" if _dark else "light"
    if _new_theme != st.session_state.get("theme", "light"):
        st.session_state["theme"] = _new_theme
        st.rerun()

    if st.button("🔄  Refresh data", key="nav_refresh", use_container_width=True):
        refresh()
    if st.button("🚪  Sign Out", key="nav_signout", use_container_width=True):
        st.session_state.pop("token", None)
        st.session_state.pop("user", None)
        st.session_state.pop("active_section", None)
        st.rerun()

section = st.session_state.active_section


# ── Section: Dashboard ────────────────────────────────────────────────────────

def section_dashboard():
    st.markdown(f'<div class="section-head">Welcome back, {user_name.split()[0]} 👋</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Here\'s a snapshot of your restaurant collection.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total restaurants", total)
    c2.metric("Visited", visited)
    c3.metric("Want to Go", want)
    c4.metric("Avg rating", avg_rating)

    if df.empty:
        st.info("No restaurants yet — head to **Add & Manage** to start your list.")
        return

    st.divider()
    left, right = st.columns(2)

    with left:
        st.markdown("##### 🍴 Top cuisines")
        top = df["cuisine"].value_counts().head(5)
        st.bar_chart(top, color="#EA580C", horizontal=True)

    with right:
        st.markdown("##### ⭐ Highest rated")
        best = df.sort_values("rating", ascending=False).head(5)
        for _, r in best.iterrows():
            st.markdown(
                f"**{r['name']}** · {r['cuisine']}, {r['city']} &nbsp; "
                f"<span style='color:#EA580C;'>{'⭐' * int(r['rating'])}</span>",
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown("##### 🆕 Recently added")
    recent = df.sort_values("id", ascending=False).head(5)[["name", "cuisine", "city", "status"]]
    st.dataframe(recent, use_container_width=True, hide_index=True)


# ── Section: Restaurants ──────────────────────────────────────────────────────

def section_restaurants():
    st.markdown('<div class="section-head">🍽️ Restaurants</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Search, sort, and browse your collection.</div>', unsafe_allow_html=True)

    # Search + sort (server-side via the API)
    sc1, sc2, sc3 = st.columns([2, 1, 1])
    search = sc1.text_input("🔍 Search", placeholder="name, cuisine, or city", key="rest_search")
    sort_by = sc2.selectbox("Sort by", ["id", "name", "rating", "city", "cuisine", "price_level"], key="rest_sort")
    order = sc3.selectbox("Order", ["asc", "desc"], key="rest_order")

    try:
        rows = list_restaurants(token, search=search or None, sort_by=sort_by, order=order)
    except Exception as exc:
        st.error(f"Could not load restaurants: `{exc}`")
        return

    rdf = pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["id", "name", "cuisine", "city", "rating", "status", "notes", "is_favorite", "price_level", "tags"]
    )

    with st.expander("More filters"):
        fc1, fc2, fc3 = st.columns(3)
        status_filter = fc1.multiselect("Status", ["Want to Go", "Visited"], default=["Want to Go", "Visited"])
        if not rdf.empty:
            cuisines = sorted(rdf["cuisine"].unique())
            cuisine_filter = fc2.multiselect("Cuisine", options=cuisines, default=cuisines)
        else:
            cuisine_filter = []
        min_rating, max_rating = fc3.slider("Rating range", 1, 5, (1, 5))
        pc1, pc2 = st.columns(2)
        price_filter = pc1.multiselect("Price", _PRICE_OPTS[1:], default=[])
        favs_only = pc2.checkbox("⭐ Favorites only")

    if not rdf.empty:
        mask = rdf["status"].isin(status_filter) & rdf["rating"].between(min_rating, max_rating)
        if cuisine_filter:
            mask &= rdf["cuisine"].isin(cuisine_filter)
        if favs_only:
            mask &= rdf["is_favorite"] == True  # noqa: E712
        if price_filter:
            wanted = {_price_to_int(p) for p in price_filter}
            mask &= rdf["price_level"].isin(wanted)
        filtered = rdf[mask].reset_index(drop=True)
    else:
        filtered = rdf

    top1, top2 = st.columns([3, 1])
    top1.caption(f"{len(filtered)} shown")
    edit_mode = top2.toggle("✏️ Edit mode", key="rest_edit_mode")

    if filtered.empty:
        st.info("No restaurants match your search/filters.")
        return

    if edit_mode:
        _restaurants_editor(filtered)
    else:
        display = filtered.copy()
        display["fav"] = display["is_favorite"].apply(lambda b: "⭐" if b else "")
        display["rating"] = display["rating"].apply(lambda r: "⭐" * int(r))
        display["price"] = display["price_level"].apply(_price_to_label)
        st.dataframe(
            display[["id", "fav", "name", "cuisine", "city", "rating", "price", "status", "tags", "notes"]],
            use_container_width=True, hide_index=True,
            column_config={
                "id":      st.column_config.NumberColumn("ID", width="small"),
                "fav":     st.column_config.TextColumn("★", width="small"),
                "name":    st.column_config.TextColumn("Name", width="medium"),
                "cuisine": st.column_config.TextColumn("Cuisine", width="small"),
                "city":    st.column_config.TextColumn("City", width="small"),
                "rating":  st.column_config.TextColumn("Rating", width="small"),
                "price":   st.column_config.TextColumn("Price", width="small"),
                "status":  st.column_config.TextColumn("Status", width="small"),
                "tags":    st.column_config.TextColumn("Tags", width="medium"),
                "notes":   st.column_config.TextColumn("Notes", width="large"),
            },
        )

    csv_bytes = filtered.to_csv(index=False).encode()
    st.download_button("⬇️ Download as CSV", data=csv_bytes,
                       file_name="foodielog_export.csv", mime="text/csv")


def _restaurants_editor(filtered):
    """Inline-editable grid. Diffs against the original rows and PUTs changed ones."""
    st.caption("Edit cells directly, then click **Save changes**.")
    editable = filtered.copy()
    editable["is_favorite"] = editable["is_favorite"].astype(bool)
    if "price_level" in editable.columns:
        editable["price_level"] = editable["price_level"].apply(
            lambda v: int(v) if pd.notna(v) else None
        )
    cols = ["id", "name", "cuisine", "city", "rating", "status", "price_level", "is_favorite", "tags", "notes"]
    edited = st.data_editor(
        editable[cols],
        use_container_width=True, hide_index=True, key="rest_data_editor",
        column_config={
            "id":          st.column_config.NumberColumn("ID", disabled=True, width="small"),
            "name":        st.column_config.TextColumn("Name", required=True),
            "cuisine":     st.column_config.TextColumn("Cuisine", required=True),
            "city":        st.column_config.TextColumn("City", required=True),
            "rating":      st.column_config.NumberColumn("Rating", min_value=1, max_value=5, step=1),
            "status":      st.column_config.SelectboxColumn("Status", options=["Want to Go", "Visited"]),
            "price_level": st.column_config.NumberColumn("Price (1-4)", min_value=1, max_value=4, step=1),
            "is_favorite": st.column_config.CheckboxColumn("⭐"),
            "tags":        st.column_config.TextColumn("Tags"),
            "notes":       st.column_config.TextColumn("Notes", width="large"),
        },
    )

    if st.button("💾 Save changes", type="primary", key="save_editor"):
        original = {int(r["id"]): r for _, r in filtered.iterrows()}
        changed = 0
        errors = []
        fields = ["name", "cuisine", "city", "rating", "status", "price_level", "is_favorite", "tags", "notes"]
        for _, row in edited.iterrows():
            rid = int(row["id"])
            orig = original.get(rid)
            if orig is None:
                continue
            if all(_cell_equal(row[f], orig.get(f)) for f in fields):
                continue
            try:
                pl = row["price_level"]
                update_restaurant(
                    rid, token,
                    name=str(row["name"]), cuisine=str(row["cuisine"]), city=str(row["city"]),
                    rating=int(row["rating"]), status=str(row["status"]),
                    notes=(str(row["notes"]) if pd.notna(row["notes"]) and str(row["notes"]).strip() else None),
                    is_favorite=bool(row["is_favorite"]),
                    price_level=(int(pl) if pd.notna(pl) else None),
                    tags=(str(row["tags"]) if pd.notna(row["tags"]) and str(row["tags"]).strip() else None),
                )
                changed += 1
            except Exception as exc:
                errors.append(f"#{rid}: {exc}")
        if errors:
            st.error("Some rows failed:\n\n" + "\n".join(errors))
        elif changed:
            st.success(f"Saved {changed} change(s).")
            refresh()
        else:
            st.info("No changes to save.")


def _cell_equal(a, b) -> bool:
    """Compare two cell values treating NaN/None/'' as equal."""
    a_empty = a is None or (isinstance(a, float) and pd.isna(a)) or a == ""
    b_empty = b is None or (isinstance(b, float) and pd.isna(b)) or b == ""
    if a_empty and b_empty:
        return True
    try:
        if isinstance(a, (int, float)) or isinstance(b, (int, float)):
            return float(a) == float(b)
    except (TypeError, ValueError):
        pass
    return str(a) == str(b)


# ── Section: Add & Manage ─────────────────────────────────────────────────────

def section_add():
    st.markdown('<div class="section-head">➕ Add & Manage</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Add new spots, mark visits, or remove entries.</div>', unsafe_allow_html=True)

    with st.expander("✨  Suggest with AI", expanded=False):
        st.caption("Let the assistant recommend a new restaurant based on your taste.")
        if st.button("✨ Suggest a restaurant", key="ai_suggest_btn"):
            try:
                with st.spinner("Thinking of somewhere you'd love…"):
                    st.session_state["ai_suggestion"] = ai_recommend(token)
            except ValueError as ve:
                st.warning(str(ve))
            except Exception:
                st.error("Couldn't get a suggestion. Try again.")

        sug = st.session_state.get("ai_suggestion")
        if sug:
            st.markdown(
                f"**{sug['name']}** — {sug['cuisine']}, {sug['city']}\n\n_{sug.get('reason', '')}_"
            )
            with st.form("ai_add_form"):
                a1, a2 = st.columns(2)
                a_rating = a1.slider("Your expected rating", 1, 5, 4)
                a_status = a2.selectbox("Status", ["Want to Go", "Visited"], key="ai_status")
                if st.form_submit_button("➕ Add to my list", use_container_width=True):
                    try:
                        create_restaurant(token, name=sug["name"], cuisine=sug["cuisine"],
                                          city=sug["city"], rating=a_rating, status=a_status,
                                          notes="Suggested by AI")
                        st.session_state.pop("ai_suggestion", None)
                        st.success(f"**{sug['name']}** added!")
                        refresh()
                    except Exception as exc:
                        st.error(f"Could not add: `{exc}`")

    with st.expander("➕  Add a restaurant", expanded=df.empty):
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Name *", placeholder="e.g. Pasta Roma")
            cuisine = c2.text_input("Cuisine *", placeholder="e.g. Italian")
            c3, c4, c5 = st.columns(3)
            city = c3.text_input("City *", placeholder="e.g. Tel Aviv")
            rating = c4.slider("Your rating", 1, 5, 3)
            status = c5.selectbox("Status", ["Want to Go", "Visited"])
            p1, p2 = st.columns([1, 2])
            price = p1.selectbox("Price", _PRICE_OPTS)
            tags = p2.text_input("Tags", placeholder="comma-separated, e.g. romantic, outdoor, vegan")
            notes = st.text_area("Notes / review", placeholder="Anything memorable? Dishes to try, vibe…")
            is_fav = st.checkbox("⭐ Mark as favorite")
            submitted = st.form_submit_button("💾 Save restaurant", use_container_width=True)

        if submitted:
            missing = [f for f, v in [("Name", name), ("Cuisine", cuisine), ("City", city)] if not v.strip()]
            if missing:
                st.warning(f"Please fill in: **{', '.join(missing)}**.")
            else:
                try:
                    created = create_restaurant(token, name=name, cuisine=cuisine, city=city,
                                                rating=rating, status=status, notes=notes or None,
                                                is_favorite=is_fav, price_level=_price_to_int(price),
                                                tags=tags or None)
                    st.success(f"**{created['name']}** added!")
                    refresh()
                except Exception as exc:
                    st.error(f"Could not save: `{exc}`")

    with st.expander("✏️  Edit a restaurant"):
        if df.empty:
            st.info("Nothing to edit yet.")
        else:
            opts = {f"{r['name']}  —  {r['cuisine']}, {r['city']}": r for _, r in df.iterrows()}
            choice = st.selectbox("Select a restaurant to edit", list(opts.keys()), key="edit_select")
            r = opts[choice]
            _cur_price = _price_to_int_safe(r.get("price_level"))
            with st.form("edit_form"):
                e1, e2 = st.columns(2)
                e_name = e1.text_input("Name", value=r["name"])
                e_cuisine = e2.text_input("Cuisine", value=r["cuisine"])
                e3, e4, e5 = st.columns(3)
                e_city = e3.text_input("City", value=r["city"])
                e_rating = e4.slider("Rating", 1, 5, int(r["rating"]))
                e_status = e5.selectbox("Status", ["Want to Go", "Visited"],
                                        index=0 if r["status"] == "Want to Go" else 1)
                ep1, ep2 = st.columns([1, 2])
                e_price = ep1.selectbox("Price", _PRICE_OPTS, index=_cur_price)
                e_tags = ep2.text_input("Tags", value=r.get("tags") or "")
                e_notes = st.text_area("Notes / review", value=r.get("notes") or "")
                e_fav = st.checkbox("⭐ Favorite", value=bool(r.get("is_favorite")))
                if st.form_submit_button("💾 Save changes", use_container_width=True):
                    try:
                        update_restaurant(int(r["id"]), token, name=e_name, cuisine=e_cuisine,
                                          city=e_city, rating=e_rating, status=e_status,
                                          notes=e_notes or None, is_favorite=e_fav,
                                          price_level=_price_to_int(e_price), tags=e_tags or None)
                        st.success("Changes saved!")
                        refresh()
                    except Exception as exc:
                        st.error(f"Update failed: `{exc}`")

    with st.expander("✅  Mark as Visited"):
        want_rows = df[df["status"] == "Want to Go"] if not df.empty else pd.DataFrame()
        if want_rows.empty:
            st.info("No 'Want to Go' restaurants right now.")
        else:
            options = {f"{r['name']}  —  {r['cuisine']}, {r['city']}": r for _, r in want_rows.iterrows()}
            chosen_label = st.selectbox("Select a restaurant", list(options.keys()))
            if st.button("✅ Mark as Visited", key="mark_visited_btn"):
                r = options[chosen_label]
                try:
                    update_restaurant(int(r["id"]), token, name=r["name"], cuisine=r["cuisine"],
                                      city=r["city"], rating=int(r["rating"]), status="Visited",
                                      notes=r.get("notes") or None, is_favorite=bool(r.get("is_favorite")),
                                      price_level=r.get("price_level") if pd.notna(r.get("price_level")) else None,
                                      tags=r.get("tags") or None)
                    st.success(f"**{r['name']}** marked as Visited!")
                    refresh()
                except Exception as exc:
                    st.error(f"Update failed: `{exc}`")

    with st.expander("🗑️  Delete a restaurant"):
        if df.empty:
            st.info("No restaurants to delete.")
        else:
            del_options = {f"{r['name']}  —  {r['cuisine']}, {r['city']}": int(r["id"]) for _, r in df.iterrows()}
            chosen = st.selectbox("Select a restaurant to delete", list(del_options.keys()), key="del_select")
            st.warning(f"You are about to permanently delete **{chosen.split('  —  ')[0]}**.")
            if st.button("🗑️ Confirm delete", type="primary", key="confirm_delete_btn"):
                try:
                    delete_restaurant(del_options[chosen], token)
                    st.success("Restaurant deleted.")
                    refresh()
                except Exception as exc:
                    st.error(f"Delete failed: `{exc}`")


# ── Section: Insights ─────────────────────────────────────────────────────────

def section_insights():
    st.markdown('<div class="section-head">📊 Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Patterns across your collection.</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("Add some restaurants to unlock insights.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Cuisines", df["cuisine"].nunique())
    c2.metric("Cities", df["city"].nunique())
    pct = round(100 * visited / total) if total else 0
    c3.metric("Visited rate", f"{pct}%")

    st.divider()
    left, right = st.columns(2)
    with left:
        st.markdown("##### Cuisine breakdown")
        st.bar_chart(df["cuisine"].value_counts(), color="#EA580C", horizontal=True)
    with right:
        st.markdown("##### Top cities")
        st.bar_chart(df["city"].value_counts().head(8), color="#FB923C", horizontal=True)

    st.divider()
    lc, rc = st.columns(2)
    with lc:
        st.markdown("##### Rating distribution")
        rating_counts = df["rating"].value_counts().sort_index()
        rating_counts.index = [f"{i}★" for i in rating_counts.index]
        st.bar_chart(rating_counts, color="#EA580C")
    with rc:
        st.markdown("##### Price range")
        if "price_level" in df.columns and df["price_level"].notna().any():
            pc = df["price_level"].dropna().astype(int).value_counts().sort_index()
            pc.index = ["$" * i for i in pc.index]
            st.bar_chart(pc, color="#FB923C")
        else:
            st.caption("No price data yet — add `$` levels when editing restaurants.")

    st.divider()
    st.markdown("##### Status")
    s1, s2, s3 = st.columns([1, 1, 2])
    s1.metric("✅ Visited", visited)
    s2.metric("📍 Want to Go", want)
    with s3:
        st.caption("Visited progress")
        st.progress(visited / total if total else 0)


# ── Section: Profile ──────────────────────────────────────────────────────────

def section_profile():
    st.markdown('<div class="section-head">👤 Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Your account details and stats.</div>', unsafe_allow_html=True)

    col_pic, col_info = st.columns([1, 2], gap="large")

    with col_pic:
        avatar = _avatar_file(user_email)
        if avatar:
            st.image(str(avatar), use_container_width=True)
        else:
            st.markdown(f'<div class="profile-avatar-fallback">{initials}</div>', unsafe_allow_html=True)

        uploaded = st.file_uploader("Update photo", type=["png", "jpg", "jpeg"], key="avatar_up")
        if uploaded is not None:
            safe = "".join(c if c.isalnum() else "_" for c in user_email)
            for e in ("png", "jpg", "jpeg"):
                old = _AVATAR_DIR / f"{safe}.{e}"
                if old.exists():
                    old.unlink()
            ext = uploaded.name.rsplit(".", 1)[-1].lower()
            (_AVATAR_DIR / f"{safe}.{ext}").write_bytes(uploaded.getbuffer())
            st.success("Photo updated!")
            st.rerun()

    with col_info:
        st.markdown(f'<div class="profile-name" style="text-align:left;">{user_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-email" style="text-align:left;">{user_email}</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="role-badge">{user_role}</span>', unsafe_allow_html=True)
        st.write("")
        st.write("")

        m1, m2, m3 = st.columns(3)
        m1.metric("Restaurants", total)
        m2.metric("Visited", visited)
        fav = df["cuisine"].mode().iloc[0] if not df.empty else "—"
        m3.metric("Favorite cuisine", fav)

        st.divider()
        st.caption("Account permissions")
        if is_admin:
            st.success("**Admin** — manages your own collection and can remove any restaurant.")
        else:
            st.info("**User** — full control over your own restaurants (add, edit, delete).")

    st.divider()
    with st.expander("⚙️  Account settings"):
        with st.form("account_form"):
            new_name = st.text_input("Display name", value=user_name)
            st.markdown("**Change password** (leave blank to keep current)")
            cur_pw = st.text_input("Current password", type="password")
            new_pw = st.text_input("New password", type="password")
            new_pw2 = st.text_input("Confirm new password", type="password")
            if st.form_submit_button("💾 Save account", use_container_width=True):
                changing_pw = bool(new_pw or new_pw2)
                if changing_pw and new_pw != new_pw2:
                    st.error("New passwords don't match.")
                elif changing_pw and len(new_pw) < 6:
                    st.error("New password must be at least 6 characters.")
                else:
                    try:
                        updated = update_account(
                            token,
                            name=new_name if new_name != user_name else None,
                            current_password=cur_pw if changing_pw else None,
                            new_password=new_pw if changing_pw else None,
                        )
                        st.session_state["user"] = updated
                        st.success("Account updated!")
                        st.rerun()
                    except ValueError as ve:
                        st.error(str(ve))
                    except Exception as exc:
                        st.error(f"Update failed: `{exc}`")


# ── Render active section ──
_RENDER = {
    "Dashboard": section_dashboard,
    "Restaurants": section_restaurants,
    "Add & Manage": section_add,
    "Insights": section_insights,
    "Profile": section_profile,
}
_RENDER.get(section, section_dashboard)()

# Floating AI assistant — bottom-right button + right-side chat drawer
_ai_widget.render(st.session_state["token"], st.session_state.get("theme", "light"))
