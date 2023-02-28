import http

import logging

import os

import time

import requests

import telegram

from dotenv import load_dotenv


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


def check_tokens():
    """Проверяет доступность переменных окружения.
       которые необходимы для работы программы.
    """
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


# Принимает на вход два параметра: экземпляр класса Bot
# и строку с текстом сообщения.
def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug('Сообщение успешно отправленно')
    except Exception as error:
        logging.error(error)


# В качестве параметра в функцию передается временная метка.
# В случае успешного запроса должна вернуть ответ API,
# приведя его из формата JSON к типам данных Python.
def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != http.HTTPStatus.OK:
            logging.error('Страница не доступна')
            raise http.exceptions.HTTPError()
        return response.json()
    except requests.exceptions.ConnectionError as error:
        logging.error(f'Ошибка подключения {error}')
    except requests.RequestException as error:
        logging.error(f'Ошибка запроса {error}')


# В качестве параметра функция получает ответ API,
# приведенный к типам данных Python.
def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if type(response) is not dict:
        raise TypeError('Ответ API не был преобразован в словарь')
    elif 'homeworks' not in response:
        raise KeyError('В ответе API нет ключа homeworks')
    elif type(response['homeworks']) is not list:
        raise TypeError('В ответе API домашней работы под ключом homeworkorks'
                        'данные приходят не в виде списка')
    elif response['homeworks'] == []:
        return {}
    return response.get('homeworks')[0]


# В качестве параметра функция получает только один элемент
# из списка домашних работ.В случае успеха, функция возвращает
# подготовленную для отправки в Telegram строку, содержащую один
# из вердиктов словаря HOMEWORK_VERDICTS
def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе.
       статус этой работы.
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


def main():
    """Основная логика работы бота.
       1. Сделать запрос к API.
       2. Проверить ответ.
       3. Если есть обновления — получить статус работы из обновления
       и отправить сообщение в Telegram.
       4. Подождать некоторое время и вернуться в пункт 1..
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
    timestamp = int(time.time())
    # timestamp = 1672133406

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if homework:
                message = parse_status(homework)
                send_message(bot, message)
            else:
                message = 'Нет домашней работы для проверки'
                send_message(bot, message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
