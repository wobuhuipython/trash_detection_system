"""
Ollama集成模块
提供本地AI模型支持
"""

from .ollama_client import OllamaClient
from .deepseek_config import (
    OLLAMA_CONFIG, 
    GARBAGE_CLASSIFICATION_SYSTEM_PROMPT,
    SUPPORTED_MODELS,
    DEFAULT_MODEL
)

__all__ = [
    'OllamaClient',
    'OLLAMA_CONFIG',
    'GARBAGE_CLASSIFICATION_SYSTEM_PROMPT',
    'SUPPORTED_MODELS',
    'DEFAULT_MODEL'
]
