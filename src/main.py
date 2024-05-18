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
import pymssql

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
        
        # my_var = {
        #     "my_server": "172.21.176.1",
        #     "my_user": "sa",
        #     "my_password": "19890729"
        # }
        print("my_var['my_server']", my_var['my_server'])
        
        # test connect to DB.
        try:
            #使用windows認證登入
            # with pymssql.connect(host = 'TWTPESQLDV2', database = 'BI_ETL') as conn:
            #使用帳密登入
            with pymssql.connect(server = my_var['my_server'], database = 'BI_Data_Alert', user = my_var['my_user'], password = my_var['my_password']) as conn:
            # with pymssql.connect(host = "172.21.176.1", user = "sa", password = "19890729", database = "BI_Data_Alert") as conn:
                with conn.cursor() as cursor:
                    sql_query = '''
                        SELECT * FROM dbo.Project
                    '''
                    cursor.execute(sql_query)
                    # conn.commit() #使用insert才需要commit

                    #迭代撈取到的資料
                    rows = cursor.fetchall()
                    #轉成list
                    project_raw_data = [list(row) for row in rows]
        except Exception as e:
            print("Something error: ", str(e))
        
        # json_data = df.to_json(orient="records")
        json_data = json.dumps({
                "response": "ok",
                "username":username,
                "password": password,
                "env_var": env_var,
                "my_var": my_var,
                "project_raw_data": project_raw_data
            })
        # return json_data
        # raise HTTPException(status_code=status.HTTP_200_OK, detail={"status_code":200, "reason":"good request", "jsss": json_data})

        return  json_data
        
    else:
        raise HTTPException(status_code=400, detail="the file extension needs to be xlsx.")