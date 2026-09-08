import requests


def login_user(username, password, api_base_url):
    """Sends a login request to the API."""
    response = requests.post(
        f"{api_base_url}/auth/api/login",
        json={"username": username, "password": password},
    )
    return response


def register_user(username, email, password, api_base_url):
    """Sends a registration request to the API."""
    response = requests.post(
        f"{api_base_url}/auth/api/register",
        json={"username": username, "email": email, "password": password},
    )
    return response


def upload_document(file_obj, token, api_base_url):
    """Uploads a document to the API."""
    return requests.post(
        f"{api_base_url}/documents/api/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (file_obj.name, file_obj.getvalue(), file_obj.type)},
        timeout=300,
    )


def search_documents(query, token, api_base_url):
    """Searches indexed document chunks."""
    return requests.post(
        f"{api_base_url}/documents/api/search",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"query": query},
        timeout=30,
    )


def chat_with_documents(query, token, api_base_url, top_k=5):
    """Asks a question against indexed document chunks."""
    return requests.post(
        f"{api_base_url}/documents/api/chat",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"query": query, "top_k": top_k},
        timeout=60,
    )
