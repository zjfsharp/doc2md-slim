from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal
import camelot
import fitz  # PyMuPDF
from io import StringIO
from collections import Counter

def clean_text(text):
    """清理文本内容，确保可以正确显示在Markdown中"""
    try:
        # 尝试解码和编码，移除无法处理的字符
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # 替换可能导致问题的特殊字符
        text = text.replace('\u2028', '\n').replace('\u2029', '\n\n')
        
        # 移除控制字符，但保留换行和制表符
        cleaned_chars = []
        for char in text:
            # 保留换行和制表符
            if char in ('\n', '\t'):
                cleaned_chars.append(char)
            # 保留可打印字符
            elif char.isprintable():
                cleaned_chars.append(char)
            # 移除其他控制字符
            else:
                cleaned_chars.append(' ')
        
        # 合并字符并移除多余的空格
        text = ''.join(cleaned_chars)
        # 移除多余空格
        text = ' '.join(text.split())
        
        # 如果清理后的文本只包含空格或为空，返回空字符串
        if not text.strip():
            return ""
            
        return text.strip()
    except Exception as e:
        print(f"Warning: Text cleaning failed: {e}")
        return ""

def pdf_to_markdown_with_camelot_tables(pdf_path, output_md_path, max_heading_level=4, table_mode="lattice"):
    markdown_content = StringIO()

    # 初始化工具
    doc = fitz.open(pdf_path)

    # 逐页处理
    for page_num, page_layout in enumerate(extract_pages(pdf_path)):
        markdown_content.write(f"# Page {page_num + 1}\n\n")

        # 存储页面元素
        elements = []
        text_sizes = []

        # 1. 提取表格（Camelot）
        tables = camelot.read_pdf(pdf_path, pages=str(page_num + 1), flavor=table_mode)
        table_bboxes = [(table._bbox[0], table._bbox[1], table._bbox[2], table._bbox[3]) for table in tables]

        for table_num, table in enumerate(tables):
            x0, y0, x1, y1 = table._bbox
            df = table.df
            if df.empty or all(all(cell == "" for cell in row) for _, row in df.iterrows()):
                continue
            # 清理表格内容
            df = df.applymap(clean_text)
            table_md = ["#### Table\n"]
            table_md.append("| " + " | ".join(str(col).replace("\n", " ") for col in df.columns) + " |")
            table_md.append("| " + " | ".join(["---"] * len(df.columns)) + " |")
            for _, row in df.iterrows():
                table_md.append("| " + " | ".join(str(cell).replace("\n", " ") if cell else "" for cell in row) + " |")
            table_md.append("\n")
            elements.append(("table", "\n".join(table_md), None, None, x0, y1))
            print(f"Page {page_num + 1} Table {table_num} at ({x0}, {y0}, {x1}, {y1})")

        # 2. 提取文本框（pdfminer.six）
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                text = clean_text(element.get_text().strip())
                if not text:
                    continue
                x0, y0, x1, y1 = element.bbox
                in_table = any(t_x0 - 5 <= x1 and t_x1 + 5 >= x0 and t_y0 - 5 <= y1 and t_y1 + 5 >= y0 
                              for t_x0, t_y0, t_x1, t_y1 in table_bboxes)
                if in_table:
                    continue
                font_size = max([char.size for char in element if hasattr(char, 'size')], default=0)
                is_bold = any("bold" in (char.fontname.lower() if hasattr(char, 'fontname') else "") 
                             for char in element)
                text_sizes.append(font_size)
                elements.append(("text", text, font_size, is_bold, x0, y1))
                print(f"Page {page_num + 1} Text {text} at ({x0}, {y0}, {x1}, {y1})")

        # 3. 动态确定标题级别
        if text_sizes:
            size_counts = sorted([(size, count) for size, count in Counter(text_sizes).items()], 
                                key=lambda x: x[1], reverse=True)
            body_size = size_counts[0][0]
            heading_sizes = [size for size, _ in size_counts if size > body_size]
            heading_map = {size: min(i + 1, max_heading_level) for i, size in enumerate(sorted(heading_sizes, reverse=True))}

        for i, (elem_type, content, font_size, is_bold, x0, y1) in enumerate(elements):
            if elem_type == "text":
                if font_size in heading_map and (font_size > body_size or is_bold):
                    level = heading_map[font_size]
                    elements[i] = ("heading", f"{'#' * (level + 1)} {content}", None, None, x0, y1)
                else:
                    elements[i] = ("text", content, None, None, x0, y1)

        # 4. 提取图片（PyMuPDF）
        page_fitz = doc[page_num]
        images = page_fitz.get_images(full=True)
        image_list = []
        # 获取页面高度用于坐标转换
        page_height = page_fitz.rect.height
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_path = f"image_{page_num}_{img_index}.{image_ext}"
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            img_rect = page_fitz.get_image_bbox(img)
            # 修正y坐标：使用页面高度减去原始y坐标
            x0 = img_rect.x0
            y0 = page_height - img_rect.y1  # 转换y0
            y1 = page_height - img_rect.y0  # 转换y1
            image_list.append((img_index, image_path, x0, y0, y1))
            print(f"Page {page_num + 1} Image {img_index} ({image_path}) at x0={x0}, y0={y0}, y1={y1}")

        # 直接添加图片到 elements，不进行预排序
        for img_index, image_path, x0, y0, y1 in image_list:
            elements.append(("image", f"![Image {img_index}]({image_path})", None, None, x0, y1))

        # 5. 按布局排序：从上到下（y1 从大到小），从左到右（x0）
        elements.sort(key=lambda x: (-x[5], x[4]))
        print(f"Page {page_num + 1} Final element order: {[x[1] for x in elements]}")

        # 6. 写入 Markdown
        for elem_type, content, _, _, x0, y1 in elements:
            if content:  # 只写入非空内容
                markdown_content.write(content + "\n\n")

    # 保存文件
    try:
        with open(output_md_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown_content.getvalue())
        print(f"Successfully saved markdown file to {output_md_path}")
    except Exception as e:
        print(f"Error saving markdown file: {e}")

    # 清理资源
    doc.close()
    markdown_content.close()

# 使用示例
pdf_path = "/Users/zhongjiafeng/Desktop/SalesMiniProgram250319.pdf"
output_md_path = "./output.md"
pdf_to_markdown_with_camelot_tables(pdf_path, output_md_path, max_heading_level=4, table_mode="lattice")