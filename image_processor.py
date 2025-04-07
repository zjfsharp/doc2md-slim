"""
图片处理模块，负责图片分析和多模态模型调用
"""

import os
import base64
import requests
import json
from PIL import Image
import io
import re
from config import MULTIMODAL_CONFIG, IMAGE_CONFIG, PROMPT_CONFIG

class ImageProcessor:
    """图片处理类，负责图片分析和多模态模型调用"""
    
    def __init__(self, config=None):
        """
        初始化图片处理器
        
        Args:
            config: 配置字典，如果为None则使用默认配置
        """
        self.config = config or MULTIMODAL_CONFIG
        self.api_key = self.config.get("api_key")
        self.base_url = self.config.get("base_url")
        self.model = self.config.get("model")
        self.temperature = self.config.get("temperature")
        self.max_tokens = self.config.get("max_tokens")
        if not self.api_key:
            raise ValueError("API密钥未设置，请在config.py中设置MULTIMODAL_CONFIG['api_key']")
    
    def encode_image(self, image_path):
        """
        将图片编码为base64字符串
        
        Args:
            image_path: 图片路径
            
        Returns:
            base64编码的图片字符串
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_image_info(self, image_path):
        """
        获取图片的基本信息
        
        Args:
            image_path: 图片路径
            
        Returns:
            包含图片信息的字典
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                format = img.format.lower()

                # 检查图片尺寸，如果宽或高超过1024，进行等比例缩放
                # max_dimension = max(width, height)
                # if max_dimension > 512:
                #     # 计算缩放比例
                #     scale_ratio = 512 / max_dimension
                #     # 按比例计算新的宽高
                #     new_width = int(width * scale_ratio)
                #     new_height = int(height * scale_ratio)
                #     # 缩放图片
                #     img = img.resize((new_width, new_height), Image.LANCZOS)
                #     # 更新宽高信息
                #     width, height = img.size
                #     print(f"图片已缩放: 从 {max_dimension} 缩放到 512，新尺寸为 {width}x{height}")

                return {
                    "width": width,
                    "height": height,
                    "format": format,
                    "size": f"{width}x{height}"
                }
        except Exception as e:
            print(f"获取图片信息失败: {e}")
            return {
                "width": 0,
                "height": 0,
                "format": "unknown",
                "size": "0x0"
            }
    
    def analyze_image(self, image_path, context=None):
        """
        使用多模态模型分析图片
        
        Args:
            image_path: 图片路径
            context: 图片的上下文信息
            
        Returns:
            图片分析结果
        """
        # 检查图片是否存在
        if not os.path.exists(image_path):
            return f"图片不存在: {image_path}"
        
        # 获取图片信息
        image_info = self.get_image_info(image_path)
        
        # 编码图片
        base64_image = self.encode_image(image_path)
        
        # 准备API请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 构建提示词
        prompt = PROMPT_CONFIG["image_analysis"]
        if context:
            prompt += f"\n\n上下文信息: {context}"
        
        # 构建请求体
        payload = {
            "model": self.config["model"],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_info['format']};base64,{base64_image}"
                            },
                            "min_pixels": 256 * 256,
                            "max_pixels": 1280 * 28 * 28,
                            "detail": "high",
                        }
                    ]
                }
            ],
            "max_tokens": self.config["max_tokens"],
            "temperature": self.config["temperature"]
        }
        
        # 发送请求
        try:
            response = requests.post(
                f"{self.config['base_url']}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            # 提取分析结果
            analysis = result["choices"][0]["message"]["content"]
            analysis = analysis.replace('\n', '|+|')
            analysis = analysis.replace('<br>', '|+|')
            # 提取OCR、DESC和CONTEXT标签中的内容
            ocr_content = ""
            desc_content = ""
            context_content = ""
            
            # 提取OCR内容
            ocr_match = re.search(r'<OCR>(.*?)</OCR>', analysis)
            if ocr_match:
                ocr_content = ocr_match.group(1)
            else:
                # 如果没有完整的OCR标签，尝试提取部分内容
                ocr_start = analysis.find('<OCR>')
                if ocr_start != -1:
                    ocr_start += 5  # 跳过<OCR>标签
                    desc_start = analysis.find('<DESC>', ocr_start)
                    if desc_start != -1:
                        ocr_content = analysis[ocr_start:desc_start]
                    else:
                        # 如果没有找到下一个标签，取到字符串结束
                        ocr_content = analysis[ocr_start:]
            
            # 提取DESC内容
            desc_match = re.search(r'<DESC>(.*?)</DESC>', analysis)
            if desc_match:
                desc_content = desc_match.group(1)
            else:
                # 如果没有完整的DESC标签，尝试提取部分内容
                desc_start = analysis.find('<DESC>')
                if desc_start != -1:
                    desc_start += 6  # 跳过<DESC>标签
                    context_start = analysis.find('<CONTEXT>', desc_start)
                    if context_start != -1:
                        desc_content = analysis[desc_start:context_start]
                    else:
                        # 如果没有找到下一个标签，取到字符串结束
                        desc_content = analysis[desc_start:]
            
            # 提取CONTEXT内容
            context_match = re.search(r'<CONTEXT>(.*?)</CONTEXT>', analysis)
            if context_match:
                context_content = context_match.group(1)
            else:
                # 如果没有完整的CONTEXT标签，尝试提取部分内容
                context_start = analysis.find('<CONTEXT>')
                if context_start != -1:
                    context_start += 9  # 跳过<CONTEXT>标签
                    context_content = analysis[context_start:]
            
            
            # 构建完整的图片描述
            # 每行的末尾都有两个空格，这是markdown语法中需要的引用块内部换行
            image_desc = f"""> IMAGE_BEGIN  
> Path: {image_path}  
> Alt: {os.path.basename(image_path)}  
> OCR: {ocr_content}  
> DESC: {desc_content}  
> CONTEXT: {context_content}  
> Type: {image_info['format']}  
> Size: {image_info['size']}  
> IMAGE_END  
"""
            print(image_desc)
            return image_desc
        except Exception as e:
            print(f"图片分析失败: {e}")
            return f"图片分析失败: {e}"
    
    def process_markdown_images(self, markdown_content):
        """
        处理Markdown内容中的图片，将其转换为向量友好的格式
        
        Args:
            markdown_content: Markdown内容
            
        Returns:
            处理后的Markdown内容
        """
        # 匹配Markdown中的图片语法
        image_pattern = r'!\[(.*?)\]\((.*?)\)'
        
        def replace_image(match):
            alt_text = match.group(1)
            image_path = match.group(2)
            
            # 检查图片是否存在
            if not os.path.exists(image_path):
                return match.group(0)  # 如果图片不存在，保持原样
            
            # 分析图片
            analysis = self.analyze_image(image_path, context=alt_text)
            
            # 返回原始图片标签和分析结果
            return f"{match.group(0)}\n{analysis}"
        
        # 替换所有图片
        # 使用re.sub函数替换所有匹配的图片标记
        # 参数1: image_pattern - 要匹配的正则表达式模式
        # 参数2: replace_image - 替换函数，处理每个匹配项
        # 参数3: markdown_content - 要处理的原始文本内容
        # 返回值: 替换后的新文本内容
        processed_content = re.sub(image_pattern, replace_image, markdown_content)
        
        return processed_content 