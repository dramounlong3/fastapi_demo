import json
from fastapi import FastAPI,Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from io import BytesIO
import pandas as pd

app = FastAPI()

templates = Jinja2Templates(directory="./src/templates")

@app.get('/')
async def my():
    return {'var1': 'hello world!'}

@app.get('/test')
async def test(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "var1": {"text": "SOME INFO. FROM SERVER"}})

@app.post('/upload', response_class=HTMLResponse)
async def upload_excel(request: Request, 
                       upload_excel: UploadFile = File(...), 
                       username: str = Form(...), 
                       password: str = Form(...)):

    if upload_excel.filename.endswith(".xlsx"):
        excel_content = await upload_excel.read()

        excel_buffer = BytesIO(excel_content)

        df = pd.read_excel(excel_buffer)

        print(df)
        
        # json_data = df.to_json(orient="records")
        json_data = json.dumps({"response": "ok", "username":username, "password": password})
    return json_data