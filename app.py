import streamlit as st
from dotenv import load_dotenv

from auth import authenticate
from orchestrator import Orchestrator

load_dotenv()

st.set_page_config(page_title="Nimbus AI Helpdesk", page_icon="💬")


@st.cache_resource
def get_orchestrator() -> Orchestrator:
    return Orchestrator()


def login_screen():
    st.title("💬 Nimbus AI Helpdesk")
    st.caption("Log in to chat with the support assistant about your account.")

    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        user = authenticate(email, password)
        if user is None:
            st.error("Invalid email or password.")
        else:
            st.session_state.user = user
            st.session_state.api_history = []
            st.session_state.display_history = []
            st.rerun()

    with st.expander("Demo accounts"):
        st.markdown(
            "Password for all demo accounts: `NimbusDemo123!`\n\n"
            "- `demo.free@nimbus.ai` — Free plan, near daily limit\n"
            "- `demo.billing@nimbus.ai` — Pro plan, duplicate charge on file\n"
            "- `demo.limits@nimbus.ai` — Pro plan, right at usage cap\n"
            "- `demo.troubleshoot@nimbus.ai` — Pro plan, general troubleshooting\n"
            "- `demo.admin@nimbus.ai` — Team admin, org has a stale active seat\n"
            "- `demo.member@nimbus.ai` — Team member (non-admin, for permission checks)"
        )


def chat_screen():
    user = st.session_state.user

    with st.sidebar:
        st.subheader(user.full_name)
        st.caption(user.email)
        st.write(f"**Plan:** {user.plan_tier.title()}")
        st.write(f"**Role:** {user.role}")
        if st.button("Log out"):
            st.session_state.user = None
            st.session_state.api_history = []
            st.session_state.display_history = []
            st.rerun()

    st.title("💬 Nimbus AI Helpdesk")

    for turn in st.session_state.display_history:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])

    prompt = st.chat_input("Ask about your plan, billing, usage, a technical issue, or your org...")
    if prompt:
        st.session_state.display_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                orchestrator = get_orchestrator()
                try:
                    reply = orchestrator.handle_message(
                        user_id=user.user_id,
                        history=st.session_state.api_history,
                        user_message=prompt,
                    )
                except Exception as exc:  # noqa: BLE001
                    reply = (
                        "Something went wrong reaching the assistant. "
                        f"({exc.__class__.__name__}: {exc})"
                    )
            st.markdown(reply)

        st.session_state.api_history.append({"role": "user", "content": prompt})
        st.session_state.api_history.append({"role": "assistant", "content": reply})
        st.session_state.display_history.append({"role": "assistant", "content": reply})


def main():
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        login_screen()
    else:
        chat_screen()


if __name__ == "__main__":
    main()
