"""
用戶資料模型
"""
from database import db


class UserModel:
    """用戶資料操作類別"""
    
    @staticmethod
    def find_by_email(email):
        """根據 email 查找用戶"""
        collection = db.get_collection('user')
        return collection.find_one({"user_email": email})
    
    @staticmethod
    def find_by_email_and_password(email, password):
        """根據 email 和 password 查找用戶"""
        collection = db.get_collection('user')
        return collection.find_one({
            "user_email": email,
            "user_password": password
        })
    
    @staticmethod
    def find_by_name_and_email(name, email):
        """根據 name 和 email 查找用戶"""
        collection = db.get_collection('user')
        return collection.find_one({
            "$and": [
                {"user_name": name},
                {"user_email": email}
            ]
        })
    
    @staticmethod
    def create(user_name, user_email, user_password):
        """建立新用戶"""
        collection = db.get_collection('user')
        return collection.insert_one({
            "user_name": user_name,
            "user_email": user_email,
            "user_password": user_password
        })
    
    @staticmethod
    def update_password(email, new_password):
        """更新用戶密碼"""
        collection = db.get_collection('user')
        return collection.update_one(
            {"user_email": email},
            {"$set": {"user_password": new_password}}
        )
    
    @staticmethod
    def find_by_name(user_name):
        """根據用戶名稱查找用戶"""
        collection = db.get_collection('user')
        return collection.find_one({'user_name': user_name})
    
    @staticmethod
    def add_report_to_user(user_id, report_id):
        """在用戶記錄中添加問題回報 ID"""
        collection = db.get_collection('user')
        return collection.update_one(
            {'_id': user_id},
            {'$push': {'reports': report_id}}
        )
    
    @staticmethod
    def count_all():
        """計算所有用戶數量"""
        collection = db.get_collection('user')
        return collection.count_documents({})
