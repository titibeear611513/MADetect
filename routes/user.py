"""
用戶功能路由
"""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models.user_model import UserModel
from models.report_model import ReportModel
from utils.gemini_service import gemini_service
from utils.text_utils import clean_markdown, format_as_list_html, format_as_list_html
from utils.file_utils import load_law_document
from utils.jwt_utils import jwt_required_page, jwt_required, JWTManager

user_bp = Blueprint('user', __name__)


@user_bp.route('/home')
@jwt_required_page
def home():
    """主功能頁面"""
    from flask import request
    from models.project_model import ProjectModel, ProjectRecordModel
    
    # 從 JWT 獲取用戶 ID
    user_id = request.current_user.get('user_id')
    
    # 獲取用戶的所有專案
    projects = ProjectModel.find_by_user_id(user_id)
    
    # 獲取當前專案 ID（從 query parameter 或 session）
    current_project_id = request.args.get('project_id')
    current_project = None
    records = []
    
    if current_project_id:
        # 驗證專案是否屬於當前用戶
        project = ProjectModel.find_by_id(current_project_id)
        if project and str(project['user_id']) == str(user_id):
            current_project = project
            records = ProjectRecordModel.find_by_project_id(current_project_id)
    elif projects:
        # 如果沒有指定專案，使用第一個專案
        current_project = ProjectModel.find_by_id(projects[0]['_id'])
        if current_project:
            records = ProjectRecordModel.find_by_project_id(current_project['_id'])
    
    return render_template('home.html', 
                         projects=projects,
                         current_project=current_project,
                         records=records)


@user_bp.route('/madetect', methods=['POST'])
@jwt_required
def madetect():
    """
    連接 Gemini 辨認廣告 API
    POST /madetect
    Body: { "input_ad": "廣告內容", "project_id": "專案ID" }
    """
    from models.project_model import ProjectModel, ProjectRecordModel
    
    data = request.get_json() or {}
    input_ad = data.get('input_ad') or request.values.get('input_ad')
    project_id = data.get('project_id')
    
    if not input_ad:
        return jsonify({
            'success': False,
            'message': '請提供廣告內容'
        }), 400
    
    if not project_id:
        return jsonify({
            'success': False,
            'message': '請提供專案 ID'
        }), 400
    
    # 驗證專案是否屬於當前用戶
    user_id = request.current_user.get('user_id')
    project = ProjectModel.find_by_id(project_id)
    
    if not project:
        return jsonify({
            'success': False,
            'message': '專案不存在'
        }), 404
    
    if str(project['user_id']) != str(user_id):
        return jsonify({
            'success': False,
            'message': '無權限訪問此專案'
        }), 403
    
    print(f"收到廣告內容: {input_ad}")
    
    try:
        # 載入法律文件
        law_text = load_law_document()
        
        # 分析廣告是否違法
        result_law = gemini_service.analyze_ad_law(input_ad, law_text)
        print(f'法律分析結果: {result_law}')
        
        # 建議修改方案
        result_advice = gemini_service.suggest_ad_revision(input_ad, result_law)
        print(f'修改建議: {result_advice}')
        
        # 清理 Markdown 格式並格式化為條列式
        result_law = clean_markdown(result_law)
        result_law = format_as_list_html(result_law)  # 轉換為 HTML 條列式
        result_advice = clean_markdown(result_advice)
        
        # 儲存記錄到資料庫
        ProjectRecordModel.create(project_id, input_ad, result_law, result_advice)
        
        response = {
            'success': True,
            'result_advice': result_advice,
            'result_law': result_law
        }
        
        return jsonify(response)
        
    except Exception as e:
        error_message = str(e)
        print(f'廣告檢測錯誤: {error_message}')
        
        # 檢查是否為配額限制錯誤
        if '配額' in error_message or 'quota' in error_message.lower() or 'ResourceExhausted' in error_message:
            return jsonify({
                'success': False,
                'message': 'API 配額已用完。免費層每日限制為 20 次請求。請稍後再試，或升級您的 API 方案。',
                'error_type': 'quota_exceeded'
            }), 429
        else:
            return jsonify({
                'success': False,
                'message': f'廣告檢測失敗：{error_message}',
                'error_type': 'api_error'
            }), 500


@user_bp.route('/report', methods=['POST'])
@jwt_required
def add_report():
    """問題回報功能"""
    # 從 JWT 獲取用戶資訊
    current_user = request.current_user
    user_name = current_user.get('user_name')
    user_id = current_user.get('user_id')
    
    # 獲取回報內容
    data = request.get_json() or {}
    report_text = data.get('report') or request.form.get('report')
    
    if not report_text:
        return jsonify({
            'success': False,
            'message': '請提供回報內容'
        }), 400
    
    # 獲取用戶完整資訊
    user = UserModel.find_by_name(user_name)
    if not user:
        return jsonify({
            'success': False,
            'message': '用戶不存在'
        }), 404
    
    user_id_obj = user['_id']
    
    # 建立問題回報
    report_id = ReportModel.create(user_name, user_id_obj, report_text)
    
    # 在用戶記錄中添加問題回報 ID
    UserModel.add_report_to_user(user_id_obj, report_id)
    
    return jsonify({
        'success': True,
        'message': '問題回報成功',
        'report_id': str(report_id)
    })
