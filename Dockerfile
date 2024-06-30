FROM python:3.12.4-slim-bullseye

RUN  mkdir /app

WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

