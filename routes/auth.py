"""
用戶認證路由（頁面路由）
"""
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from utils.jwt_utils import JWTManager, jwt_required_page
from models.user_model import UserModel

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login_page():
    """登入頁面"""
    # 檢查是否已登入（透過 JWT）
    token = JWTManager.get_token_from_request()
    if token:
        payload = JWTManager.verify_token(token)
        if payload:
            # 已登入，重定向到首頁
            return redirect(url_for('user.home'))
    
    return render_template('auth.html', 
                         form_type='login',
                         page_title='Login',
                         submit_text='Log in')


@auth_bp.route('/signup')
def signup_page():
    """註冊頁面"""
    # 檢查是否已登入（透過 JWT）
    token = JWTManager.get_token_from_request()
    if token:
        payload = JWTManager.verify_token(token)
        if payload:
            # 已登入，重定向到首頁
            return redirect(url_for('user.home'))
    
    return render_template('auth.html',
                         form_type='signup',
                         page_title='Sign Up',
                         submit_text='Sign up')


# 註冊和檢查 email 功能已移至 RESTful API
# 請使用 /api/auth/register 和 /api/auth/check-email


@auth_bp.route('/forgetpsw')
def forgetpsw():
    """忘記密碼頁面"""
    return render_template('auth.html',
                         form_type='forget',
                         page_title='Forget Password',
                         submit_text='Next')


@auth_bp.route('/forgetpsw_function', methods=['POST'])
def forgetpsw_function():
    """忘記密碼功能（保留舊的 API 以向後兼容）"""
    user_name = request.values.get("user_name")
    user_email = request.values.get("user_email")
    
    result = UserModel.find_by_name_and_email(user_name, user_email)
    
    if result is not None:
        # 使用 JWT token 來儲存 user_email（用於重設密碼）
        # 這裡可以生成一個臨時的 token 或使用其他方式
        response = {"exists": True}
    else:
        response = {"exists": False}
    
    return jsonify(response)


@auth_bp.route('/reset')
def resetpsw():
    """重設密碼頁面"""
    return render_template('auth.html',
                         form_type='reset',
                         page_title='Reset Password',
                         submit_text='Done')


@auth_bp.route('/reset_function', methods=['POST'])
def reset_function():
    """重設密碼功能（保留舊的 API 以向後兼容）"""
    # 注意：這個功能需要改進，應該使用 JWT token 來驗證身份
    # 目前保留基本功能，但建議使用 RESTful API
    user_password = request.values.get("user_password")
    user_email = request.values.get("user_email")  # 應該從 token 獲取
    
    if user_email:
        UserModel.update_password(user_email, user_password)
    
    return render_template('userLogin.html')


@auth_bp.route('/signout')
def signout():
    """登出（頁面路由）"""
    from flask import make_response
    # 重定向到首頁，前端會清除 token
    response = redirect("/")
    # 清除 Cookie
    response.set_cookie('access_token', '', max_age=0)
    return response
