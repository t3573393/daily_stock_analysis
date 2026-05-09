# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill - 热点板块报告导出模块
===================================

功能：
1. 生成包含图表的热点板块报告
2. 支持动态趋势图表
3. 支持排名变化可视化
4. 输出 Markdown/PDF 格式
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .report_exporter import MarkdownExporter, ReportMetadata
from .chart_generator import ChartGenerator, ChartConfig
from .sector_history import SectorHistoryStore

logger = logging.getLogger(__name__)


class HotSectorReportExporter:
    """
    热点板块报告导出器
    
    生成包含图表的热点板块追踪报告。
    """
    
    def __init__(
        self,
        include_html_charts: bool = True,
        include_ascii_charts: bool = True
    ):
        """
        初始化导出器
        
        Args:
            include_html_charts: 是否包含 HTML 交互式图表
            include_ascii_charts: 是否包含 ASCII 文本图表
        """
        self.include_html = include_html_charts
        self.include_ascii = include_ascii_charts
        self.chart_generator = ChartGenerator(ChartConfig(width=700, height=350))
        self.history_store = SectorHistoryStore()

    def _generate_mock_trend_data(
        self,
        sectors: List[Dict],
        days: int = 30
    ) -> Dict[str, Dict]:
        """
        生成模拟历史趋势数据用于演示

        Args:
            sectors: 当前板块数据
            days: 模拟天数

        Returns:
            {板块名: {"dates": [...], "scores": [...]}}
        """
        import random
        random.seed(42)

        result = {}
        base_date = datetime.now()

        for sector in sectors[:5]:
            name = sector.get("name", f"Sector{len(result)}")
            current_score = sector.get("heat_score", 70)

            dates = []
            scores = []

            for i in range(days, 0, -1):
                date = (base_date - timedelta(days=i)).strftime("%Y-%m-%d")
                variation = random.uniform(-15, 15)
                score = max(10, min(100, current_score - (days - i) * 0.5 + variation))
                dates.append(date)
                scores.append(round(score, 1))

            result[name] = {"dates": dates, "scores": scores}

        return result

    def generate_report(
        self,
        current_sectors: List[Dict],
        days: int = 30,
        top_n: int = 10
    ) -> str:
        """
        生成热点板块报告（包含图表）
        
        Args:
            current_sectors: 当前板块数据
            days: 追踪天数
            top_n: 展示板块数量
            
        Returns:
            Markdown 格式的报告
        """
        exporter = MarkdownExporter()
        
        # 元数据
        metadata = ReportMetadata(
            title="市场热点板块追踪报告",
            author="Stock Analyzer",
            tags=["热点板块", "市场分析", "投资策略"]
        )
        exporter.set_metadata(metadata)
        
        # 标题
        exporter.add_heading("📊 市场热点板块追踪报告", 1)
        exporter.add_paragraph(f"**报告日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        exporter.add_paragraph(f"**追踪周期**: 近 {days} 个交易日")
        exporter.add_divider()
        
        # 保存当前数据到历史
        today = datetime.now().strftime("%Y-%m-%d")
        self.history_store.add_snapshot(today, current_sectors)
        
        # 1. 热门板块排行
        self._add_ranking_section(exporter, current_sectors, top_n)
        
        # 2. 热度趋势图表
        self._add_trend_charts(exporter, current_sectors, days, top_n)
        
        # 3. 排名变化图表
        self._add_rank_change_chart(exporter, current_sectors)
        
        # 4. 涨幅分布图表
        self._add_change_distribution_chart(exporter, current_sectors, top_n)
        
        # 5. 新晋/退潮热点
        self._add_hot_change_section(exporter)
        
        # 6. 操作建议
        self._add_suggestions(exporter, current_sectors)
        
        # 免责声明
        exporter.add_divider()
        exporter.add_warning(
            "免责声明：本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。"
        )
        
        return exporter.generate()
    
    def _add_ranking_section(
        self,
        exporter: MarkdownExporter,
        sectors: List[Dict],
        top_n: int
    ):
        """添加排行榜部分"""
        exporter.add_heading("🔥 热门板块 TOP 10（按热度）", 2)
        
        headers = ["排名", "板块名称", "涨跌幅", "热度指数", "趋势"]
        rows = []
        
        for i, sector in enumerate(sectors[:top_n], 1):
            change = sector.get("change_percent", 0)
            trend = sector.get("trend", "stable")
            trend_icon = "📈" if trend == "rising" else ("📉" if trend == "falling" else "➡️")
            
            change_str = f"{change:+.2f}%"
            change_style = f"**{change_str}**" if change > 0 else change_str
            
            rows.append([
                str(i),
                f"**{sector.get('name', '')}**",
                change_style,
                f"**{sector.get('heat_score', 0):.1f}**",
                trend_icon
            ])
        
        exporter.add_table(headers, rows)
        exporter.add_paragraph("")
    
    def _add_trend_charts(
        self,
        exporter: MarkdownExporter,
        sectors: List[Dict],
        days: int,
        top_n: int
    ):
        """添加趋势图表"""
        exporter.add_heading("📈 板块热度趋势", 2)
        exporter.add_paragraph("以下图表展示热门板块近期的热度变化趋势：")
        exporter.add_paragraph("")

        top_sectors = [s.get("name", f"Sector{i}") for i, s in enumerate(sectors[:5])]

        dates = self.history_store.get_dates()[-days:]
        historical_data = {}

        for date in dates:
            day_scores = self.history_store.get_all_sectors_scores(date)
            for sector_name in top_sectors:
                found = next((s for s in day_scores if s["name"] == sector_name), None)
                if found:
                    if sector_name not in historical_data:
                        historical_data[sector_name] = {"dates": [], "scores": []}
                    historical_data[sector_name]["dates"].append(date)
                    historical_data[sector_name]["scores"].append(found["score"])

        if not historical_data or all(len(v["scores"]) < 2 for v in historical_data.values()):
            mock_data = self._generate_mock_trend_data(sectors, days)
            historical_data = mock_data
            exporter.add_paragraph("*📌 当前为演示数据，实际使用时会显示真实历史趋势*")
            exporter.add_paragraph("")

        if self.include_html and historical_data:
            first_series = next(iter(historical_data.values()), None)
            chart_dates = first_series["dates"] if isinstance(first_series, dict) else dates[:30]
            html_chart = self.chart_generator.generate_trend_comparison_chart(
                {k: v["scores"] if isinstance(v, dict) else v for k, v in historical_data.items()},
                chart_dates,
                title="板块热度趋势对比"
            )
            exporter.add_paragraph("**交互式图表：**")
            exporter.add_code_block(html_chart, language="html")
            exporter.add_paragraph("")

        if self.include_ascii and top_sectors:
            for sector_name in top_sectors[:3]:
                if sector_name in historical_data:
                    data = historical_data[sector_name]
                    scores = data["scores"] if isinstance(data, dict) else data
                    chart_dates = data["dates"] if isinstance(data, dict) else dates[:len(scores)]
                else:
                    scores = []
                    chart_dates = []
                if len(scores) >= 2:
                    ascii_chart = self.chart_generator.generate_ascii_chart(
                        scores,
                        chart_dates,
                        title=f"{sector_name} 热度趋势"
                    )
                    exporter.add_code_block(ascii_chart)
                    exporter.add_paragraph("")
    
    def _add_rank_change_chart(
        self,
        exporter: MarkdownExporter,
        sectors: List[Dict]
    ):
        """添加排名变化图表"""
        exporter.add_heading("🔄 排名变化追踪", 2)
        
        dates = self.history_store.get_dates()
        if len(dates) < 2:
            exporter.add_paragraph("*暂无历史数据，无法计算排名变化*")
            exporter.add_paragraph("")
            return
        
        # 获取当前和之前的排名
        current_date = dates[-1]
        prev_date = dates[-2] if len(dates) >= 2 else None
        
        if not prev_date:
            exporter.add_paragraph("*暂无对比数据*")
            exporter.add_paragraph("")
            return
        
        current_scores = {s.get("name"): s.get("heat_score", 0) for s in sectors}
        
        current_ranks = {}
        prev_ranks = {}
        
        current_sectors = self.history_store.get_all_sectors_scores(current_date)
        for i, s in enumerate(current_sectors, 1):
            current_ranks[s["name"]] = i
        
        prev_sectors = self.history_store.get_all_sectors_scores(prev_date)
        for i, s in enumerate(prev_sectors, 1):
            prev_ranks[s["name"]] = i
        
        # 计算排名变化
        rank_changes = {}
        for sector_name in current_ranks:
            if sector_name in prev_ranks:
                rank_changes[sector_name] = prev_ranks[sector_name] - current_ranks[sector_name]
            else:
                rank_changes[sector_name] = 0  # 新上榜
        
        # 生成排名变化条形图
        sorted_changes = sorted(rank_changes.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if self.include_html:
            html_chart = self.chart_generator.generate_bar_chart(
                [c[1] for c in sorted_changes],
                [c[0] for c in sorted_changes],
                title="板块排名变化（正=上升，负=下降）",
                horizontal=True
            )
            exporter.add_paragraph("**排名变化条形图：**")
            exporter.add_code_block(html_chart, language="html")
            exporter.add_paragraph("")
        
        # 表格展示
        headers = ["板块名称", "昨日排名", "今日排名", "变化", "趋势"]
        rows = []
        
        for sector_name, change in sorted_changes[:10]:
            curr_rank = current_ranks.get(sector_name, "-")
            prev_rank = prev_ranks.get(sector_name, "-")
            
            if change > 0:
                change_str = f"📈 +{change}"
            elif change < 0:
                change_str = f"📉 {change}"
            else:
                change_str = "➡️ 不变"
            
            rows.append([
                sector_name,
                str(prev_rank),
                str(curr_rank),
                change_str,
                "上升" if change > 0 else ("下降" if change < 0 else "不变")
            ])
        
        exporter.add_table(headers, rows)
        exporter.add_paragraph("")
    
    def _add_change_distribution_chart(
        self,
        exporter: MarkdownExporter,
        sectors: List[Dict],
        top_n: int
    ):
        """添加涨跌幅分布图表"""
        exporter.add_heading("📊 涨跌幅分布", 2)
        
        # 按涨跌幅排序
        sorted_by_change = sorted(sectors[:top_n], key=lambda x: x.get("change_percent", 0), reverse=True)
        
        names = [s.get("name", "")[:8] for s in sorted_by_change]
        changes = [s.get("change_percent", 0) for s in sorted_by_change]
        
        # 生成柱状图
        if self.include_html:
            html_chart = self.chart_generator.generate_bar_chart(
                changes,
                names,
                title="热门板块涨跌幅分布"
            )
            exporter.add_paragraph("**涨跌幅柱状图：**")
            exporter.add_code_block(html_chart, language="html")
            exporter.add_paragraph("")
        
        # ASCII 条形图
        if self.include_ascii:
            exporter.add_paragraph("**涨跌幅对比：**")
            max_change = max(abs(c) for c in changes) if changes else 10
            for sector, change in zip(sorted_by_change, changes):
                bar_length = int(abs(change) / max_change * 30)
                bar = "█" * bar_length
                prefix = "" if change >= 0 else "-"
                exporter.add_paragraph(
                    f"{sector.get('name', ''):<10} [{prefix}{bar:<30}] {change:+.2f}%"
                )
            exporter.add_paragraph("")
    
    def _add_hot_change_section(self, exporter: MarkdownExporter):
        """添加热点变化部分"""
        exporter.add_heading("⭐ 热点轮动分析", 2)
        
        new_hot = self.history_store.get_new_hot_sectors()
        fading = self.history_store.get_fading_sectors()
        trending_up = self.history_store.get_trending_up(5)
        trending_down = self.history_store.get_trending_down(5)
        
        # 新晋热点
        if new_hot:
            exporter.add_heading("新晋热点 🆕", 3)
            for sector_name in new_hot[:5]:
                trend = self.history_store.get_sector_trend(sector_name)
                if trend:
                    score_change = trend.get("score_change", 0)
                    exporter.add_paragraph(
                        f"- **{sector_name}**: 热度变化 {score_change:+.1f}"
                    )
            exporter.add_paragraph("")
        
        # 退潮热点
        if fading:
            exporter.add_heading("退潮概念 🔻", 3)
            exporter.add_list([f"**{s}**" for s in fading[:5]])
            exporter.add_paragraph("")
        
        # 热度上升最快
        if trending_up:
            exporter.add_heading("热度上升最快 📈", 3)
            headers = ["板块名称", "热度变化", "当前热度"]
            rows = [
                [s["name"], f"{s['score_change']:+.1f}", f"{s['current_score']:.1f}"]
                for s in trending_up[:5]
            ]
            exporter.add_table(headers, rows)
            exporter.add_paragraph("")
        
        # 热度下降最快
        if trending_down:
            exporter.add_heading("热度下降最快 📉", 3)
            headers = ["板块名称", "热度变化", "当前热度"]
            rows = [
                [s["name"], f"{s['score_change']:+.1f}", f"{s['current_score']:.1f}"]
                for s in trending_down[:5]
            ]
            exporter.add_table(headers, rows)
            exporter.add_paragraph("")
    
    def _add_suggestions(
        self,
        exporter: MarkdownExporter,
        sectors: List[Dict]
    ):
        """添加操作建议"""
        exporter.add_heading("💡 操作建议", 2)
        
        # 强势板块
        strong = [s.get("name") for s in sectors[:5]]
        exporter.add_paragraph(f"**主线热点**: {', '.join(strong)}")
        exporter.add_paragraph("")
        
        # 建议列表
        suggestions = [
            "关注主线热点板块的回调机会",
            "配置热门板块龙头股",
            "控制仓位，分散风险",
            "设置止损位，严格执行",
            "关注资金轮动节奏"
        ]
        exporter.add_list(suggestions)
        
        # 仓位建议
        exporter.add_heading("仓位建议", 3)
        exporter.add_kv_list({
            "当前建议仓位": "60%-70%",
            "激进策略": "80%以内",
            "保守策略": "50%以内"
        })
    
    def save_report(
        self,
        content: str,
        output_path: str,
        format: str = "md"
    ) -> str:
        """
        保存报告
        
        Args:
            content: 报告内容
            output_path: 输出路径（不含扩展名）
            format: 输出格式
            
        Returns:
            保存的文件路径
        """
        if format == "md":
            path = f"{output_path}.md"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content, encoding="utf-8")
            return path
        
        elif format == "pdf":
            from .report_exporter import PDFExporter
            pdf_exporter = PDFExporter()
            path = f"{output_path}.pdf"
            result = pdf_exporter.markdown_to_pdf(content, path)
            return result if result else path
        
        return output_path
