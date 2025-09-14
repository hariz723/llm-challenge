import streamlit as st
from src.core.config import settings
from api_consumer import login_user, register_user


API_BASE_URL = settings.API_BASE_URL

# logger.info(f"API Base URL: {API_BASE_URL}")


def login_page():
    """Login/Register page"""
    st.title("🤖 RAG Chat Application")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                response = login_user(username, password, API_BASE_URL)

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.user_id = data["user_id"]
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            username = st.text_input("Username", key="reg_username")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input(
                "Confirm Password", type="password", key="reg_confrim_password"
            )
            submit = st.form_submit_button("Register")

            if password != confirm_password:
                st.error("Passwords do not match")

            if submit:
                response = register_user(username, email, password, API_BASE_URL)

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.user_id = data["user_id"]
                    st.success("Registered successfully!")
                    st.rerun()
                else:
                    st.error("Registration failed")


if __name__ == "__main__":
    login_page()
