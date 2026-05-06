# Telegram бот для уведомлений Devman

Бот отправляет уведомления в Telegram о проверке работ на платформе Devman через API.

## Возможности

- Отслеживание статуса проверки работ через API Devman
- Уведомления в Telegram при получении результата
- Long polling для получения обновлений
- Обработка сетевых ошибок

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/mikrukovd/Notification_bot.git
cd notification_bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv .venv
```

3. Активируйте виртуальное окружение:

Windows:
```bash
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Конфигурация

1. Получите Telegram бот токен через BotFather
2. Получите Devman API токен на сайте dvmn.org
3. Найдите ваш Telegram `chat_id`
4. Создайте файл `.env` в корне проекта:

```env
TG_BOT_TOKEN=your_telegram_bot_token
DVMN_TOKEN=your_devman_api_token
CHAT_ID=your_telegram_chat_id
```

## Использование

Запустите бота:

```bash
python bot.py
```

Бот будет отправлять уведомления о проверке работ в указанный Telegram чат.

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).