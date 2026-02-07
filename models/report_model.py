"""
問題回報資料模型
"""
from database import db


class ReportModel:
    """問題回報資料操作類別"""
    
    @staticmethod
    def create(user_name, user_id, report_text):
        """建立新問題回報"""
        collection = db.get_collection('report')
        result = collection.insert_one({
            'user_name': user_name,
            'user_id': user_id,
            'report_text': report_text
        })
        return result.inserted_id
    
    @staticmethod
    def count_all():
        """計算所有問題回報數量"""
        collection = db.get_collection('report')
        return collection.count_documents({})
