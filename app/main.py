# FastAPI主程式

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.qa_service import QAService
import uvicorn
from contextlib import asynccontextmanager
import webbrowser
import threading
import time
import os
import mysql.connector
from dotenv import load_dotenv

# ✅ 載入 .env 並檢查必要變數
load_dotenv()

required_keys = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME", "OPENAI_API_KEY"]
for key in required_keys:
    if not os.getenv(key):
        raise ValueError(f"❌ 缺少環境變數：{key}，請確認 .env 檔案是否正確設定")

# ✅ 建立 db_config
db_config = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3307)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

agent_configs = [
    {"name": "default", "index_path": "faiss_index/default"},
    {"name": "finance", "index_path": "faiss_index/finance"},
    {"name": "medical", "index_path": "faiss_index/medical"},
    {"name": "legal", "index_path": "faiss_index/legal"},
    {"name": "tech", "index_path": "faiss_index/tech"}
]

# ✅ 全域 QAService（由 lifespan 初始化）
qa_service = None

# ✅ 等待 MySQL 啟動
def wait_for_mysql(config, retries=10, delay=2):
    for _ in range(retries):
        try:
            conn = mysql.connector.connect(**config)
            conn.close()
            return True
        except mysql.connector.Error as e:
            print(f"等待 MySQL 中... {e}")
            time.sleep(delay)
    raise RuntimeError("MySQL 連線失敗，請確認容器是否啟動完成")

# ✅ FastAPI lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    global qa_service
    wait_for_mysql(db_config)
    qa_service = QAService(db_config=db_config, agent_configs=agent_configs)
    yield
    qa_service.shutdown()

# ✅ 建立 FastAPI 應用
app = FastAPI(lifespan=lifespan)

# ✅ 掛載靜態檔案與模板
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ✅ CORS（若前端獨立部署則啟用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 首頁：載入 HTML
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ✅ 問答 API（接收 JSON）
class QuestionRequest(BaseModel):
    question: str
    agent_name: str

@app.post("/ask")
async def ask(request: QuestionRequest):
    answer = qa_service.process_question(request.question, request.agent_name)
    return {"question": request.question, "answer": answer}

# ✅ 啟動時自動開啟瀏覽器
def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # bash : docker-compose up -d -> docker ps -> docker logs -f nlp_mysql
    
    # threading.Thread(target=open_browser).start()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
