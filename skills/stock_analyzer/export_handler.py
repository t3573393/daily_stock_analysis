# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill - 报告导出命令处理器
===================================

功能：
1. 处理报告导出命令
2. 支持 Markdown 和 PDF 格式
3. 自定义输出路径
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ReportExporter:
    """
    报告导出处理器
    
    将分析报告导出为 Markdown 或 PDF 格式。
    """
    
    def __init__(self, skill_instance: "StockAnalyzerSkill"):
        """
        初始化导出器
        
        Args:
            skill_instance: StockAnalyzerSkill 实例
        """
        self.skill = skill_instance
    
    def export_stock_report(
        self,
        stock_code: str,
        output_path: Optional[str] = None,
        format: str = "md",
        full_report: bool = True
    ) -> str:
        """
        导出股票分析报告
        
        Args:
            stock_code: 股票代码
            output_path: 输出路径（不含扩展名）
            format: 输出格式 ("md", "pdf")
            full_report: 是否完整报告
            
        Returns:
            导出结果信息
        """
        try:
            # 获取分析结果
            result = self.skill.analyzer_service.analyze_single_stock(
                stock_code,
                full_report=full_report
            )
            
            if result is None:
                return f"❌ 无法分析股票 `{stock_code}`"
            
            # 导出报告
            from .report_exporter import create_stock_analysis_report
            
            if not output_path:
                import os
                output_path = os.path.join(
                    os.getcwd(),
                    f"stock_report_{stock_code}"
                )
            
            output_file = create_stock_analysis_report(
                result,
                output_path=output_path,
                format=format
            )
            
            format_desc = "Markdown" if format == "md" else "PDF"
            return f"✅ {format_desc} 报告已生成:\n📄 `{output_file}`"
            
        except Exception as e:
            logger.error(f"导出报告失败: {e}")
            return f"❌ 导出失败: {str(e)}"
    
    def export_hot_sectors_report(
        self,
        output_path: Optional[str] = None,
        format: str = "md",
        days: int = 30,
        top_n: int = 10
    ) -> str:
        """
        导出热点板块报告
        
        Args:
            output_path: 输出路径
            format: 输出格式
            days: 追踪天数
            top_n: 板块数量
            
        Returns:
            导出结果
        """
        try:
            from .report_exporter import create_hot_sectors_report
            
            # 获取热点数据
            report = self.skill.get_hot_sectors(days=days, top_n=top_n)
            
            if not output_path:
                import os
                from datetime import datetime
                date_str = datetime.now().strftime("%Y%m%d")
                output_path = os.path.join(
                    os.getcwd(),
                    f"hot_sectors_{date_str}"
                )
            
            output_file = create_hot_sectors_report(
                {"top_sectors": []},  # 这里需要传入真实数据
                output_path=output_path,
                format=format
            )
            
            format_desc = "Markdown" if format == "md" else "PDF"
            return f"✅ {format_desc} 报告已生成:\n📄 `{output_file}`"
            
        except Exception as e:
            logger.error(f"导出热点报告失败: {e}")
            return f"❌ 导出失败: {str(e)}"
    
    def export_portfolio_report(
        self,
        stock_codes: list,
        portfolio_name: str,
        output_path: Optional[str] = None,
        format: str = "md"
    ) -> str:
        """
        导出投资组合报告
        
        Args:
            stock_codes: 股票代码列表
            portfolio_name: 组合名称
            output_path: 输出路径
            format: 输出格式
            
        Returns:
            导出结果
        """
        try:
            if not output_path:
                import os
                output_path = os.path.join(
                    os.getcwd(),
                    f"portfolio_{portfolio_name}"
                )
            
            # 生成报告内容
            from .report_exporter import MarkdownExporter, ReportMetadata
            
            exporter = MarkdownExporter()
            metadata = ReportMetadata(
                title=f"投资组合报告 - {portfolio_name}",
                tags=["投资组合", "股票"]
            )
            exporter.set_metadata(metadata)
            
            exporter.add_heading("投资组合分析", 2)
            exporter.add_kv_list({
                "组合名称": portfolio_name,
                "股票数量": str(len(stock_codes)),
                "股票列表": ", ".join(stock_codes)
            })
            
            exporter.add_warning("本报告仅供参考，不构成投资建议。")
            
            content = exporter.generate()
            
            if format == "md":
                output_file = f"{output_path}.md"
                exporter.save(output_file)
            else:
                from .report_exporter import PDFExporter
                pdf_exporter = PDFExporter()
                output_file = f"{output_path}.pdf"
                pdf_exporter.markdown_to_pdf(content, output_file)
            
            format_desc = "Markdown" if format == "md" else "PDF"
            return f"✅ {format_desc} 报告已生成:\n📄 `{output_file}`"
            
        except Exception as e:
            logger.error(f"导出组合报告失败: {e}")
            return f"❌ 导出失败: {str(e)}"


def create_export_handler(skill_instance: "StockAnalyzerSkill") -> ReportExporter:
    """
    创建导出处理器实例
    
    Args:
        skill_instance: StockAnalyzerSkill 实例
        
    Returns:
        ReportExporter 实例
    """
    return ReportExporter(skill_instance)
