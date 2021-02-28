# Dockerfile
FROM python:3.8.7-alpine3.12

COPY . .

RUN apt-get -y update && apt-get install -y htop tmux vim nginx
RUN pip install fastapi uvicorn
RUN pip install -r requirements.txt

