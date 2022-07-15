from fastapi import FastAPI, Form, Request, File, UploadFile, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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

    return "Google Dịch là một công cụ dịch thuật trực tuyến do Google phát triển. Nó cung cấp giao diện trang web, ứng dụng trên thiết bị di động cho hệ điều hành Android và iOS và giao diện lập trình ứng dụng giúp nhà phát triển xây dựng tiện ích mở rộng trình duyệt web và ứng dụng phần mềm."