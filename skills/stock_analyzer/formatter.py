# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill - 对话式输出格式化
===================================

职责：
1. 将分析结果转换为人类可读的对话式文本
2. 支持多种输出格式（Markdown、纯文本）
3. 支持中英文输出
4. 提供丰富的表情符号和格式化
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class ReportFormatter:
    """
    报告格式化器
    
    将结构化的分析结果转换为适合对话界面展示的文本格式。
    """
    
    # 情绪分数对应的表情
    SENTIMENT_EMOJIS = {
        (0, 30): "🔴",      # 极度悲观
        (30, 45): "🟠",     # 悲观
        (45, 55): "🟡",     # 中性
        (55, 70): "🟢",     # 乐观
        (70, 100): "🚀",    # 极度乐观
    }
    
    # 决策类型对应的表情和建议
    DECISION_STYLES = {
        "buy": ("🟢", "买入", "建议积极介入"),
        "hold": ("🟡", "持有", "建议继续持有观望"),
        "sell": ("🔴", "卖出", "建议减仓或离场"),
        "watch": ("👀", "观望", "建议保持观望"),
    }
    
    def __init__(self, language: str = "zh"):
        """
        初始化格式化器
        
        Args:
            language: 输出语言（"zh" 或 "en"）
        """
        self.language = language
    
    def format_single_stock_report(self, result: Dict[str, Any]) -> str:
        """
        格式化单股分析报告
        
        Args:
            result: 分析结果字典
            
        Returns:
            格式化后的报告文本
        """
        if not result:
            return self._get_error_message("无法获取分析结果")
        
        code = result.get("code", "")
        name = result.get("name", "")
        sentiment_score = result.get("sentiment_score", 50)
        operation_advice = result.get("operation_advice", "")
        decision_type = result.get("decision_type", "watch")
        dashboard = result.get("dashboard", {})
        
        # 获取情绪表情
        sentiment_emoji = self._get_sentiment_emoji(sentiment_score)
        
        # 获取决策样式
        decision_emoji, decision_text, decision_desc = self.DECISION_STYLES.get(
            decision_type, ("⚪", "未知", "")
        )
        
        lines = []
        
        # 标题
        lines.append(f"📊 **{name} ({code}) 分析报告**")
        lines.append("")
        
        # 核心结论
        lines.append("🎯 核心结论")
        lines.append(f"{sentiment_emoji} 情绪得分: {sentiment_score}/100")
        lines.append(f"{decision_emoji} 操作建议: {operation_advice or decision_desc}")
        lines.append("")
        
        # 核心结论详情
        core_conclusion = dashboard.get("core_conclusion", {})
        if core_conclusion:
            one_sentence = core_conclusion.get("one_sentence", "")
            if one_sentence:
                lines.append(f"💡 {one_sentence}")
                lines.append("")
        
        # 技术面分析
        data_perspective = dashboard.get("data_perspective", {})
        if data_perspective:
            lines.append("📈 技术面分析")
            
            trend = data_perspective.get("trend_status", {})
            if trend:
                trend_desc = trend.get("description", "")
                if trend_desc:
                    lines.append(f"- 趋势: {trend_desc}")
            
            price_pos = data_perspective.get("price_position", {})
            if price_pos:
                pos_desc = price_pos.get("description", "")
                if pos_desc:
                    lines.append(f"- 价格位置: {pos_desc}")
            
            volume = data_perspective.get("volume_analysis", {})
            if volume:
                vol_desc = volume.get("description", "")
                if vol_desc:
                    lines.append(f"- 量能: {vol_desc}")
            
            chip = data_perspective.get("chip_structure", {})
            if chip:
                chip_desc = chip.get("description", "")
                if chip_desc:
                    lines.append(f"- 筹码: {chip_desc}")
            
            lines.append("")
        
        # 情报面
        intelligence = dashboard.get("intelligence", {})
        if intelligence:
            lines.append("📰 市场情报")
            
            # 积极因素
            catalysts = intelligence.get("positive_catalysts", [])
            if catalysts:
                lines.append("✅ 积极因素:")
                for catalyst in catalysts[:3]:  # 最多显示3条
                    lines.append(f"  • {catalyst}")
            
            # 风险警报
            risks = intelligence.get("risk_alerts", [])
            if risks:
                lines.append("⚠️ 风险因素:")
                for risk in risks[:3]:  # 最多显示3条
                    lines.append(f"  • {risk}")
            
            lines.append("")
        
        # 操作策略
        battle_plan = dashboard.get("battle_plan", {})
        if battle_plan:
            lines.append("🎯 操作策略")
            
            sniper = battle_plan.get("sniper_points", {})
            if sniper:
                entry = sniper.get("entry", "")
                stop_loss = sniper.get("stop_loss", "")
                target = sniper.get("target", "")
                
                if entry:
                    lines.append(f"- 买入区间: {entry}")
                if stop_loss:
                    lines.append(f"- 止损位: {stop_loss}")
                if target:
                    lines.append(f"- 目标位: {target}")
            
            position = battle_plan.get("position_strategy", {})
            if position:
                position_desc = position.get("description", "")
                if position_desc:
                    lines.append(f"- 仓位建议: {position_desc}")
            
            risk_ctrl = battle_plan.get("risk_control", [])
            if risk_ctrl:
                lines.append("- 风险控制:")
                for ctrl in risk_ctrl[:3]:
                    lines.append(f"  • {ctrl}")
            
            lines.append("")
        
        # 免责声明
        lines.append("---")
        lines.append("*⚠️ 免责声明: 以上分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。*")
        
        return "\n".join(lines)
    
    def format_multiple_stocks_report(
        self, 
        results: List[Dict[str, Any]], 
        comparison_mode: bool = False
    ) -> str:
        """
        格式化多股分析报告
        
        Args:
            results: 分析结果列表
            comparison_mode: 是否启用对比模式
            
        Returns:
            格式化后的报告文本
        """
        if not results:
            return self._get_error_message("无法获取分析结果")
        
        lines = []
        lines.append(f"📊 **多股分析报告 ({len(results)} 只)**")
        lines.append("")
        
        if comparison_mode and len(results) > 1:
            # 对比模式：显示对比表格
            lines.append("📈 综合对比")
            lines.append("")
            lines.append("| 股票 | 情绪得分 | 操作建议 | 趋势 |")
            lines.append("|------|---------|---------|------|")
            
            for result in results:
                code = result.get("code", "")
                name = result.get("name", "")
                sentiment = result.get("sentiment_score", 50)
                advice = result.get("operation_advice", "")[:20]  # 截断
                
                dashboard = result.get("dashboard", {})
                data_perspective = dashboard.get("data_perspective", {})
                trend = data_perspective.get("trend_status", {})
                trend_desc = trend.get("description", "")[:10]  # 截断
                
                lines.append(f"| {name}({code}) | {sentiment} | {advice} | {trend_desc} |")
            
            lines.append("")
        
        # 每只股票的简要分析
        for i, result in enumerate(results, 1):
            code = result.get("code", "")
            name = result.get("name", "")
            sentiment_score = result.get("sentiment_score", 50)
            operation_advice = result.get("operation_advice", "")
            
            sentiment_emoji = self._get_sentiment_emoji(sentiment_score)
            
            lines.append(f"{i}. **{name} ({code})**")
            lines.append(f"   {sentiment_emoji} 情绪: {sentiment_score}/100 | 💡 {operation_advice[:30]}")
            lines.append("")
        
        # 免责声明
        lines.append("---")
        lines.append("*⚠️ 免责声明: 以上分析仅供参考，不构成投资建议。*")
        
        return "\n".join(lines)
    
    def format_market_review_report(self, report_text: str) -> str:
        """
        格式化大盘复盘报告
        
        Args:
            report_text: 原始复盘报告文本
            
        Returns:
            格式化后的报告文本
        """
        if not report_text:
            return self._get_error_message("无法获取大盘复盘报告")
        
        # 添加标题和格式化
        lines = []
        lines.append("📊 **A股市场复盘**")
        lines.append("")
        lines.append(report_text)
        lines.append("")
        lines.append("---")
        lines.append("*⚠️ 免责声明: 以上分析仅供参考，不构成投资建议。*")
        
        return "\n".join(lines)
    
    def format_portfolio_report(
        self, 
        results: List[Dict[str, Any]], 
        portfolio_name: str = "我的组合"
    ) -> str:
        """
        格式化投资组合报告
        
        Args:
            results: 组合中各股票的分析结果
            portfolio_name: 组合名称
            
        Returns:
            格式化后的报告文本
        """
        if not results:
            return self._get_error_message("组合为空或无法获取分析结果")
        
        lines = []
        lines.append(f"📊 **{portfolio_name} 分析报告**")
        lines.append("")
        
        # 计算组合整体情绪
        avg_sentiment = sum(r.get("sentiment_score", 50) for r in results) / len(results)
        sentiment_emoji = self._get_sentiment_emoji(avg_sentiment)
        
        lines.append(f"📈 组合概况")
        lines.append(f"- 股票数量: {len(results)} 只")
        lines.append(f"- 平均情绪: {sentiment_emoji} {avg_sentiment:.1f}/100")
        lines.append("")
        
        # 买入/卖出建议统计
        buy_signals = [r for r in results if r.get("decision_type") == "buy"]
        sell_signals = [r for r in results if r.get("decision_type") == "sell"]
        hold_signals = [r for r in results if r.get("decision_type") == "hold"]
        
        lines.append("🎯 信号分布")
        lines.append(f"- 🟢 买入信号: {len(buy_signals)} 只")
        lines.append(f"- 🟡 持有信号: {len(hold_signals)} 只")
        lines.append(f"- 🔴 卖出信号: {len(sell_signals)} 只")
        lines.append("")
        
        # 重点关注股票
        if buy_signals:
            lines.append("✨ 重点关注（买入信号）")
            for r in buy_signals[:5]:
                code = r.get("code", "")
                name = r.get("name", "")
                advice = r.get("operation_advice", "")
                lines.append(f"- {name}({code}): {advice[:30]}")
            lines.append("")
        
        if sell_signals:
            lines.append("⚠️ 风险提示（卖出信号）")
            for r in sell_signals[:3]:
                code = r.get("code", "")
                name = r.get("name", "")
                advice = r.get("operation_advice", "")
                lines.append(f"- {name}({code}): {advice[:30]}")
            lines.append("")
        
        # 免责声明
        lines.append("---")
        lines.append("*⚠️ 免责声明: 以上分析仅供参考，不构成投资建议。*")
        
        return "\n".join(lines)
    
    def format_backtest_report(
        self, 
        strategy_name: str, 
        stock_code: str, 
        backtest_result: Dict[str, Any]
    ) -> str:
        """
        格式化回测报告
        
        Args:
            strategy_name: 策略名称
            stock_code: 股票代码
            backtest_result: 回测结果
            
        Returns:
            格式化后的报告文本
        """
        lines = []
        lines.append(f"📊 **策略回测报告**")
        lines.append("")
        lines.append(f"策略: {strategy_name}")
        lines.append(f"标的: {stock_code}")
        lines.append("")
        
        if not backtest_result:
            lines.append("❌ 回测失败，无法获取结果")
            return "\n".join(lines)
        
        # 回测结果
        total_return = backtest_result.get("total_return", 0)
        max_drawdown = backtest_result.get("max_drawdown", 0)
        sharpe_ratio = backtest_result.get("sharpe_ratio", 0)
        trade_count = backtest_result.get("trade_count", 0)
        
        lines.append("📈 回测结果")
        lines.append(f"- 总收益率: {total_return:+.2f}%")
        lines.append(f"- 最大回撤: {max_drawdown:.2f}%")
        lines.append(f"- 夏普比率: {sharpe_ratio:.2f}")
        lines.append(f"- 交易次数: {trade_count} 次")
        lines.append("")
        
        # 免责声明
        lines.append("---")
        lines.append("*⚠️ 免责声明: 历史回测不代表未来表现，仅供参考。*")
        
        return "\n".join(lines)
    
    def format_error_message(self, error: str, suggestion: str = "") -> str:
        """
        格式化错误消息
        
        Args:
            error: 错误信息
            suggestion: 建议
            
        Returns:
            格式化后的错误消息
        """
        lines = []
        lines.append("❌ **分析失败**")
        lines.append("")
        lines.append(f"错误: {error}")
        
        if suggestion:
            lines.append("")
            lines.append(f"💡 建议: {suggestion}")
        
        return "\n".join(lines)
    
    def _get_sentiment_emoji(self, score: int) -> str:
        """根据情绪分数获取对应的表情"""
        for (low, high), emoji in self.SENTIMENT_EMOJIS.items():
            if low <= score < high:
                return emoji
        return "⚪"
    
    def _get_error_message(self, message: str) -> str:
        """获取错误消息"""
        return self.format_error_message(
            message,
            "请检查股票代码是否正确，或稍后重试。"
        )
    
    def format_hot_sectors_report(self, report: "HotSectorReport", show_chart: bool = True) -> str:
        """
        格式化热点板块报告
        
        Args:
            report: HotSectorReport 对象
            show_chart: 是否显示图表
            
        Returns:
            格式化后的热点板块报告
        """
        if not report:
            return self._get_error_message("无法获取热点板块数据")
        
        lines = []
        
        # 标题
        lines.append(f"🔥 **市场热点板块追踪报告**")
        lines.append(f"📅 日期: {report.date}")
        lines.append("")
        
        # 热门板块排行
        if report.top_sectors:
            lines.append("📈 **热门板块 TOP 10**")
            lines.append("")
            lines.append("| 排名 | 板块名称 | 涨跌幅 | 换手率 | 热度指数 | 趋势 |")
            lines.append("|------|---------|-------|--------|---------|------|")
            
            for i, sector in enumerate(report.top_sectors[:10], 1):
                change_str = f"{sector.change_percent:+.2f}%"
                trend_emoji = "📈" if sector.trend == "rising" else ("📉" if sector.trend == "falling" else "➡️")
                lines.append(f"| {i} | {sector.name} | {change_str} | {sector.turnover_rate:.2f}% | {sector.heat_score:.1f} | {trend_emoji} |")
            
            lines.append("")
        
        # 涨幅概念
        if report.rising_concepts:
            lines.append("🚀 **强势概念**")
            lines.append("  " + " | ".join([f"`{c}`" for c in report.rising_concepts[:8]]))
            lines.append("")
        
        # 弱势概念
        if report.falling_concepts:
            lines.append("📉 **弱势概念**")
            lines.append("  " + " | ".join([f"`{c}`" for c in report.falling_concepts[:8]]))
            lines.append("")
        
        # 新晋热点
        if report.new_hot_concepts:
            lines.append("⭐ **新晋热点**")
            lines.append("  " + " | ".join([f"`{c}`" for c in report.new_hot_concepts]))
            lines.append("")
        
        # 退潮概念
        if report.fading_concepts:
            lines.append("💨 **退潮概念**")
            lines.append("  " + " | ".join([f"`{c}`" for c in report.fading_concepts]))
            lines.append("")
        
        # 热度分布图
        if show_chart and report.top_sectors:
            lines.append("📊 **热度分布**")
            lines.append("")
            for sector in report.top_sectors[:8]:
                bar_length = int(sector.heat_score / 2)
                bar = "█" * bar_length + "░" * (50 - bar_length)
                change_str = f"{sector.change_percent:+.1f}%"
                lines.append(f"{sector.name:<12} [{bar}] {change_str} ({sector.heat_score:.0f})")
            lines.append("")
        
        # 投资建议
        lines.append("💡 **操作建议**")
        if report.top_sectors:
            top_3 = [s.name for s in report.top_sectors[:3]]
            lines.append(f"- 关注强势板块: {', '.join(top_3)}")
            lines.append("- 建议配置热门板块龙头股")
            lines.append("- 注意轮动节奏，避免追高")
        lines.append("")
        
        # 免责声明
        lines.append("---")
        lines.append("*⚠️ 免责声明: 以上分析仅供参考，不构成投资建议。热点轮动较快，请注意风险。*")
        
        return "\n".join(lines)


class SimpleFormatter(ReportFormatter):
    """
    简化版格式化器
    
    生成更简洁的输出，适合快速查看。
    """
    
    def format_single_stock_report(self, result: Dict[str, Any]) -> str:
        """简化版单股报告"""
        if not result:
            return self._get_error_message("无法获取分析结果")
        
        code = result.get("code", "")
        name = result.get("name", "")
        sentiment_score = result.get("sentiment_score", 50)
        operation_advice = result.get("operation_advice", "")
        
        sentiment_emoji = self._get_sentiment_emoji(sentiment_score)
        
        lines = [
            f"📊 {name} ({code})",
            f"{sentiment_emoji} 情绪: {sentiment_score}/100",
            f"💡 {operation_advice}",
            "",
            "*仅供参考，不构成投资建议*"
        ]
        
        return "\n".join(lines)


def get_formatter(language: str = "zh", simple_mode: bool = False) -> ReportFormatter:
    """
    获取格式化器实例
    
    Args:
        language: 输出语言
        simple_mode: 是否使用简化模式
        
    Returns:
        ReportFormatter 实例
    """
    if simple_mode:
        return SimpleFormatter(language)
    return ReportFormatter(language)
