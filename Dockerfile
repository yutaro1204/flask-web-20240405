FROM python:3.12.2-slim-bookworm
WORKDIR /app
COPY . /app
RUN apt update -y \
  && pip install --upgrade pip \
  && pip install -r requirements.txt
