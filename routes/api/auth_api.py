"""
認證 API 路由（RESTful）
"""
from flask import Blueprint, request, jsonify, make_response
from models.user_model import UserModel
from utils.jwt_utils import JWTManager

auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')


@auth_api_bp.route('/login', methods=['POST'])
def login():
    """
    用戶登入 API
    POST /api/auth/login
    Body: { "email": "user@example.com", "password": "password123" }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': '請提供 JSON 資料'
        }), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({
            'success': False,
            'message': '請提供 email 和 password'
        }), 400
    
    # 查找用戶
    user = UserModel.find_by_email_and_password(email, password)
    
    if user is None:
        return jsonify({
            'success': False,
            'message': '帳號或密碼錯誤'
        }), 401
    
    # 生成 JWT token
    token = JWTManager.generate_token(
        user_id=user['_id'],
        user_name=user['user_name'],
        user_type='user'
    )
    
    # 建立回應
    response = make_response(jsonify({
        'success': True,
        'message': '登入成功',
        'token': token,
        'user': {
            'id': str(user['_id']),
            'name': user['user_name'],
            'email': user['user_email']
        }
    }))
    
    # 設置 Cookie
    response.set_cookie(
        'access_token',
        token,
        max_age=7*24*60*60,  # 7天
        httponly=True,
        samesite='Lax'
    )
    
    return response


@auth_api_bp.route('/register', methods=['POST'])
def register():
    """
    用戶註冊 API
    POST /api/auth/register
    Body: { "name": "張三", "email": "user@example.com", "password": "password123" }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': '請提供 JSON 資料'
        }), 400
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({
            'success': False,
            'message': '請提供完整資料（name, email, password）'
        }), 400
    
    # 檢查 email 是否已存在
    existing_user = UserModel.find_by_email(email)
    if existing_user:
        return jsonify({
            'success': False,
            'message': '此 email 已被使用'
        }), 409
    
    # 建立新用戶
    try:
        result = UserModel.create(name, email, password)
        return jsonify({
            'success': True,
            'message': '註冊成功',
            'user_id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'註冊失敗: {str(e)}'
        }), 500


@auth_api_bp.route('/check-email', methods=['POST'])
def check_email():
    """
    檢查 email 是否已存在
    POST /api/auth/check-email
    Body: { "email": "user@example.com" }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'exists': False,
            'message': '請提供 JSON 資料'
        }), 400
    
    email = data.get('email')
    
    if not email:
        return jsonify({
            'exists': False,
            'message': '請提供 email'
        }), 400
    
    user = UserModel.find_by_email(email)
    
    return jsonify({
        'exists': user is not None
    })


@auth_api_bp.route('/logout', methods=['POST'])
def logout():
    """
    登出 API
    POST /api/auth/logout
    """
    response = make_response(jsonify({
        'success': True,
        'message': '登出成功'
    }))
    
    # 清除 Cookie
    response.set_cookie('access_token', '', max_age=0)
    
    return response


@auth_api_bp.route('/verify', methods=['GET'])
def verify_token():
    """
    驗證 token API
    GET /api/auth/verify
    """
    token = JWTManager.get_token_from_request()
    
    if not token:
        return jsonify({
            'valid': False,
            'message': '缺少 token'
        }), 401
    
    payload = JWTManager.verify_token(token)
    
    if not payload:
        return jsonify({
            'valid': False,
            'message': '無效或過期的 token'
        }), 401
    
    return jsonify({
        'valid': True,
        'user': {
            'id': payload.get('user_id'),
            'name': payload.get('user_name'),
            'type': payload.get('user_type')
        }
    })
