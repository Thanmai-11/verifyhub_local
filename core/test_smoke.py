import pytest
from playwright.sync_api import sync_playwright, expect
import subprocess
import sys

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session", autouse=True)
def setup_smoke_users():
    subprocess.run([sys.executable, "manage.py", "shell", "-c", """
from django.contrib.auth.models import User
User.objects.filter(username='smokeuser').delete()
u = User.objects.create_user('smokeuser', 'smoke@test.com', 'Testpass@123')
print('smokeuser created')
"""], check=True)
    yield
    subprocess.run([sys.executable, "manage.py", "shell", "-c", """
from django.contrib.auth.models import User
User.objects.filter(username='smokeuser').delete()
print('smokeuser deleted')
"""], check=True)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


# ─────────────────────────────────────────────
#  SMOKE TESTS — critical path only
# ─────────────────────────────────────────────

def test_smoke_site_is_up(page):
    """Site loads and returns 200"""
    response = page.goto(BASE_URL)
    assert response.status == 200

def test_smoke_home_page_title(page):
    """Home page has correct title"""
    page.goto(BASE_URL)
    expect(page).to_have_title("VerifyHub — Home")

def test_smoke_login_page_loads(page):
    """Login page is accessible"""
    response = page.goto(f"{BASE_URL}/login/")
    assert response.status == 200

def test_smoke_register_page_loads(page):
    """Register page is accessible"""
    response = page.goto(f"{BASE_URL}/register/")
    assert response.status == 200

def test_smoke_login_works(page):
    """User can login successfully"""
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "smokeuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/dashboard/")

def test_smoke_dashboard_loads(page):
    """Dashboard loads after login"""
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "smokeuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    expect(page.locator("text=Welcome back, smokeuser")).to_be_visible()

def test_smoke_logout_works(page):
    """User can logout"""
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "smokeuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    page.goto(f"{BASE_URL}/logout/")
    expect(page).to_have_url(f"{BASE_URL}/")

def test_smoke_protected_routes_redirect(page):
    """Protected pages redirect to login"""
    page.goto(f"{BASE_URL}/dashboard/")
    assert "/login/" in page.url

def test_smoke_profile_page_loads(page):
    """Public profile page loads"""
    response = page.goto(f"{BASE_URL}/profile/smokeuser/")
    assert response.status == 200

def test_smoke_404_works(page):
    """Non-existent pages return 404"""
    response = page.goto(f"{BASE_URL}/profile/nonexistentuser999/")
    assert response.status == 404
def test_smoke_nav_brand_visible(page):
    """VerifyHub brand is visible on all pages"""
    for url in ['/', '/login/', '/register/']:
        page.goto(f"{BASE_URL}{url}")
        expect(page.locator(".nav-brand")).to_be_visible()