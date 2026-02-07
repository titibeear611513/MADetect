"""
應用程式配置檔案
"""
import os
import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


class Config:
    """應用程式基本配置"""
    # Flask 配置
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'secret')
    
    # JWT 配置
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DELTA = datetime.timedelta(days=7)  # 7天過期
    
    # MongoDB 配置
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = 'madetect'
    
    # Gemini API 配置
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        raise ValueError(
            "請設定 GEMINI_API_KEY 環境變數。"
            "可以在 .env 檔案中設定，或使用 export GEMINI_API_KEY='your-api-key'"
        )
    
    # 法律文件路徑
    LAW_DOC_PATH = './static/doc/醫療法補充二.txt'
    
    # Flask 運行配置
    HOST = '0.0.0.0'
    PORT = 5001
    DEBUG = True
