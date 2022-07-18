FROM python:3.8

WORKDIR /app

COPY ./src .
COPY ./requirements.txt .

RUN apt-get update
RUN apt-get install libsndfile1 -y

RUN pip3 install -r ./requirements.txt
