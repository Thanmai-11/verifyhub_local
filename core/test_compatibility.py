import pytest
from playwright.sync_api import sync_playwright, expect
import subprocess
import sys

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session", autouse=True)
def setup_compat_users():
    subprocess.run([sys.executable, "manage.py", "shell", "-c", """
from django.contrib.auth.models import User
User.objects.filter(username='compatuser').delete()
u = User.objects.create_user('compatuser', 'compat@test.com', 'Testpass@123')
print('compatuser created')
"""], check=True)
    yield
    subprocess.run([sys.executable, "manage.py", "shell", "-c", """
from django.contrib.auth.models import User
User.objects.filter(username='compatuser').delete()
print('compatuser deleted')
"""], check=True)


# ─────────────────────────────────────────────
#  RESPONSIVE / VIEWPORT TESTS
# ─────────────────────────────────────────────
@pytest.mark.parametrize("device,width,height", [
    ("Mobile S",  320,  568),
    ("Mobile M",  375,  667),
    ("Mobile L",  425,  812),
    ("Tablet",    768, 1024),
    ("Laptop",   1280,  800),
    ("Desktop",  1920, 1080),
])
def test_responsive_home_page(device, width, height):
    """Home page is responsive across different screen sizes"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(BASE_URL)
        expect(page.locator(".nav-brand")).to_be_visible()
        expect(page.locator("text=Don't just claim skills")).to_be_visible()
        browser.close()
        print(f"✅ {device} ({width}x{height}) — home page OK")


@pytest.mark.parametrize("device,width,height", [
    ("Mobile S",  320,  568),
    ("Mobile M",  375,  667),
    ("Tablet",    768, 1024),
    ("Laptop",   1280,  800),
    ("Desktop",  1920, 1080),
])
def test_responsive_login_page(device, width, height):
    """Login page is responsive across different screen sizes"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"{BASE_URL}/login/")
        expect(page.locator("input[name='username']")).to_be_visible()
        expect(page.locator("input[name='password']")).to_be_visible()
        browser.close()
        print(f"✅ {device} ({width}x{height}) — login page OK")


@pytest.mark.parametrize("device,width,height", [
    ("Mobile S",  320,  568),
    ("Mobile M",  375,  667),
    ("Tablet",    768, 1024),
    ("Laptop",   1280,  800),
    ("Desktop",  1920, 1080),
])
def test_responsive_register_page(device, width, height):
    """Register page is responsive across different screen sizes"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"{BASE_URL}/register/")
        expect(page.locator("input[name='username']")).to_be_visible()
        expect(page.locator("input[name='password1']")).to_be_visible()
        browser.close()
        print(f"✅ {device} ({width}x{height}) — register page OK")


@pytest.mark.parametrize("device,width,height", [
    ("Mobile S",  320,  568),
    ("Mobile M",  375,  667),
    ("Tablet",    768, 1024),
    ("Laptop",   1280,  800),
    ("Desktop",  1920, 1080),
])
def test_responsive_profile_page(device, width, height):
    """Profile page is responsive across different screen sizes"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"{BASE_URL}/profile/compatuser/")
        expect(page.locator(".nav-brand")).to_be_visible()
        browser.close()
        print(f"✅ {device} ({width}x{height}) — profile page OK")