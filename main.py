"""
主程序，负责调用各个模块完成PDF到Markdown的转换
"""

import os
import argparse
from pdf2md import pdf_to_markdown
from markdown_converter import MarkdownConverter
from config import PATH_CONFIG
from env_loader import load_env

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='PDF转Markdown工具')
    parser.add_argument('--pdf', type=str, help='PDF文件路径')
    parser.add_argument('--raw', type=str, default=PATH_CONFIG["raw_md"], help='原始Markdown文件路径')
    parser.add_argument('--emb', type=str, default=PATH_CONFIG["emb_md"], help='向量友好的Markdown文件路径')
    parser.add_argument('--max-heading', type=int, default=4, help='最大标题级别')
    parser.add_argument('--table-mode', type=str, default="lattice", choices=["lattice", "stream"], help='表格提取模式')
    parser.add_argument('--skip-pdf', action='store_true', help='跳过PDF转换步骤，直接处理已有的raw.md文件')
    return parser.parse_args()

def main():
    """主函数"""
    # 加载环境变量
    load_env()
    
    args = parse_args()
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(args.raw) or '.', exist_ok=True)
    os.makedirs(os.path.dirname(args.emb) or '.', exist_ok=True)
    
    # 步骤1: PDF转Markdown (如果未跳过)
    if not args.skip_pdf:
        if not args.pdf:
            print("错误: 未指定PDF文件路径，请使用--pdf参数指定")
            return
        
        print(f"正在将PDF转换为Markdown: {args.pdf} -> {args.raw}")
        pdf_to_markdown(args.pdf, args.raw, max_heading_level=args.max_heading, table_mode=args.table_mode)
    
    # 步骤2: 处理Markdown，转换为向量友好的格式
    print(f"正在处理Markdown，转换为向量友好的格式: {args.raw} -> {args.emb}")
    converter = MarkdownConverter(raw_md_path=args.raw, emb_md_path=args.emb)
    converter.convert()
    
    print("处理完成!")

if __name__ == "__main__":
    main() 