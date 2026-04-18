import pytest
from playwright.sync_api import sync_playwright
import subprocess
import sys

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session", autouse=True)
def setup_test_users():
    subprocess.run([sys.executable, "manage.py", "shell", "-c", """
from django.contrib.auth.models import User
User.objects.filter(username='a11yuser').delete()
u = User.objects.create_user('a11yuser', 'a11y@test.com', 'Testpass@123')
print('a11yuser created')
"""], check=True)
    yield
    subprocess.run([sys.executable, "manage.py", "shell", "-c", """
from django.contrib.auth.models import User
User.objects.filter(username='a11yuser').delete()
print('a11yuser deleted')
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


def run_axe(page):
    """Inject axe-core and run accessibility checks"""
    page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js")
    results = page.evaluate("""
        async () => {
            const results = await axe.run();
            return {
                violations: results.violations.map(v => ({
                    id: v.id,
                    impact: v.impact,
                    description: v.description,
                    nodes: v.nodes.length
                }))
            };
        }
    """)
    return results


# ─────────────────────────────────────────────
#  ACCESSIBILITY TESTS
# ─────────────────────────────────────────────
def test_home_page_accessibility(page):
    """Home page should have no critical accessibility violations"""
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    results = run_axe(page)
    critical = [v for v in results['violations'] if v['impact'] == 'critical']
    print(f"\n✅ Home page - {len(results['violations'])} violations found")
    for v in results['violations']:
        print(f"  [{v['impact']}] {v['id']}: {v['description']} ({v['nodes']} nodes)")
    assert len(critical) == 0, f"Critical accessibility violations found: {critical}"


def test_login_page_accessibility(page):
    """Login page should have no critical accessibility violations"""
    page.goto(f"{BASE_URL}/login/")
    page.wait_for_load_state("networkidle")
    results = run_axe(page)
    critical = [v for v in results['violations'] if v['impact'] == 'critical']
    print(f"\n✅ Login page - {len(results['violations'])} violations found")
    for v in results['violations']:
        print(f"  [{v['impact']}] {v['id']}: {v['description']} ({v['nodes']} nodes)")
    assert len(critical) == 0, f"Critical accessibility violations found: {critical}"


def test_register_page_accessibility(page):
    """Register page should have no critical accessibility violations"""
    page.goto(f"{BASE_URL}/register/")
    page.wait_for_load_state("networkidle")
    results = run_axe(page)
    critical = [v for v in results['violations'] if v['impact'] == 'critical']
    print(f"\n✅ Register page - {len(results['violations'])} violations found")
    for v in results['violations']:
        print(f"  [{v['impact']}] {v['id']}: {v['description']} ({v['nodes']} nodes)")
    assert len(critical) == 0, f"Critical accessibility violations found: {critical}"


def test_dashboard_accessibility(page):
    """Dashboard should have no critical accessibility violations"""
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "a11yuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    results = run_axe(page)
    critical = [v for v in results['violations'] if v['impact'] == 'critical']
    print(f"\n✅ Dashboard - {len(results['violations'])} violations found")
    for v in results['violations']:
        print(f"  [{v['impact']}] {v['id']}: {v['description']} ({v['nodes']} nodes)")
    assert len(critical) == 0, f"Critical accessibility violations found: {critical}"


def test_profile_page_accessibility(page):
    """Profile page should have no critical accessibility violations"""
    page.goto(f"{BASE_URL}/profile/a11yuser/")
    page.wait_for_load_state("networkidle")
    results = run_axe(page)
    critical = [v for v in results['violations'] if v['impact'] == 'critical']
    print(f"\n✅ Profile page - {len(results['violations'])} violations found")
    for v in results['violations']:
        print(f"  [{v['impact']}] {v['id']}: {v['description']} ({v['nodes']} nodes)")
    assert len(critical) == 0, f"Critical accessibility violations found: {critical}"


def test_upload_page_accessibility(page):
    """Upload page should have no critical accessibility violations"""
    page.goto(f"{BASE_URL}/login/")
    page.fill("input[name='username']", "a11yuser")
    page.fill("input[name='password']", "Testpass@123")
    page.click("button[type='submit']")
    page.goto(f"{BASE_URL}/upload/")
    page.wait_for_load_state("networkidle")
    results = run_axe(page)
    critical = [v for v in results['violations'] if v['impact'] == 'critical']
    print(f"\n✅ Upload page - {len(results['violations'])} violations found")
    for v in results['violations']:
        print(f"  [{v['impact']}] {v['id']}: {v['description']} ({v['nodes']} nodes)")
    assert len(critical) == 0, f"Critical accessibility violations found: {critical}"