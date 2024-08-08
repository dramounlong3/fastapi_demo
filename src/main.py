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

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from apscheduler.triggers.interval import IntervalTrigger
from copy import deepcopy

from src.service import router as service_router
from loguru import logger
from src.another import svc
import sys
import src.config as gl

load_dotenv()


# 添加日志处理程序
logger.add(
    os.path.join("./log/", "fastapi_demo_{time:YYYY-MM-DD}.log"),  # 日志文件名包含日期
    rotation="00:00",  # 每天0:00轮转
    retention="7 day",  # 保留1天的日志
    compression="tar.gz",  # 压缩为 .tar.gz 格式
    level="DEBUG",  # 设置记录的最低日志级别
)

# # 将标准输出和标准错误重定向到同一个日志文件
# logger.add(sys.stdout, level="INFO", format="{message}")
# logger.add(sys.stderr, level="ERROR", format="{message}")

# logger.add(os.path.join("./log/", "fastapi_demo_{time:YYYY-MM-DD}.log"), level="INFO")  # 将标准输出记录到同一个文件
# logger.add(os.path.join("./log/", "fastapi_demo_{time:YYYY-MM-DD}.log"), level="ERROR")  # 将标准错误记录到同一个文件



hostname = socket.gethostname()
print(hostname)
sit_ip = os.getenv('SIT_SERVER')
uat_ip = os.getenv('UAT_SERVER')
prod_ip = os.getenv('PROD_SERVER')
print(sit_ip)
print(uat_ip)
print(prod_ip)

my_server = os.getenv('REPORT_SERVER', 'localhost')
my_user = os.getenv('DB_AD_ACCOUNT', 'sa')
secret_password = os.getenv('DB_PASSWORD', 'NmYzNjlkMWFmOTk2NTlmZDgxM2NiYTlmYTFmODkzM2E1MDI4ZjAyMTRjZDBlMDM2Y2IzOTMyZGRjNDNkNTI1NA==')
# print("my_server", my_server)
# print("my_user", my_user)
# print("my_password", my_password)

def testenv():
    with open('.env', 'r') as f:
        for line in f:
            print("YA: ", line.strip())
testenv()

print("current path: ", os.getcwd())

# 切換目錄
#os.chdir()

def encrypt_password(password, secret_key_hex):
    # Convert the hex string to bytes
    key = bytes.fromhex(secret_key_hex)
    
    # Generate a random IV (initialization vector)
    iv = os.urandom(16)
    
    # Pad the password to ensure it's a multiple of the block size (16 bytes for AES)
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(password.encode()) + padder.finalize()
    
    # Encrypt the padded password
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_password = encryptor.update(padded_data) + encryptor.finalize()
    
    # Combine IV and encrypted password and convert to hex string
    encrypted_data = iv + encrypted_password
    encrypted_hex = encrypted_data.hex()
    print("encrypted_hex", encrypted_hex)
    
    # Encode the hex string to base64
    encrypted_base64 = base64.b64encode(encrypted_hex.encode()).decode()
    print("encrypted_base64", encrypted_base64)
    
    return encrypted_base64

def decrypt_password(encrypted_hex, secret_key_hex):
    # Convert the hex string to bytes
    key = bytes.fromhex(secret_key_hex)
    
    # Decode the base64 string to hex string
    # k8s will decode base64 actively
    encrypted_hex = base64.b64decode(encrypted_hex).decode()
    
    # Convert the encrypted hex string back to bytes
    encrypted_data = bytes.fromhex(encrypted_hex)
    
    # Extract the IV and the encrypted password
    iv = encrypted_data[:16]
    encrypted_password = encrypted_data[16:]
    
    # Decrypt the password
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_password = decryptor.update(encrypted_password) + decryptor.finalize()
    
    # Unpad the password
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    password = unpadder.update(padded_password) + unpadder.finalize()
    
    return password.decode()



secret_key_hex = '55519d41df5220b2e6e544fb1ad863b6f010111b09ad9c7bae987f46380b685b'
# 取得密碼加密後轉16進制的base64字串
result_en_pwd = encrypt_password('19890729', secret_key_hex)
print("result_en_pwd", result_en_pwd)
# 測試的參數必須先手動解開base64
# final_result_pwd = decrypt_password(result_en_pwd, secret_key_hex)
# print("final_result_pwd", final_result_pwd)


# 清理過期檔案的函數
def period_job():
    print("Executing job at:", datetime.now())

# 設置排程器
scheduler = BackgroundScheduler()
# scheduler.add_job(period_job, 'cron', hour=2, minute=0)  # 每天凌晨2點執行
# scheduler.add_job(period_job, 'cron', minute='*') #每分鐘執行

# 使用 IntervalTrigger 每 30 秒运行一次任务
trigger = IntervalTrigger(minutes=600)
scheduler.add_job(period_job, trigger=trigger)



from contextlib import asynccontextmanager


@asynccontextmanager
async def mylifespan(app: FastAPI):
    # 啟動時執行一次
    if not scheduler.running:
        print("start job first time")
        scheduler.start()
    yield
    # 關閉時執行一次
    print("finish job last time")
    scheduler.shutdown()


#將lifespan傳入到FastAPI的參數
app = FastAPI(lifespan=mylifespan)
app.mount("/static", StaticFiles(directory="./src/static"), name="static")
templates = Jinja2Templates(directory="./src/templates")

app.include_router(service_router, prefix="/service")

@app.get('/')
async def my():
    return {'var1': 'hello world!'}

@app.get('/test', status_code=status.HTTP_200_OK)
async def test(request: Request):
    logger.info("logger.info in the test.")
    print("print in the test.")
    return templates.TemplateResponse("index.html", {"request": request, "var1": {"text": "SOME INFO. FROM SERVER"}})

@app.post('/upload', response_class=HTMLResponse)
async def upload_excel(request: Request, 
                       upload_excel: UploadFile = File(...), 
                       username: str = Form(...), 
                       password: str = Form(...)):
    gl._init()
    config = gl.get_value()
    
    if username == "abc":
        config["first_key"]["inner2"] = "aaa"
        gl.set_value(config)
        
    print("username", username)
    print("first_key", gl.get_value())
    svc()
    print("after first_key:", gl.get_value())

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
        
        secret_key_hex = '55519d41df5220b2e6e544fb1ad863b6f010111b09ad9c7bae987f46380b685b'
        
        # 解密secret拿回來的值
        decrypt_pwd = decrypt_password(secret_password, secret_key_hex)
        
        
        my_var = {
            "my_server": my_server,
            "my_user": my_user,
            "my_encrypt_password": secret_password,
            "my_password": decrypt_pwd
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
            # with pymssql.connect(server = my_var['my_server'], database = 'BI_Data_Alert', user = my_var['my_user'], password = my_var['my_password']) as conn:
            with pymssql.connect(server = 'localhost', database = 'BI_Data_Alert', user = my_var['my_user'], password = my_var['my_password']) as conn:
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
        logger.error("logger.error in the upload file.")
        raise HTTPException(status_code=400, detail="the file extension needs to be xlsx.")
    
    
    
    


# @app.on_event("startup")
# def on_startup():
#     # 確保應用啟動時排程器也一起啟動
#     if not scheduler.running:
#         print("start job first time")
#         scheduler.start()

# @app.on_event("shutdown")
# def on_shutdown():
#     # 確保應用關閉時排程器也一起關閉
#     print("finish job last time")
#     scheduler.shutdown()
    
    
    
    
