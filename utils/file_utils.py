"""
檔案處理工具函數
"""
from config import Config


def load_law_document():
    """
    載入法律文件
    
    Returns:
        法律文件內容
    """
    try:
        with open(Config.LAW_DOC_PATH, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"警告: 找不到法律文件 {Config.LAW_DOC_PATH}")
        return ""
    except Exception as e:
        print(f"讀取法律文件時發生錯誤: {e}")
        return ""
