# ***Foodgram***
Проект Foodgram пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

___

## Разворачивание проекта локально
Склонируйте репозиторий к себе
```
git clone git@github.com:Ivanov-R/foodgram-project-react.git
```
Создайте и активируйте виртуальное окружение, установите в него зависимости:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
```
pip install -r ./backend/requirements.txt
```
Проект будет доступен по адресу http://127.0.0.1:8000/

## Разворачивание проекта на сервере
Склонируйте репозиторий к себе
```
git clone git@github.com:Ivanov-R/foodgram-project-react.git
```
Установите Docker и Docker-compose
Создайте .env файл (шаблон наполнения - ниже)
```
touch .env
```
Скопируйте директорию 'infra/' на ваш сервер:
```
scp -r infra/* <server user>@<server IP>:/home/<server user>/foodgram/
```
Перейдите в директорию infra/
```
cd infra/
```
Запустите docker-compose
```
sudo docker-compose up -d
```


## Шаблон наполнения .env
DEBUG=False

SECRET_KEY=<ваш ключ>

DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql

DB_NAME=postgres # имя базы данных

POSTGRES_USER=postgres # логин для подключения к базе данных

POSTGRES_PASSWORD=123 # пароль для подключения к БД (установите свой)

DB_HOST=db # название сервиса (контейнера)

DB_PORT=5432 # порт для подключения к БД

## Команды внутри контейнера
Команды внутри контейнеров выполняют посредством подкоманды docker-compose exec. 
Это эквивалент docker exec: с её помощью можно выполнять произвольные команды в сервисах внутри контейнеров.
```
docker-compose exec web python manage.py migrate # выполнить миграции
```
```
docker-compose exec web python manage.py createsuperuser # создать суперюзера
```
```
docker-compose exec web python manage.py collectstatic --no-input # собрать статику 
```

## Об авторе:
Иванов Роман, студент 37-й когорты Яндекс.Практикума
