import http
import logging
import os
import time
from json.decoder import JSONDecodeError

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot: telegram.Bot, message: str) -> None:
    """
    Отправляет сообщение в Telegram чат.

    Принимает на вход два параметра: экземпляр класса Bot
    и строку с текстом сообщения.
    """
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug('Сообщение успешно отправленно.')

    except telegram.error.TelegramError as error:
        logging.error(f'Не удалось отправть сообщение - {error}')


def get_api_answer(timestamp: int) -> dict:
    """
    Делает запрос к единственному эндпоинту API-сервиса.

    В качестве параметра в функцию передается временная метка.
    В случае успешного запроса должна вернуть ответ API,
    приведя его из формата JSON к типам данных Python.
    """
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != http.HTTPStatus.OK:
            raise exceptions.IncorrectStatusCode(
                f'Не коректный статус-код {response.status_code}'
            )
    except requests.exceptions.ConnectionError as error:
        raise exceptions.ConnectionFailed(f'Ошибка соединения -{error}')

    except requests.RequestException as error:
        raise exceptions.RequestFailed(f'Ошибка в запросе к API {error}')

    try:
        response = response.json()
    except JSONDecodeError as error:
        raise exceptions.CannotDecodJson(f'Не был декодирован json - {error} ')

    return response


def check_response(response: dict) -> list:
    """
    Проверяет ответ API на соответствие документации.

    В качестве параметра функция получает ответ API,
    приведенный к типам данных Python.
    """

    if not isinstance(response, dict):
        raise TypeError('Ответ API не был преобразован в словарь')

    if 'homeworks' in response and 'current_date' in response:
        homeworks = response['homeworks']
    else:
        raise KeyError('В ответе API нет ключей homeworks и current_date')

    if not isinstance(homeworks, list):
        raise TypeError('В ответе API домашней работы под ключом homeworkorks'
                        'данные приходят не в виде списка')

    return homeworks


def parse_status(homework: dict) -> str:
    """
    Извлекает статус домашней работы.

    В качестве параметра функция получает только один элемент
    из списка домашних работ.В случае успеха, функция возвращает
    подготовленную для отправки в Telegram строку, содержащую один
    из вердиктов словаря HOMEWORK_VERDICTS
    """
    if 'status' not in homework:
        raise KeyError('В homework отсутсвует ключ status')
    homework_status = homework.get('status')

    if 'homework_name' not in homework:
        raise KeyError('В homework отсутсвует ключ homework_name')

    homework_name = homework.get('homework_name')

    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError('Нет такого статуса')

    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """
    Основная логика работы бота.

    1.Сделать запрос к API.
    2.Проверить ответ.
    3.Если есть обновления — получить статус работы из обновления
    и отправить сообщение в Telegram.
    4.Подождать некоторое время и вернуться в пункт 1..
    """
    logging.basicConfig(
        level=logging.DEBUG,
        filename='main.log',
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
    )
    if check_tokens() is not True:
        logging.critical('Нет переменных окружения..')
        raise SystemExit

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    # timestamp = int(time.time())
    timestamp = 1672133406

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            timestamp = response.get('current_date')
            if homeworks:
                last_homework = homeworks[0]
                message = parse_status(last_homework)
                send_message(bot, message)
            else:
                message = 'Нет новых статусов о домашнем задании в ответе'
                logging.debug(message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.critical(message)
            send_message(bot, message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
