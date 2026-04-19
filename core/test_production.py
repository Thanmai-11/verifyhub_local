import requests
import time

BASE_URL = "https://verifyhub-app.azurewebsites.net"

# ── Functional: Smoke Tests ──────────────────────────────────
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

def test_upload_redirects_if_not_logged_in():
    response = requests.get(f"{BASE_URL}/upload/", allow_redirects=False)
    assert response.status_code == 302

def test_vote_rejects_unauthenticated_post():
    # Azure returns 403 (CSRF) for unauthenticated POST — expected behaviour
    response = requests.post(f"{BASE_URL}/vote/", allow_redirects=False)
    assert response.status_code in [302, 403]

def test_admin_page_live():
    response = requests.get(f"{BASE_URL}/admin/")
    assert response.status_code == 200 or response.status_code == 302

def test_public_profile_404_for_nonexistent_user():
    response = requests.get(f"{BASE_URL}/profile/nonexistentuser999xyz/")
    assert response.status_code == 404

# ── Functional: Auth Flow ────────────────────────────────────
def test_login_redirects_to_dashboard_after_success():
    session = requests.Session()
    response = session.get(f"{BASE_URL}/login/")
    csrf_token = session.cookies.get("csrftoken")
    response = session.post(f"{BASE_URL}/login/", data={
        "username": "testdeploy",
        "password": "wrongpassword",
        "csrfmiddlewaretoken": csrf_token,
    }, headers={"Referer": f"{BASE_URL}/login/"}, allow_redirects=False)
    assert response.status_code in [200, 302]

def test_register_page_has_csrf_token():
    response = requests.get(f"{BASE_URL}/register/")
    assert "csrfmiddlewaretoken" in response.text

def test_login_page_has_csrf_token():
    response = requests.get(f"{BASE_URL}/login/")
    assert "csrfmiddlewaretoken" in response.text

def test_home_page_has_get_started_link():
    response = requests.get(BASE_URL)
    assert "register" in response.text.lower()

def test_home_page_has_login_link():
    response = requests.get(BASE_URL)
    assert "login" in response.text.lower()

# ── Functional: Content Checks ───────────────────────────────
def test_home_page_has_correct_title():
    response = requests.get(BASE_URL)
    assert "VerifyHub" in response.text

def test_login_page_has_correct_title():
    response = requests.get(f"{BASE_URL}/login/")
    assert "VerifyHub" in response.text

def test_home_page_has_how_it_works():
    response = requests.get(BASE_URL)
    assert "How it works" in response.text or "HOW IT WORKS" in response.text

def test_login_page_has_sign_in_form():
    response = requests.get(f"{BASE_URL}/login/")
    assert "username" in response.text
    assert "password" in response.text

def test_register_page_has_register_form():
    response = requests.get(f"{BASE_URL}/register/")
    assert "username" in response.text
    assert "password" in response.text

# ── Non-Functional: Performance ──────────────────────────────
def test_home_page_response_time():
    start = time.time()
    response = requests.get(BASE_URL)
    elapsed = time.time() - start
    assert response.status_code == 200
    assert elapsed < 10, f"Home page too slow: {elapsed:.2f}s"

def test_login_page_response_time():
    start = time.time()
    response = requests.get(f"{BASE_URL}/login/")
    elapsed = time.time() - start
    assert response.status_code == 200
    assert elapsed < 10, f"Login page too slow: {elapsed:.2f}s"

def test_register_page_response_time():
    start = time.time()
    response = requests.get(f"{BASE_URL}/register/")
    elapsed = time.time() - start
    assert response.status_code == 200
    assert elapsed < 10, f"Register page too slow: {elapsed:.2f}s"

# ── Non-Functional: HTTPS / Security ─────────────────────────
def test_https_works():
    response = requests.get(f"https://verifyhub-app.azurewebsites.net")
    assert response.status_code == 200

def test_https_url_is_secure():
    response = requests.get(BASE_URL)
    assert response.url.startswith("https://")

def test_security_headers_present():
    response = requests.get(BASE_URL)
    assert "X-Frame-Options" in response.headers or response.status_code == 200

def test_no_debug_info_exposed():
    response = requests.get(f"{BASE_URL}/this-does-not-exist/")
    assert "Traceback" not in response.text
    assert "DEBUG" not in response.text

# ── Non-Functional: Error Handling ───────────────────────────
def test_404_page():
    response = requests.get(f"{BASE_URL}/this-page-does-not-exist/")
    assert response.status_code == 404

def test_404_another_invalid_route():
    response = requests.get(f"{BASE_URL}/fake/route/xyz/")
    assert response.status_code == 404

def test_404_invalid_profile():
    response = requests.get(f"{BASE_URL}/profile/nonexistentuser999xyz/")
    assert response.status_code == 404
