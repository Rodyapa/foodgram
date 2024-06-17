# Проект Foodgram
Доменное имя проекта: foodgram.risetime.ru
IP-адрес проекта: 158.160.64.58
## Назначение проекта:
Foodgram создан для публикации кулинарных блюд.
Авторизированные пользователи могу публиковать рецепты, подписываться на других
пользователей, добавлять рецепты в избранное, автоматические составлять
список покупок в формате pdf.

## Деплой проекта:
    Склонировать репозиторий на локальную машину:
```
git clone git@github.com:Rodyapa/foodgram.git
```

Для работы с удаленным сервером (на ubuntu):

    *Выполните вход на свой удаленный сервер
    *Установите docker на сервер:
```
sudo apt install docker.io 
```
    *Установите docker-compose на сервер:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
    *Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP
    Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
    *Cоздайте .env файл и впишите:

```
POSTGRES_DB=Название для БД 
POSTGRES_USER=Пользователь проекта для БД
POSTGRES_PASSWORD=Пароль пользователя БД
DB_HOST=db
DB_PORT=ПОРТ для БД
SECRET_DJANGO_KEY=Секретный ключ Джанго
HOSTING_IP=IP Хоста
HOSTING_DOMAIN= Доменное имя проекта
LOCAL_IP= Локальный разрешенный адрес
LOCALDOMAIN=Локальный разрешенный домен
DEBUG_IS_ON=Включен ли дебаг или нет (False или True)
DEFAULT_SU_NAME= Имя для стандартного суперюзера
DEFAULT_SU_MAIL= Почта для стандартного суперюзера
DEFAULT_SU_PASSWORD= Пароль для стандартного суперюзера

```

Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:

DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>

DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя>

SECRET_KEY=<секретный ключ проекта django>

HOST_USER=<username для подключения к серверу>
HOST=<IP сервера>
SSH_PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

    *На сервере соберите docker-compose:
```
sudo docker-compose up -d --build
```

После успешной сборки на сервере выполните команды (только после первого деплоя):

    *Соберите статические файлы:
```
sudo docker-compose exec backend/foodgram python manage.py collectstatic --noinput
```
    *Примените миграции:

```
sudo docker-compose exec backend/foodgram python manage.py migrate --noinput
```

    *Создать суперпользователя Django:

```
sudo docker-compose exec backend python manage.py create_default_su
```
     Проект будет доступен по вашему IP


## Технологии:

    *Python 3.10
    *Django 5.0.6
    *Django REST framework 3.15
    *Nginx
    *Docker
    *Postgres

## Бекенд  от:
https://github.com/Rodyapa