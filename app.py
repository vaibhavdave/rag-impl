import streamlit as st
from dotenv import load_dotenv

from auth import authenticate
from orchestrator import Orchestrator

load_dotenv()

st.set_page_config(page_title="Nimbus AI Helpdesk", page_icon="💬", layout="centered")

# ── Inject global CSS ─────────────────────────────────────────────────────────
# Hide the invisible container Streamlit creates for the <style> block
st.markdown("""
<style>
.element-container:has(style) { display: none; }
/* ── Global Reset ──────────────────── */
.stApp { background: #0f0f1a; }
.block-container { padding-top: 2rem; }

/* ── Gradient accent divider ──────── */
.gradient-div {
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
    border-radius: 2px;
    margin: 1rem 0 1.5rem 0;
}

/* ── Login card ────────────────────── */
.login-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    max-width: 440px;
    margin: 3rem auto 1rem auto;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 80px rgba(99,102,241,0.05);
}
.login-card h1 {
    background: linear-gradient(135deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.25rem;
}
.login-card .subtitle {
    color: #8b8ba0;
    text-align: center;
    font-size: 0.9rem;
    margin-bottom: 0;
}

/* ── Chat header ───────────────────── */
.chat-header {
    background: linear-gradient(135deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

/* ── Message bubbles ──────────────── */
.user-bubble {
    background: linear-gradient(135deg, #6366f1, #7c3aed);
    color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1.1rem;
    max-width: 80%;
    margin-left: auto;
    line-height: 1.4;
    font-size: 0.95rem;
}
.assistant-bubble {
    background: #1e1e32;
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 18px 18px 18px 4px;
    padding: 0.75rem 1.1rem;
    max-width: 85%;
    margin-right: auto;
    line-height: 1.4;
    font-size: 0.95rem;
}
.assistant-bubble h1, .assistant-bubble h2, .assistant-bubble h3 {
    color: #a78bfa;
    margin-top: 0.5rem;
    margin-bottom: 0.25rem;
}
.assistant-bubble p { margin: 0.25rem 0; }
.assistant-bubble ul { padding-left: 1.2rem; }
.assistant-bubble li { margin: 0.15rem 0; }

/* ── Sidebar ───────────────────────── */
section[data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
}
section[data-testid="stSidebar"] .sidebar-content {
    padding: 1.5rem 1rem;
}

/* ── Input stylin' ─────────────────── */
.stChatInputContainer {
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 12px !important;
    background: #1a1a2e !important;
}
.stChatInputContainer:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}

/* ── Demo accounts expander ────────── */
.streamlit-expanderHeader {
    color: #8b8ba0 !important;
    font-size: 0.85rem !important;
}
.streamlit-expanderContent {
    background: #1a1a2e !important;
    border: 1px solid rgba(99,102,241,0.1) !important;
    border-radius: 0 0 10px 10px !important;
    font-size: 0.85rem;
}

/* ── Spinner ───────────────────────── */
.stSpinner > div {
    border-top-color: #6366f1 !important;
}

/* ── Button ────────────────────────── */
.stButton > button {
    width: 100%;
    border-radius: 10px !important;
    background: linear-gradient(135deg, #6366f1, #7c3aed) !important;
    color: #fff !important;
    border: none !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    transition: transform .15s, box-shadow .15s !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(99,102,241,0.3) !important;
}

/* ── Error banner ──────────────────── */
div[data-baseweb="alert"] {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_orchestrator() -> Orchestrator:
    return Orchestrator()


# ── Login screen ───────────────────────────────────────────────────────────────
def login_screen():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center'>Nimbus AI</h1>", unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Helpdesk Assistant</p>', unsafe_allow_html=True)
    st.markdown('<div class="gradient-div"></div>', unsafe_allow_html=True)

    with st.form("login", clear_on_submit=False):
        st.text_input("Email", key="login_email", placeholder="you@example.com")
        st.text_input("Password", type="password", key="login_password",
                       placeholder="Enter your password")
        st.markdown("")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

    if submitted:
        email = st.session_state.login_email
        password = st.session_state.login_password
        user = authenticate(email, password)
        if user is None:
            st.error("Invalid email or password.", icon="❌")
        else:
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

    st.markdown('</div>', unsafe_allow_html=True)


# ── Chat screen ────────────────────────────────────────────────────────────────
def chat_screen():
    user = st.session_state.user

    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin-bottom:0'>{user.full_name}</h3>",
                    unsafe_allow_html=True)
        st.caption(user.email)
        st.markdown('<div class="gradient-div" style="margin:0.8rem 0"></div>',
                    unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<span style='color:#8b8ba0;font-size:0.8rem'>Plan</span><br>"
                        f"<span style='font-weight:600'>{user.plan_tier.title()}</span>",
                        unsafe_allow_html=True)
        with col2:
            st.markdown(f"<span style='color:#8b8ba0;font-size:0.8rem'>Role</span><br>"
                        f"<span style='font-weight:600'>{user.role.title()}</span>",
                        unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Log out", key="logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.api_history = []
            st.session_state.display_history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chat-header">Nimbus AI Helpdesk</div>',
                unsafe_allow_html=True)
    st.caption("Ask about your plan, billing, usage, or account.")

    # Render chat history
    for i, turn in enumerate(st.session_state.display_history):
        cls = "user-bubble" if turn["role"] == "user" else "assistant-bubble"
        align = "flex-end" if turn["role"] == "user" else "flex-start"
        st.markdown(
            f'<div style="display:flex;justify-content:{align};margin-bottom:0.6rem">'
            f'<div class="{cls}">{turn["content"]}</div></div>',
            unsafe_allow_html=True,
        )

    prompt = st.chat_input("Ask about your plan, billing, usage, or account...",
                           key="chat_input")
    if prompt:
        st.session_state.display_history.append({"role": "user", "content": prompt})
        st.session_state.api_history.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner(""):
                orchestrator = get_orchestrator()
                try:
                    reply = orchestrator.handle_message(
                        user_id=user.user_id,
                        history=st.session_state.api_history[:-1],  # all except current
                        user_message=prompt,
                    )
                except Exception as exc:  # noqa: BLE001
                    reply = (
                        "Something went wrong reaching the assistant. "
                        f"({exc.__class__.__name__}: {exc})"
                    )
            st.markdown(reply)

        st.session_state.api_history.append({"role": "assistant", "content": reply})
        st.session_state.display_history.append({"role": "assistant", "content": reply})
        st.rerun()


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