![Main workflow](https://github.com/NovaHFly/foodgram/actions/workflows/main.yml/badge.svg)

# Foodgram
https://food-novaprojects.ddns.net/

## Описание прокта
Foodgram - сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек технологий
- Python 3.9
- Django 3.2.16
- DRF 3.12.4
- DJoser 2
- PostgreSQL 13
- React 17

## Деплой проекта
1. Установить на сервер nginx
   - Настроить на сервере перенаправление всех запросов с нужного доменного имени на локальный порт 8010
   - Настроить максимальный размер для тела запроса - 10MB
   - Настроить SSL-шифрование
2. Установить на сервер docker
3. Форкнуть репозиторий
4. Настроить секреты для Actions:
   - Все переменные окружения
   - DOCKER_USERNAME - Имя пользователя на dockerhub
   - DOCKER_PASSWORD - Пароль аккаунта dockerhub
   - SSH_HOST - Адрес сервера (для ssh подключения)
   - SSH_KEY - Приватный ключ ssh
   - SSH_PASSPHRASE - Кодовое слово для ключа ssh
   - TG_TOKEN - токен бота телеграм, который будет присылать отчёты
   - TG_ID - Id пользователя в телеграм, кому нужно присылать отчёты об успешном деплое
5. Запустить Deploy workflow с вкладки Actions в репозитории

## Переменные окружения (.env)
- **POSTGRES_DB** - имя базы данных PostgreSQL
  - Значение по умолчанию - django
- **POSTGRES_USER** - имя пользователя PostgreSQL
  - Значение по умолчанию - django
- **POSTGRES_PASSWORD** - пароль для пользователя PostgreSQL
  - Значение по умолчанию - пустая строка
- **DB_HOST** - имя хоста сервера, на котором расположена бд
  - Значение по умолчанию - пустая строка
- **DB_PORT** - порт хоста базы данных
  - Значение по умолчанию - 5432
- **DJANGO_SECRET** - секретный ключ Django
  - Значение по умолчанию - случайный ключ
- **ALLOWED_HOSTS** - допустимые имена хостов для обращения к серверу, на котором расположен проект
  - Прописываются в строку через запятую без пробелов
  - Значение по умолчанию - "localhost,127.0.0.1"

## Автор
#### *Сергей Захаров @NovaHFly*
