"""
Word文档转Markdown模块，负责将Word文档转换为Markdown格式
"""

import os
import pypandoc
import re

def clean_text(text):
    """清理文本内容，确保可以正确显示在Markdown中"""
    try:
        # 尝试解码和编码，移除无法处理的字符
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # 替换可能导致问题的特殊字符
        text = text.replace('\u2028', '\n').replace('\u2029', '\n\n')
        
        # 合并字符并移除多余的空格
        text = ' '.join(text.split())
        
        # 如果清理后的文本只包含空格或为空，返回空字符串
        if not text.strip():
            return ""
            
        return text.strip()
    except Exception as e:
        print(f"警告: 文本清理失败: {e}")
        return ""

def post_process_markdown(file_path):
    """对转换后的Markdown文件进行后处理，移除图片宽高属性"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式移除图片宽高属性
        cleaned_content = re.sub(r'(!\[.*?\]\(.*?\))(\{.*?\})', r'\1', content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
            
        print(f"已完成Markdown文件后处理: {file_path}")
    except Exception as e:
        print(f"后处理过程中出错: {e}")

def fix_tables(file_path):
    """专门处理表格格式问题"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 将内容分成段落，以便单独处理每个表格
        paragraphs = re.split(r'\n\n+', content)
        fixed_paragraphs = []
        
        for paragraph in paragraphs:
            # 检查段落是否包含表格（以 | 开头的行）
            if re.search(r'^\|', paragraph, re.MULTILINE):
                fixed_paragraph = fix_table_paragraph(paragraph)
                fixed_paragraphs.append(fixed_paragraph)
            else:
                fixed_paragraphs.append(paragraph)
        
        # 重新组合文档
        fixed_content = '\n\n'.join(fixed_paragraphs)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
            
        print(f"已完成表格格式修复: {file_path}")
    except Exception as e:
        print(f"表格修复过程中出错: {e}")

def fix_table_paragraph(paragraph):
    """修复单个表格段落的格式"""
    # 分割表格行
    lines = paragraph.split('\n')
    
    # 初始化结果
    table_lines = []
    header_found = False
    separator_found = False
    row_idx = 0
    
    # 遍历所有行，识别表格部分
    for line in lines:
        # 跳过空行
        if not line.strip():
            continue
            
        # 跳过纯分隔符行，比如 +-----+-----+
        if re.match(r'^[\+\-]+$', line.strip()):
            continue
            
        # 处理表格行（以 | 开头）
        if line.strip().startswith('|'):
            # 移除行中的 # 符号
            cleaned_line = line.replace('#', '')
            
            # 特殊情况：跳过纯分隔符行，比如 | ---- | ---- | ---- | ---- |
            if row_idx > 1 and re.match(r'^\|\s*-+\s*(\|\s*-+\s*)+\|$', cleaned_line):
                continue
                
            # 记录标题行
            if row_idx == 0:
                header_found = True
                table_lines.append(cleaned_line)
                
            # 添加分隔行（如果这是第二行）
            elif row_idx == 1:
                # 如果第二行不是分隔行，手动生成一个
                if not re.search(r'-{3,}', cleaned_line):
                    # 计算标题行中的列数
                    col_count = len(table_lines[0].split('|')) - 2  # 减去开头和结尾的 |
                    table_lines.append('| ' + ' | '.join(['----'] * col_count) + ' |')
                    separator_found = True
                    
                    # 然后添加这一行作为数据
                    table_lines.append(cleaned_line)
                else:
                    table_lines.append(cleaned_line)
                    separator_found = True
                    
            # 添加数据行
            else:
                table_lines.append(cleaned_line)
                
            row_idx += 1
        else:
            # 非表格行直接添加
            table_lines.append(line)
    
    # 确保表格格式完整
    if header_found and not separator_found and len(table_lines) >= 1:
        # 标题行存在但分隔行不存在，在标题行后插入分隔行
        header = table_lines[0]
        col_count = len(header.split('|')) - 2  # 减去开头和结尾的 |
        separator = '| ' + ' | '.join(['----'] * col_count) + ' |'
        table_lines.insert(1, separator)
    
    return '\n'.join(table_lines)

def docx_to_markdown(docx_path, output_md_path):
    """
    将Word文档转换为Markdown格式
    
    Args:
        docx_path: Word文档路径
        output_md_path: 输出的Markdown文件路径
    """
    # 创建图片保存目录
    img_dir = 'images'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    
    try:
        # 检查文件是否存在
        if not os.path.exists(docx_path):
            print(f"错误：文件 '{docx_path}' 不存在！")
            return False
        
        # 设置转换参数
        extra_args = [
            f'--extract-media={img_dir}',  # 提取媒体文件到images目录
            '--wrap=none',                 # 保留原文换行符
            '--standalone'                 # 生成完整的文档
        ]
        
        # 执行转换
        print(f"正在将Word文档转换为Markdown: {docx_path} -> {output_md_path}")
        output = pypandoc.convert_file(
            docx_path,
            'markdown',
            outputfile=output_md_path,
            extra_args=extra_args
        )
        
        # 后处理：移除图片宽高属性
        post_process_markdown(output_md_path)
        
        # 专门处理表格格式
        fix_tables(output_md_path)
        
        print(f"文档转换完成！已保存为 {output_md_path}")
        return True
        
    except Exception as e:
        print(f"转换失败：{e}")
        return False 