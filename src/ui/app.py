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
    page_title="RAG Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_custom_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        /* Global Theme */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: radial-gradient(circle at 15% 15%, #111827 0%, #080C14 85%) !important;
            color: #F3F4F6 !important;
        }

        /* Headings */
        h1, h2, h3, h4 {
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.02em;
            color: #F9FAFB !important;
        }

        .hero-title {
            font-size: 2.25rem !important;
            font-weight: 700;
            background: linear-gradient(135deg, #C084FC 0%, #60A5FA 50%, #34D399 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.25rem;
        }

        .hero-caption {
            color: #94A3B8;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.85) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 16px 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(10px);
            margin-bottom: 16px;
        }

        .user-badge {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(139, 92, 246, 0.12);
            border: 1px solid rgba(139, 92, 246, 0.28);
            padding: 10px 14px;
            border-radius: 12px;
            color: #E9D5FF;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 12px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #10B981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px #10B981;
            margin-right: 6px;
        }

        /* Form Inputs */
        div[data-baseweb="input"] {
            background-color: rgba(30, 41, 59, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: #F8FAFC !important;
        }

        div[data-baseweb="input"]:focus-within {
            border-color: #8B5CF6 !important;
            box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.3) !important;
        }

        /* Modern Buttons */
        div.stButton > button {
            background: linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 0.55rem 1.25rem !important;
            transition: all 0.2s ease-in-out !important;
            box-shadow: 0 4px 14px 0 rgba(124, 58, 237, 0.35) !important;
        }

        div.stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 22px 0 rgba(124, 58, 237, 0.55) !important;
            border-color: rgba(255, 255, 255, 0.3) !important;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            color: #94A3B8 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #A78BFA !important;
            border-bottom-color: #8B5CF6 !important;
        }

        /* Chat messages */
        [data-testid="stChatMessage"] {
            background: rgba(30, 41, 59, 0.45) !important;
            border: 1px solid rgba(255, 255, 255, 0.07) !important;
            border-radius: 14px !important;
            padding: 14px 18px !important;
            margin-bottom: 12px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }

        /* Source citations */
        .source-card {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 10px;
        }

        .source-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            color: #E2E8F0;
            font-size: 0.85rem;
            margin-bottom: 6px;
        }

        .score-pill {
            background: rgba(139, 92, 246, 0.2);
            color: #C4B5FD;
            border: 1px solid rgba(139, 92, 246, 0.35);
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 600;
        }

        .source-text {
            color: #94A3B8;
            font-size: 0.82rem;
            line-height: 1.5;
            white-space: pre-wrap;
        }

        /* Feature Chips */
        .feature-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 0.8rem;
            color: #CBD5E1;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state():
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("last_search_results", [])
    st.session_state.setdefault("indexed_file_ids", set())


def logout():
    for key in (
        "token",
        "user_id",
        "chat_history",
        "last_search_results",
        "indexed_file_ids",
    ):
        st.session_state.pop(key, None)
    st.rerun()


def login_page():
    apply_custom_styles()

    col1, col2, col3 = st.columns([1, 2.2, 1])

    with col2:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 2rem; margin-bottom: 1.5rem;">
                <div style="font-size: 2.8rem; margin-bottom: 0.25rem;">⚡</div>
                <div class="hero-title">RAG Intelligence</div>
                <div class="hero-caption">
                    Unified semantic search, document ingestion, and conversational AI
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            with st.form("login_form"):
                st.subheader("Welcome Back")
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input(
                    "Password", type="password", placeholder="Enter password"
                )
                submit = st.form_submit_button("Sign In", use_container_width=True)

                if submit:
                    response = login_user(username, password, API_BASE_URL)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.user_id = str(
                            data.get("user_id") or data.get("id")
                        )
                        st.success("Authenticated successfully.")
                        st.rerun()
                    st.error(response.json().get("detail", "Invalid credentials"))
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            with st.form("register_form"):
                st.subheader("Create Account")
                username = st.text_input(
                    "Username", key="reg_username", placeholder="Choose username"
                )
                email = st.text_input(
                    "Email", key="reg_email", placeholder="name@example.com"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    key="reg_password",
                    placeholder="Choose password",
                )
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    key="reg_confirm_password",
                    placeholder="Repeat password",
                )
                submit = st.form_submit_button("Register Now", use_container_width=True)

                if submit:
                    if password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        response = register_user(
                            username, email, password, API_BASE_URL
                        )
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.token = data["access_token"]
                            st.session_state.user_id = str(data["id"])
                            st.success("Account created successfully.")
                            st.rerun()
                        st.error(response.json().get("detail", "Registration failed"))
            st.markdown("</div>", unsafe_allow_html=True)


def sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1rem;">
                <span style="font-size: 1.6rem;">⚡</span>
                <span style="font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">
                    RAG Workspace
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="user-badge">
                <span><span class="status-dot"></span>Connected</span>
                <span style="opacity: 0.8; font-size: 0.78rem;">User #{st.session_state.user_id}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.button("Logout", on_click=logout, use_container_width=True)

        st.divider()

        st.markdown("### 📁 Document Vault")
        st.caption("Supported formats: PDF, DOCX, TXT, MD, PY, JSON, CSV")

        uploaded_file = st.file_uploader(
            "Upload Document",
            type=["txt", "md", "py", "json", "csv", "pdf", "docx"],
            label_visibility="collapsed",
        )

        if uploaded_file:
            file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            if file_key not in st.session_state.indexed_file_ids:
                with st.spinner(f"⚡ Auto-indexing {uploaded_file.name}..."):
                    try:
                        response = upload_document(
                            uploaded_file, st.session_state.token, API_BASE_URL
                        )
                        if response.status_code == 200:
                            st.session_state.indexed_file_ids.add(file_key)
                            st.success(
                                f"Indexed **{response.json()['filename']}** successfully."
                            )
                        else:
                            try:
                                detail = response.json().get("detail", "Upload failed")
                            except Exception:
                                detail = "Upload failed"
                            st.error(detail)
                    except Exception as e:
                        st.error(f"Upload failed: {e}")
            else:
                st.caption(f"✅ `{uploaded_file.name}` is indexed and ready.")

        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="font-size: 0.72rem; color: #64748B;">
                Endpoint: <code>{API_BASE_URL}</code><br>
                Model: <code>all-MiniLM-L6-v2</code><br>
                Observability: <code>Langfuse</code>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_chat_tab():
    st.markdown("### 💬 Document Conversation")

    if not st.session_state.chat_history:
        st.markdown(
            """
            <div class="glass-card" style="text-align: center; padding: 2.5rem 1.5rem; margin-top: 1rem;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🤖</div>
                <div style="font-size: 1.15rem; font-weight: 600; color: #F1F5F9; margin-bottom: 0.25rem;">
                    Ready for your queries
                </div>
                <div style="color: #94A3B8; font-size: 0.88rem; max-width: 480px; margin: 0 auto;">
                    Upload documents from the sidebar to ask questions grounded directly in your source material with semantic citations.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for message in st.session_state.chat_history:
        avatar = "👤" if message["role"] == "user" else "⚡"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander(
                    f"📚 Retrieved Citations ({len(message['sources'])} chunks)"
                ):
                    for idx, source in enumerate(message["sources"], start=1):
                        score = source.get("score", 0.0)
                        st.markdown(
                            f"""
                            <div class="source-card">
                                <div class="source-header">
                                    <span>📄 {idx}. {source['filename']}</span>
                                    <span class="score-pill">Match: {score:.4f}</span>
                                </div>
                                <div class="source-text">{source['text']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            if message.get("trace_url"):
                st.caption(f"⚡ [View Langfuse Trace]({message['trace_url']})")

    query = st.chat_input("Ask a question about your indexed documents...")
    if query:
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user", avatar="👤"):
            st.markdown(query)

        with st.chat_message("assistant", avatar="⚡"):
            with st.spinner("Searching semantic vectors and synthesizing answer..."):
                response = chat_with_documents(
                    query=query,
                    token=st.session_state.token,
                    api_base_url=API_BASE_URL,
                )

            if response.status_code == 200:
                payload = response.json()
                st.markdown(payload["answer"])
                if payload.get("sources"):
                    with st.expander(
                        f"📚 Retrieved Citations ({len(payload['sources'])} chunks)",
                        expanded=True,
                    ):
                        for idx, source in enumerate(payload["sources"], start=1):
                            score = source.get("score", 0.0)
                            st.markdown(
                                f"""
                                <div class="source-card">
                                    <div class="source-header">
                                        <span>📄 {idx}. {source['filename']}</span>
                                        <span class="score-pill">Match: {score:.4f}</span>
                                    </div>
                                    <div class="source-text">{source['text']}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                if payload.get("trace_url"):
                    st.caption(f"⚡ [View Langfuse Trace]({payload['trace_url']})")
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": payload["answer"],
                        "sources": payload.get("sources", []),
                        "trace_url": payload.get("trace_url"),
                    }
                )
            else:
                try:
                    detail = response.json().get("detail", "Chat failed")
                except Exception:
                    detail = "Chat failed"
                st.error(detail)


def render_search_tab():
    st.markdown("### 🔍 Semantic Retrieval Inspector")
    st.caption("Inspect raw vector similarity chunks without LLM synthesis")

    with st.form("search_form"):
        col_q, col_btn = st.columns([4, 1])
        with col_q:
            query = st.text_input(
                "Similarity query",
                placeholder="Search for phrases, topics, or entities...",
                label_visibility="collapsed",
            )
        with col_btn:
            submit = st.form_submit_button("Search Vectors", use_container_width=True)

        if submit and query.strip():
            with st.spinner("Executing similarity search in Qdrant..."):
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
        st.markdown(
            f"**Found {len(st.session_state.last_search_results)} matching chunks:**"
        )
        for idx, result in enumerate(st.session_state.last_search_results, start=1):
            score = result.get("score", 0.0)
            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-header">
                        <span>📄 {idx}. {result['filename']}</span>
                        <span class="score-pill">Relevance: {score:.4f}</span>
                    </div>
                    <div class="source-text">{result['text']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info(
            "Enter a query above to inspect the top matching chunks returned by Qdrant."
        )


def app():
    apply_custom_styles()
    initialize_state()

    if not st.session_state.token:
        login_page()
        return

    sidebar()

    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <span class="hero-title">RAG Intelligence Studio</span>
            <div class="hero-caption">Interact with uploaded documents using semantic vector search and grounded LLM answers</div>
            <div>
                <span class="feature-chip">⚡ Embeddings: all-MiniLM-L6-v2</span>
                <span class="feature-chip">📦 Vector DB: Qdrant</span>
                <span class="feature-chip">☁️ Storage: Azure Blob</span>
                <span class="feature-chip">🔭 Observability: Langfuse</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chat_tab, search_tab = st.tabs(["💬 Conversation", "🔍 Retrieval Inspector"])
    with chat_tab:
        render_chat_tab()
    with search_tab:
        render_search_tab()


if __name__ == "__main__":
    app()
