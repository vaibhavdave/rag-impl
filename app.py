import html
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from auth import authenticate
from orchestrator import Orchestrator

load_dotenv()

st.set_page_config(page_title="Nimbus AI Helpdesk", page_icon="🤖", layout="centered")

# ── Inject global CSS via components (height=0 = no visible rectangle) ──
components.html(
    """
<style>
/* ── Global style ────────────────── */
.stApp { background: #f8fafc; }
.block-container { padding-top: 1.5rem; }

/* ── Robot icon SVG ────────────── */
.robot-icon {
    width: 48px;
    height: 48px;
    display: block;
    margin: 0 auto 0.5rem auto;
}

/* ── Gradient accent divider ──── */
.gradient-div {
    height: 2px;
    background: linear-gradient(90deg, #2563eb, #06b6d4, #2563eb);
    border-radius: 2px;
    margin: 0.8rem 0 1.2rem 0;
}

/* ── Login card ──────────────── */
.st-key-login-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px !important;
    padding: 2rem 2rem 1.5rem !important;
    max-width: 420px !important;
    margin: 2rem auto 1rem auto !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.02) !important;
}
.st-key-login-card h1 {
    color: #1e293b !important;
    font-size: 1.8rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0 !important;
}
.st-key-login-card .subtitle {
    color: #64748b;
    text-align: center;
    font-size: 0.9rem;
    margin-bottom: 0;
}

/* ── Sidebar ─────────────────── */
.st-key-sidebar-card {
    padding: 1rem 0.5rem !important;
}
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
section[data-testid="stSidebar"] .sidebar-robot {
    width: 36px;
    height: 36px;
    display: inline-block;
    vertical-align: middle;
    margin-right: 8px;
}

/* ── Chat bubbles ────────────── */
[data-testid="stChatMessage"] {
    max-width: 78% !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stChatMessage"][aria-label*="user"] {
    margin-left: auto !important;
}
[data-testid="stChatMessage"][aria-label*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    color: #fff !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 0.7rem 1rem !important;
    line-height: 1.4 !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatMessage"][aria-label*="assistant"] {
    margin-right: auto !important;
}
[data-testid="stChatMessage"][aria-label*="assistant"] [data-testid="stChatMessageContent"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 0.7rem 1rem !important;
    line-height: 1.4 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
[data-testid="stChatMessage"][aria-label*="assistant"] h1,
[data-testid="stChatMessage"][aria-label*="assistant"] h2,
[data-testid="stChatMessage"][aria-label*="assistant"] h3 {
    color: #2563eb;
    margin-top: 0.5rem;
    margin-bottom: 0.25rem;
}
[data-testid="stChatMessage"][aria-label*="assistant"] p { margin: 0.2rem 0; }
[data-testid="stChatMessage"][aria-label*="assistant"] ul { padding-left: 1.2rem; }
[data-testid="stChatMessage"][aria-label*="assistant"] li { margin: 0.1rem 0; }

/* ── Chat header ────────────── */
.chat-header-wrapper {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.25rem;
}
.chat-header-robot {
    width: 36px;
    height: 36px;
    flex-shrink: 0;
}
.chat-header {
    color: #1e293b;
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 0;
}

/* ── Chat input ────────────── */
div[data-testid="stChatInput"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    background: #ffffff !important;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.1) !important;
}

/* ── Form submit button ──────── */
div[data-testid="stFormSubmitButton"] button {
    width: 100%;
    border-radius: 10px !important;
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    color: #fff !important;
    border: none !important;
    font-weight: 600 !important;
    padding: 0.45rem 1rem !important;
    transition: transform .15s, box-shadow .15s !important;
}
div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(37,99,235,0.25) !important;
}

/* ── Sidebar logout button ─── */
section[data-testid="stSidebar"] button {
    width: 100%;
    border-radius: 10px !important;
    background: #f1f5f9 !important;
    color: #475569 !important;
    border: 1px solid #e2e8f0 !important;
    font-weight: 500 !important;
    padding: 0.4rem 1rem !important;
}
section[data-testid="stSidebar"] button:hover {
    background: #e2e8f0 !important;
}

/* ── Expander ──────────────── */
[data-testid="stExpander"] summary {
    color: #64748b !important;
    font-size: 0.85rem !important;
}
[data-testid="stExpander"] > div[data-testid="stExpanderContent"] {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 0 0 10px 10px !important;
    font-size: 0.85rem;
}

/* ── Spinner ──────────────── */
.stSpinner > div {
    border-top-color: #2563eb !important;
}

/* ── Error ────────────────── */
div[data-baseweb="alert"] {
    border-radius: 10px !important;
}

/* ── Text inputs ──────────── */
.stTextInput input {
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
}
.stTextInput input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.1) !important;
}
</style>
""",
    height=0,
)

# ── SVG robot icon (to reuse) ─────────────────────────────────────────────────
ROBOT_SVG = """<svg class="robot-icon" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect x="12" y="8" width="24" height="18" rx="4" fill="#2563eb" opacity="0.9"/>
<circle cx="48" cy="48" r="1" fill="none"/>
<rect x="17" y="3" width="14" height="5" rx="2.5" fill="#3b82f6"/>
<circle cx="20" cy="17" r="3" fill="#fff" opacity="0.9"/>
<circle cx="28" cy="17" r="3" fill="#fff" opacity="0.9"/>
<circle cx="20" cy="17" r="1.5" fill="#1e293b"/>
<circle cx="28" cy="17" r="1.5" fill="#1e293b"/>
<rect x="18" y="22" width="12" height="2" rx="1" fill="#fff" opacity="0.8"/>
<rect x="12" y="26" width="24" height="14" rx="4" fill="#2563eb" opacity="0.85"/>
<circle cx="16" cy="33" r="1.2" fill="#60a5fa"/>
<circle cx="24" cy="33" r="1.2" fill="#60a5fa"/>
<circle cx="32" cy="33" r="1.2" fill="#60a5fa"/>
<rect x="18" y="40" width="12" height="4" rx="2" fill="#1e40af" opacity="0.5"/>
</svg>"""

ROBOT_SMALL = """<svg class="sidebar-robot" viewBox="0 0 36 36" fill="none">
<rect x="10" y="6" width="16" height="12" rx="3" fill="#2563eb" opacity="0.85"/>
<rect x="14" y="2" width="8" height="5" rx="2" fill="#3b82f6"/>
<circle cx="15" cy="12" r="2.5" fill="#fff" opacity="0.9"/>
<circle cx="21" cy="12" r="2.5" fill="#fff" opacity="0.9"/>
<circle cx="15" cy="12" r="1.2" fill="#1e293b"/>
<circle cx="21" cy="12" r="1.2" fill="#1e293b"/>
<rect x="13" y="16" width="10" height="1.5" rx="0.7" fill="#fff" opacity="0.8"/>
<rect x="10" y="18" width="16" height="10" rx="3" fill="#2563eb" opacity="0.8"/>
<circle cx="13" cy="23" r="1" fill="#60a5fa"/>
<circle cx="18" cy="23" r="1" fill="#60a5fa"/>
<circle cx="23" cy="23" r="1" fill="#60a5fa"/>
<rect x="14" y="28" width="8" height="3" rx="1.5" fill="#1e40af" opacity="0.4"/>
</svg>"""

ROBOT_HEADER = """<svg class="chat-header-robot" viewBox="0 0 36 36" fill="none">
<rect x="10" y="6" width="16" height="12" rx="3" fill="#2563eb" opacity="0.8"/>
<rect x="14" y="2" width="8" height="5" rx="2" fill="#3b82f6"/>
<circle cx="15" cy="12" r="2.5" fill="#fff"/>
<circle cx="21" cy="12" r="2.5" fill="#fff"/>
<circle cx="15" cy="12" r="1.2" fill="#1e293b"/>
<circle cx="21" cy="12" r="1.2" fill="#1e293b"/>
<rect x="13" y="16" width="10" height="1.5" rx="0.7" fill="#fff"/>
<rect x="10" y="18" width="16" height="10" rx="3" fill="#2563eb" opacity="0.75"/>
<circle cx="13" cy="23" r="1" fill="#60a5fa"/>
<circle cx="18" cy="23" r="1" fill="#60a5fa"/>
<circle cx="23" cy="23" r="1" fill="#60a5fa"/>
<rect x="14" y="28" width="8" height="3" rx="1.5" fill="#1e40af" opacity="0.35"/>
</svg>"""


@st.cache_resource
def get_orchestrator() -> Orchestrator:
    return Orchestrator()


# ── Login screen ───────────────────────────────────────────────────────────────
def login_screen():
    with st.container(key="login-card"):
        st.markdown(ROBOT_SVG, unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center'>Nimbus AI</h1>", unsafe_allow_html=True)
        st.markdown('<p class="subtitle" style="text-align:center">Helpdesk Assistant</p>',
                    unsafe_allow_html=True)
        st.markdown('<div class="gradient-div"></div>', unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        with st.form("login", clear_on_submit=True):
            submitted = st.form_submit_button("Sign in", use_container_width=True)

        if submitted:
            user = authenticate(email, password)
            if user is None:
                st.error("Invalid email or password.", icon="❌")
            else:
                password = None
                st.session_state.user = user
                st.session_state.api_history = []
                st.session_state.display_history = []
                st.rerun()

        with st.expander("🔍 Demo accounts"):
            st.markdown(
                "Password for all: `NimbusDemo123!`\n\n"
                "| Email | Scenario |\n"
                "|-------|----------|\n"
                "| `demo.free@nimbus.ai` | Free plan, near daily limit |\n"
                "| `demo.billing@nimbus.ai` | Pro plan, duplicate charge |\n"
                "| `demo.limits@nimbus.ai` | Pro plan, at usage cap |\n"
                "| `demo.troubleshoot@nimbus.ai` | General troubleshooting |\n"
                "| `demo.admin@nimbus.ai` | Team admin, stale seat |\n"
                "| `demo.member@nimbus.ai` | Team member, permission check |"
            )


# ── Chat screen ────────────────────────────────────────────────────────────────
def chat_screen():
    user = st.session_state.user

    with st.sidebar:
        with st.container(key="sidebar-card"):
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px">'
                f'{ROBOT_SMALL}'
                f'<div><h3 style="margin:0">{html.escape(user.full_name)}</h3>'
                f'<span style="color:#64748b;font-size:0.8rem">{html.escape(user.email)}</span></div></div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="gradient-div" style="margin:0.8rem 0"></div>',
                        unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f"<span style='color:#64748b;font-size:0.8rem'>Plan</span><br>"
                    f"<span style='font-weight:600'>{html.escape(user.plan_tier.title())}</span>",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"<span style='color:#64748b;font-size:0.8rem'>Role</span><br>"
                    f"<span style='font-weight:600'>{html.escape(user.role.title())}</span>",
                    unsafe_allow_html=True,
                )

            if st.button("Log out", key="logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.api_history = []
                st.session_state.display_history = []
                st.rerun()

    # Chat header with robot icon
    st.markdown(
        f'<div class="chat-header-wrapper">'
        f'{ROBOT_HEADER}'
        f'<span class="chat-header">Nimbus AI Helpdesk</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("Ask about your plan, billing, usage, or account.")

    # Render chat history
    for turn in st.session_state.display_history:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])

    prompt = st.chat_input("Ask about your plan, billing, usage, or account...",
                           key="chat_input")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.display_history.append({"role": "user", "content": prompt})
        st.session_state.api_history.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                orchestrator = get_orchestrator()
                try:
                    reply = orchestrator.handle_message(
                        user_id=user.user_id,
                        history=list(st.session_state.api_history[:-1]),
                        user_message=prompt,
                    )
                except Exception as exc:
                    reply = (
                        "Something went wrong reaching the assistant. "
                        f"({exc.__class__.__name__}: {exc})"
                    )
            st.markdown(reply)

        st.session_state.api_history.append({"role": "assistant", "content": reply})
        st.session_state.display_history.append({"role": "assistant", "content": reply})


# ── Main dispatcher ────────────────────────────────────────────────────────────
def main():
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        login_screen()
    else:
        chat_screen()


if __name__ == "__main__":
    main()