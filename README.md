# 💙 Chelsea Fan Bot

Telegram-бот для фанатов Chelsea FC — актуальные новости, расписание матчей и турнирная таблица АПЛ прямо в мессенджере.

---

## Возможности

- **Новости** — свежие материалы с Chelsea-тематикой
- **Следующие матчи** — ближайшие игры с датой, временем и турниром
- **Прошедшие матчи** — результаты последних встреч
- **Таблица АПЛ** — актуальная турнирная таблица с выделением позиции Chelsea

---

## Стек

| Технология | Назначение |
|---|---|
| [aiogram 3](https://docs.aiogram.dev/) | Telegram Bot Framework |
| [asyncpg](https://github.com/MagicStack/asyncpg) | Асинхронная работа с PostgreSQL |
| [httpx](https://www.python-httpx.org/) | Async HTTP-клиент для парсинга |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | HTML-парсинг |
| PostgreSQL | Хранение данных |
| Python 3.10+ | Язык разработки |

---

## Структура проекта

```
main.py             # Точка входа, обработчики команд бота
MSportParser.py     # Парсер данных (матчи, новости, таблица)
PostgreSQLData.py   # Работа с БД: создание таблиц, обновление и чтение данных
logger.py           # Настройка логирования (RotatingFileHandler)
.env                # Переменные окружения
logs.log            # Файл логов (генерируется автоматически)
```

---

## Установка и запуск

### 1. Клонируй репозиторий

```bash
git clone https://github.com/your-username/chelsea-telegram-bot.git
cd chelsea-telegram-bot
```

### 2. Установи зависимости

```bash
pip install -r requirements.txt
```

### 3. Создай файл `.env`

```env
TOKEN=your_telegram_bot_token

# PostgreSQL
USER=your_db_user
PASSWORD=your_db_password
DATABASE=your_db_name
HOST=localhost

# URLs для парсера
BASE_CALENDAR_URL=https://...
NEWS_URL=https://...
TABLE_URL=https://...
```

### 4. Заполни базу данных

Перед первым запуском бота нужно загрузить данные в БД:

```bash
python PostgreSQLData.py
```

### 5. Запусти бота

```bash
python main.py
```

---

## Обновление данных

Данные хранятся в PostgreSQL и не обновляются автоматически. Для регулярного обновления рекомендуется настроить cron-задачу:

```bash
# Обновление каждые 6 часов
0 */6 * * * /usr/bin/python3 /path/to/PostgreSQLData.py
```

---

## Логирование

Логи пишутся в файл `logs.log` с ротацией (максимум 5 МБ, 3 бэкапа). Уровень логирования — `INFO`.

---

## Схема БД

| Таблица | Поля |
|---|---|
| `news` | id, date, time, text |
| `next_games` | id, first_team, second_team, tournament_name, datetime, day_of_week |
| `prev_games` | id, first_team, second_team, tournament_name, datetime, day_of_week, result, score |
| `tournament_table_epl` | id, place, name, score |

---
