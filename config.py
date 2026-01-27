import os
from dotenv import load_dotenv
import google.generativeai as genai

# 加载环境变量
load_dotenv()

# 从环境变量获取API密钥
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 初始化Gemini Client
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    client = genai.GenerativeModel('gemini-1.5-pro')
else:
    print("警告: GEMINI_API_KEY 环境变量未设置")
    client = None