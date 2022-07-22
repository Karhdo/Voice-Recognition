FROM duyducdev/voice-recognition:latest
WORKDIR /app

COPY ./template ./template
COPY ./uploads ./uploads
COPY ./vietnamese_asr ./vietnamese_asr
COPY ./main.py .

RUN python3 ./vietnamese_asr/load_model.py
# COPY ./requirements.txt .

# RUN apt-get update
# RUN apt-get install libsndfile1 -y

# RUN pip3 install -r ./requirements.txt
# RUN pip install https://github.com/kpu/kenlm/archive/master.zip

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "15400"]
