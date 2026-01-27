import re
from config import gemini_client, openai_client, LLM_MODEL, USE_OPENAI_COMPATIBLE

def clean_json_text(text):
    """
    清理 LLM 返回的文本，去除 Markdown 代码块标记，提取纯 JSON。
    """
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\n", "", text)
    text = re.sub(r"\n```$", "", text)
    return text.strip()

def call_llm(prompt, model_name="default"):
    """
    统一的 LLM 调用接口
    支持 Gemini 和所有 OpenAI 兼容接口 (DeepSeek, Groq, etc.)
    """
    try:
        # 1. 优先尝试 OpenAI 兼容接口 (如果你在 .env 配置了的话)
        if USE_OPENAI_COMPATIBLE:
            if not openai_client:
                return "错误: OpenAI 客户端未正确初始化"
            
            response = openai_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        # 2. 回退到 Gemini
        else:
            if not gemini_client:
                return "错误: 未检测到任何可用的 API 配置 (Gemini 或 OpenAI 兼容均未配置)"
            
            response = gemini_client.generate_content(prompt)
            return response.text

    except Exception as e:
        return f"LLM 调用发生错误: {str(e)}"