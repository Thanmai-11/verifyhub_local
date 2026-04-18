import pytest
from playwright.sync_api import sync_playwright, expect
import django
from django.contrib.auth.models import User

BASE_URL = "http://127.0.0.1:8000"


# ─────────────────────────────────────────────
#  SETUP & TEARDOWN — runs once per session
# ─────────────────────────────────────────────
import subprocess
import sys

@pytest.fixture(scope="session", autouse=True)
def setup_test_users():
    """Create test users before all tests, delete after."""
    # Create users using management command
    subprocess.run([sys.executable, "manage.py", "shell", "-c", """
from django.contrib.auth.models import User
User.objects.filter(username__in=['playwrightuser', 'playwrightuser2']).delete()
u1, _ = User.objects.get_or_create(username='playwrightuser')
u1.set_password('Testpass@123')
u1.email = 'pw@test.com'
u1.save()
u2, _ = User.objects.get_or_create(username='playwrightuser2')
u2.set_password('Testpass@123')
u2.email = 'pw2@test.com'
u2.save()
print('Users created')
"""], check=True)

    yield  # tests run here

    # Cleanup after all tests
    subprocess.run([sys.executable, "manage.py", "shell", "-c", """
from django.contrib.auth.models import User
User.objects.filter(username__in=['playwrightuser', 'playwrightuser2', 'playwrightuser3']).delete()
print('Users deleted')
"""], check=True)

# ─────────────────────────────────────────────
#  BROWSER & PAGE FIXTURES
# ─────────────────────────────────────────────
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
#  HOME PAGE
# ─────────────────────────────────────────────
def test_home_page_loads(page):
    page.goto(BASE_URL)
    expect(page).to_have_title("VerifyHub — Home")
    expect(page.locator("text=Don't just claim skills")).to_be_visible()
    expect(page.locator("text=Create your profile")).to_be_visible()
    expect(page.locator("text=Sign in")).to_be_visible()

def test_home_page_has_how_it_works(page):
    page.goto(BASE_URL)
    expect(page.locator("text=HOW IT WORKS")).to_be_visible()
    expect(page.locator("text=Upload Proof")).to_be_visible()
    expect(page.locator("text=Peer Review")).to_be_visible()
    expect(page.locator("text=Get Verified")).to_be_visible()


# ─────────────────────────────────────────────
#  REGISTER
# ─────────────────────────────────────────────
def test_register_new_user(page):
    # Delete if exists from previous run
    subprocess.run([sys.executable, "manage.py", "shell", "-c",
        "from django.contrib.auth.models import User; User.objects.filter(username='playwrightuser3').delete()"
    ], check=True)

    page.goto(f"{BASE_URL}/register/")
    page.fill("input[name='username']", "playwrightuser3")
    page.fill("input[name='email']", "pw3@test.com")
    page.fill("input[name='password1']", "Testpass@123")
    page.fill("input[name='password2']", "Testpass@123")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/dashboard/")
    expect(page.locator("text=playwrightuser3")).to_be_visible()

    # Cleanup
    subprocess.run([sys.executable, "manage.py", "shell", "-c",
        "from django.contrib.auth.models import User; User.objects.filter(username='playwrightuser3').delete()"
    ], check=True)
    
def test_register_mismatched_passwords(page):
    page.goto(f"{BASE_URL}/register/")
    page.fill("input[name='username']", "baduser")
    page.fill("input[name='password1']", "Testpass@123")
    page.fill("input[name='password2']", "Wrongpass@123")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/register/")


# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────
def test_login_valid(page):
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "playwrightuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/dashboard/")

def test_login_invalid(page):
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "playwrightuser")
    page.fill("input[name='password']", "wrongpassword")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/login/")
    expect(page.locator("text=Invalid username or password")).to_be_visible()

def test_redirect_to_login_when_not_authenticated(page):
    page.goto(f"{BASE_URL}/dashboard/")
    expect(page).to_have_url(f"{BASE_URL}/login/?next=/dashboard/")


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────
def test_dashboard_shows_username(page):
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "playwrightuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    expect(page.locator("text=Welcome back, playwrightuser")).to_be_visible()

def test_dashboard_shows_no_submissions(page):
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "playwrightuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    expect(page.locator("text=No submissions yet")).to_be_visible()

def test_logged_in_home_shows_dashboard_button(page):
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "playwrightuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    page.goto(BASE_URL)
    expect(page.locator("text=Go to Dashboard")).to_be_visible()


# ─────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────
def test_logout_redirects_home(page):
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "playwrightuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    page.goto(f"{BASE_URL}/logout/")
    expect(page).to_have_url(f"{BASE_URL}/")
    expect(page.locator("text=Create your profile")).to_be_visible()


# ─────────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────────
def test_public_profile_accessible(page):
    page.goto(f"{BASE_URL}/profile/playwrightuser/")
    expect(page.locator("text=playwrightuser")).to_be_visible()
    expect(page.locator("text=SKILL RADAR")).to_be_visible()

def test_profile_shows_no_verified_skills(page):
    page.goto(f"{BASE_URL}/profile/playwrightuser/")
    expect(page.locator("text=No verified skills to display yet")).to_be_visible()


# ─────────────────────────────────────────────
#  NAVIGATION
# ─────────────────────────────────────────────
def test_nav_links_when_logged_out(page):
    page.goto(BASE_URL)
    expect(page.locator("text=Login")).to_be_visible()
    expect(page.locator("text=Get Started")).to_be_visible()

def test_nav_links_when_logged_in(page):
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "playwrightuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    nav = page.locator("#navMenu")
    expect(nav.get_by_role("link", name="Dashboard")).to_be_visible()
    expect(nav.get_by_role("link", name="Upload Proof")).to_be_visible()
    expect(nav.get_by_role("link", name="Review Queue")).to_be_visible()
    expect(nav.get_by_role("link", name="Profile")).to_be_visible()
    expect(nav.get_by_role("link", name="Sign out")).to_be_visible()


# ─────────────────────────────────────────────
#  UPLOAD PAGE
# ─────────────────────────────────────────────
def test_upload_page_loads(page):
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "playwrightuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    page.goto(f"{BASE_URL}/upload/")
    expect(page.locator("text=Submit a Skill Artifact")).to_be_visible()
    expect(page.get_by_text("Skill", exact=True)).to_be_visible()
    expect(page.get_by_text("Title", exact=True)).to_be_visible()
    expect(page.get_by_text("File", exact=True)).to_be_visible()

def test_upload_page_requires_login(page):
    page.goto(f"{BASE_URL}/upload/")
    expect(page).to_have_url(f"{BASE_URL}/login/?next=/upload/")


# ─────────────────────────────────────────────
#  REVIEW QUEUE
# ─────────────────────────────────────────────
def test_review_queue_requires_login(page):
    page.goto(f"{BASE_URL}/review/")
    expect(page).to_have_url(f"{BASE_URL}/login/?next=/review/")

def test_review_queue_empty_for_unverified_user(page):
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "playwrightuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    page.goto(f"{BASE_URL}/review/")
    expect(page.locator("text=Nothing to review")).to_be_visible()


# ─────────────────────────────────────────────
#  REGISTER PAGE UI
# ─────────────────────────────────────────────
def test_register_page_has_link_to_login(page):
    page.goto(f"{BASE_URL}/register/")
    expect(page.locator("text=Sign in")).to_be_visible()
    page.click("text=Sign in")
    expect(page).to_have_url(f"{BASE_URL}/login/")

def test_login_page_has_link_to_register(page):
    page.goto(f"{BASE_URL}/login/")
    expect(page.locator("text=Create an account")).to_be_visible()
    page.click("text=Create an account")
    expect(page).to_have_url(f"{BASE_URL}/register/")


# ─────────────────────────────────────────────
#  404 PAGE
# ─────────────────────────────────────────────
def test_nonexistent_profile_returns_404(page):
    response = page.goto(f"{BASE_URL}/profile/nonexistentuser123/")
    assert response.status == 404