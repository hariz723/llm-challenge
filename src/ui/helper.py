import streamlit as st
import requests
from ..core.config import settings


def make_authenticated_request(endpoint, method="GET", data=None, files=None):
    """Make authenticated API request"""
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    url = f"{settings.API_BASE_URL}{endpoint}"

    if method == "POST":
        if files:
            response = requests.post(url, headers=headers, files=files, data=data)
        else:
            headers["Content-Type"] = "application/json"
            response = requests.post(url, headers=headers, json=data)
    else:
        response = requests.get(url, headers=headers)

    return response
