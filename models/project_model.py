"""
專案資料模型
"""
from database import db
from datetime import datetime
from bson import ObjectId


class ProjectModel:
    """專案資料操作類別"""
    
    @staticmethod
    def create(user_id, project_name):
        """建立新專案"""
        collection = db.get_collection('project')
        result = collection.insert_one({
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'project_name': project_name,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
        return result.inserted_id
    
    @staticmethod
    def find_by_user_id(user_id):
        """根據用戶 ID 查找所有專案"""
        collection = db.get_collection('project')
        projects = list(collection.find({
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id
        }).sort('created_at', -1))
        # 轉換 ObjectId 為字串
        for project in projects:
            project['_id'] = str(project['_id'])
            project['user_id'] = str(project['user_id'])
        return projects
    
    @staticmethod
    def find_by_id(project_id):
        """根據專案 ID 查找專案"""
        collection = db.get_collection('project')
        project = collection.find_one({
            '_id': ObjectId(project_id) if isinstance(project_id, str) else project_id
        })
        if project:
            project['_id'] = str(project['_id'])
            project['user_id'] = str(project['user_id'])
        return project
    
    @staticmethod
    def update_name(project_id, new_name):
        """更新專案名稱"""
        collection = db.get_collection('project')
        return collection.update_one(
            {'_id': ObjectId(project_id) if isinstance(project_id, str) else project_id},
            {
                '$set': {
                    'project_name': new_name,
                    'updated_at': datetime.now()
                }
            }
        )
    
    @staticmethod
    def delete(project_id):
        """刪除專案（同時刪除相關記錄）"""
        collection = db.get_collection('project')
        project_id_obj = ObjectId(project_id) if isinstance(project_id, str) else project_id
        
        # 刪除專案
        result = collection.delete_one({'_id': project_id_obj})
        
        # 刪除專案的所有記錄
        from models.project_record_model import ProjectRecordModel
        ProjectRecordModel.delete_by_project_id(project_id)
        
        return result


class ProjectRecordModel:
    """專案記錄資料操作類別"""
    
    @staticmethod
    def create(project_id, input_ad, result_law, result_advice):
        """建立新專案記錄"""
        collection = db.get_collection('project_record')
        result = collection.insert_one({
            'project_id': ObjectId(project_id) if isinstance(project_id, str) else project_id,
            'input_ad': input_ad,
            'result_law': result_law,
            'result_advice': result_advice,
            'created_at': datetime.now()
        })
        return result.inserted_id
    
    @staticmethod
    def find_by_project_id(project_id):
        """根據專案 ID 查找所有記錄"""
        collection = db.get_collection('project_record')
        records = list(collection.find({
            'project_id': ObjectId(project_id) if isinstance(project_id, str) else project_id
        }).sort('created_at', 1))
        # 轉換 ObjectId 為字串
        for record in records:
            record['_id'] = str(record['_id'])
            record['project_id'] = str(record['project_id'])
        return records
    
    @staticmethod
    def delete_by_project_id(project_id):
        """根據專案 ID 刪除所有記錄"""
        collection = db.get_collection('project_record')
        return collection.delete_many({
            'project_id': ObjectId(project_id) if isinstance(project_id, str) else project_id
        })
