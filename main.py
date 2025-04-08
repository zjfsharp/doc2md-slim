"""
主程序，负责调用各个模块完成文档到Markdown的转换
"""

import os
import argparse
from utils.pdf2md import pdf_to_markdown
from utils.docx2md import docx_to_markdown
from utils.markdown_converter import MarkdownConverter
from utils.image_processor import ImageProcessor
from config import PATH_CONFIG
from env_loader import load_env

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='文档转Markdown工具')
    parser.add_argument('--pdf', type=str, help='PDF文件路径')
    parser.add_argument('--docx', type=str, help='Word文档路径')
    parser.add_argument('--image', type=str, help='单张图片路径')
    parser.add_argument('--image-dir', type=str, help='图片目录路径，处理目录下所有图片')
    parser.add_argument('--raw', type=str, default=PATH_CONFIG["raw_md"], help='原始Markdown文件路径')
    parser.add_argument('--emb', type=str, default=PATH_CONFIG["emb_md"], help='向量友好的Markdown文件路径')
    parser.add_argument('--max-heading', type=int, default=4, help='最大标题级别 (仅PDF)')
    parser.add_argument('--table-mode', type=str, default="lattice", choices=["lattice", "stream"], help='表格提取模式 (仅PDF)')
    parser.add_argument('--skip-convert', action='store_true', help='跳过文档转换步骤，直接处理已有的raw.md文件')
    parser.add_argument('--skip-emb', action='store_true', help='跳过向量友好转换步骤，只生成raw.md文件')
    return parser.parse_args()

def main():
    """主函数"""
    # 加载环境变量
    load_env()
    
    args = parse_args()
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(args.raw) or '.', exist_ok=True)
    os.makedirs(os.path.dirname(args.emb) or '.', exist_ok=True)
    
    # 标记是否已执行转换
    conversion_done = False
    
    # 步骤1: 文档转Markdown (如果未跳过)
    if not args.skip_convert:
        if args.pdf:
            print(f"正在将PDF转换为Markdown: {args.pdf} -> {args.raw}")
            pdf_to_markdown(args.pdf, args.raw, max_heading_level=args.max_heading, table_mode=args.table_mode)
            conversion_done = True
        elif args.docx:
            print(f"正在将Word文档转换为Markdown: {args.docx} -> {args.raw}")
            docx_to_markdown(args.docx, args.raw)
            conversion_done = True
        elif args.image:
            print(f"正在将图片转换为Markdown: {args.image} -> {args.raw}")
            image_processor = ImageProcessor()
            image_processor.image_to_markdown(args.image, args.raw)
            conversion_done = True
        elif args.image_dir:
            print(f"正在将图片目录转换为Markdown: {args.image_dir} -> {args.raw}")
            image_processor = ImageProcessor()
            image_processor.image_dir_to_markdown(args.image_dir, args.raw)
            conversion_done = True
        else:
            if not os.path.exists(args.raw):
                print("错误: 未指定输入文件路径，请使用--pdf、--docx、--image或--image-dir参数指定")
                return
            else:
                print(f"跳过文档转换，直接使用已有的原始Markdown文件: {args.raw}")
                conversion_done = True
    
    # 如果没有执行任何转换，也没有现有的raw.md文件，则退出
    if not conversion_done and not os.path.exists(args.raw):
        print(f"错误: 原始Markdown文件不存在: {args.raw}")
        return
        
    # 步骤2: 处理Markdown，转换为向量友好的格式 (如果未跳过)
    if not args.skip_emb:
        print(f"正在处理Markdown，转换为向量友好的格式: {args.raw} -> {args.emb}")
        converter = MarkdownConverter(raw_md_path=args.raw, emb_md_path=args.emb)
        converter.convert()
    else:
        print(f"跳过向量友好转换步骤，只生成raw.md文件: {args.raw}")
    
    print("处理完成!")

# 使用示例:
# python main.py --pdf your_file.pdf
# python main.py --docx your_file.docx
# python main.py --image your_image.jpg
# python main.py --image-dir your_image_directory
if __name__ == "__main__":
    main() 