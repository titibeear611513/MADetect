"""
專案管理 RESTful API 路由
"""
from flask import Blueprint, request, jsonify
from models.project_model import ProjectModel, ProjectRecordModel
from utils.jwt_utils import jwt_required
from bson import ObjectId

project_api_bp = Blueprint('project_api', __name__, url_prefix='/api/project')


@project_api_bp.route('/list', methods=['GET'])
@jwt_required
def list_projects():
    """獲取用戶的所有專案"""
    user_id = request.current_user.get('user_id')
    projects = ProjectModel.find_by_user_id(user_id)
    return jsonify({
        'success': True,
        'projects': projects
    })


@project_api_bp.route('/create', methods=['POST'])
@jwt_required
def create_project():
    """建立新專案"""
    user_id = request.current_user.get('user_id')
    data = request.get_json()
    project_name = data.get('project_name', '').strip()
    
    if not project_name:
        return jsonify({
            'success': False,
            'message': '請輸入專案名稱'
        }), 400
    
    project_id = ProjectModel.create(user_id, project_name)
    project = ProjectModel.find_by_id(project_id)
    
    return jsonify({
        'success': True,
        'message': '專案建立成功',
        'project': project
    }), 201


@project_api_bp.route('/<project_id>', methods=['GET'])
@jwt_required
def get_project(project_id):
    """獲取專案詳情和記錄"""
    user_id = request.current_user.get('user_id')
    project = ProjectModel.find_by_id(project_id)
    
    if not project:
        return jsonify({
            'success': False,
            'message': '專案不存在'
        }), 404
    
    # 檢查專案是否屬於當前用戶
    if str(project['user_id']) != str(user_id):
        return jsonify({
            'success': False,
            'message': '無權限訪問此專案'
        }), 403
    
    # 獲取專案記錄
    records = ProjectRecordModel.find_by_project_id(project_id)
    
    return jsonify({
        'success': True,
        'project': project,
        'records': records
    })


@project_api_bp.route('/<project_id>', methods=['PUT'])
@jwt_required
def update_project(project_id):
    """更新專案名稱"""
    user_id = request.current_user.get('user_id')
    project = ProjectModel.find_by_id(project_id)
    
    if not project:
        return jsonify({
            'success': False,
            'message': '專案不存在'
        }), 404
    
    # 檢查專案是否屬於當前用戶
    if str(project['user_id']) != str(user_id):
        return jsonify({
            'success': False,
            'message': '無權限修改此專案'
        }), 403
    
    data = request.get_json()
    new_name = data.get('project_name', '').strip()
    
    if not new_name:
        return jsonify({
            'success': False,
            'message': '請輸入專案名稱'
        }), 400
    
    ProjectModel.update_name(project_id, new_name)
    updated_project = ProjectModel.find_by_id(project_id)
    
    return jsonify({
        'success': True,
        'message': '專案名稱更新成功',
        'project': updated_project
    })


@project_api_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required
def delete_project(project_id):
    """刪除專案"""
    user_id = request.current_user.get('user_id')
    project = ProjectModel.find_by_id(project_id)
    
    if not project:
        return jsonify({
            'success': False,
            'message': '專案不存在'
        }), 404
    
    # 檢查專案是否屬於當前用戶
    if str(project['user_id']) != str(user_id):
        return jsonify({
            'success': False,
            'message': '無權限刪除此專案'
        }), 403
    
    ProjectModel.delete(project_id)
    
    return jsonify({
        'success': True,
        'message': '專案刪除成功'
    })


@project_api_bp.route('/<project_id>/record', methods=['POST'])
@jwt_required
def create_record(project_id):
    """建立專案記錄"""
    user_id = request.current_user.get('user_id')
    project = ProjectModel.find_by_id(project_id)
    
    if not project:
        return jsonify({
            'success': False,
            'message': '專案不存在'
        }), 404
    
    # 檢查專案是否屬於當前用戶
    if str(project['user_id']) != str(user_id):
        return jsonify({
            'success': False,
            'message': '無權限訪問此專案'
        }), 403
    
    data = request.get_json()
    input_ad = data.get('input_ad', '')
    result_law = data.get('result_law', '')
    result_advice = data.get('result_advice', '')
    
    record_id = ProjectRecordModel.create(project_id, input_ad, result_law, result_advice)
    
    return jsonify({
        'success': True,
        'message': '記錄建立成功',
        'record_id': str(record_id)
    }), 201
