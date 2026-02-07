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


def format_as_list_html(text):
    """
    將文字轉換為 HTML 條列式格式（用於前端顯示）
    
    Args:
        text: 原始文字
        
    Returns:
        HTML 格式的條列式文字
    """
    if not text:
        return text
    
    lines = text.strip().split('\n')
    html_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 如果是編號開頭（1. 2. 等）
        if re.match(r'^[\d一二三四五六七八九十]+[\.、)]', line):
            html_lines.append(f'<div class="list-item-numbered">{line}</div>')
        # 如果是項目符號開頭（• - 等）
        elif re.match(r'^[•·\-*]\s*', line):
            html_lines.append(f'<div class="list-item-bullet">{line}</div>')
        # 如果是縮排的項目（  - 等）
        elif re.match(r'^\s+[-•·*]', line):
            html_lines.append(f'<div class="list-item-indented">{line.strip()}</div>')
        # 其他行
        else:
            html_lines.append(f'<div class="list-item">{line}</div>')
    
    return ''.join(html_lines)
