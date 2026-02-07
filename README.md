# MADetect
113畢業專題

## 專案說明
這是一個使用 Flask 開發的醫療廣告檢測系統，整合 Google Gemini API 來分析廣告是否符合台灣醫療法規。

## 專案結構
```
MADetect/
├── app.py                 # 主應用程式入口
├── config.py              # 配置檔案
├── database.py            # 資料庫連接模組
├── routes/                # 路由模組（Blueprint）
│   ├── main.py           # 主頁路由
│   ├── auth.py            # 用戶認證路由（頁面）
│   ├── user.py            # 用戶功能路由
│   ├── admin.py           # 管理員路由
│   └── api/               # RESTful API 路由
│       └── auth_api.py    # 認證 API（JWT）
├── models/                # 資料模型層
│   ├── user_model.py      # 用戶資料操作
│   ├── admin_model.py     # 管理員資料操作
│   └── report_model.py    # 問題回報資料操作
├── utils/                 # 工具函數模組
│   ├── gemini_service.py  # Gemini API 服務
│   ├── text_utils.py      # 文字處理工具
│   ├── file_utils.py      # 檔案處理工具
│   └── jwt_utils.py       # JWT 認證工具
├── templates/             # HTML 模板
│   ├── base.html         # 基礎模板
│   ├── auth.html         # 統一認證頁面（登入/註冊/忘記密碼）
│   ├── home.html         # 用戶主頁
│   ├── components/        # 可重用組件
│   │   ├── sidebar.html  # 側邊欄
│   │   └── modals.html   # 模態框
│   └── *.html            # 其他頁面模板
├── static/               # 靜態檔案
│   ├── css/              # 樣式表
│   │   ├── auth.css      # 認證頁面樣式（統一）
│   │   ├── common.css    # 通用樣式
│   │   └── *.css         # 其他頁面樣式
│   ├── js/               # JavaScript 檔案
│   │   ├── auth.js       # 認證相關函數
│   │   ├── auth-forms.js # 認證表單處理
│   │   ├── home.js       # 主頁功能
│   │   └── modal-handlers.js # 模態框處理
│   ├── pic/              # 圖片
│   └── doc/              # 文件資料
└── requirements.txt       # Python 依賴套件
```

## 環境需求
- Python 3.7 或以上版本
- MongoDB 資料庫（本地端，預設 port 27017）

## 安裝步驟

### 1. 安裝並啟動 MongoDB（本地端）
#### macOS (使用 Homebrew):
```bash
# 安裝 MongoDB
brew tap mongodb/brew
brew install mongodb-community

# 啟動 MongoDB 服務
brew services start mongodb-community
```

#### 或使用 Docker:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 2. 安裝 Python 依賴套件
```bash
pip install -r requirements.txt
```

### 3. 設定環境變數（API Key）
為了安全起見，請使用環境變數來儲存敏感資訊（API Key）。

#### 方法一：使用 .env 檔案（推薦）
1. 在專案根目錄建立 `.env` 檔案：
```bash
# 前往 https://makersuite.google.com/app/apikey 取得您的 API Key
GEMINI_API_KEY=your-gemini-api-key-here

# Flask Secret Key（用於 JWT 加密）
FLASK_SECRET_KEY=your-secret-key-here
```

#### 方法二：直接在終端設定（臨時使用）
```bash
export GEMINI_API_KEY='your-gemini-api-key-here'
export FLASK_SECRET_KEY='your-secret-key-here'
```

## 啟動專案

### 方法一：直接執行
```bash
python3 app.py
```

### 方法二：使用 Flask 命令
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5001
```

## 訪問應用程式
啟動成功後，在瀏覽器開啟：
- 首頁：http://localhost:5001
- 會員登入：http://localhost:5001/login
- 管理員登入：http://localhost:5001/adminlogin

## API 端點（RESTful）

### 認證 API
- `POST /api/auth/login` - 用戶登入
- `POST /api/auth/admin/login` - 管理員登入
- `POST /api/auth/register` - 用戶註冊
- `POST /api/auth/check-email` - 檢查 email 是否存在
- `POST /api/auth/logout` - 登出
- `GET /api/auth/verify` - 驗證 token

### 用戶 API
- `POST /madetect` - 廣告檢測（需要 JWT 認證）
- `POST /report` - 問題回報（需要 JWT 認證）

**注意**：所有 API 請求需要在 Header 中包含 `Authorization: Bearer <token>`，或使用 Cookie 中的 `access_token`。

## 認證方式

本專案使用 **JWT (JSON Web Token)** 進行身份驗證：

1. **登入後**：系統會自動將 token 儲存在：
   - localStorage（前端使用）
   - Cookie（HttpOnly，後端使用）

2. **Token 有效期**：7 天

3. **自動重定向**：已登入用戶訪問 `/login` 或 `/signup` 會自動重定向到首頁

4. **Token 使用**：
   - API 請求：在 Header 中加入 `Authorization: Bearer <token>`
   - 頁面訪問：自動從 Cookie 讀取

## 前端架構優化

### 模板統一化
- **認證頁面**：使用統一的 `auth.html` 模板，通過參數區分登入/註冊/忘記密碼
- **基礎模板**：使用 `base.html` 作為所有頁面的基礎
- **組件化**：側邊欄和模態框提取為可重用組件

### CSS 統一化
- **auth.css**：統一的認證頁面樣式（取代多個獨立的 CSS 檔案）
- **common.css**：通用樣式和工具類

### JavaScript 模組化
- **auth.js**：認證相關函數（登入、註冊、token 管理等）
- **auth-forms.js**：表單處理邏輯
- **home.js**：主頁功能
- **modal-handlers.js**：模態框處理

## 注意事項
- 確保 MongoDB 本地服務已啟動（預設運行在 localhost:27017）
- 確保 Gemini API Key 有效且有足夠的額度
- **重要**：`.env` 檔案已加入 `.gitignore`，不會被提交到版本控制系統
- 預設運行在 port 5001，如被占用請修改 `config.py` 中的 PORT 設定
- MongoDB 資料庫名稱預設為 `madetect`，首次運行會自動建立
- 如果沒有設定環境變數，應用程式會提示錯誤並停止運行
- 所有 API 都使用 RESTful 風格，並需要 JWT 認證
