import os
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI

# 加载环境变量
load_dotenv()

# --- 配置中心 ---

# 1. Google Gemini 配置 (原生支持)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_client = genai.GenerativeModel('gemini-1.5-pro')
else:
    gemini_client = None

# 2. OpenAI 兼容协议配置 (支持 DeepSeek, Groq, Qwen, Kimi 等)
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo") # 默认模型名

openai_client = None
if LLM_API_KEY and LLM_BASE_URL:
    try:
        openai_client = OpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL
        )
    except Exception as e:
        print(f"警告: OpenAI 客户端初始化失败: {e}")

# 当前使用的主要模型模式
# 如果配置了 LLM_BASE_URL，优先使用通用模式；否则回退到 Gemini
USE_OPENAI_COMPATIBLE = bool(openai_client)