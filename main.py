from fastapi import FastAPI, Form, Request, File, UploadFile, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from vietnamese_asr.audio_to_text import inference
from vietnamese_asr.audio_to_text_api_gg import asr_gg

app = FastAPI()

app.mount("/template", StaticFiles(directory="./template"), name="static")
templates = Jinja2Templates(directory="./template")

@app.get('/')
def main(request: Request):
    return templates.TemplateResponse('main.html', {'request': request})

@app.post('/upload/audio', status_code=status.HTTP_200_OK)
async def predict(file: UploadFile = File(...)):
    file_location = f"./uploads/{file.filename}"
    contents = await file.read()
    with open(file_location, 'wb') as f:
        f.write(contents)
    
    greedy_output, beam_output = inference(file_location)
    data = {
        'greedy_output': greedy_output,
        'beam_output': beam_output
    }
    return JSONResponse(data)