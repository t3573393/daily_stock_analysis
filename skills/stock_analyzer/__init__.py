# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill
===================================

AI驱动的股票分析助手，提供专业的股票分析、市场复盘和投资建议。

使用方法:
    from skills.stock_analyzer import StockAnalyzerSkill, analyze, market_review
    
    # 创建 skill 实例
    skill = StockAnalyzerSkill()
    
    # 分析股票
    result = skill.process("/analyze 600989")
    print(result)
    
    # 或使用便捷函数
    result = analyze("600989")
    print(result)

配置:
    在 ~/.config/claude/stock_analyzer.yaml 创建配置文件:
    
    stock_analyzer:
      llm:
        provider: openai
        api_key: sk-your-api-key
        model: gpt-4o
      
      data_source:
        primary: akshare
        tushare_token: your-token
"""

__version__ = "1.0.0"
__author__ = "Dragon Stock Analyzer Team"

# 主要导出
from .commands import StockAnalyzerSkill, create_skill, analyze, market_review
from .config import (
    SkillConfig,
    LLMConfig,
    DataSourceConfig,
    AnalysisConfig,
    ConfigManager,
    get_config,
    get_config_manager,
)
from .formatter import ReportFormatter, SimpleFormatter, get_formatter
from .analyzer import StockAnalyzerService, AnalysisResultWrapper
from .hot_sectors import HotSectorTracker, HotSectorReport, SectorData, get_trend_ascii_chart

__all__ = [
    # 主类
    "StockAnalyzerSkill",
    "StockAnalyzerService",
    
    # 配置类
    "SkillConfig",
    "LLMConfig",
    "DataSourceConfig",
    "AnalysisConfig",
    "ConfigManager",
    
    # 格式化类
    "ReportFormatter",
    "SimpleFormatter",
    
    # 热点板块
    "HotSectorTracker",
    "HotSectorReport",
    "SectorData",
    "get_trend_ascii_chart",
    
    # 便捷函数
    "create_skill",
    "analyze",
    "market_review",
    "get_config",
    "get_config_manager",
    "get_formatter",
    
    # 其他
    "AnalysisResultWrapper",
]
