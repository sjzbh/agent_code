import re

def clean_json_text(text):
    """清理 Markdown 标记，提取纯文本/JSON"""
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\n", "", text)
    text = re.sub(r"\n```$", "", text)
    return text.strip()

def call_llm(config, prompt):
    """
    万能调用接口：根据传入的 config 自动判断是调 Gemini 还是 OpenAI
    Args:
        config: 包含 client, type, model 的字典 (来自 config.py)
        prompt: 提示词
    """
    client = config.get("client")
    model_type = config.get("type")
    model_name = config.get("model")

    if not client:
        return "错误: 此角色的 AI 客户端未初始化，请检查 .env 配置"

    try:
        # 分流逻辑
        if model_type == "gemini":
            response = client.generate_content(prompt)
            return response.text
        
        elif model_type == "openai":
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        
        else:
            return f"错误: 未知的模型类型 {model_type}"

    except Exception as e:
        return f"API 调用报错: {str(e)}"