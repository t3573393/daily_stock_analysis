# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill - 图表生成模块
===================================

功能：
1. 生成多种类型的图表（折线图、柱状图、饼图等）
2. 支持 ASCII 文本图表和 HTML 图表
3. 支持导出为图片文件（PNG/SVG）
4. 支持 Markdown 嵌入格式
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChartConfig:
    """图表配置"""
    width: int = 800
    height: int = 600
    title: str = ""
    x_label: str = ""
    y_label: str = ""
    show_grid: bool = True
    show_legend: bool = True
    colors: List[str] = None
    output_path: Optional[str] = None
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = [
                "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0",
                "#9966FF", "#FF9F40", "#FF6384", "#C9CBC9"
            ]


class ChartGenerator:
    """
    图表生成器
    
    支持多种输出格式：
    - ASCII 文本（终端显示）
    - HTML + Chart.js（交互式图表）
    - PNG/SVG（图片文件）
    - Markdown 嵌入格式
    """
    
    def __init__(self, config: Optional[ChartConfig] = None):
        self.config = config or ChartConfig()
    
    def generate_line_chart(
        self,
        data: List[float],
        labels: List[str] = None,
        title: str = "折线图",
        multi_series: List[Dict[str, Any]] = None
    ) -> str:
        """
        生成折线图
        
        Args:
            data: 数据列表
            labels: 标签列表
            title: 图表标题
            multi_series: 多系列数据 [{name, data, color}]
            
        Returns:
            HTML 格式的图表
        """
        if labels is None:
            labels = [f"Day {i+1}" for i in range(len(data))]
        
        # 单系列数据
        if multi_series is None:
            multi_series = [{"name": "数据", "data": data, "color": self.config.colors[0]}]
        
        return self._generate_html_chart(
            chart_type="line",
            labels=labels,
            series=multi_series,
            title=title
        )
    
    def generate_bar_chart(
        self,
        data: List[float],
        labels: List[str],
        title: str = "柱状图",
        horizontal: bool = False
    ) -> str:
        """生成柱状图"""
        series = [{
            "name": "数值",
            "data": data,
            "color": self.config.colors[0]
        }]
        
        return self._generate_html_chart(
            chart_type="bar",
            labels=labels,
            series=series,
            title=title,
            horizontal=horizontal
        )
    
    def generate_multi_bar_chart(
        self,
        data_dict: Dict[str, List[float]],
        labels: List[str],
        title: str = "多系列柱状图"
    ) -> str:
        """生成多系列柱状图"""
        series = []
        for i, (name, data) in enumerate(data_dict.items()):
            series.append({
                "name": name,
                "data": data,
                "color": self.config.colors[i % len(self.config.colors)]
            })
        
        return self._generate_html_chart(
            chart_type="bar",
            labels=labels,
            series=series,
            title=title
        )
    
    def generate_radar_chart(
        self,
        data: Dict[str, float],
        title: str = "雷达图"
    ) -> str:
        """生成雷达图"""
        labels = list(data.keys())
        values = list(data.values())
        
        series = [{
            "name": "指标",
            "data": values,
            "color": self.config.colors[0]
        }]
        
        return self._generate_html_chart(
            chart_type="radar",
            labels=labels,
            series=series,
            title=title
        )
    
    def _generate_html_chart(
        self,
        chart_type: str,
        labels: List[str],
        series: List[Dict[str, Any]],
        title: str = "",
        horizontal: bool = False
    ) -> str:
        """生成 HTML 格式的图表"""
        
        labels_json = str(labels).replace("'", '"')
        series_json = str(series).replace("'", '"')
        
        index_axis = "index" if horizontal else "x"
        orientation = "horizontal" if horizontal else "vertical"
        
        html = f"""
<div class="chart-container" style="position: relative; height:{self.config.height}px; width:{self.config.width}px;">
    <canvas id="chart-{id(self)}"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
(function() {{
    const ctx = document.getElementById('chart-{id(self)}');
    if (ctx) {{
        new Chart(ctx, {{
            type: '{chart_type}',
            data: {{
                labels: {labels_json},
                datasets: {series_json}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: '{index_axis}',
                plugins: {{
                    title: {{
                        display: {"true" if title else "false"},
                        text: '{title}',
                        font: {{ size: 16, weight: 'bold' }}
                    }},
                    legend: {{
                        display: {str(self.config.show_legend).lower()},
                        position: 'top'
                    }},
                    tooltip: {{
                        enabled: true,
                        mode: 'index',
                        intersect: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{
                            display: {str(self.config.show_grid).lower()}
                        }}
                    }},
                    x: {{
                        grid: {{
                            display: {str(self.config.show_grid).lower()}
                        }}
                    }}
                }}
            }}
        }});
    }}
}})();
</script>
"""
        return html
    
    def generate_ascii_chart(
        self,
        data: List[float],
        labels: List[str] = None,
        title: str = "",
        width: int = 50,
        height: int = 15
    ) -> str:
        """生成 ASCII 文本图表"""
        if not data or len(data) < 2:
            return "数据不足，无法生成图表"
        
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        for i, val in enumerate(data):
            x = int(i / (len(data) - 1) * (width - 1))
            y = height - 1 - int((val - min_val) / range_val * (height - 1))
            y = max(0, min(height - 1, y))
            grid[y][x] = '●'
        
        for i in range(len(data) - 1):
            x1 = int(i / (len(data) - 1) * (width - 1))
            x2 = int((i + 1) / (len(data) - 1) * (width - 1))
            y1 = height - 1 - int((data[i] - min_val) / range_val * (height - 1))
            y2 = height - 1 - int((data[i + 1] - min_val) / range_val * (height - 1))
            
            y1 = max(0, min(height - 1, y1))
            y2 = max(0, min(height - 1, y2))
            
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx - dy
            
            x, y = x1, y1
            while True:
                if 0 <= x < width and 0 <= y < height and grid[y][x] == ' ':
                    grid[y][x] = '•'
                if x == x2 and y == y2:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x += sx
                if e2 < dx:
                    err += dx
                    y += sy
        
        lines = []
        if title:
            lines.append(f"【{title}】")
            lines.append("")
        
        for i in range(height):
            y_val = min_val + (height - 1 - i) / (height - 1) * range_val
            line = f"{y_val:>8.1f} │ " + ''.join(grid[i])
            lines.append(line)
        
        lines.append("         └" + "─" * width)
        
        if labels and len(labels) <= width:
            tick_count = min(5, len(labels))
            for t in range(tick_count):
                pos = int(t / (tick_count - 1) * (width - 1)) if tick_count > 1 else 0
                idx = int(t / (tick_count - 1) * (len(labels) - 1)) if tick_count > 1 else 0
                label = labels[idx][:8] if labels[idx] else str(idx)
                spaces = " " * pos
                lines.append(f"         {spaces}{label}")
        
        lines.append("")
        lines.append(f"数据范围: {min_val:.2f} ~ {max_val:.2f}")
        
        return '\n'.join(lines)
    
    def generate_trend_comparison_chart(
        self,
        sectors_data: Dict[str, List[float]],
        dates: List[str],
        title: str = "板块热点趋势对比"
    ) -> str:
        """
        生成趋势对比图（多板块折线对比）
        
        Args:
            sectors_data: {板块名称: [数据列表]}
            dates: 日期列表
            title: 图表标题
            
        Returns:
            HTML 格式的图表
        """
        series = []
        for i, (name, data) in enumerate(sectors_data.items()):
            series.append({
                "name": name,
                "data": data,
                "color": self.config.colors[i % len(self.config.colors)],
                "tension": 0.3,
                "fill": False
            })
        
        return self._generate_html_chart(
            chart_type="line",
            labels=dates,
            series=series,
            title=title
        )
    
    def generate_heat_map_data(
        self,
        sectors: List[str],
        dates: List[str],
        data_matrix: List[List[float]]
    ) -> str:
        """
        生成热力图数据
        
        Args:
            sectors: 板块列表
            dates: 日期列表
            data_matrix: 数据矩阵 [板块数][天数]
            
        Returns:
            HTML 格式的热力图
        """
        labels_json = str(sectors).replace("'", '"')
        
        # 转换为 Chart.js 热力图格式
        datasets = []
        for i, sector in enumerate(sectors):
            datasets.append({
                "label": sector,
                "data": [{"x": dates[j], "y": data, "v": data} 
                        for j, data in enumerate(data_matrix[i])],
                "backgroundColor": self._get_color_for_value(data_matrix[i])
            })
        
        html = f"""
<div class="heatmap-container" style="overflow-x: auto;">
    <canvas id="heatmap-{id(self)}"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-matrix"></script>
<script>
(function() {{
    const ctx = document.getElementById('heatmap-{id(self)}');
    if (ctx) {{
        new Chart(ctx, {{
            type: 'matrix',
            data: {{
                datasets: {str(datasets).replace("'", '"')}
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: '板块热点热力图'
                    }},
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.raw.label + ': ' + context.raw.v;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'category',
                        labels: {labels_json}
                    }},
                    y: {{
                        type: 'category'
                    }}
                }}
            }}
        }});
    }}
}})();
</script>
"""
        return html
    
    def _get_color_for_value(self, values: List[float]) -> List[str]:
        """根据数值获取颜色"""
        colors = []
        min_val = min(values) if values else 0
        max_val = max(values) if values else 1
        
        for v in values:
            ratio = (v - min_val) / (max_val - min_val) if max_val != min_val else 0.5
            if ratio > 0.7:
                colors.append("#FF6384")  # 红色 - 高热度
            elif ratio > 0.4:
                colors.append("#FFCE56")  # 黄色 - 中热度
            else:
                colors.append("#4BC0C0")  # 绿色 - 低热度
        
        return colors
    
    def save_chart_as_html(self, chart_html: str, output_path: str) -> str:
        """将图表保存为 HTML 文件"""
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Stock Analysis Chart</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .chart-wrapper {{
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: white;
        }}
    </style>
</head>
<body>
    <div class="chart-wrapper">
        {chart_html}
    </div>
</body>
</html>"""
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(full_html, encoding="utf-8")
        
        logger.info(f"图表已保存: {output_path}")
        return str(path)
    
    def embed_chart_for_markdown(self, chart_html: str) -> str:
        """将图表转换为 Markdown 嵌入格式"""
        return f'\n<!-- Chart -->\n{chart_html}\n<!-- /Chart -->\n'
    
    def generate_markdown_with_chart(
        self,
        title: str,
        description: str,
        chart_html: str,
        ascii_chart: str = None
    ) -> str:
        """
        生成包含图表的 Markdown 内容
        
        Args:
            title: 标题
            description: 描述
            chart_html: HTML 图表
            ascii_chart: ASCII 图表（备用）
            
        Returns:
            Markdown 格式的内容
        """
        md = f"""
### {title}

{description}

**交互式图表：**

{chart_html}

**文本图表（兼容版）：**

```
{ascii_chart or "（请在支持 HTML 的环境中查看上方图表）"}
```
"""
        return md


def create_trend_chart(
    historical_data: Dict[str, List[Dict]],
    sectors: List[str] = None,
    output_path: Optional[str] = None
) -> Tuple[str, str]:
    """
    创建热点板块趋势图
    
    Args:
        historical_data: 历史数据 {日期: [{板块名, 热度指数, 涨跌幅}]}
        sectors: 要展示的板块列表（默认取前5）
        output_path: 输出路径
        
    Returns:
        (HTML图表, ASCII图表)
    """
    generator = ChartGenerator()
    
    # 提取日期和系列数据
    dates = sorted(historical_data.keys())
    
    # 获取需要展示的板块
    if sectors is None:
        latest_data = historical_data.get(dates[-1], []) if dates else []
        sectors = [d.get("name", f"Sector{i}") for i, d in enumerate(latest_data[:5])]
    
    # 构建数据
    sectors_data = {}
    for sector in sectors:
        data = []
        for date in dates:
            sector_data = historical_data.get(date, [])
            found = next((s.get("heat_score", 0) for s in sector_data if s.get("name") == sector), 0)
            data.append(found)
        sectors_data[sector] = data
    
    # 生成 HTML 图表
    html_chart = generator.generate_trend_comparison_chart(
        sectors_data,
        dates,
        title="板块热点趋势对比"
    )
    
    # 生成 ASCII 图表
    if sectors:
        ascii_chart = generator.generate_ascii_chart(
            sectors_data[sectors[0]],
            dates,
            title=f"{sectors[0]} 热度趋势"
        )
    else:
        ascii_chart = "暂无数据"
    
    # 保存 HTML 文件
    if output_path:
        html_path = f"{output_path}.html"
        generator.save_chart_as_html(html_chart, html_path)
    
    return html_chart, ascii_chart


def generate_sector_change_chart(
    rank_changes: Dict[str, int],
    current_scores: Dict[str, float]
) -> str:
    """
    生成板块排名变化图
    
    Args:
        rank_changes: 板块排名变化 {板块名: 变化值}
        current_scores: 当前热度 {板块名: 热度值}
        
    Returns:
        HTML 图表
    """
    generator = ChartGenerator()
    
    # 按变化排序
    sorted_sectors = sorted(rank_changes.items(), key=lambda x: x[1], reverse=True)
    
    labels = [s[0] for s in sorted_sectors]
    changes = [s[1] for s in sorted_sectors]
    scores = [current_scores.get(s, 0) for s in labels]
    
    # 生成双向柱状图
    bar_colors = []
    for c in changes:
        if c > 0:
            bar_colors.append("#4BC0C0")  # 上升 - 绿色
        elif c < 0:
            bar_colors.append("#FF6384")  # 下降 - 红色
        else:
            bar_colors.append("#C9CBC9")  # 不变 - 灰色
    
    series = [{
        "name": "排名变化",
        "data": changes,
        "backgroundColor": bar_colors
    }]
    
    return generator._generate_html_chart(
        chart_type="bar",
        labels=labels,
        series=series,
        title="板块排名变化（相比昨日）"
    )
