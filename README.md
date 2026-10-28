# Kanban-доска (аналог Jira)

Лабораторная работа по дисциплине «Поддержка и тестирование программных модулей».

## Стек

- Backend: Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL 16
- Frontend: Vue 3, TypeScript, Pinia, Vite, vuedraggable
- Тестирование: PyTest, httpx, Testcontainers, Playwright, Locust, OWASP ZAP
- CI/CD: GitHub Actions
- Инфраструктура: Docker, Docker Compose

## Быстрый старт

    git clone https://github.com/FVladisla/kanban-lab.git
    cd kanban-lab
    docker compose up --build

Открыть в браузере:

- Frontend: http://localhost:5173
- Swagger: http://localhost:8000/docs

Тестовый пользователь: admin@example.com / admin1234 (создаётся через /auth/register).

## Структура проекта

    kanban-lab/
    ├── backend/          # FastAPI + SQLAlchemy
    │   ├── app/          # исходный код
    │   ├── tests/        # unit, integration, e2e
    │   └── alembic/      # миграции
    ├── frontend/         # Vue 3 + TypeScript
    ├── .github/workflows/ci.yml
    ├── docker-compose.yml
    └── README.md

## API

Полная документация: http://localhost:8000/docs (Swagger UI).

Основные эндпоинты:

- POST /auth/register, POST /auth/login, GET /auth/me
- GET/POST /projects, GET/PATCH/DELETE /projects/{id}
- GET/POST /projects/{id}/boards
- GET/POST /boards/{id}/columns
- GET/POST /columns/{id}/cards, PATCH /cards/{id}/move
- GET /cards?search=&priority=&assignee_id=
- GET/POST /cards/{id}/comments, GET /cards/{id}/history

## Тестирование

    docker compose exec backend pytest tests/unit -v
    docker compose exec backend pytest tests/integration -v
    docker compose exec -e E2E_FRONTEND_URL=http://host.docker.internal:5173 backend pytest tests/e2e -v
    docker compose exec backend locust -f locustfile.py --host=http://backend:8000 --headless -u 100 -r 10 --run-time 1m
    docker run --rm -v "${PWD}:/zap/wrk/:rw" -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://host.docker.internal:8000 -r zap_report.html

## CI/CD

Пайплайн GitHub Actions (.github/workflows/ci.yml) запускается при пуше в main и выполняет:

1. Lint (flake8)
2. Unit-тесты + покрытие
3. Миграции Alembic
4. Интеграционные тесты
5. Сборку фронтенда

## Метрики

- Покрытие тестами: 75% (цель ≥80%)
- Unit-тестов: 15
- Интеграционных: 25
- E2E: 4
- Нагрузочный тест: 100 пользователей, 0 ошибок, RPS 32.4

## Лицензия

Учебный проект. MIT.