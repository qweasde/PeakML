# PeakML

Инструментарий для игроков в **Mobile Legends: Bang Bang** (СНГ-сегмент).  
Мета-тирлист, гайды по ролям, анализ драфта, билды, турниры — всё в одном месте.

---

## Стек

| Слой | Технология |
|------|-----------|
| Backend | Django 5.1 + Django REST Framework 3.15 |
| База данных | PostgreSQL 16 (Docker) / SQLite (локально) |
| Кэш / брокер | Redis 7 |
| Фоновые задачи | Celery 5 + django-celery-beat |
| Аутентификация | django-allauth 65 (email + Google OAuth) |
| Frontend | Django Templates + Tailwind CSS v3 + Alpine.js + HTMX |
| Статика | WhiteNoise |
| Python | 3.11+ |

---

## Быстрый старт — локально (без Docker)

### 1. Клонирование и виртуальное окружение

```powershell
git clone <repo-url> mlsite
cd mlsite
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Зависимости

```powershell
pip install -r requirements.txt
```

### 3. Переменные окружения

Скопируй `.env.example` в `.env` и заполни:

```powershell
Copy-Item .env.example .env
```

Минимально необходимые поля:

```ini
DEBUG=True
SECRET_KEY=любая-длинная-строка-символов
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. CSS (Tailwind)

```powershell
npm install
npm run build:css
```

### 5. Миграции и начальные данные

```powershell
.\.venv\Scripts\python.exe manage.py migrate --settings=config.settings.local
.\.venv\Scripts\python.exe manage.py seed_meta --settings=config.settings.local
.\.venv\Scripts\python.exe manage.py seed_guides --settings=config.settings.local
```

### 6. Суперпользователь (для доступа в /admin/)

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser --settings=config.settings.local
```

### 7. Запуск сервера

```powershell
.\.venv\Scripts\python.exe manage.py runserver --settings=config.settings.local
```

Открой **http://127.0.0.1:8000/**

---

## Быстрый старт — Docker Compose

### 1. Переменные окружения

```powershell
Copy-Item .env.example .env
```

### 2. Запуск всех сервисов

```bash
docker-compose up --build -d
```

Поднимаются: `db` (PostgreSQL), `redis`, `web` (Django), `celery`, `celery-beat`.

### 3. Миграции и данные

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_meta
docker-compose exec web python manage.py seed_guides
docker-compose exec web python manage.py createsuperuser
```

Открой **http://localhost:8000/**

---

## Страницы приложения

| URL | Описание | Авторизация |
|-----|----------|-------------|
| `/` | Главная: hero-секция + топ S-тира текущего патча | — |
| `/meta/` | Мета-тирлист: все герои по тирам S/A/B/C с фильтрацией по роли и патчу | — |
| `/meta/?role=assassin` | Тирлист с фильтром по роли | — |
| `/meta/?patch=1.9.04` | Тирлист конкретного патча | — |
| `/meta/vote/<id>/` | HTMX-голосование за тир героя (POST) | Требуется |
| `/guide/` | Список серий гайдов и последние публикации | — |
| `/guide/<slug>/` | Детальная страница гайда (Markdown → HTML) | — |
| `/admin/` | Django Admin — управление всеми данными | Суперпользователь |
| `/accounts/login/` | Вход в аккаунт | — |
| `/accounts/signup/` | Регистрация | — |
| `/accounts/logout/` | Выход | — |
| `/accounts/password/reset/` | Сброс пароля | — |
| `/api/meta/heroes/` | REST API: список героев (JSON) | — |
| `/api/meta/tier-list/` | REST API: тирлист текущего патча (JSON) | — |

---

## Управляющие команды

### `seed_meta` — роли, герои, патч, тирлист

```powershell
# Засеять начальные данные
.\.venv\Scripts\python.exe manage.py seed_meta --settings=config.settings.local

# Очистить всё и засеять заново
.\.venv\Scripts\python.exe manage.py seed_meta --reset --settings=config.settings.local
```

Создаёт: **6 ролей**, патч **1.9.04**, **30 героев**, **26 тир-записей**.

---

### `seed_guides` — серии гайдов и словарь

```powershell
.\.venv\Scripts\python.exe manage.py seed_guides --settings=config.settings.local
```

Создаёт: **10 терминов словаря**, **2 серии**, **3 гайда**.

---

### Tailwind CSS

```powershell
# Собрать один раз
npm run build:css

# Следить за изменениями в разработке
npm run watch:css
```

---

## Структура проекта

```
mlsite/
├── apps/
│   ├── core/          # Кастомная модель User, главная страница
│   ├── meta/          # Тирлист: Hero, Role, Patch, TierEntry, HeroVote
│   ├── guide/         # Гайды: GuideSeries, Guide, GlossaryTerm
│   ├── draft/         # [в разработке] Анализатор драфта
│   ├── builds/        # [в разработке] Билды героев
│   ├── tournaments/   # [в разработке] Турнирный календарь
│   ├── heroes/        # [в разработке] Страницы героев (союзники/контры)
│   └── profile/       # [в разработке] Профиль игрока
│
├── config/
│   ├── settings/
│   │   ├── base.py    # Общие настройки
│   │   └── local.py   # Локальная разработка (SQLite, LocMemCache)
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── partials/      # navbar, footer, messages
│   ├── meta/          # tier_list.html + vote_buttons partial
│   ├── guide/         # index.html, detail.html
│   └── account/       # login, signup, logout, password reset (7 шт.)
│
├── static/
│   ├── src/input.css  # Исходник Tailwind + кастомные компоненты
│   └── css/main.css   # Скомпилированный CSS (не редактировать вручную)
│
├── docker-compose.yml
├── requirements.txt
├── package.json       # npm для Tailwind
├── tailwind.config.js
└── .env.example
```

---

## Переменные окружения

| Переменная | Описание | Пример |
|-----------|----------|--------|
| `SECRET_KEY` | Django secret key | `abc123...` (50+ символов) |
| `DEBUG` | Режим отладки | `True` / `False` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `localhost,127.0.0.1` |
| `POSTGRES_DB` | Имя базы данных | `mlsite` |
| `POSTGRES_USER` | Пользователь БД | `mlsite` |
| `POSTGRES_PASSWORD` | Пароль БД | `mlsite` |
| `POSTGRES_HOST` | Хост БД | `db` (Docker) / `localhost` |
| `POSTGRES_PORT` | Порт БД | `5432` |
| `REDIS_URL` | URL Redis | `redis://redis:6379/0` |
| `GOOGLE_CLIENT_ID` | Google OAuth (опционально) | `...apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth (опционально) | `...` |

> **Локальная разработка:** `config/settings/local.py` перекрывает базовые настройки — используется SQLite и in-memory кэш, PostgreSQL и Redis **не нужны**.

---

## Модели данных

### `apps.core`
- **User** — расширяет `AbstractUser`: поля `is_pro`, `pro_until`, `avatar`, `ml_server`

### `apps.meta`
- **Role** — роль героя (tank / fighter / assassin / mage / marksman / support)
- **Hero** — герой: имя, роль, специализация, изображение
- **Patch** — версия патча; только один может быть `is_current=True`
- **TierEntry** — позиция героя в тире конкретного патча (S/A/B/C), счётчики голосов
- **HeroVote** — голос пользователя за тир (up/down, по одному на запись)

### `apps.guide`
- **GuideSeries** — серия гайдов, привязана к роли
- **Guide** — гайд в формате Markdown, поле `published` для управления видимостью
- **GlossaryTerm** — термин словаря с определением и примером

---

## Roadmap

- [x] Мета-тирлист с голосованием (HTMX)
- [x] Гайды (Markdown-рендеринг)
- [x] Аутентификация (email + страницы в стиле сайта)
- [ ] **Анализатор драфта** — выбор состава, контрики, синергии
- [ ] **Билды героев** — предметные сборки с голосованием
- [ ] **Страницы героев** — статистика, союзники, контры, история по патчам
- [ ] **Турнирный календарь** — расписание и результаты
- [ ] **Профиль игрока** — трекер матчей (через ML API)
- [ ] **Google OAuth** — вход через аккаунт Google
- [ ] **PRO-подписка** — интеграция YooKassa
