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

my_server = os.getenv('MY_SERVER')
my_user = os.getenv('MY_USER')
my_password = os.getenv('MY_PASSWORD')



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
        
        # 保存 Excel 文件到主机上的目录
        save_path = "/path/to/save/excel/"  # 将该路径修改为你想要保存的目录
        os.makedirs(save_path, exist_ok=True)
        
        # excel_file_path = os.path.join(save_path, upload_excel.filename)
        # with open(excel_file_path, "wb") as f:
        #     f.write(excel_content)
        
        print(1)
        print("os.path.splitext(upload_excel.filename)[1]\n", os.path.splitext(upload_excel.filename)[1]) 
        print(2)
        
        try:
            save_path += f'{upload_excel.filename}'
            # 使用 DataFrame 的 to_excel() 方法將資料儲存到 Excel 檔案中
            df.to_excel(save_path, index=False)
        except Exception as e:
            print("進到valueError")
            print("e是啥:\n", str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        print(df)
        
        env_var = {
            "sit_ip": sit_ip,
            "uat_ip": uat_ip,
            "prod_ip": prod_ip
        }
        
        my_var = {
            "my_server": my_server,
            "my_user": my_user,
            "my_password": my_password
        }
        
        # json_data = df.to_json(orient="records")
        json_data = json.dumps({"response": "ok", "username":username, "password": password, "env_var": env_var, "my_var": my_var})
        # return json_data
        # raise HTTPException(status_code=status.HTTP_200_OK, detail={"status_code":200, "reason":"good request", "jsss": json_data})
        

        return  json_data
        
    else:
        raise HTTPException(status_code=400, detail="the file extension needs to be xlsx.")