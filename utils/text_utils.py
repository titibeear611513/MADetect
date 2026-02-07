"""
文字處理工具函數
"""
import re


def clean_markdown(text):
    """
    移除 Markdown 格式符號
    
    Args:
        text: 需要清理的文字
        
    Returns:
        清理後的純文字
    """
    if not text:
        return text
    
    # 移除標題符號 (#, ##, ###, etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # 移除粗體和斜體符號 (**text**, *text*, __text__, _text_)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **text** -> text
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *text* -> text
    text = re.sub(r'__([^_]+)__', r'\1', text)  # __text__ -> text
    text = re.sub(r'_([^_]+)_', r'\1', text)  # _text_ -> text
    
    # 移除刪除線 (~~text~~)
    text = re.sub(r'~~([^~]+)~~', r'\1', text)
    
    # 移除代碼塊符號 (```text```)
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    
    # 移除行內代碼 (`text`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # 移除多餘的空白行
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()
