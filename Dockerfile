FROM python:3.11-slim

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./app/locales /src/app/locales
COPY ./app /src/app
COPY ./alembic.ini /src/alembic.ini

RUN pybabel compile -d /src/app/locales -D messages

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]