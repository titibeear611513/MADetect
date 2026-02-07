"""
Gemini API 服務模組
"""
import google.generativeai as genai
from config import Config


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
        """
        prompt = f"""你是一個專業的律師，並具有台灣的醫療法相關知識。

請先分析相關文件：
{law_context}

請用你自己的話並以繁體中文告訴我此廣告詞是否違法：{ad_text}"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def suggest_ad_revision(self, ad_text, law_analysis):
        """
        建議廣告修改方案
        
        Args:
            ad_text: 原始廣告文字
            law_analysis: 法律分析結果
            
        Returns:
            修改建議文字
        """
        prompt = f"""你是一個專業的廣告詞家，具有台灣的醫療法相關知識。

{law_analysis}

請參考上述語句幫我以繁體中文建議我如何修改此廣告詞以達到不違法的目的，請只要告訴我修改後的結果就好：{ad_text}"""
        
        response = self.model.generate_content(prompt)
        return response.text


# 建立全域服務實例
gemini_service = GeminiService()
