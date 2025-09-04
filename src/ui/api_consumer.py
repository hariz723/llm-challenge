import requests


def login_user(username, password, api_base_url):
    """Sends a login request to the API."""
    response = requests.post(
    f"{api_base_url}/auth/api/login", json={"username": username, "password": password}
    )
    return response


def register_user(username, email, password, api_base_url):
    """Sends a registration request to the API."""
    response = requests.post(
        f"{api_base_url}/auth/api/register",
        json={"username": username, "email": email, "password": password},
    )
    return response
