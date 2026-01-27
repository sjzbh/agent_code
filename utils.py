from config import client

def call_llm(prompt, model_name="gemini"):
    """
    调用LLM模型生成响应
    
    Args:
        prompt: 提示词
        model_name: 模型名称，默认为"gemini"
    
    Returns:
        模型生成的响应文本
    """
    if model_name == "gemini":
        if not client:
            return "错误: Gemini客户端未初始化，请检查GEMINI_API_KEY"
        
        response = client.generate_content(prompt)
        return response.text
    else:
        # 后续可以添加其他模型的支持
        return f"错误: 模型 {model_name} 暂不支持"
