from fastapi import FastAPI, Form, Request, File, UploadFile, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from vietnamese_asr.audio_to_text import inference, load_pretrained_model, get_large_audio_transcription
from vietnamese_asr.audio_to_text_api_gg import asr_gg
import os

app = FastAPI()

app.mount("/template", StaticFiles(directory="./template"), name="static")
templates = Jinja2Templates(directory="./template")

@app.get('/')
def main(request: Request):
    return templates.TemplateResponse('main.html', {'request': request})

# Load model
cache_dir = './vietnamese_asr/cache/'
processor, model, lm_file = load_pretrained_model(cache_dir)

@app.post('/upload/audio', status_code=status.HTTP_200_OK)
async def predict(file: UploadFile = File(...)):
    if not os.path.isdir("./uploads"):
        os.mkdir("./uploads")
    file_location = f"./uploads/{file.filename}"
    contents = await file.read()
    with open(file_location, 'wb') as f:
        f.write(contents)
    
    greedy_output, beam_output = get_large_audio_transcription(file_location, model, lm_file, processor)
    # greedy_output, beam_output = inference(file_location, model, lm_file, processor)

    # # Delete file audio after handle voice recognition
    # if os.path.exists(file_location):
    #     os.remove(file_location)
    # else:
    #     print("The file does not exist")

    data = {}
    if ( greedy_output and beam_output ):
        data = {
            'greedy_output': greedy_output,
            'beam_output': beam_output
        }
    return JSONResponse(data)