# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill - 报告导出模块
===================================

功能：
1. 生成美化的 Markdown 报告
2. 支持 PDF 格式导出
3. 内置图表渲染（支持 Mermaid, Chart.js 等）
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChartData:
    """图表数据"""
    chart_type: str  # line, bar, pie, candlestick
    title: str
    labels: List[str]
    datasets: List[Dict[str, Any]]
    
    def to_mermaid(self) -> str:
        """转换为 Mermaid 图表"""
        if self.chart_type == "line":
            return self._to_mermaid_line()
        elif self.chart_type == "bar":
            return self._to_mermaid_bar()
        elif self.chart_type == "pie":
            return self._to_mermaid_pie()
        return ""
    
    def _to_mermaid_line(self) -> str:
        """Mermaid 折线图"""
        lines = [f"%% {self.title}", "```mermaid", "graph LR"]
        
        # 简化处理：输出数据摘要
        lines.append(f'    A["{self.title}"] --> B["数据点: {len(self.labels)}"]')
        
        # 添加数据趋势描述
        if self.datasets:
            dataset = self.datasets[0]
            data = dataset.get("data", [])
            if len(data) >= 2:
                trend = "上涨 📈" if data[-1] > data[0] else "下跌 📉"
                change_pct = ((data[-1] - data[0]) / data[0] * 100) if data[0] != 0 else 0
                lines.append(f'    B --> C["{trend} ({change_pct:+.2f}%)"]')
        
        lines.append("```")
        return "\n".join(lines)
    
    def _to_mermaid_bar(self) -> str:
        """Mermaid 柱状图"""
        lines = [f"%% {self.title}", "```mermaid", "graph TB"]
        lines.append(f'    A["{self.title}"]')
        
        if self.datasets:
            dataset = self.datasets[0]
            data = dataset.get("data", [])
            labels = self.labels[:len(data)]
            
            for i, (label, value) in enumerate(zip(labels, data)):
                bar = "█" * min(int(value / 10), 20)
                lines.append(f'    A --> B{i}["{label}: {value:.2f} {bar}"]')
        
        lines.append("```")
        return "\n".join(lines)
    
    def _to_mermaid_pie(self) -> str:
        """Mermaid 饼图"""
        lines = [f"%% {self.title}", "```mermaid", f"pie \"{self.title}\""]
        
        if self.datasets:
            dataset = self.datasets[0]
            data = dataset.get("data", [])
            labels = self.labels[:len(data)]
            
            colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"]
            
            for i, (label, value) in enumerate(zip(labels, data)):
                color = colors[i % len(colors)]
                lines.append(f'    "{label}" : {value:.1f}')
        
        lines.append("```")
        return "\n".join(lines)


@dataclass
class ReportMetadata:
    """报告元数据"""
    title: str
    author: str = "Stock Analyzer"
    date: str = ""
    tags: List[str] = None
    version: str = "1.0"
    
    def __post_init__(self):
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d %H:%M")
        if self.tags is None:
            self.tags = []


class MarkdownExporter:
    """
    Markdown 报告导出器
    
    生成美化的 Markdown 报告，支持：
    - 标题层级结构
    - 表格美化
    - 图表嵌入（Mermaid, PlantUML）
    - 代码高亮
    - 警告框
    """
    
    def __init__(self):
        self._sections = []
        self._metadata: Optional[ReportMetadata] = None
        self._charts: List[ChartData] = []
    
    def set_metadata(self, metadata: ReportMetadata):
        """设置报告元数据"""
        self._metadata = metadata
    
    def add_section(self, title: str, level: int = 2, content: str = ""):
        """添加章节"""
        prefix = "#" * level
        self._sections.append(f"{prefix} {title}\n\n{content}")
    
    def add_heading(self, text: str, level: int = 2):
        """添加标题"""
        prefix = "#" * level
        self._sections.append(f"\n{prefix} {text}\n")
    
    def add_paragraph(self, text: str):
        """添加段落"""
        self._sections.append(f"{text}\n")
    
    def add_table(self, headers: List[str], rows: List[List[str]], 
                  bordered: bool = True, striped: bool = True):
        """
        添加美化表格
        
        Args:
            headers: 表头
            rows: 数据行
            bordered: 是否有边框
            striped: 是否斑马纹
        """
        lines = []
        
        if bordered:
            # 表头分隔线
            separator = "| " + " | ".join(["---" for _ in headers]) + " |"
            lines.append(separator)
        
        # 表头
        lines.insert(0, "| " + " | ".join(headers) + " |")
        
        # 数据行
        for i, row in enumerate(rows):
            row_class = "_striped" if striped and i % 2 == 1 else ""
            lines.append(f"| " + " | ".join(str(cell) for cell in row) + " |")
        
        self._sections.append("\n".join(lines) + "\n")
    
    def add_chart(self, chart: ChartData):
        """添加图表"""
        self._charts.append(chart)
        self._sections.append(chart.to_mermaid() + "\n")
    
    def add_warning(self, text: str, title: str = "⚠️ 注意"):
        """添加警告框"""
        warning = f"> ** {title} **\n>\n> {text}\n"
        self._sections.append(warning)
    
    def add_info(self, text: str, title: str = "💡 提示"):
        """添加信息框"""
        info = f"> ** {title} **\n>\n> {text}\n"
        self._sections.append(info)
    
    def add_code_block(self, code: str, language: str = ""):
        """添加代码块"""
        block = f"```{language}\n{code}\n```\n"
        self._sections.append(block)
    
    def add_divider(self):
        """添加分隔线"""
        self._sections.append("\n---\n")
    
    def add_image(self, image_path: str, alt_text: str = "", width: str = ""):
        """添加图片"""
        size_attr = f" width={width}" if width else ""
        self._sections.append(f"![{alt_text}]({image_path}){size_attr}\n")
    
    def add_list(self, items: List[str], ordered: bool = False):
        """添加列表"""
        lines = []
        for i, item in enumerate(items, 1):
            prefix = f"{i}." if ordered else "-"
            lines.append(f"{prefix} {item}")
        self._sections.append("\n".join(lines) + "\n")
    
    def add_kv_list(self, items: Dict[str, str]):
        """添加键值对列表"""
        lines = []
        for key, value in items.items():
            lines.append(f"- **{key}**: {value}")
        self._sections.append("\n".join(lines) + "\n")
    
    def add_emoji_table(self, items: List[tuple], emoji_getter=None):
        """
        添加表情列表
        
        Args:
            items: (标题, 数值) 元组列表
            emoji_getter: 获取表情的函数
        """
        lines = []
        for title, value in items:
            emoji = emoji_getter(value) if emoji_getter else ""
            if isinstance(value, (int, float)):
                lines.append(f"- {emoji} **{title}**: `{value:,.2f}`")
            else:
                lines.append(f"- {emoji} **{title}**: `{value}`")
        
        self._sections.append("\n".join(lines) + "\n")
    
    def generate(self) -> str:
        """生成 Markdown 报告"""
        lines = []
        
        # 元数据
        if self._metadata:
            lines.append("---")
            lines.append(f"title: {self._metadata.title}")
            lines.append(f"date: {self._metadata.date}")
            lines.append(f"author: {self._metadata.author}")
            lines.append(f"version: {self._metadata.version}")
            if self._metadata.tags:
                lines.append(f"tags: [{', '.join(self._metadata.tags)}]")
            lines.append("---")
            lines.append("")
        
        # 标题
        if self._metadata:
            lines.append(f"# {self._metadata.title}\n")
        
        # 内容
        lines.append("\n".join(self._sections))
        
        return "\n".join(lines)
    
    def save(self, filepath: str) -> str:
        """
        保存报告到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            保存的文件路径
        """
        content = self.generate()
        
        # 确保目录存在
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        path.write_text(content, encoding="utf-8")
        
        logger.info(f"报告已保存: {filepath}")
        return str(path)
    
    def preview(self, max_lines: int = 50) -> str:
        """
        预览报告（限制行数）
        
        Args:
            max_lines: 最大行数
            
        Returns:
            报告预览
        """
        content = self.generate()
        lines = content.split("\n")
        
        if len(lines) <= max_lines:
            return content
        
        preview = "\n".join(lines[:max_lines])
        preview += f"\n\n... (还有 {len(lines) - max_lines} 行)"
        
        return preview


class PDFExporter:
    """
    PDF 报告导出器
    
    将 Markdown 报告转换为 PDF 格式。
    支持多种渲染引擎：
    - WeasyPrint（推荐）
    - pdfkit + wkhtmltopdf
    - pandoc
    """
    
    def __init__(self):
        self._markdown_exporter = MarkdownExporter()
        self._engine = self._detect_engine()
    
    def _detect_engine(self) -> str:
        """检测可用的 PDF 渲染引擎"""
        # 按优先级尝试导入
        try:
            import weasyprint
            return "weasyprint"
        except ImportError:
            pass
        
        try:
            import pdfkit
            return "pdfkit"
        except ImportError:
            pass
        
        try:
            import subprocess
            result = subprocess.run(["pandoc", "--version"], capture_output=True)
            if result.returncode == 0:
                return "pandoc"
        except FileNotFoundError:
            pass
        
        return "none"
    
    def get_engine_name(self) -> str:
        """获取当前使用的引擎名称"""
        engines = {
            "weasyprint": "WeasyPrint (推荐)",
            "pdfkit": "pdfkit + wkhtmltopdf",
            "pandoc": "Pandoc",
            "none": "无可用引擎"
        }
        return engines.get(self._engine, "未知")
    
    def markdown_to_pdf(self, markdown_content: str, output_path: str) -> Optional[str]:
        """
        将 Markdown 转换为 PDF
        
        Args:
            markdown_content: Markdown 内容
            output_path: 输出路径
            
        Returns:
            生成的 PDF 文件路径，失败返回 None
        """
        if self._engine == "none":
            logger.warning("没有可用的 PDF 渲染引擎")
            return None
        
        # 确保目录存在
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if self._engine == "weasyprint":
                return self._convert_weasyprint(markdown_content, output_path)
            elif self._engine == "pdfkit":
                return self._convert_pdfkit(markdown_content, output_path)
            elif self._engine == "pandoc":
                return self._convert_pandoc(markdown_content, output_path)
        except Exception as e:
            logger.error(f"PDF 转换失败: {e}")
            return None
        
        return None
    
    def _convert_weasyprint(self, markdown: str, output: str) -> str:
        """使用 WeasyPrint 转换"""
        from weasyprint import HTML, CSS
        
        # 简单的 Markdown 到 HTML 转换
        html = self._markdown_to_html(markdown)
        
        # 添加样式
        css = CSS(string="""
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
                font-size: 12pt;
                line-height: 1.6;
            }
            h1 { font-size: 24pt; color: #333; border-bottom: 2px solid #333; }
            h2 { font-size: 18pt; color: #444; }
            h3 { font-size: 14pt; color: #555; }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th { background-color: #f5f5f5; }
            code {
                background-color: #f5f5f5;
                padding: 2px 4px;
                border-radius: 3px;
            }
            blockquote {
                border-left: 4px solid #ddd;
                padding-left: 1em;
                color: #666;
            }
        """)
        
        HTML(string=html).write_pdf(output, stylesheets=[css])
        return output
    
    def _convert_pdfkit(self, markdown: str, output: str) -> str:
        """使用 pdfkit 转换"""
        import pdfkit
        import markdown2
        
        html = markdown2.markdown(markdown, extras=['tables', 'fenced-code-blocks'])
        html = self._add_html_wrapper(html)
        
        pdfkit.from_string(html, output)
        return output
    
    def _convert_pandoc(self, markdown: str, output: str) -> str:
        """使用 Pandoc 转换"""
        import subprocess
        
        # 创建临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(markdown)
            temp_path = f.name
        
        try:
            cmd = [
                'pandoc', temp_path,
                '-o', output,
                '--pdf-engine=xelatex',
                '-V', 'mainfont=Microsoft YaHei',
                '-V', 'geometry:margin=2cm'
            ]
            subprocess.run(cmd, check=True)
            return output
        finally:
            os.unlink(temp_path)
    
    def _markdown_to_html(self, markdown: str) -> str:
        """简单的 Markdown 到 HTML 转换"""
        import re
        
        html = markdown
        
        # 标题
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # 粗体和斜体
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # 代码块
        html = re.sub(r'```(\w*)\n(.+?)\n```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        
        # 链接
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        
        # 列表
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # 段落
        html = re.sub(r'\n\n+', r'</p><p>', html)
        
        return self._add_html_wrapper(f'<p>{html}</p>')
    
    def _add_html_wrapper(self, content: str) -> str:
        """添加 HTML 包装"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Stock Analysis Report</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", "SimHei", sans-serif;
            font-size: 12pt;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        code {{ background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{
            border-left: 4px solid #3498db;
            background-color: #f0f7ff;
            padding: 10px 15px;
            margin: 15px 0;
        }}
        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px 15px;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""


def create_stock_analysis_report(
    stock_data: Dict[str, Any],
    output_path: Optional[str] = None,
    format: str = "md"
) -> str:
    """
    创建股票分析报告的便捷函数
    
    Args:
        stock_data: 股票数据
        output_path: 输出路径（不含扩展名）
        format: 输出格式 ("md", "pdf")
        
    Returns:
        生成的报告内容或文件路径
    """
    exporter = MarkdownExporter()
    
    # 设置元数据
    metadata = ReportMetadata(
        title=f"{stock_data.get('name', '股票')} ({stock_data.get('code', '')}) 分析报告",
        tags=["股票分析", "技术分析"]
    )
    exporter.set_metadata(metadata)
    
    # 添加内容
    exporter.add_heading("核心结论", 2)
    sentiment = stock_data.get("sentiment_score", 50)
    sentiment_emoji = "📈" if sentiment > 50 else "📉"
    exporter.add_kv_list({
        "情绪评分": f"{sentiment}/100",
        "操作建议": stock_data.get("operation_advice", ""),
        "信号类型": sentiment_emoji
    })
    
    exporter.add_heading("技术面分析", 2)
    if "dashboard" in stock_data:
        tech_data = stock_data["dashboard"].get("data_perspective", {})
        
        if "trend_status" in tech_data:
            exporter.add_paragraph(f"**趋势**: {tech_data['trend_status'].get('description', '')}")
        
        if "price_position" in tech_data:
            exporter.add_paragraph(f"**价格位置**: {tech_data['price_position'].get('description', '')}")
    
    exporter.add_warning("本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。")
    
    # 生成报告
    if format == "md":
        content = exporter.generate()
        if output_path:
            path = f"{output_path}.md"
            exporter.save(path)
            return path
        return content
    
    elif format == "pdf":
        pdf_exporter = PDFExporter()
        content = exporter.generate()
        
        if not output_path:
            output_path = f"stock_report_{stock_data.get('code', 'unknown')}"
        
        path = f"{output_path}.pdf"
        result = pdf_exporter.markdown_to_pdf(content, path)
        
        if result:
            return result
        else:
            logger.warning(f"PDF 转换失败，可用的引擎: {pdf_exporter.get_engine_name()}")
            # 回退到 Markdown
            md_path = f"{output_path}.md"
            exporter.save(md_path)
            return md_path
    
    return exporter.generate()


def create_hot_sectors_report(
    sectors_data: Dict[str, Any],
    output_path: Optional[str] = None,
    format: str = "md"
) -> str:
    """
    创建热点板块报告的便捷函数
    
    Args:
        sectors_data: 板块数据
        output_path: 输出路径（不含扩展名）
        format: 输出格式
        
    Returns:
        生成的报告
    """
    exporter = MarkdownExporter()
    
    metadata = ReportMetadata(
        title="市场热点板块追踪报告",
        tags=["热点板块", "市场分析"]
    )
    exporter.set_metadata(metadata)
    
    # 热门板块
    exporter.add_heading("热门板块 TOP 10", 2)
    
    top_sectors = sectors_data.get("top_sectors", [])
    headers = ["排名", "板块名称", "涨跌幅", "换手率", "热度指数", "趋势"]
    rows = []
    
    for i, sector in enumerate(top_sectors[:10], 1):
        rows.append([
            i,
            sector.get("name", ""),
            f"{sector.get('change_percent', 0):+.2f}%",
            f"{sector.get('turnover_rate', 0):.2f}%",
            f"{sector.get('heat_score', 0):.1f}",
            sector.get("trend", "")
        ])
    
    exporter.add_table(headers, rows)
    
    # 操作建议
    exporter.add_heading("操作建议", 2)
    exporter.add_list([
        "关注强势板块轮动机会",
        "注意热点切换节奏",
        "控制仓位，分散风险"
    ])
    
    exporter.add_warning("热点轮动较快，请注意风险控制。")
    
    # 生成
    if format == "md":
        content = exporter.generate()
        if output_path:
            path = f"{output_path}.md"
            exporter.save(path)
            return path
        return content
    
    return exporter.generate()
