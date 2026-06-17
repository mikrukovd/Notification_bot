import time
import logging
import requests
from environs import Env
from telegram import Bot


class TelegramLogHandler(logging.Handler):
    def __init__(self, bot: Bot, chat_id: str):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        message = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=message[:4096])


def format_attempt_message(attempt: dict) -> str:
    lesson_title = attempt["lesson_title"]
    lesson_url = attempt["lesson_url"]
    is_negative = attempt["is_negative"]
    result = "не принято" if is_negative else "принято"
    return (
        f'Преподаватель проверил работу "{lesson_title}".\n\n'
        f"Результат: {result}\n"
        f"Ссылка на урок: {lesson_url}"
    )


def handle_found_response(task_details: dict, chat_id: str, bot: Bot) -> str:
    new_timestamp = task_details["last_attempt_timestamp"]
    attempts = task_details.get("new_attempts", [])
    for attempt in attempts:
        text = format_attempt_message(attempt)
        bot.send_message(chat_id=chat_id, text=text)
    return new_timestamp


def run_long_polling(bot: Bot, chat_id: str, token: str) -> None:
    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {token}"}
    timestamp = None
    while True:
        params = {}
        if timestamp is not None:
            params["timestamp"] = timestamp
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=90)
            resp.raise_for_status()
            task_details = resp.json()

            if task_details["status"] == "found":
                timestamp = handle_found_response(task_details, chat_id, bot)
            elif task_details["status"] == "timeout":
                timestamp = task_details["timestamp_to_request"]
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            continue


def main():
    env = Env()
    env.read_env()

    bot_token = env.str("TG_BOT_TOKEN")
    dvmn_token = env.str("DVMN_TOKEN")
    chat_id = env.str("CHAT_ID")

    bot = Bot(token=bot_token)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = TelegramLogHandler(bot, chat_id)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.info("Бот запущен")

    run_long_polling(bot, chat_id, dvmn_token)


if __name__ == "__main__":
    main()
