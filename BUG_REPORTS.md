# Баг-репорты

Все дефекты, найденные в процессе разработки и тестирования Kanban-доски.

## BUG-001: MissingGreenlet при сериализации assignee_email

**Окружение:** Chrome 120, Windows 10, staging
**Шаги:**
1. Войти как администратор.
2. Открыть доску с карточками, у которых назначен исполнитель.
3. Обновить страницу.

**Ожидаемый результат:** карточки отображаются с email исполнителя.
**Фактический результат:** 500 Internal Server Error, в логах `MissingGreenlet: greenlet_spawn has not been called`.

**Severity:** Major
**Priority:** High
**Статус:** Fixed
**Исправление:** добавлен `selectinload(Card.assignee)` в запросы карточек.

## BUG-002: BOM в alembic.ini ломает миграции

**Окружение:** Windows 10, Docker Desktop
**Шаги:**
1. Выполнить `docker compose exec backend alembic revision --autogenerate -m "initial"`.

**Ожидаемый результат:** создаётся файл миграции.
**Фактический результат:** `configparser.MissingSectionHeaderError: File contains no section headers`, в начале файла `\ufeff[alembic]`.

**Severity:** Major
**Priority:** High
**Статус:** Fixed
**Исправление:** перезапись `alembic.ini` без BOM через `[System.IO.File]::WriteAllText(..., UTF8Encoding($false))`.

## BUG-003: Несовместимость passlib и bcrypt ломает регистрацию

**Окружение:** Docker, Python 3.12
**Шаги:**
1. Отправить `POST /auth/register` с валидными данными.

**Ожидаемый результат:** 201 Created.
**Фактический результат:** 500 Internal Server Error, в логах `ValueError: password cannot be longer than 72 bytes`.

**Severity:** Critical
**Priority:** High
**Статус:** Fixed
**Исправление:** зафиксирована версия `bcrypt==4.0.1` в `requirements.txt`.

## BUG-004: npm ci падает из-за отсутствия package-lock.json

**Окружение:** GitHub Actions, ubuntu-latest, Node.js 20
**Шаги:**
1. Запушить изменения в main.
2. Открыть вкладку Actions.

**Ожидаемый результат:** job `frontend-build` проходит.
**Фактический результат:** `npm error code EUSAGE: The npm ci command can only install with an existing package-lock.json`.

**Severity:** Major
**Priority:** Medium
**Статус:** Fixed
**Исправление:** сгенерирован и закоммичен `frontend/package-lock.json`.

## BUG-005: import.meta.env не типизирован в vue-tsc

**Окружение:** GitHub Actions, ubuntu-latest
**Шаги:**
1. Запустить `npm run build` (vue-tsc && vite build).

**Ожидаемый результат:** сборка проходит.
**Фактический результат:** `src/api/client.ts(4,24): error TS2339: Property 'env' does not exist on type 'ImportMeta'`.

**Severity:** Major
**Priority:** Medium
**Статус:** Fixed
**Исправление:** создан `frontend/src/vite-env.d.ts` с `/// <reference types="vite/client" />` и интерфейсом `ImportMetaEnv`.

## BUG-006: WIP-лимит не отображается в UI

**Окружение:** Chrome 120, Windows 10, staging
**Шаги:**
1. Создать колонку с WIP-лимитом 2.
2. Добавить две карточки.

**Ожидаемый результат:** в шапке колонки отображается «Лимит 2/2», при превышении — красный бейдж.
**Фактический результат:** бейдж не отображается, лимит не виден.

**Severity:** Minor
**Priority:** Low
**Статус:** Fixed
**Исправление:** добавлен бейдж `Лимит X/Y` в `KanbanColumn.vue`, при достижении лимита — класс `wip-warn`.

## Сводка

| ID | Severity | Priority | Статус |
|----|----------|----------|--------|
| BUG-001 | Major | High | Fixed |
| BUG-002 | Major | High | Fixed |
| BUG-003 | Critical | High | Fixed |
| BUG-004 | Major | Medium | Fixed |
| BUG-005 | Major | Medium | Fixed |
| BUG-006 | Minor | Low | Fixed |

**Итого:** 6 багов, все исправлены. Критических (Critical) — 1, Major — 4, Minor — 1.
