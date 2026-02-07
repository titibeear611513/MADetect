"""
管理員資料模型
"""
from database import db


class AdminModel:
    """管理員資料操作類別"""
    
    @staticmethod
    def find_by_email_and_password(email, password):
        """根據 email 和 password 查找管理員"""
        collection = db.get_collection('admin')
        return collection.find_one({
            "admin_email": email,
            "admin_password": password
        })
