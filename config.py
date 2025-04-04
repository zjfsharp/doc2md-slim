"""
配置文件，包含多模态模型的相关配置
"""

# 多模态模型配置
MULTIMODAL_CONFIG = {
    "base_url": "https://api.openai.com/v1",  # OpenAI API基础URL
    "model": "gpt-4-vision-preview",  # 使用的模型名称
    "api_key": "",  # API密钥，需要用户自行填写
    "max_tokens": 1024,  # 最大生成token数
    "temperature": 0.7,  # 温度参数
}

# 图片处理配置
IMAGE_CONFIG = {
    "max_size": 1024,  # 图片最大尺寸
    "output_dir": "images",  # 图片输出目录
    "supported_formats": ["png", "jpg", "jpeg", "gif", "bmp"],  # 支持的图片格式
}

# 提示词配置
PROMPT_CONFIG = {
    "image_analysis": """
    请分析这张图片并提供以下信息：
    1. 请识别图片中的文字信息，输出识别的内容（如果有）
    2. 在1的基础上，用一句话描述图片信息，描述要涵盖内容并描述内容，且准确
    3. 图片的上下文意义(如果可以推断的话)
    输出格式如下:
    <OCR>
    识别的内容(如果可以识别的话)
    </OCR>
    <DESC>
    图片信息描述
    </DESC>
    <CONTEXT>
    图片的上下文意义(如果可以推断的话)
    </CONTEXT>
    """,
}

# 文件路径配置
PATH_CONFIG = {
    "raw_md": "raw.md",  # 原始Markdown文件路径
    "emb_md": "emb.md",  # 向量友好的Markdown文件路径
} 