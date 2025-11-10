BookNoteProject - пет-проект в котором демонстрируются навыки работы с FastAPI, SQLAlchemy, Postgresql, Docker, Prometheus и др.

Это система работы с API на примере с книгами.

ИНСТРУКЦИЯ ПО ЗАПУСКУ ПРОЕКТА

pip install pipenv - окружение

pipenv shell - вход в окружение


Установка библиотек:

pip install fastapi==0.116.1

pip install uvicorn==0.35.0

pip install sqlalchemy==2.0.43

pip install asyncpg==0.30.0

pip install psycopg2-binary==2.9.10

pip install loguru==0.7.3

pip install "fastapi[standard]"

pip install passlib[bcrypt]

pip install python-jose

pip install prometheus_client

pip install bcrypt==4.0.0


Запуск контейнеров:

docker-compose up -d


Запуск проекта:

python start_up.py
