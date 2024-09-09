# Проект Foodgram
Доменное имя проекта: foodgram.risetime.ru
## Назначение проекта:
Foodgram создан для публикации кулинарных блюд.
Авторизированные пользователи могу публиковать рецепты, подписываться на других
пользователей, добавлять рецепты в избранное, автоматические составлять и выгружать
список покупок в формате pdf.

## Деплой проекта:
Склонировать репозиторий на локальную машину:
```
git clone git@github.com:Rodyapa/foodgram.git
```
Для работы с удаленным сервером (на ubuntu):
Выполните вход на свой удаленный сервер
Установите docker на сервер:
```
sudo apt install docker.io 
```
Также установите docker-compose на сервер:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP
Скопируйте файлы docker-compose.yml и nginx.conf(конфигурации проекта для обратного прокси сервера на вашем сервере) из директории infra на сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
Cоздайте .env файл и впишите:
```
POSTGRES_DB=Название для БД 
POSTGRES_USER=Пользователь проекта для БД
POSTGRES_PASSWORD=Пароль пользователя БД
DB_HOST=db
DB_PORT=ПОРТ для БД (5432 - стандартный порт для PostgreSQL)
SECRET_DJANGO_KEY=Секретный ключ Джанго
HOSTING_IP=IP Хоста
HOSTING_DOMAIN= Доменное имя проекта
DEBUG_IS_ON=Включен ли дебаг или нет (False или True)
# При предоставлении последующих констант, при запуске проекта будет автоматически создан суперпользователь.
DEFAULT_SU_NAME= Имя для стандартного суперюзера
DEFAULT_SU_MAIL= Почта для стандартного суперюзера
DEFAULT_SU_PASSWORD= Пароль для стандартного суперюзера
```
Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:

```
# Необходимы для работы бекенда.
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>

#Необходимы для работы docker compose.
DOCKER_USERNAME=<имя пользователя DockerHub>
DOCKER_PASSWORD=<пароль от DockerHub>

SECRET_KEY=<секретный ключ проекта django>

HOST_USER=<username для подключения к серверу>
HOST=<IP сервера>
SSH_PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>
```
На сервере соберите docker-compose:
```
sudo docker-compose up -d --build
```

## Технологии:
    *Python 3.10
    *Django 5.0.6
    *Django REST framework 3.15
    *Nginx
    *Docker
    *Postgres
    *Poetry
https://github.com/Rodyapa
