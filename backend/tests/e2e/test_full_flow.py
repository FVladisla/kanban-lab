
import os
import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://backend:8000")
FRONTEND_URL = os.getenv("E2E_FRONTEND_URL", "http://localhost:5173")

# Уникальный email на каждый прогон, чтобы не ловить 409
import time
UNIQUE = str(int(time.time()))
ADMIN_EMAIL = f"e2e_admin_{UNIQUE}@example.com"
DEV_EMAIL = f"e2e_dev_{UNIQUE}@example.com"
PASSWORD = "password123"


@pytest.fixture(scope="session")
def admin_token():
    """Регистрирует админа через API и возвращает токен."""
    import httpx
    r = httpx.post(
        f"{BASE_URL}/auth/register",
        json={"email": ADMIN_EMAIL, "password": PASSWORD, "role": "admin"},
        timeout=10,
    )
    assert r.status_code == 201, r.text
    login = httpx.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": PASSWORD},
        timeout=10,
    )
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def test_health(page: Page):
    """Проверяем, что backend жив."""
    page.goto(f"{BASE_URL}/health")
    expect(page.locator("body")).to_contain_text("ok")


def test_register_and_login_ui(page: Page):
    page.goto(f"{FRONTEND_URL}/register", wait_until="networkidle")
    page.wait_for_selector("form, .auth-card", timeout=15000)
    page.fill('input[type="email"], input[placeholder*="mail" i]', DEV_EMAIL)
    page.fill('input[type="password"]', PASSWORD)
    page.select_option("select", "developer")
    page.click('button:has-text("Зарегистрироваться")')
    page.screenshot(path="/tmp/e2e_register_debug.png", full_page=True)
    print(f"DEBUG URL after register: {page.url}")
    page.wait_for_selector('button:has-text("Создать проект"), h1:has-text("Проекты")', timeout=15000)


def test_full_kanban_flow(page: Page, admin_token: str):
    page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
    page.wait_for_selector("form, .auth-card", timeout=15000)
    page.fill('input[type="email"], input[placeholder*="mail" i]', ADMIN_EMAIL)
    page.fill('input[type="password"]', PASSWORD)
    page.click('button:has-text("Войти")')
    page.screenshot(path="/tmp/e2e_login_debug.png", full_page=True)
    print(f"DEBUG URL after login: {page.url}")
    page.wait_for_selector('button:has-text("Создать проект"), h1:has-text("Проекты")', timeout=15000)

    page.click('button:has-text("Создать проект")')
    page.fill('input[placeholder*="азвание" i]', f"E2E Project {UNIQUE}")
    page.fill('textarea', "created by e2e")
    page.click('.create-form button:has-text("Создать")')
    page.wait_for_selector(".project-card")

    page.on("dialog", lambda d: d.accept(f"E2E Board {UNIQUE}"))
    page.click('.board-add-btn')
    page.wait_for_selector(".board-chip")
    page.click(".board-chip")
    page.wait_for_url(f"{FRONTEND_URL}/boards/*")

    page.fill('input[placeholder*="азвание" i]', "To Do")
    page.click('.add-column button:has-text("+ Добавить")')
    page.wait_for_selector(".kanban-column")

    page.click('.add-card-btn')
    page.fill('.add-card-form input', f"E2E Task {UNIQUE}")
    page.keyboard.press("Enter")
    page.wait_for_selector(".kanban-card")


def test_unauthorized_redirect(page: Page):
    page.goto(f"{FRONTEND_URL}/projects", wait_until="networkidle")
    page.wait_for_url(f"{FRONTEND_URL}/login", timeout=10000)