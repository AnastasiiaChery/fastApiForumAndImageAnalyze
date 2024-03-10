FROM python:3.10

# Обновление и установка python3-pip
RUN apt-get update && \
    apt-get install -y python3-pip

# Устанавливаем переменные среды
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Создаем миграцию базы данных
RUN mkdir -p /app/alembic
COPY ./alembic.ini /app/alembic.ini

# Копируем каталог Alembic
COPY ./alembic /app/alembic

# Копируем все файлы из текущего каталога в контейнер
COPY . /app

# Команда, которая будет выполнена при запуске контейнера
#CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
