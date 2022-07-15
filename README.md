# Voice Recognition

<!-- ABOUT THE PROJECT -->

## About The Project
- This project builds a website for voice recognition
- This project use a pretrained model of [nguyenvulebinh](https://huggingface.co/nguyenvulebinh/wav2vec2-base-vietnamese-250h)

## Build With
- HTML/CSS
- JQuery
- FastAPI

## Installation
1. Python: version over 3.8
2. Install required libraries in [requirement.txt](https://github.com/Karhdo/Voice-Recognition/blob/86ae116bba8478a737743b05015b479a79948fc0/requirements.txt)
```bash
# Example
pip install torch==1.8.0
```

## Run project
- Run below command, project will run at `http://127.0.0.1:8000`
```bash
uvicorn main:app --reload 
```
