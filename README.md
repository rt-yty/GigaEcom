# Giga Agent API

Небольшой e-commerce backend на FastAPI с встроенным AI‑агентом (LangGraph + GigaChat), который может создавать, обновлять и удалять категории и товары через инструменты.

## Быстрый старт

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

## Запуск в Docker

```bash
docker build -t giga .
docker run --rm -p 8000:8000 --env-file .env giga
```

Сервис поднимется на `http://localhost:8000`, документация доступна на `/docs`.

## API

- `POST /categories/` — создать категорию
- `PATCH /categories/{id}` / `DELETE /categories/{id}` — мягкие обновления и удаление
- `POST /products/` и аналогичные эндпоинты для товаров
- `POST /chat` — обращение к агенту (использует GigaChat; нужен `GIGACHAT_TOKEN` в `.env`)

Все операции с категориями и товарами — мягкие удалений (поле `is_deleted`), поэтому записи можно восстановить вручную.
