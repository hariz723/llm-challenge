import streamlit as st
from core.config import settings
from ui.api_consumer import (
    chat_with_documents,
    login_user,
    register_user,
    search_documents,
    upload_document,
)


API_BASE_URL = settings.API_BASE_URL
st.set_page_config(
    page_title="RAG Chat Application", page_icon=":books:", layout="wide"
)


def initialize_state():
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("last_search_results", [])


def logout():
    for key in ("token", "user_id", "chat_history", "last_search_results"):
        st.session_state.pop(key, None)
    st.rerun()


def login_page():
    st.title("RAG Chat Application")
    st.caption(
        "Upload documents, retrieve the most relevant chunks, and ask grounded questions."
    )

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                response = login_user(username, password, API_BASE_URL)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.user_id = str(data["user_id"])
                    st.success("Logged in successfully.")
                    st.rerun()
                st.error(response.json().get("detail", "Invalid credentials"))

    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            username = st.text_input("Username", key="reg_username")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input(
                "Confirm Password", type="password", key="reg_confirm_password"
            )
            submit = st.form_submit_button("Register", use_container_width=True)

            if submit:
                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    response = register_user(username, email, password, API_BASE_URL)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.user_id = str(data["id"])
                        st.success("Registered successfully.")
                        st.rerun()
                    st.error(response.json().get("detail", "Registration failed"))


def sidebar():
    with st.sidebar:
        st.header("Workspace")
        st.write(f"API: `{API_BASE_URL}`")
        st.write(f"User ID: `{st.session_state.user_id}`")
        st.button("Logout", on_click=logout, use_container_width=True)

        st.divider()
        st.subheader("Upload Documents")
        uploaded_file = st.file_uploader(
            "Choose a text document",
            type=["txt", "md", "py", "json", "csv"],
        )
        if st.button(
            "Index Document", use_container_width=True, disabled=not uploaded_file
        ):
            with st.spinner("Uploading and indexing document..."):
                response = upload_document(
                    uploaded_file, st.session_state.token, API_BASE_URL
                )
            if response.status_code == 200:
                st.success(f"Indexed {response.json()['filename']}.")
            else:
                try:
                    detail = response.json().get("detail", "Upload failed")
                except Exception:
                    detail = "Upload failed"
                st.error(detail)


def render_chat_tab():
    st.subheader("Ask Your Documents")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("Sources"):
                    for idx, source in enumerate(message["sources"], start=1):
                        st.markdown(
                            f"**{idx}. {source['filename']}**  \n"
                            f"Score: `{source['score']:.4f}`  \n"
                            f"{source['text']}"
                        )

    query = st.chat_input("Ask a question about your indexed documents")
    if query:
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving context and generating answer..."):
                response = chat_with_documents(
                    query=query,
                    token=st.session_state.token,
                    api_base_url=API_BASE_URL,
                )

            if response.status_code == 200:
                payload = response.json()
                st.markdown(payload["answer"])
                if payload["sources"]:
                    with st.expander("Sources", expanded=True):
                        for idx, source in enumerate(payload["sources"], start=1):
                            st.markdown(
                                f"**{idx}. {source['filename']}**  \n"
                                f"Score: `{source['score']:.4f}`  \n"
                                f"{source['text']}"
                            )
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": payload["answer"],
                        "sources": payload["sources"],
                    }
                )
            else:
                try:
                    detail = response.json().get("detail", "Chat failed")
                except Exception:
                    detail = "Chat failed"
                st.error(detail)


def render_search_tab():
    st.subheader("Inspect Retrieval")
    with st.form("search_form"):
        query = st.text_input("Similarity search query")
        submit = st.form_submit_button("Search", use_container_width=True)

        if submit and query.strip():
            with st.spinner("Searching indexed chunks..."):
                response = search_documents(query, st.session_state.token, API_BASE_URL)
            if response.status_code == 200:
                st.session_state.last_search_results = response.json()
            else:
                try:
                    detail = response.json().get("detail", "Search failed")
                except Exception:
                    detail = "Search failed"
                st.error(detail)

    if st.session_state.last_search_results:
        for idx, result in enumerate(st.session_state.last_search_results, start=1):
            st.markdown(
                f"**{idx}. {result['filename']}**  \n"
                f"Score: `{result['score']:.4f}`  \n"
                f"{result['text']}"
            )
    else:
        st.info("Run a search to inspect the chunks the retriever finds most relevant.")


def app():
    initialize_state()
    if not st.session_state.token:
        login_page()
        return

    sidebar()
    st.title("RAG Workspace")

    chat_tab, search_tab = st.tabs(["Chat", "Search"])
    with chat_tab:
        render_chat_tab()
    with search_tab:
        render_search_tab()


if __name__ == "__main__":
    app()
