import pytest
from playwright.sync_api import sync_playwright, expect
import subprocess
import sys
import os

BASE_URL = "http://127.0.0.1:8000"
SNAPSHOTS_DIR = "core/snapshots"


@pytest.fixture(scope="session", autouse=True)
def setup_visual_users():
    subprocess.run([sys.executable, "manage.py", "shell", "-c", """
from django.contrib.auth.models import User
User.objects.filter(username='visualuser').delete()
u = User.objects.create_user('visualuser', 'visual@test.com', 'Testpass@123')
print('visualuser created')
"""], check=True)
    yield
    subprocess.run([sys.executable, "manage.py", "shell", "-c", """
from django.contrib.auth.models import User
User.objects.filter(username='visualuser').delete()
print('visualuser deleted')
"""], check=True)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    yield page
    page.close()


def take_screenshot(page, name):
    """Take screenshot and save to snapshots directory"""
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
    path = f"{SNAPSHOTS_DIR}/{name}.png"
    page.screenshot(path=path, full_page=True)
    return path


def compare_screenshots(page, name):
    """
    Take screenshot and compare with baseline.
    First run creates baseline, subsequent runs compare.
    """
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
    baseline_path = f"{SNAPSHOTS_DIR}/{name}_baseline.png"
    current_path = f"{SNAPSHOTS_DIR}/{name}_current.png"

    page.screenshot(path=current_path, full_page=True)

    if not os.path.exists(baseline_path):
        # First run — save as baseline
        page.screenshot(path=baseline_path, full_page=True)
        print(f"\n📸 Baseline created: {baseline_path}")
        return True

    # Compare file sizes as basic check
    baseline_size = os.path.getsize(baseline_path)
    current_size = os.path.getsize(current_path)
    diff_percent = abs(baseline_size - current_size) / baseline_size * 100

    print(f"\n📸 {name}: baseline={baseline_size}bytes, current={current_size}bytes, diff={diff_percent:.1f}%")
    return diff_percent < 10  # Allow 10% difference


# ─────────────────────────────────────────────
#  VISUAL REGRESSION TESTS
# ─────────────────────────────────────────────
def test_visual_home_page(page):
    """Home page visual regression"""
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    result = compare_screenshots(page, "home_page")
    assert result, "Home page visual regression detected!"

def test_visual_login_page(page):
    """Login page visual regression"""
    page.goto(f"{BASE_URL}/login/")
    page.wait_for_load_state("networkidle")
    result = compare_screenshots(page, "login_page")
    assert result, "Login page visual regression detected!"

def test_visual_register_page(page):
    """Register page visual regression"""
    page.goto(f"{BASE_URL}/register/")
    page.wait_for_load_state("networkidle")
    result = compare_screenshots(page, "register_page")
    assert result, "Register page visual regression detected!"

def test_visual_dashboard(page):
    """Dashboard visual regression"""
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "visualuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    result = compare_screenshots(page, "dashboard")
    assert result, "Dashboard visual regression detected!"

def test_visual_profile_page(page):
    """Profile page visual regression"""
    page.goto(f"{BASE_URL}/profile/visualuser/")
    page.wait_for_load_state("networkidle")
    result = compare_screenshots(page, "profile_page")
    assert result, "Profile page visual regression detected!"

def test_visual_upload_page(page):
    """Upload page visual regression"""
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "visualuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    page.goto(f"{BASE_URL}/upload/")
    page.wait_for_load_state("networkidle")
    result = compare_screenshots(page, "upload_page")
    assert result, "Upload page visual regression detected!"

def test_visual_review_page(page):
    """Review queue visual regression"""
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "visualuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    page.goto(f"{BASE_URL}/review/")
    page.wait_for_load_state("networkidle")
    result = compare_screenshots(page, "review_page")
    assert result, "Review page visual regression detected!"