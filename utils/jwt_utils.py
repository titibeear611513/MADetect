"""
JWT 工具函數模組
"""
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from config import Config


class JWTManager:
    """JWT 管理類別"""
    
    @staticmethod
    def generate_token(user_id, user_name, user_type='user'):
        """
        生成 JWT token
        
        Args:
            user_id: 用戶 ID
            user_name: 用戶名稱
            user_type: 用戶類型 ('user' 或 'admin')
            
        Returns:
            JWT token 字串
        """
        payload = {
            'user_id': str(user_id),
            'user_name': user_name,
            'user_type': user_type,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),  # 7天過期
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            Config.SECRET_KEY,
            algorithm='HS256'
        )
        
        return token
    
    @staticmethod
    def verify_token(token):
        """
        驗證 JWT token
        
        Args:
            token: JWT token 字串
            
        Returns:
            如果有效，返回 payload 字典；如果無效，返回 None
        """
        try:
            payload = jwt.decode(
                token,
                Config.SECRET_KEY,
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def get_token_from_request():
        """
        從請求中獲取 token
        
        優先順序：
        1. Authorization header (Bearer token)
        2. Cookie
        3. Query parameter
        
        Returns:
            token 字串或 None
        """
        # 從 Authorization header 獲取
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
                return token
            except IndexError:
                pass
        
        # 從 Cookie 獲取
        token = request.cookies.get('access_token')
        if token:
            return token
        
        # 從 Query parameter 獲取
        token = request.args.get('token')
        if token:
            return token
        
        return None


def jwt_required(f):
    """
    JWT 驗證裝飾器（用於 API 路由）
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = JWTManager.get_token_from_request()
        
        if not token:
            return jsonify({
                'success': False,
                'message': '缺少認證 token'
            }), 401
        
        payload = JWTManager.verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'message': '無效或過期的 token'
            }), 401
        
        # 將用戶資訊添加到 request
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated


def jwt_required_page(f):
    """
    JWT 驗證裝飾器（用於頁面路由）
    如果未登入，重定向到登入頁面
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = JWTManager.get_token_from_request()
        
        if not token:
            from flask import redirect, url_for, make_response
            # 清除可能存在的無效 cookie
            response = make_response(redirect(url_for('auth.login_page')))
            response.set_cookie('access_token', '', max_age=0)
            return response
        
        payload = JWTManager.verify_token(token)
        
        if not payload:
            from flask import redirect, url_for, make_response
            # Token 無效，清除 cookie 並重定向
            response = make_response(redirect(url_for('auth.login_page')))
            response.set_cookie('access_token', '', max_age=0)
            return response
        
        # 將用戶資訊添加到 request
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    管理員驗證裝飾器
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = JWTManager.get_token_from_request()
        
        if not token:
            return jsonify({
                'success': False,
                'message': '缺少認證 token'
            }), 401
        
        payload = JWTManager.verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'message': '無效或過期的 token'
            }), 401
        
        if payload.get('user_type') != 'admin':
            return jsonify({
                'success': False,
                'message': '需要管理員權限'
            }), 403
        
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated
