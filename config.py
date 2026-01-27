import os
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI

# 加载环境变量
load_dotenv()

# ==============================
# 1. 初始化各种 AI 服务提供商 (Providers)
# ==============================

# --- Google Gemini (适合做 PM / 统筹) ---
gemini_key = os.getenv("GEMINI_API_KEY")
gemini_client = None
if gemini_key:
    genai.configure(api_key=gemini_key)
    gemini_client = genai.GenerativeModel('gemini-1.5-pro')

# --- OpenAI 兼容接口 (适合 DeepSeek/Qwen/Groq 做 Worker) ---
# 你可以在 .env 里配置 DeepSeek 或其他便宜强大的模型
openai_key = os.getenv("LLM_API_KEY")
openai_base = os.getenv("LLM_BASE_URL")
openai_model_name = os.getenv("LLM_MODEL", "deepseek-chat") # 默认模型名

openai_client_obj = None
if openai_key and openai_base:
    try:
        openai_client_obj = OpenAI(api_key=openai_key, base_url=openai_base)
    except Exception as e:
        print(f"警告: OpenAI 兼容客户端初始化失败: {e}")

# ==============================
# 2. 角色分配 (Role Assignment)
# 这里决定了谁干什么活！
# ==============================

# 【项目经理 (PM)】：负责逻辑、规划。Gemini 1.5 Pro 的长窗口非常适合。
PM_CONFIG = {
    "client": gemini_client,
    "type": "gemini",
    "model": "gemini-1.5-pro"
}

# 【打工仔 (Worker)】：负责写代码。建议用 DeepSeek V3 或 Qwen-Coder (便宜、代码能力强)。
# 如果配置了 OpenAI 兼容接口，就优先用它；否则回退给 Gemini。
if openai_client_obj:
    WORKER_CONFIG = {
        "client": openai_client_obj,
        "type": "openai",
        "model": openai_model_name
    }
else:
    WORKER_CONFIG = PM_CONFIG # 如果没配 DeepSeek，就让 PM 兼职

# 【审计员 (Auditor)】：负责找茬。可以用 Gemini (逻辑好) 或其他模型。
AUDITOR_CONFIG = PM_CONFIG # 默认使用 Gemini 复查