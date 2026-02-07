"""
資料庫連接模組
"""
import pymongo
from config import Config


class Database:
    """資料庫連接類別"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """連接到 MongoDB"""
        try:
            self.client = pymongo.MongoClient(Config.MONGODB_URI)
            self.db = self.client[Config.MONGODB_DB_NAME]
            # 測試連接
            self.client.admin.command('ping')
            print(f"成功連接到 MongoDB: {Config.MONGODB_DB_NAME}")
        except Exception as e:
            print(f"MongoDB 連接失敗: {e}")
            raise
    
    def get_collection(self, collection_name):
        """獲取集合"""
        return self.db[collection_name]
    
    def close(self):
        """關閉資料庫連接"""
        if self.client:
            self.client.close()


# 建立全域資料庫實例
db = Database()
