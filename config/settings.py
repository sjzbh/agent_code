import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    """
    全局配置类
    """
    # 项目配置
    PROJECT_NAME: str = "AI Collaboration Tool"
    VERSION: str = "2.0.0"
    
    # 环境配置
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # AI 配置
    # Google Gemini
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    
    # OpenAI 兼容接口
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")
    LLM_BASE_URL: Optional[str] = os.getenv("LLM_BASE_URL")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-chat")
    
    # 沙箱配置
    SANDBOX_DIR: str = os.getenv("SANDBOX_DIR", "./sandbox_env")
    SANDBOX_TIMEOUT: int = int(os.getenv("SANDBOX_TIMEOUT", "300"))  # 沙箱操作超时时间（秒）
    
    # 测试配置
    TEST_TIMEOUT: int = int(os.getenv("TEST_TIMEOUT", "600"))  # 测试超时时间（秒）
    MAX_TEST_RETRIES: int = int(os.getenv("MAX_TEST_RETRIES", "3"))  # 最大测试重试次数
    
    # 部署配置
    DEPLOYMENT_DIR: str = os.getenv("DEPLOYMENT_DIR", "./deployed_projects")
    
    # 工作流配置
    MAX_PROJECT_CREATION_TIME: int = int(os.getenv("MAX_PROJECT_CREATION_TIME", "600"))  # 项目创建最大时间（秒）
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()

# 导出配置常量，便于其他模块使用
PROJECT_NAME = settings.PROJECT_NAME
VERSION = settings.VERSION
ENVIRONMENT = settings.ENVIRONMENT
DEBUG = settings.DEBUG

GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_MODEL = settings.GEMINI_MODEL

LLM_API_KEY = settings.LLM_API_KEY
LLM_BASE_URL = settings.LLM_BASE_URL
LLM_MODEL = settings.LLM_MODEL

SANDBOX_DIR = settings.SANDBOX_DIR
SANDBOX_TIMEOUT = settings.SANDBOX_TIMEOUT

TEST_TIMEOUT = settings.TEST_TIMEOUT
MAX_TEST_RETRIES = settings.MAX_TEST_RETRIES

DEPLOYMENT_DIR = settings.DEPLOYMENT_DIR

MAX_PROJECT_CREATION_TIME = settings.MAX_PROJECT_CREATION_TIME
