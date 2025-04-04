"""
Markdown转换模块，负责将raw.md转换为emb.md
"""

import os
import re
from image_processor import ImageProcessor
from config import PATH_CONFIG

class MarkdownConverter:
    """Markdown转换类，负责将raw.md转换为emb.md"""
    
    def __init__(self, raw_md_path=None, emb_md_path=None):
        """
        初始化Markdown转换器
        
        Args:
            raw_md_path: 原始Markdown文件路径
            emb_md_path: 向量友好的Markdown文件路径
        """
        self.raw_md_path = raw_md_path or PATH_CONFIG["raw_md"]
        self.emb_md_path = emb_md_path or PATH_CONFIG["emb_md"]
        self.image_processor = ImageProcessor()
    
    def read_markdown(self, file_path):
        """
        读取Markdown文件
        
        Args:
            file_path: Markdown文件路径
            
        Returns:
            Markdown内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取Markdown文件失败: {e}")
            return ""
    
    def write_markdown(self, content, file_path):
        """
        写入Markdown文件
        
        Args:
            content: Markdown内容
            file_path: Markdown文件路径
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"成功写入Markdown文件: {file_path}")
        except Exception as e:
            print(f"写入Markdown文件失败: {e}")
    
    def process_images(self, content):
        """
        处理Markdown内容中的图片
        
        Args:
            content: Markdown内容
            
        Returns:
            处理后的Markdown内容
        """
        return self.image_processor.process_markdown_images(content)
    
    # def process_tables(self, content):
    #     """
    #     处理Markdown内容中的表格
        
    #     Args:
    #         content: Markdown内容
            
    #     Returns:
    #         处理后的Markdown内容
    #     """
    #     # 匹配Markdown中的表格语法
    #     table_pattern = r'(\|[^\n]+\|\n\|[-:\|\s]+\|\n)(\|[^\n]+\|\n)+'
        
    #     def replace_table(match):
    #         table = match.group(0)
            
    #         # 提取表格内容
    #         rows = table.strip().split('\n')
    #         if len(rows) < 3:
    #             return table  # 如果表格行数不足，保持原样
            
    #         # 构建表格描述
    #         table_desc = (
    #             "\n> TABLE BEGIN [table1]\n"
    #             f"> Rows: {len(rows) - 2}  # 减去表头和分隔行\n"
    #             f"> Columns: {len(re.findall(r'\|', rows[0])) - 1}  # 减去第一个和最后一个|\n"
    #             f"> Content: {rows[0].strip()}\n"
    #             "> TABLE END\n"
    #         )
            
    #         # 返回原始表格和描述
    #         return f"{table}{table_desc}"
        
    #     # 替换所有表格
    #     processed_content = re.sub(table_pattern, replace_table, content)
        
    #     return processed_content
    
    # def process_urls(self, content):
    #     """
    #     处理Markdown内容中的URL
        
    #     Args:
    #         content: Markdown内容
            
    #     Returns:
    #         处理后的Markdown内容
    #     """
    #     # 匹配Markdown中的URL语法
    #     url_pattern = r'\[(.*?)\]\((https?://[^\s\)]+)\)'
        
    #     def replace_url(match):
    #         text = match.group(1)
    #         url = match.group(2)
            
    #         # 构建URL描述
    #         url_desc = (
    #             "\n> URL BEGIN [url1]\n"
    #             f"> Text: {text}\n"
    #             f"> Link: {url}\n"
    #             "> URL END\n"
    #         )
            
    #         # 返回原始URL和描述
    #         return f"{match.group(0)}{url_desc}"
        
    #     # 替换所有URL
    #     processed_content = re.sub(url_pattern, replace_url, content)
        
    #     return processed_content
    
    # def process_formulas(self, content):
    #     """
    #     处理Markdown内容中的数学公式
        
    #     Args:
    #         content: Markdown内容
            
    #     Returns:
    #         处理后的Markdown内容
    #     """
    #     # 匹配Markdown中的数学公式语法
    #     inline_formula_pattern = r'\$([^\$]+)\$'
    #     block_formula_pattern = r'\$\$([^\$]+)\$\$'
        
    #     def replace_inline_formula(match):
    #         formula = match.group(1)
            
    #         # 构建公式描述
    #         formula_desc = (
    #             "\n> FORMULA BEGIN [formula1]\n"
    #             "> Type: inline\n"
    #             f"> Content: {formula}\n"
    #             "> FORMULA END\n"
    #         )
            
    #         # 返回原始公式和描述
    #         return f"{match.group(0)}{formula_desc}"
        
    #     def replace_block_formula(match):
    #         formula = match.group(1)
            
    #         # 构建公式描述
    #         formula_desc = (
    #             "\n> FORMULA BEGIN [formula1]\n"
    #             "> Type: block\n"
    #             f"> Content: {formula}\n"
    #             "> FORMULA END\n"
    #         )
            
    #         # 返回原始公式和描述
    #         return f"{match.group(0)}{formula_desc}"
        
    #     # 替换所有公式
    #     processed_content = re.sub(inline_formula_pattern, replace_inline_formula, content)
    #     processed_content = re.sub(block_formula_pattern, replace_block_formula, processed_content)
        
    #     return processed_content
    
    def convert(self):
        """
        将raw.md转换为emb.md
        """
        # 读取原始Markdown文件
        content = self.read_markdown(self.raw_md_path)
        if not content:
            print(f"原始Markdown文件为空或不存在: {self.raw_md_path}")
            return
        
        # 处理图片
        content = self.process_images(content)
        
        # 处理表格
        # content = self.process_tables(content)
        
        # 处理URL
        # content = self.process_urls(content)
        
        # 处理数学公式
        # content = self.process_formulas(content)
        
        # 写入向量友好的Markdown文件
        self.write_markdown(content, self.emb_md_path) 