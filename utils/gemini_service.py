"""
Gemini API 服務模組
"""
import google.generativeai as genai
import time
from config import Config

# 嘗試導入 Google API 異常類別
try:
    from google.api_core import exceptions as google_exceptions
    GOOGLE_EXCEPTIONS_AVAILABLE = True
except ImportError:
    # 如果無法導入，使用通用異常處理
    GOOGLE_EXCEPTIONS_AVAILABLE = False
    google_exceptions = None


class GeminiService:
    """Gemini API 服務類別"""
    
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = self._get_available_model()
    
    def _get_available_model(self):
        """獲取可用的 Gemini 模型"""
        model = None
        
        # 嘗試動態獲取可用的模型
        try:
            available_models = list(genai.list_models())
            for m in available_models:
                if 'generateContent' in m.supported_generation_methods:
                    model_name = m.name.replace('models/', '')
                    try:
                        model = genai.GenerativeModel(model_name)
                        print(f"成功使用模型: {model_name}")
                        break
                    except:
                        continue
        except Exception as e:
            print(f"無法列出模型: {e}")
        
        # 如果無法動態獲取，嘗試常見的模型名稱
        if model is None:
            model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            for name in model_names:
                try:
                    model = genai.GenerativeModel(name)
                    print(f"成功使用模型: {name}")
                    break
                except Exception as e:
                    print(f"嘗試 {name} 失敗: {str(e)[:100]}")
                    continue
        
        if model is None:
            raise Exception(
                "無法找到可用的 Gemini 模型。"
                "請檢查 API Key 是否正確，或更新 google-generativeai 套件版本。"
            )
        
        return model
    
    def analyze_ad_law(self, ad_text, law_context):
        """
        分析廣告是否違法
        
        Args:
            ad_text: 廣告文字
            law_context: 法律文件內容
            
        Returns:
            分析結果文字
            
        Raises:
            Exception: 當 API 調用失敗時
        """
        prompt = f"""你是一個專業的律師，並具有台灣的醫療法相關知識。

請先分析相關文件：
{law_context}

請仔細分析此廣告詞是否違法：{ad_text}

**重要原則：**
1. **首先判斷是否為醫療相關廣告**：如果廣告詞內容與醫療、診所、醫院、治療、健康服務等無關（例如：純數字、一般商品、非醫療服務等），請直接回答「此非醫療相關廣告詞」
2. 必須根據實際廣告內容判斷，不要假設或推測
3. 如果廣告詞中沒有違法元素（如「免費」、「贈送」、「折扣」等禁止用語），應判斷為「不違法」
4. 如果廣告詞已經移除了違法元素，即使之前版本違法，現在版本也應判斷為「不違法」
5. 仔細檢查每個字詞，不要因為廣告詞看起來像醫療廣告就假設違法
6. 只有當廣告詞明確包含禁止用語或違法行為時，才判斷為「違法」

請以條列式的方式回答，格式要求：
1. 違法/不違法（根據實際內容判斷，簡短結論，一行，不超過 10 字）
2. 違反的法條（如有違法，寫法條名稱和簡短說明，不超過 20 字；如不違法，寫「無」）
3. 違法原因（如有違法，簡短說明違法原因，每點一行，不超過 25 字；如不違法，寫「無違法行為」）
4. 具體違規內容（如有違法，說明具體違規行為，每點一行，不超過 25 字；如不違法，寫「符合法規」）

重要要求：
- 每點需要有一些描述性說明，但保持簡潔
- 總長度不超過 80 字
- 最多 4 行
- 必須根據實際廣告內容判斷，不要假設
- 如果廣告詞沒有違法元素，必須明確寫「不違法」
- 避免冗長描述、重複說明和過多解釋
- 直接列出重點，不要寫「您好」、「綜合分析」等開場白
- 格式範例（違法情況）：
  1. 違法
  2. 醫療法第61條第1項：禁止不正當招攬病人
  3. 廣告宣稱贈送禮品或免費服務
  4. 使用「免費送」、「免費體驗」等字眼招攬病人
- 格式範例（不違法情況）：
  1. 不違法
  2. 無
  3. 無違法行為
  4. 符合法規
- 格式範例（非醫療廣告情況）：
  1. 此非醫療相關廣告詞
  2. 無
  3. 無違法行為
  4. 符合法規"""
        
        result = self._generate_content_with_retry(prompt)
        # 格式化為條列式
        return self._format_as_list(result)
    
    def suggest_ad_revision(self, ad_text, law_analysis):
        """
        建議廣告修改方案
        
        Args:
            ad_text: 原始廣告文字
            law_analysis: 法律分析結果
            
        Returns:
            修改建議文字
            
        Raises:
            Exception: 當 API 調用失敗時
        """
        # 檢查是否為非醫療廣告
        if '此非醫療相關廣告詞' in law_analysis or '非醫療相關' in law_analysis:
            return '請輸入醫療相關廣告詞'
        
        prompt = f"""你是一個專業的廣告詞家，具有台灣的醫療法相關知識。

{law_analysis}

請參考上述語句幫我以繁體中文建議我如何修改此廣告詞以達到不違法的目的，請只要告訴我修改後的結果就好：{ad_text}"""
        
        return self._generate_content_with_retry(prompt)
    
    def _generate_content_with_retry(self, prompt, max_retries=3):
        """
        生成內容，帶有重試機制
        
        Args:
            prompt: 提示文字
            max_retries: 最大重試次數
            
        Returns:
            API 回應的文字內容
            
        Raises:
            Exception: 當所有重試都失敗時
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
                
            except Exception as e:
                # 檢查是否為配額限制錯誤
                error_str = str(e)
                is_quota_error = (
                    'ResourceExhausted' in error_str or
                    'quota' in error_str.lower() or
                    '429' in error_str or
                    '配額' in error_str
                )
                
                if is_quota_error:
                    # 處理配額限制錯誤
                    last_exception = e
                    # 從錯誤訊息中提取重試延遲時間
                    retry_delay = self._extract_retry_delay(e)
                    
                    if attempt < max_retries - 1:
                        print(f"API 配額已用完，等待 {retry_delay} 秒後重試 (嘗試 {attempt + 1}/{max_retries})...")
                        time.sleep(retry_delay)
                        continue  # 繼續下一次重試
                    else:
                        # 最後一次嘗試也失敗
                        raise Exception(
                            f"API 配額已用完。免費層每日限制為 20 次請求。"
                            f"請稍後再試（建議等待 {retry_delay} 秒），或升級您的 API 方案。"
                            f"詳細資訊：https://ai.google.dev/gemini-api/docs/rate-limits"
                        )
                else:
                    # 其他類型的錯誤，直接拋出
                    raise Exception(f"API 調用失敗: {str(e)}")
        
        # 如果所有重試都失敗
        if last_exception:
            raise last_exception
    
    def _extract_retry_delay(self, exception):
        """
        從 ResourceExhausted 異常中提取重試延遲時間（秒）
        
        Args:
            exception: ResourceExhausted 異常
            
        Returns:
            重試延遲時間（秒），預設為 60 秒
        """
        try:
            # 嘗試從異常訊息中提取 retry_delay
            error_message = str(exception)
            if 'retry_delay' in error_message or 'Please retry in' in error_message:
                # 從錯誤訊息中提取秒數
                import re
                match = re.search(r'retry in ([\d.]+)s', error_message, re.IGNORECASE)
                if match:
                    return int(float(match.group(1))) + 1  # 加 1 秒緩衝
        except:
            pass
        
        # 預設返回 60 秒
        return 60
    
    def _format_as_list(self, text):
        """
        將文字格式化為條列式
        
        Args:
            text: 原始文字
            
        Returns:
            格式化後的條列式文字
        """
        if not text:
            return text
        
        import re
        
        lines = text.strip().split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 移除多餘的空白
            line = re.sub(r'\s+', ' ', line)
            
            # 如果行已經以數字、項目符號開頭，保持原樣
            if re.match(r'^[\d一二三四五六七八九十]+[\.、)\-]', line) or \
               re.match(r'^[•·\-*]', line):
                formatted_lines.append(line)
            # 如果行以特定關鍵字開頭，添加項目符號
            elif line.startswith('違反') or line.startswith('違法') or \
                 line.startswith('根據') or line.startswith('該廣告') or \
                 line.startswith('綜合') or line.startswith('結論'):
                # 確保有適當的格式
                if not re.match(r'^[\d一二三四五六七八九十]+', line):
                    formatted_lines.append(f"• {line}")
                else:
                    formatted_lines.append(line)
            else:
                # 其他行，如果是要點則添加項目符號
                if len(line) < 50 and (line.endswith('。') or line.endswith('：') or '、' in line):
                    formatted_lines.append(f"  - {line}")
                else:
                    formatted_lines.append(line)
        
        result = '\n'.join(formatted_lines)
        
        # 如果結果太長，精簡到前 4 行
        if len(result) > 80:
            lines = result.split('\n')
            important_lines = []
            for line in lines[:4]:  # 最多保留 4 行
                if line.strip():
                    important_lines.append(line)
            result = '\n'.join(important_lines)
        
        return result


# 建立全域服務實例
gemini_service = GeminiService()
