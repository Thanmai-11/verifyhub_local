import requests

BASE_URL = "https://verifyhub-app.azurewebsites.net"

def test_home_page_live():
    response = requests.get(BASE_URL)
    assert response.status_code == 200

def test_login_page_live():
    response = requests.get(f"{BASE_URL}/login/")
    assert response.status_code == 200

def test_register_page_live():
    response = requests.get(f"{BASE_URL}/register/")
    assert response.status_code == 200

def test_dashboard_redirects_if_not_logged_in():
    response = requests.get(f"{BASE_URL}/dashboard/", allow_redirects=False)
    assert response.status_code == 302

def test_review_queue_redirects_if_not_logged_in():
    response = requests.get(f"{BASE_URL}/review/", allow_redirects=False)
    assert response.status_code == 302
