# Система аутентификации и авторизации

Backend-приложение на FastAPI с собственной реализацией системы разграничения доступа (RBAC + ACL).

## Стек технологий

- Python 3.11+, FastAPI, SQLAlchemy (async) + asyncpg
- PostgreSQL 15, Alembic
- Pydantic v2, python-jose (JWT), passlib[bcrypt]
- Docker + docker-compose, Poetry

## Схема разграничения доступа

Система построена на комбинации RBAC (Role-Based Access Control) и ACL (Access Control List).

### Таблицы БД

| Таблица | Назначение |
|---|---|
| `users` | Пользователи системы |
| `roles` | Роли (admin, manager, viewer и т.д.) |
| `user_roles` | Связь пользователей и ролей (M2M) |
| `resources` | Ресурсы, к которым ограничивается доступ (orders, products, reports, users) |
| `permissions` | Разрешения: какая роль что может делать с каким ресурсом |

### Логика проверки доступа

1. Пользователь может иметь одну или несколько ролей (через `user_roles`)
2. Для каждой роли определены разрешения на ресурсы (через `permissions`)
3. При запросе к ресурсу система получает все роли пользователя, затем все разрешения этих ролей, и проверяет наличие `can_{action}=True` на запрашиваемый ресурс
4. Права суммируются по принципу OR: достаточно, чтобы хотя бы одна роль пользователя имела нужное право
5. `is_superuser=True` даёт полный доступ ко всем ресурсам без проверки прав

### Seed-данные

После применения миграций создаются:

**Роли:**
- `admin` — полный доступ (системная, нельзя удалить)
- `manager` — управление заказами и товарами
- `viewer` — чтение заказов, товаров и отчётов

**Ресурсы:** orders, products, reports, users

**Тестовый пользователь:** `admin@example.com` / `admin123` (is_superuser=True)

### JWT

Используется только access token (без refresh). Время жизни — 30 минут (настраивается через `ACCESS_TOKEN_EXPIRE_MINUTES` в `.env`).

Серверная blacklist-инвалидация токенов не реализована (для тестового задания избыточно). При необходимости добавляется таблица `token_blacklist` с проверкой при каждом запросе.

## API Endpoints

| Метод | Путь | Доступ | Описание |
|---|---|---|---|
| POST | /api/v1/auth/register | public | Регистрация |
| POST | /api/v1/auth/login | public | Вход → JWT |
| POST | /api/v1/auth/logout | любой auth | Выход (заглушка) |
| GET | /api/v1/users/me | любой auth | Профиль |
| PATCH | /api/v1/users/me | любой auth | Обновление профиля |
| DELETE | /api/v1/users/me | любой auth | Мягкое удаление |
| GET | /api/v1/admin/users | admin | Список пользователей |
| GET | /api/v1/admin/users/{id} | admin | Пользователь |
| PATCH | /api/v1/admin/users/{id} | admin | Изменить пользователя |
| DELETE | /api/v1/admin/users/{id} | admin | Удалить пользователя |
| GET | /api/v1/admin/roles | admin | Список ролей |
| POST | /api/v1/admin/roles | admin | Создать роль |
| PATCH | /api/v1/admin/roles/{id} | admin | Изменить роль |
| DELETE | /api/v1/admin/roles/{id} | admin | Удалить роль |
| POST | /api/v1/admin/users/{id}/roles | admin | Назначить роль |
| DELETE | /api/v1/admin/users/{id}/roles/{role_id} | admin | Отозвать роль |
| GET | /api/v1/admin/permissions | admin | Список разрешений |
| POST | /api/v1/admin/permissions | admin | Создать разрешение |
| PATCH | /api/v1/admin/permissions/{id} | admin | Изменить разрешение |
| DELETE | /api/v1/admin/permissions/{id} | admin | Удалить разрешение |
| GET | /api/v1/resources/{name} | зависит от прав | Mock: список |
| POST | /api/v1/resources/{name} | зависит от прав | Mock: создать |
| PATCH | /api/v1/resources/{name}/{id} | зависит от прав | Mock: обновить |
| DELETE | /api/v1/resources/{name}/{id} | зависит от прав | Mock: удалить |

## Быстрый старт

```bash
# Запуск
docker compose up --build

# Применение миграций (выполняется автоматически при старте)
docker compose exec app alembic upgrade head

# Тесты
docker compose exec app poetry run pytest tests/ -v
```

## Примеры запросов

```bash
# Регистрация
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123","password_confirm":"secret123"}'

# Логин
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Доступ к ресурсу (с токеном)
curl http://localhost:8000/api/v1/resources/orders \
  -H "Authorization: Bearer <token>"
```
