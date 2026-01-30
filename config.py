"""
Configuration for Next Generation Virtual Software Company
Optimized for Linux environment
"""
import os
import warnings
import google.generativeai as genai
from openai import OpenAI

# Suppress google.generativeai deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=FutureWarning, message=".*google.generativeai.*")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Gemini client
gemini_key = os.getenv("GEMINI_API_KEY")
gemini_client = None
if gemini_key:
    try:
        genai.configure(api_key=gemini_key)
        gemini_client = genai.GenerativeModel('gemini-1.5-pro')
    except Exception as e:
        print(f"Warning: Failed to initialize Gemini client: {e}")

# Initialize OpenAI-compatible client
openai_key = os.getenv("LLM_API_KEY")
openai_base = os.getenv("LLM_BASE_URL")
openai_model_name = os.getenv("LLM_MODEL", "deepseek-chat")

openai_client_obj = None
if openai_key and openai_base:
    try:
        openai_client_obj = OpenAI(api_key=openai_key, base_url=openai_base)
    except Exception as e:
        print(f"Warning: Failed to initialize OpenAI-compatible client: {e}")

# Role configurations - optimized for Linux environment
PM_CONFIG = {
    "client": gemini_client or openai_client_obj,
    "type": "gemini" if gemini_client else "openai",
    "model": "gemini-1.5-pro" if gemini_client else openai_model_name
}

# For all other workers, use the same configuration as PM to reduce complexity
WORKER_CONFIG = PM_CONFIG

# Auditor uses the same configuration as PM
AUDITOR_CONFIG = PM_CONFIG