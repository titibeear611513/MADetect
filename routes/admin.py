"""
管理員路由
"""
from flask import Blueprint, render_template, redirect, jsonify
from utils.jwt_utils import JWTManager, jwt_required_page, jwt_required
from models.user_model import UserModel
from models.report_model import ReportModel

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/adminlogin')
def adminlogin_page():
    """管理員登入頁面"""
    # 檢查是否已登入（透過 JWT）
    token = JWTManager.get_token_from_request()
    if token:
        payload = JWTManager.verify_token(token)
        if payload and payload.get('user_type') == 'admin':
            # 已登入，重定向到管理員首頁
            return redirect('/adminhome')
    
    return render_template('auth.html',
                         form_type='admin_login',
                         page_title='Administrator Login',
                         subtitle='login',
                         submit_text='Log in')


@admin_bp.route('/adminforgetpsw')
def adminforgetpsw_page():
    """管理員忘記密碼頁面"""
    return render_template('auth.html',
                         form_type='forget',
                         page_title='Administrator Forget Password',
                         submit_text='Next')


@admin_bp.route('/adminresetpsw')
def adminresetpsw_pages():
    """管理員重設密碼頁面"""
    return render_template('auth.html',
                         form_type='reset',
                         page_title='Administrator Reset Password',
                         submit_text='Done')


@admin_bp.route('/adminhome')
@jwt_required_page
def admin_home():
    """管理員首頁"""
    return render_template('admin_home.html')


@admin_bp.route('/adminsignout')
def adminsignout():
    """管理員登出"""
    from flask import make_response
    # 重定向到登入頁面，前端會清除 token
    response = redirect('/adminlogin')
    # 清除 Cookie
    response.set_cookie('access_token', '', max_age=0)
    return response


@admin_bp.route('/get_user_count', methods=['GET'])
@jwt_required
def get_user_count():
    """獲取總用戶數 API"""
    user_count = UserModel.count_all()
    return jsonify(user_count)


@admin_bp.route('/get_report_count', methods=['GET'])
@jwt_required
def get_report_count():
    """獲取問題回報數量 API"""
    report_count = ReportModel.count_all()
    return jsonify(report_count)


@admin_bp.route('/adminmanage')
@jwt_required_page
def admin_manage():
    """管理管理員"""
    return render_template('admin_manage.html')


@admin_bp.route('/membermanage')
@jwt_required_page
def member_manage():
    """管理會員"""
    return render_template('member_manage.html')


@admin_bp.route('/normalmanage')
@jwt_required_page
def normal_manage():
    """管理一般用戶"""
    return render_template('normal_manage.html')
