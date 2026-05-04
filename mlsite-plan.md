# MLsite — план проекта

> ML (Mobile Legends: Bang Bang) companion сайт для игроков СНГ.  
> Без AI внутри продукта — всё на логике и данных.

---

## Название

Финалисты: PeakML

---

## Разделы сайта

| Этап | Роут | Описание |
|------|------|----------|
| 1 | `/meta` | Тир-лист героев по патчу, фильтр по роли, голосование |
| 1 | `/guide` | Гайды по ролям и механикам, текст + картинки, словарь |
| 2 | `/draft` | Оценщик 5 vs 5, контр-пики, сила состава |
| 3 | `/builds` | Билды с голосованием, сортировка по патч-версии |
| 4 | `/tournaments` | Календарь турниров, агрегатор Moonton + комьюнити |
| 5 | `/heroes/:id` | Страницы героев, SEO, союзники, матчапы, история |
| 6 | `/profile` | Трекер игрока по нику — парсинг, риск, делать последним |

---

## Стек

### Backend
- Django 5 + Django REST Framework
- PostgreSQL
- Redis — кэш + очередь задач
- Celery — фоновые задачи

### Frontend
- Django Templates
- Tailwind CSS
- Alpine.js — интерактив
- HTMX — AJAX без JS

### Авторизация
- django-allauth (email + Google OAuth)

### Оплата *(позже)*
- YooKassa — РФ карты, СБП

### Хостинг *(позже)*
- Selectel или Timeweb Cloud

---

## Структура проекта

```
mlsite/
├── apps/
│   ├── core/          — User, общее
│   ├── meta/          — тир-лист
│   ├── guide/         — гайды
│   ├── draft/         — оценщик драфта
│   ├── builds/        — билды
│   ├── tournaments/   — турниры
│   ├── heroes/        — страницы героев
│   └── profile/       — трекер (последний)
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── celery.py
├── templates/
│   ├── base.html
│   ├── meta/
│   ├── guide/
│   ├── draft/
│   └── ...
├── static/
│   ├── css/
│   ├── js/
│   ├── heroes/
│   └── items/
├── manage.py
├── requirements.txt
├── .env
├── Dockerfile
└── docker-compose.yml
```

### Структура одного app (пример: meta)

```
apps/meta/
├── models.py          — Hero, Patch, TierEntry
├── views.py
├── urls.py
├── serializers.py
├── admin.py
├── tasks.py
├── tests.py
└── migrations/
```

### Core app

```
apps/core/
├── models.py          — User (расширенный)
└── context_processors.py
```

---

## Монетизация *(позже)*

**Free** — базовый доступ ко всем разделам  
**Pro (~400–600 руб/мес):**
- история драфтов
- архив патчей
- алёрты на патчи
- про-билды от топ игроков
- заявки на турниры

---

## Контекст и заметки

- Разработчик играет в ML активно — знает игру изнутри
- Россия — Stripe недоступен, используем YooKassa
- Аудитория ML в СНГ большая, конкуренты с плохим UX
- `/profile` — последний этап, риск блокировки парсинга
- Подписка и оплата — добавить после запуска MVP

---

## Следующие шаги

- [ ] Выбрать название
- [ ] Инициализировать Django проект
- [ ] Настроить docker-compose (django + postgres + redis)
- [ ] Сделать модели для `meta` и `guide`
- [ ] Верстка base.html + Tailwind
- [ ] Запустить этап 1
