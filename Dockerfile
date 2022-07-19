FROM python:3.9.10
WORKDIR /app

COPY ./template ./template
COPY ./uploads ./uploads
COPY ./vietnamese_asr ./vietnamese_asr
COPY ./main.py .
COPY ./requirements.txt .

RUN apt-get update
RUN apt-get install libsndfile1 -y

RUN pip3 install -r ./requirements.txt
RUN pip install https://github.com/kpu/kenlm/archive/master.zip

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "15400"]
