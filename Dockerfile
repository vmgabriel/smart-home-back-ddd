FROM python:3.12-slim-bullseye
LABEL maintainer="smart.home.com"

ENV PYTHONUNBUFFERED 1

RUN apt-get update --fix-missing && apt-get --yes upgrade

RUN apt-get --yes install libpq5


RUN python3 -m pip install --upgrade pip

COPY requirements.txt /app/requirements.txt

RUN python3 -m pip install "psycopg[binary]"
RUN python3 -m pip install -r /app/requirements.txt

COPY main.py /app/main.py
COPY . /app

WORKDIR /app
EXPOSE 3030