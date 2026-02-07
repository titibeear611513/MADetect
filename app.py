"""
MADetect 主應用程式
"""
from flask import Flask
from config import Config
from routes.main import main_bp
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.api.auth_api import auth_api_bp
from routes.api.project_api import project_api_bp

# 嘗試導入 CORS（如果已安裝）
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("警告: flask-cors 未安裝，CORS 功能將被禁用")


def create_app():
    """建立並配置 Flask 應用程式"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    
    # 啟用 CORS（如果可用）
    if CORS_AVAILABLE:
        CORS(app, supports_credentials=True)
    
    # 註冊 Blueprint
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_api_bp)  # RESTful API
    app.register_blueprint(project_api_bp)  # 專案管理 API
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
