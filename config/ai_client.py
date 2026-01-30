import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

import os
import google.generativeai as genai
from openai import OpenAI
from .settings import settings

class AIClientManager:
    """
    AI客户端管理类
    负责初始化和管理不同的AI客户端
    """
    def __init__(self):
        self.gemini_client = None
        self.openai_client = None
        self._init_clients()
    
    def _init_clients(self):
        """
        初始化AI客户端
        """
        # 初始化Gemini客户端
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_client = genai.GenerativeModel(settings.GEMINI_MODEL)
                print(f"✅ Gemini客户端初始化成功: {settings.GEMINI_MODEL}")
            except Exception as e:
                print(f"❌ Gemini客户端初始化失败: {e}")
        else:
            print("⚠️ Gemini API Key未配置，跳过初始化")
        
        # 初始化OpenAI兼容客户端
        if settings.LLM_API_KEY and settings.LLM_BASE_URL:
            try:
                self.openai_client = OpenAI(
                    api_key=settings.LLM_API_KEY,
                    base_url=settings.LLM_BASE_URL
                )
                print(f"✅ OpenAI兼容客户端初始化成功: {settings.LLM_MODEL}")
            except Exception as e:
                print(f"❌ OpenAI兼容客户端初始化失败: {e}")
        else:
            print("⚠️ LLM API Key或Base URL未配置，跳过初始化")
    
    def get_client(self, client_type: str = "auto"):
        """
        获取AI客户端
        
        Args:
            client_type: 客户端类型，可选值: "auto", "gemini", "openai"
            
        Returns:
            对应的AI客户端
        """
        if client_type == "gemini":
            return self.gemini_client
        elif client_type == "openai":
            return self.openai_client
        elif client_type == "auto":
            # 自动选择客户端
            if self.openai_client:
                return self.openai_client
            elif self.gemini_client:
                return self.gemini_client
            else:
                return None
        else:
            raise ValueError(f"无效的客户端类型: {client_type}")
    
    def get_config(self, client_type: str = "auto"):
        """
        获取客户端配置
        
        Args:
            client_type: 客户端类型
            
        Returns:
            客户端配置字典
        """
        client = self.get_client(client_type)
        if not client:
            return None
        
        if client_type == "gemini" or (client_type == "auto" and self.gemini_client == client):
            return {
                "client": client,
                "type": "gemini",
                "model": settings.GEMINI_MODEL
            }
        elif client_type == "openai" or (client_type == "auto" and self.openai_client == client):
            return {
                "client": client,
                "type": "openai",
                "model": settings.LLM_MODEL
            }
        else:
            return None

# 创建全局AI客户端管理器实例
ai_client_manager = AIClientManager()
