import streamlit as st
import yaml
from langchain.globals import set_debug
from streamlit import _bottom
from streamlit_authenticator import Authenticate
from yaml import SafeLoader

from src.inference_pipeline import GPT4Ouro
from src.utils import log_text_convo, collect_feedback, clear_chat

set_debug(True)

# Load project settings
with open("setup.yaml", "r") as file:
    config = yaml.load(file, yaml.Loader)


def activate_register_user_view() -> None:
    st.session_state["register_user_view"] = True


def deactivate_register_user_view() -> None:
    st.session_state["register_user_view"] = False


def register_new_user() -> None:
    # Register new user
    _, c, _ = st.columns([0.2, 0.6, 0.2], gap="small")
    with c:
        st.warning("Do not use HQ-credentials!", icon="⚠️")
        try:
            _, username_of_registered_user, _ = authenticator.register_user(
                location="main",
                preauthorization=False,
                fields={
                    'Form name': 'Sign Up',
                    'Email': 'Email',
                    'Username': 'Username',
                    'Password': 'Password',
                    'Repeat password': 'Repeat password',
                    'Register': 'Register'}
            )
            if username_of_registered_user:
                with open('auth_creds.yaml', 'w') as x:
                    yaml.dump(auth_file, x, default_flow_style=False)
                st.success('User registered successfully')
        except Exception as e:
            st.error(e)

        # Go back to login page
        st.button("Go to login", on_click=deactivate_register_user_view, type="primary")
        st.caption("Click this button to go back")


def do_security_check() -> bool:
    _, c, _ = st.columns([0.2, 0.6, 0.2], gap="small")
    with c:
        _, authentication_status, username = authenticator.login("main")
        if authentication_status:
            authenticator.logout(location="sidebar")
            st.session_state["username"] = username
            return True
        elif authentication_status is None:
            st.warning("Please enter your username and password")
            return False
        elif not authentication_status:
            st.error("username/password is incorrect")
            return False
        else:
            return False


@st.cache_resource(show_spinner=False)
def load_inference_pipeline() -> GPT4Ouro:
    return GPT4Ouro()


# chatbot
def chatbot():
    """
    Space for interacting with LLM
    """
    # Model settings
    with st.sidebar:
        # Show current user
        st.write(f"You are logged in as **{st.session_state['username']}**")
        st.divider()
        st.write("# Model Settings")
        st.session_state["model_name"] = st.selectbox(
            "#### Select Model",
            options=config["MODEL_MAP"].keys(),
            index=list(config["MODEL_MAP"].keys()).index(st.session_state["model_name"]),
            placeholder="Select Model",
            format_func=lambda x: config["MODEL_DISPLAY_MAP"][x]
        )
        st.session_state["model_temperature"] = st.slider(
            '#### Temperature',
            min_value=0.0,
            max_value=2.0,
            value=st.session_state["model_temperature"],
            step=0.1
        )
        st.session_state["system_prompt"] = st.text_area(
            label="#### System Prompt",
            value=st.session_state["system_prompt"],
            height=600
        )

    # Notification about sidebar
    st.caption("Expand sidebar to change settings")

    # Show clear chat option
    _, c2 = st.columns([0.8, 0.2], gap="small")
    with c2:
        st.button(
            label="Clear chat",
            on_click=clear_chat,
            disabled=len(st.session_state["messages"]) == 0
        )
    st.divider()

    # Show chat history
    for message in st.session_state.messages:
        st.chat_message("human").write(message[0])
        st.chat_message("ai").write(message[1])

    # Load inference pipeline
    inference_chain = load_inference_pipeline()

    # Query and response
    question = st.chat_input("How can I assist you?")
    if question:
        # Print user input
        with st.chat_message("user"):
            st.markdown(question)

        # Generate Response
        response = inference_chain.run(
            query=question,
            chat_history=st.session_state.messages,
            system_prompt=st.session_state["system_prompt"],
            llm_base_url=config["MODEL_MAP"][st.session_state["model_name"]],
            model_name=st.session_state["model_name"],
            temperature=st.session_state["model_temperature"]
        )
        # Show response
        st.chat_message("ai").write(response)

        # Update chat history
        st.session_state["messages"].append((question, response))
        log_text_convo()

    # Take feedback and log user convo
    if len(st.session_state["messages"]) != len(st.session_state["feedback"]):
        c1, c2, _ = st.columns([0.08, 0.08, 0.84], gap="small")
        with c1:
            st.button("👍", on_click=collect_feedback, args=[True])
        with c2:
            st.button("👎", on_click=collect_feedback, args=[False])

    # Add disclaimer
    _bottom.caption(
        "⚠️ Disclaimer: This response was generated using LLM, an experimental AI tool. \
        While we aim for accuracy, the tool may produce errors or incomplete information. \
        Please use these responses with caution and verify critical details independently.")


if __name__ == "__main__":
    # Initialize a session
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "feedback" not in st.session_state:
        st.session_state["feedback"] = []
    if "log_success" not in st.session_state:
        st.session_state["log_success"] = []
    if "model_temperature" not in st.session_state:
        st.session_state["model_temperature"] = config["MODEL_TEMPERATURE"]
    if "llm_base_url" not in st.session_state:
        st.session_state["llm_base_url"] = config["DEFAULT_BASE_URL"]
    if "model_name" not in st.session_state:
        st.session_state["model_name"] = config["DEFAULT_MODEL_NAME"]
    if "system_prompt" not in st.session_state:
        st.session_state["system_prompt"] = config["SYSTEM_PROMPT"]
    if "register_user_view" not in st.session_state:
        st.session_state["register_user_view"] = False

    # Page Config
    st.set_page_config(page_title="LLM Park", layout="wide", initial_sidebar_state="collapsed")
    st.write("### 🤖 OuroGPT")  # title
    st.caption(
        "On-premises chatbot solution, ensuring security and reliability while providing responses akin to OpenAI's ChatGPT")
    st.markdown("""
            <style>
                    .block-container {
                        padding-top: 3rem;
                        padding-bottom: 0rem;
                        padding-left: 5rem;
                        padding-right: 5rem;
                    }
            </style>
            """, unsafe_allow_html=True
                )

    # Load a common authentication object for both login and sign up
    with open("auth_creds.yaml") as f:
        auth_file = yaml.load(f, Loader=SafeLoader)
    authenticator = Authenticate(
        auth_file["credentials"],
        auth_file["cookie"]["name"],
        auth_file["cookie"]["key"],
        auth_file["cookie"]["expiry_days"],
        auth_file["preauthorized"]
    )

    _, c, _ = st.columns([0.1, 0.8, 0.1])
    with c:
        # Register new user
        if st.session_state["register_user_view"]:
            register_new_user()
            st.stop()

        # Authenticate user
        if not do_security_check():
            # Option to register new user
            _, c2, _ = st.columns([0.2, 0.5, 0.3])
            with c2:
                st.button("New user?", on_click=activate_register_user_view, type="primary")
            st.stop()

    # Inference
    chatbot()
