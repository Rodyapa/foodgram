FROM python:3.10


RUN pip install --upgrade pip
COPY ./requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . /app
WORKDIR /app

COPY ./entrypoint.sh .
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
