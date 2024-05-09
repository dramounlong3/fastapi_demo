import json
from fastapi import FastAPI, HTTPException,Request, File, UploadFile, Form, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from io import BytesIO
import pandas as pd
import os
from dotenv import load_dotenv
import socket
from starlette.staticfiles import StaticFiles

load_dotenv()

hostname = socket.gethostname()
print(hostname)
sit_ip = os.getenv('SIT_SERVER')
uat_ip = os.getenv('UAT_SERVER')
prod_ip = os.getenv('PROD_SERVER')
print(sit_ip)
print(uat_ip)
print(prod_ip)



app = FastAPI()
app.mount("/static", StaticFiles(directory="./src/static"), name="static")
templates = Jinja2Templates(directory="./src/templates")

@app.get('/')
async def my():
    return {'var1': 'hello world!'}

@app.get('/test', status_code=status.HTTP_200_OK)
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
        
        print("before write")
        
        # 保存 Excel 文件到主机上的目录
        save_path = "/path/to/save/excel/"  # 将该路径修改为你想要保存的目录
        os.makedirs(save_path, exist_ok=True)
        
        excel_file_path = os.path.join(save_path, upload_excel.filename)
        with open(excel_file_path, "wb") as f:
            f.write(excel_content)

        print(df)
        print("excel_file_path", os.path)
        
        # json_data = df.to_json(orient="records")
        json_data = json.dumps({"response": "ok", "username":username, "password": password})
        # return json_data
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"status_code":400, "reason":"bad request", "jsss": json_data})
    else:
        raise HTTPException(status_code=400, detail="the file extension needs to be xlsx.")