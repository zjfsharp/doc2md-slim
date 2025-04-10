"""
Markdown转换模块，负责将raw.md转换为emb.md
"""

import os
import re
from utils.image_processor import ImageProcessor
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
    
    def process_tables(self, content):
        """
        处理Markdown内容中的表格
        
        Args:
            content: Markdown内容
            
        Returns:
            处理后的Markdown内容
        """
        # 匹配Markdown中的表格语法
        table_pattern = r'(\|[^\n]+\|\n\|[-:\|\s]+\|\n)(\|[^\n]+\|\n)+'
        
        def replace_table(match):
            table = match.group(0)
            
            # 提取表格内容
            table_rows = table.strip().split('\n')
            if len(table_rows) < 3:
                return table  # 如果表格行数不足，保持原样
            
            # 提取表头（列名）
            header_row = table_rows[0].strip()
            # 从表头行中提取列名
            headers = [h.strip() for h in header_row.split('|')[1:-1]]  # 跳过首尾的|
            
            # 构建表格描述
            row_count = len(table_rows) - 2  # 减去表头和分隔行
            column_count = len(headers)
            
            # 生成表格描述开始部分，注意：这里需要多添加两个空格保证markdown语法中的引用正常换行
            table_desc = [
                "> TABLE_BEGIN  ",
                f"> Rows: {row_count}  ",
                f"> Columns: {column_count}  ",
                f"> Header: {header_row}  "
            ]
            
            # 处理每一行的内容
            for row_idx, row in enumerate(table_rows[2:], 1):  # 跳过表头和分隔行，从第一个数据行开始
                # 跳过空行
                if not row.strip():
                    continue
                    
                # 从行中提取单元格内容
                cells = [cell.strip() for cell in row.split('|')[1:-1]]  # 跳过首尾的|
                
                # 添加行描述
                table_desc.append(f"> 第{row_idx}行:")
                
                # 遍历每个单元格，添加列描述
                for col_idx, (header, cell) in enumerate(zip(headers, cells)):
                    # 确保不会访问越界，且同时限制只输出有标题的列
                    if cell and header:  # 只有当单元格和标题都有内容时才输出
                        # 这里需要多添加两个空格保证markdown语法中的引用正常换行
                        table_desc.append(f">   列\"{header}\"的内容是\"{cell}\"  ")
            
            # 添加表格描述结束标记
            table_desc.append("> TABLE_END")
            
            # 返回原始表格和描述 (使用连接符号而非f-string来避免转义问题)
            return table + "\n" + "\n".join(table_desc)
        
        # 替换所有表格
        processed_content = re.sub(table_pattern, replace_table, content)
        
        return processed_content
    
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
        
        # 写入向量友好的Markdown文件
        self.write_markdown(content, self.emb_md_path) 