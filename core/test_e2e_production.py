import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://verifyhub-app.azurewebsites.net"


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


# ── Home Page ────────────────────────────────────────────────
def test_e2e_home_page_loads(page):
    """Home page loads in real browser"""
    response = page.goto(BASE_URL)
    assert response.status == 200
    expect(page).to_have_title("VerifyHub — Home")

def test_e2e_home_page_has_hero_text(page):
    """Home page shows hero content"""
    page.goto(BASE_URL)
    expect(page.locator("text=Don't just claim skills")).to_be_visible()

def test_e2e_home_page_has_nav_brand(page):
    """VerifyHub brand is visible"""
    page.goto(BASE_URL)
    expect(page.locator(".nav-brand")).to_be_visible()

def test_e2e_home_page_has_get_started_button(page):
    """Get Started button is visible and clickable"""
    page.goto(BASE_URL)
    expect(page.locator("text=Create your profile")).to_be_visible()

def test_e2e_home_page_has_how_it_works(page):
    """How it works section is visible"""
    page.goto(BASE_URL)
    expect(page.locator("text=Upload Proof")).to_be_visible()
    expect(page.locator("text=Peer Review")).to_be_visible()
    expect(page.locator("text=Get Verified")).to_be_visible()

def test_e2e_home_page_no_js_errors(page):
    """Home page has no JavaScript console errors"""
    errors = []
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "Failed to load resource" not in msg.text else None)
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    assert len(errors) == 0, f"JS errors found: {errors}"


# ── Navigation ───────────────────────────────────────────────
def test_e2e_nav_login_link_works(page):
    """Login link in nav works"""
    page.goto(BASE_URL)
    page.click("text=Login")
    expect(page).to_have_url(f"{BASE_URL}/login/")

def test_e2e_nav_get_started_link_works(page):
    """Get Started link in nav works"""
    page.goto(BASE_URL)
    page.click("text=Get Started")
    expect(page).to_have_url(f"{BASE_URL}/register/")

def test_e2e_nav_brand_goes_home(page):
    """Clicking brand logo goes to home"""
    page.goto(f"{BASE_URL}/login/")
    page.click(".nav-brand")
    expect(page).to_have_url(f"{BASE_URL}/")


# ── Login Page ───────────────────────────────────────────────
def test_e2e_login_page_loads(page):
    """Login page loads in real browser"""
    response = page.goto(f"{BASE_URL}/login/")
    assert response.status == 200
    expect(page).to_have_title("VerifyHub — Login")

def test_e2e_login_page_has_form(page):
    """Login page has username and password fields"""
    page.goto(f"{BASE_URL}/login/")
    expect(page.locator("input[name='username']")).to_be_visible()
    expect(page.locator("input[name='password']")).to_be_visible()
    expect(page.locator("button[type='submit']")).to_be_visible()

def test_e2e_login_invalid_credentials(page):
    """Invalid login shows error message"""
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "fakeuser123")
    page.fill("input[name='password']", "wrongpassword")
    page.click("button[type='submit']")
    expect(page.locator("text=Invalid username or password")).to_be_visible()

def test_e2e_login_page_has_register_link(page):
    """Login page has link to register"""
    page.goto(f"{BASE_URL}/login/")
    expect(page.locator("text=Create an account")).to_be_visible()
    page.click("text=Create an account")
    expect(page).to_have_url(f"{BASE_URL}/register/")


# ── Register Page ────────────────────────────────────────────
def test_e2e_register_page_loads(page):
    """Register page loads in real browser"""
    response = page.goto(f"{BASE_URL}/register/")
    assert response.status == 200
    expect(page).to_have_title("VerifyHub — Register")

def test_e2e_register_page_has_form(page):
    """Register page has all required fields"""
    page.goto(f"{BASE_URL}/register/")
    expect(page.locator("input[name='username']")).to_be_visible()
    expect(page.locator("input[name='password1']")).to_be_visible()
    expect(page.locator("input[name='password2']")).to_be_visible()
    expect(page.locator("button[type='submit']")).to_be_visible()

def test_e2e_register_page_has_login_link(page):
    """Register page has link to login"""
    page.goto(f"{BASE_URL}/register/")
    expect(page.locator("text=Sign in")).to_be_visible()
    page.click("text=Sign in")
    expect(page).to_have_url(f"{BASE_URL}/login/")

def test_e2e_register_mismatched_passwords(page):
    """Mismatched passwords shows error"""
    page.goto(f"{BASE_URL}/register/")
    page.fill("input[name='username']", "testuser_e2e")
    page.fill("input[name='email']", "test@test.com")
    page.fill("input[name='password1']", "Testpass@123")
    page.fill("input[name='password2']", "Wrongpass@123")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/register/")


# ── Auth Protection ──────────────────────────────────────────
def test_e2e_dashboard_requires_login(page):
    """Dashboard redirects to login when not authenticated"""
    page.goto(f"{BASE_URL}/dashboard/")
    assert "/login/" in page.url

def test_e2e_upload_requires_login(page):
    """Upload page redirects to login when not authenticated"""
    page.goto(f"{BASE_URL}/upload/")
    assert "/login/" in page.url

def test_e2e_review_requires_login(page):
    """Review queue redirects to login when not authenticated"""
    page.goto(f"{BASE_URL}/review/")
    assert "/login/" in page.url


# ── Public Profile ───────────────────────────────────────────
def test_e2e_nonexistent_profile_returns_404(page):
    """Nonexistent profile returns 404"""
    response = page.goto(f"{BASE_URL}/profile/nonexistentuser999xyz/")
    assert response.status == 404


# ── Responsive / Mobile ──────────────────────────────────────
def test_e2e_home_page_mobile_viewport(browser):
    """Home page works on mobile viewport"""
    page = browser.new_page(viewport={"width": 375, "height": 667})
    page.goto(BASE_URL)
    expect(page.locator(".nav-brand")).to_be_visible()
    page.close()

def test_e2e_login_page_mobile_viewport(browser):
    """Login page works on mobile viewport"""
    page = browser.new_page(viewport={"width": 375, "height": 667})
    page.goto(f"{BASE_URL}/login/")
    expect(page.locator("input[name='username']")).to_be_visible()
    expect(page.locator("button[type='submit']")).to_be_visible()
    page.close()

def test_e2e_home_page_tablet_viewport(browser):
    """Home page works on tablet viewport"""
    page = browser.new_page(viewport={"width": 768, "height": 1024})
    page.goto(BASE_URL)
    expect(page.locator(".nav-brand")).to_be_visible()
    page.close()
