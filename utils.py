import re
from config import client

def clean_json_text(text):
    """
    清理 LLM 返回的文本，去除 Markdown 代码块标记，提取纯 JSON。
    """
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\n", "", text)
    text = re.sub(r"\n```$", "", text)
    return text.strip()

def call_llm(prompt, model_name="gemini"):
    """
    调用LLM模型生成响应
    """
    if model_name == "gemini":
        if not client:
            return "错误: Gemini客户端未初始化，请检查GEMINI_API_KEY"
        
        response = client.generate_content(prompt)
        return response.text
    else:
        return f"错误: 模型 {model_name} 暂不支持"