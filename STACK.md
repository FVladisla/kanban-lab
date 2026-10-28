# Обоснование выбора стека

**Проект:** Kanban-доска (аналог Jira)
**Команда:** Владислав Ф.

## Выбранный стек

- Backend: Python 3.12 + FastAPI — автоматический Swagger (требование лабы), асинхронность, высокая производительность.
- ORM: SQLAlchemy 2.0 (async) — полный контроль над SQL, поддержка async, миграции через Alembic.
- БД: PostgreSQL 16 — реляционная, надёжная, поддержка JSONB для меток.
- Frontend: Vue 3 + TypeScript + Pinia — лёгкий старт, реактивность, vuedraggable для drag-and-drop.
- E2E: Playwright (Python) — кросс-браузерность (Chromium/Firefox/WebKit), встроен в pytest.
- Нагрузочные: Locust — сценарии на Python, distributed-режим для 1000+ пользователей.
- Безопасность: OWASP ZAP + pip-audit — стандарт DAST-сканирования + проверка зависимостей.
- CI/CD: GitHub Actions — простая интеграция с Docker, матрица браузеров для Playwright.

## Альтернативы, которые рассматривались

- Django — избыточен для API-центричного приложения; встроенная админка не нужна, а автоматический Swagger отсутствует (нужен drf-spectacular).
- Node.js + NestJS — меньше опыта у команды; TypeScript на бэкенде усложняет поддержку.
- React вместо Vue — сопоставим по возможностям, но Vue проще для быстрого старта.
- k6 / JMeter вместо Locust — Locust выбран из-за Python-сценариев (единый язык с бэкендом).

## Ограничения стека

- Производительность: FastAPI + asyncpg выдерживает ~100 RPS на локальной машине; для 1000 RPS нужна оптимизация (индексы, кэш Redis, горизонтальное масштабирование).
- Real-time: WebSocket не реализован (опционален в лабе); при необходимости — FastAPI WebSocket + Redis pub/sub.
- Мониторинг: Prometheus + Grafana не настроены (опционально).

## Критерии выбора

1. Опыт команды с Python и Vue.
2. Требование лабы: Swagger/OpenAPI — FastAPI даёт «из коробки».
3. Простота написания автотестов: pytest + httpx + Playwright — единый язык.
4. Поддержка в CI/CD: GitHub Actions + Docker Compose.
