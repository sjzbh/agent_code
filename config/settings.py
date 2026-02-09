import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class LLMConfig(BaseModel):
    provider: str = "openai"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = True


class MemoryConfig(BaseModel):
    enabled: bool = True
    vector_db_path: str = "./data/vectors"
    embedding_model: str = "text-embedding-3-small"
    max_memory_items: int = 1000
    similarity_threshold: float = 0.75


class EngineConfig(BaseModel):
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: int = 60
    parallel_tasks: int = 3
    enable_streaming: bool = True


class Settings(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    engine: EngineConfig = Field(default_factory=EngineConfig)
    debug: bool = False
    log_level: str = "INFO"
    project_root: str = str(Path.cwd())

    class Config:
        env_prefix = "ZWGENT_"


def get_llm_config() -> LLMConfig:
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL")
    model = os.getenv("LLM_MODEL", "deepseek-chat")
    
    return LLMConfig(
        provider="openai",
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096")),
        stream=os.getenv("LLM_STREAM", "true").lower() == "true"
    )


def get_gemini_config() -> Optional[Dict[str, Any]]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return {
        "provider": "gemini",
        "api_key": api_key,
        "model": os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    }


settings = Settings(
    llm=get_llm_config(),
    debug=os.getenv("ZWGENT_DEBUG", "false").lower() == "true",
    log_level=os.getenv("ZWGENT_LOG_LEVEL", "INFO")
)


ROLE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "planner": {
        "description": "任务规划器，负责将用户需求拆解为可执行任务",
        "temperature": 0.3,
        "requires_json": True
    },
    "coder": {
        "description": "代码生成器，负责生成高质量代码",
        "temperature": 0.5,
        "requires_json": False
    },
    "executor": {
        "description": "执行器，负责运行代码和命令",
        "temperature": 0.1,
        "requires_json": False
    },
    "auditor": {
        "description": "审计员，负责评估执行结果",
        "temperature": 0.2,
        "requires_json": True
    },
    "tech_lead": {
        "description": "技术主管，负责分析错误并提供修复建议",
        "temperature": 0.3,
        "requires_json": False
    },
    "intent_recognizer": {
        "description": "意图识别器，负责识别用户意图",
        "temperature": 0.1,
        "requires_json": True
    }
}
