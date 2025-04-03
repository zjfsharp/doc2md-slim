"""
环境变量加载模块，用于加载API密钥等敏感信息
"""

import os
from dotenv import load_dotenv
from config import MULTIMODAL_CONFIG

def load_env():
    """
    加载环境变量
    
    Returns:
        更新后的配置字典
    """
    # 加载.env文件中的环境变量
    load_dotenv()
    
    # 获取环境变量中的API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("BASE_URL")
    model = os.getenv("MODEL")
    temperature = os.getenv("TEMPERATURE")
    max_tokens = os.getenv("MAX_TOKENS")
    
    # 如果环境变量中有API密钥，则更新配置
    if api_key:
        MULTIMODAL_CONFIG["api_key"] = api_key
        MULTIMODAL_CONFIG["base_url"] = base_url
        MULTIMODAL_CONFIG["model"] = model
        MULTIMODAL_CONFIG["temperature"] = temperature
        MULTIMODAL_CONFIG["max_tokens"] = max_tokens
        print("已从环境变量加载API密钥")
    else:
        print("警告: 未找到环境变量OPENAI_API_KEY，请确保已在config.py中设置API密钥或在.env文件中设置OPENAI_API_KEY")
    
    return MULTIMODAL_CONFIG 