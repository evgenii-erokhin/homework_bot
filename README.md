# Статсус-чекер бот
### Описание:
Телеграм бот для проверки статуса работы после ревью в ЯП. Работает с API Яндекс Практикума.
Получить токен для работы с API **Яндекс Практикума** можно <a href="https://oauth.yandex.ru/authorize?
response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a.">тут</a>

### Используемые технологии:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
<img src="https://img.shields.io/badge/Python_Telegram_Bot-blue?style=for-the-badge&logo=python telegram bot&logoColor=green"/>
![PythonAnywhere](https://img.shields.io/badge/pythonanywhere-%232F9FD7.svg?style=for-the-badge&logo=pythonanywhere&logoColor=151515)
## Как запустить проект:
1. В корне проекта создать файл `.env` и заполнить его по шаблону
```
PRACTICUM_TOKEN=<Token от ЯП API> 
TELEGRAM_TOKEN=<Token Вашего Телеграм бота> 
TELEGRAM_CHAT_ID=<Ваш chat_id>
```
2. Находясь в корне проекта создать виртуальное окружение.
- Win:
  ```
  python -m venv venv
  ```
- Linux/MacOs:
  ```
  python3 -m venv venv
  ```
3. Активировать виртуальное окружение.
- Win:
  ```
  source venv/Scripts/activate
  ```
- Linux/MacOs:
  ```
  source venv/bib/activate
  ```
4. Установить завистимости.
```
pip install requirements.txt
```
5. Запустить файл `homework.py`
```
python homework.py
```
## Контакты:
**Евгений Ерохин**
<br>

<a href="https://t.me/juandart" target="_blank">
<img src=https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white />
</a>
<a href="mailto:evgeniierokhin@proton.me?">
<img src=https://img.shields.io/badge/ProtonMail-8B89CC?style=for-the-badge&logo=protonmail&logoColor=white />
</a>
