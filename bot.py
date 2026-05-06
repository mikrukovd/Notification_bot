import argparse

import requests
from environs import Env
from telegram import Bot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Бот отправляет уведомления о проверке работ на DVMN в Telegram.')
    parser.add_argument('--chat_id', type=str, required=True, help='ID чата в Telegram')
    return parser.parse_args()


def get_settings() -> dict:
    env = Env()
    env.read_env()
    return {
        'bot_token': env.str('TG_BOT_TOKEN'),
        'dvmn_token': env.str('DVMN_TOKEN'),
    }


def format_attempt_message(attempt: dict) -> str:
    lesson_title = attempt['lesson_title']
    lesson_url = attempt['lesson_url']
    is_negative = attempt['is_negative']
    result = "не принято" if is_negative else "принято"
    return (
        f'Преподаватель проверил работу "{lesson_title}".\n\n'
        f'Результат: {result}\n'
        f'Ссылка на урок: {lesson_url}'
    )


def handle_found_response(task_details: dict, chat_id: str, bot: Bot) -> str:
    new_timestamp = task_details['last_attempt_timestamp']
    attempts = task_details.get('new_attempts', [])
    for attempt in attempts:
        text = format_attempt_message(attempt)
        bot.send_message(chat_id=chat_id, text=text)
    return new_timestamp


def handle_timeout_response(task_details: dict) -> str:
    return task_details['timestamp_to_request']


def run_long_polling(bot: Bot, chat_id: str, headers: dict) -> None:
    url = 'https://dvmn.org/api/long_polling/'
    timestamp = None
    while True:
        params = {}
        if timestamp is not None:
            params['timestamp'] = timestamp
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=90)
            resp.raise_for_status()
            task_details = resp.json()

            if task_details['status'] == 'found':
                timestamp = handle_found_response(task_details, chat_id, bot)
            elif task_details['status'] == 'timeout':
                timestamp = handle_timeout_response(task_details)
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            continue


def main():
    args = parse_args()
    settings = get_settings()
    bot = Bot(token=settings['bot_token'])
    headers = {'Authorization': f'Token {settings["dvmn_token"]}'}
    run_long_polling(bot, args.chat_id, headers)


if __name__ == '__main__':
    main()