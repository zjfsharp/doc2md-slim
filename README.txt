# PDF转Markdown工具

这是一个将PDF文件转换为Markdown格式的工具，并进一步处理为向量友好的格式。

## 功能特点

- 将PDF文件转换为Markdown格式
- 提取PDF中的文本、表格、图片等内容
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

3. 安装系统依赖（camelot-py需要）：

- macOS: `brew install ghostscript`
- Ubuntu/Debian: `sudo apt-get install ghostscript`
- Windows: 从 https://ghostscript.com/releases/gsdnld.html 下载安装程序

4. 配置API密钥：

复制 `.env.example` 文件为 `.env`，并填入你的OpenAI API密钥：

```bash
cp .env.example .env
# 编辑.env文件，填入你的API密钥
```

## 使用方法

### 基本用法

```bash
python main.py --pdf your_file.pdf
```

### 高级用法

```bash
python main.py --pdf your_file.pdf --raw custom_raw.md --emb custom_emb.md --max-heading 3 --table-mode stream
```

### 跳过PDF转换步骤

如果你已经有了raw.md文件，可以跳过PDF转换步骤：

```bash
python main.py --skip-pdf --raw existing_raw.md --emb output_emb.md
```

## 参数说明

- `--pdf`: PDF文件路径
- `--raw`: 原始Markdown文件路径（默认为raw.md）
- `--emb`: 向量友好的Markdown文件路径（默认为emb.md）
- `--max-heading`: 最大标题级别（默认为4）
- `--table-mode`: 表格提取模式，可选"lattice"或"stream"（默认为"lattice"）
- `--skip-pdf`: 跳过PDF转换步骤，直接处理已有的raw.md文件

## 输出格式

### 图片处理

原始格式：
```
![产品销售图表](images/sales_chart.png)
```

转换后格式：
```
![产品销售图表](images/sales_chart.png)
> IMAGE BEGIN [img1]
> Desc: 产品销售图表
> Alt: 产品销售图表
> Path: images/sales_chart.png
> Type: png
> Size: 640x480
> IMAGE END
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
> TABLE BEGIN [table1]
> Rows: 2
> Columns: 3
> Content: | 产品 | 销量 | 价格 |
> TABLE END
```

## 许可证

MIT
