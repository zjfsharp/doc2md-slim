# 文档转Markdown工具

这是一个将PDF文件、Word文档和图片转换为Markdown格式的工具，并进一步处理为向量友好的格式。

## 功能特点

- 将PDF文件转换为Markdown格式
- 将Word文档转换为Markdown格式
- 将图片文件及图片目录转换为Markdown格式
- 提取文档中的文本、表格、图片等内容
- 使用多模态模型分析图片内容
- 将Markdown转换为向量友好的格式，便于后续处理

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/doc2md-slim.git
cd doc2md-slim
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 安装系统依赖：

- camelot-py需要Ghostscript：
  - macOS: `brew install ghostscript`
  - Ubuntu/Debian: `sudo apt-get install ghostscript`
  - Windows: 从 https://ghostscript.com/releases/gsdnld.html 下载安装程序

- pypandoc需要pandoc：
  - macOS: `brew install pandoc`
  - Ubuntu/Debian: `sudo apt-get install pandoc`
  - Windows: 从 https://pandoc.org/installing.html 下载安装程序

4. 配置API密钥：

复制 `.env.example` 文件为 `.env`，并填入你的OpenAI API密钥：

```bash
cp .env.example .env
# 编辑.env文件，填入你的API密钥
```

## 使用方法

### 基本用法

#### 转换PDF文件
```bash
python main.py --pdf your_file.pdf
```

#### 转换Word文档
```bash
python main.py --docx your_file.docx
```

#### 转换单张图片
```bash
python main.py --image your_image.jpg
```

#### 转换图片目录
```bash
python main.py --image-dir your_images_folder
```

### 高级用法

```bash
python main.py --pdf your_file.pdf --raw custom_raw.md --emb custom_emb.md --max-heading 3 --table-mode stream
```

### 跳过文档转换步骤

如果你已经有了raw.md文件，可以跳过文档转换步骤：

```bash
python main.py --skip-convert --raw existing_raw.md --emb output_emb.md
```

### 仅生成原始Markdown（不生成向量友好格式）

如果你只想生成原始Markdown而不需要向量友好格式：

```bash
python main.py --image your_image.jpg --skip-emb
```

## 参数说明

- `--pdf`: PDF文件路径
- `--docx`: Word文档路径
- `--image`: 单张图片路径
- `--image-dir`: 图片目录路径，处理目录中的所有图片
- `--raw`: 原始Markdown文件路径（默认为raw.md）
- `--emb`: 向量友好的Markdown文件路径（默认为emb.md）
- `--max-heading`: 最大标题级别（PDF专用，默认为4）
- `--table-mode`: 表格提取模式，可选"lattice"或"stream"（PDF专用，默认为"lattice"）
- `--skip-convert`: 跳过文档转换步骤，直接处理已有的raw.md文件
- `--skip-emb`: 跳过向量友好转换步骤，只生成raw.md文件

## 输出格式

### 图片处理

原始格式：
```
![产品销售图表](images/sales_chart.png)
```

转换后格式：
```
![产品销售图表](images/sales_chart.png)
> IMAGE_BEGIN
> Path: images/sales_chart.png
> Alt: sales_chart.png
> Desc: 这是一张显示不同产品销售数据的条形图
> OCR: 产品A: 250万元, 产品B: 180万元, 产品C: 320万元
> Context: 2023年第一季度销售业绩对比
> Type: png
> Size: 640x480
> IMAGE_END
```

### 表格处理

原始格式：
```
| 产品 | 销量 | 价格 |
| --- | --- | --- |
| A | 100 | 10 |
| B | 200 | 20 |
```

转换后格式：
```
| 产品 | 销量 | 价格 |
| --- | --- | --- |
| A | 100 | 10 |
| B | 200 | 20 |
> TABLE_BEGIN
> Rows: 2
> Columns: 3
> Header: | 产品 | 销量 | 价格 |
> 第1行:
>   列"产品"的内容是"A"
>   列"销量"的内容是"100"
>   列"价格"的内容是"10"
> 第2行:
>   列"产品"的内容是"B"
>   列"销量"的内容是"200"
>   列"价格"的内容是"20"
> TABLE_END
```

## 许可证

MIT
