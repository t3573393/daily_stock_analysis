# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill - 核心分析服务封装
===================================

职责：
1. 封装项目原有的分析能力，提供简洁的接口
2. 处理配置转换和初始化
3. 管理分析流程和错误处理
4. 返回结构化的分析结果
"""

import os
import sys
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class StockAnalyzerService:
    """
    股票分析服务封装类
    
    封装了原项目的分析能力，提供简洁的接口供 skill 使用。
    """
    
    def __init__(self, skill_config: "SkillConfig"):
        """
        初始化分析服务
        
        Args:
            skill_config: Skill 配置对象
        """
        self.skill_config = skill_config
        self._initialized = False
        self._pipeline = None
        self._analyzer = None
        
    def _ensure_initialized(self):
        """确保服务已初始化"""
        if self._initialized:
            return
        
        try:
            # 添加项目根目录到 Python 路径
            project_root = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            # 设置环境变量（用于原项目配置）
            self._setup_environment()
            
            # 延迟导入原项目模块（避免循环依赖）
            from src.config import get_config as get_project_config
            from src.core.pipeline import StockAnalysisPipeline
            from src.core.market_review import run_market_review
            from src.analyzer import GeminiAnalyzer
            from src.enums import ReportType
            
            # 获取或创建项目配置
            project_config = get_project_config()
            
            # 创建分析流水线
            import uuid
            self._pipeline = StockAnalysisPipeline(
                config=project_config,
                query_id=uuid.uuid4().hex,
                query_source="skill"
            )
            
            self._analyzer = GeminiAnalyzer(config=project_config)
            self._run_market_review = run_market_review
            self._ReportType = ReportType
            
            self._initialized = True
            logger.info("StockAnalyzerService 初始化成功")
            
        except Exception as e:
            logger.error(f"初始化分析服务失败: {e}")
            raise RuntimeError(f"无法初始化股票分析服务: {e}")
    
    def _setup_environment(self):
        """设置环境变量"""
        # 设置 LLM 相关环境变量
        if self.skill_config.llm.api_key:
            os.environ["OPENAI_API_KEY"] = self.skill_config.llm.api_key
        if self.skill_config.llm.model:
            os.environ["LLM_MODEL"] = self.skill_config.llm.model
        if self.skill_config.llm.provider:
            os.environ["LLM_PROVIDER"] = self.skill_config.llm.provider
        if self.skill_config.llm.base_url:
            os.environ["LLM_BASE_URL"] = self.skill_config.llm.base_url
        
        # 设置数据源相关环境变量
        if self.skill_config.data_source.tushare_token:
            os.environ["TUSHARE_TOKEN"] = self.skill_config.data_source.tushare_token
        if self.skill_config.data_source.primary:
            os.environ["DATA_SOURCE_PRIMARY"] = self.skill_config.data_source.primary
        
        # 设置分析参数
        os.environ["ANALYSIS_REPORT_TYPE"] = self.skill_config.analysis.default_report_type
        os.environ["ANALYSIS_NEWS_WINDOW"] = str(self.skill_config.analysis.news_window)
        os.environ["ANALYSIS_LANGUAGE"] = self.skill_config.analysis.language
    
    def analyze_single_stock(
        self, 
        stock_code: str, 
        full_report: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        分析单只股票
        
        Args:
            stock_code: 股票代码（如 "600989" 或 "茅台"）
            full_report: 是否生成完整报告
            
        Returns:
            分析结果字典，失败返回 None
        """
        self._ensure_initialized()
        
        try:
            # 标准化股票代码
            stock_code = self._normalize_stock_code(stock_code)
            if not stock_code:
                return None
            
            # 设置报告类型
            report_type = self._ReportType.FULL if full_report else self._ReportType.SIMPLE
            
            # 执行分析
            result = self._pipeline.process_single_stock(
                code=stock_code,
                skip_analysis=False,
                single_stock_notify=False,
                report_type=report_type
            )
            
            if result is None:
                logger.warning(f"股票 {stock_code} 分析返回空结果")
                return None
            
            # 转换为字典格式
            return self._convert_result_to_dict(result)
            
        except Exception as e:
            logger.error(f"分析股票 {stock_code} 失败: {e}")
            return None
    
    def analyze_multiple_stocks(
        self, 
        stock_codes: List[str], 
        full_report: bool = False
    ) -> List[Dict[str, Any]]:
        """
        分析多只股票
        
        Args:
            stock_codes: 股票代码列表
            full_report: 是否为每只股票生成完整报告
            
        Returns:
            分析结果字典列表
        """
        self._ensure_initialized()
        
        results = []
        for code in stock_codes:
            result = self.analyze_single_stock(code, full_report=full_report)
            if result:
                results.append(result)
        
        return results
    
    def perform_market_review(self) -> Optional[str]:
        """
        执行大盘复盘
        
        Returns:
            复盘报告文本，失败返回 None
        """
        self._ensure_initialized()
        
        try:
            report = self._run_market_review(
                notifier=self._pipeline.notifier,
                analyzer=self._analyzer,
                search_service=self._pipeline.search_service
            )
            return report
            
        except Exception as e:
            logger.error(f"执行大盘复盘失败: {e}")
            return None
    
    def _normalize_stock_code(self, code: str) -> Optional[str]:
        """
        标准化股票代码
        
        支持：
        - 纯数字代码（如 "600989"）
        - 股票名称（如 "茅台"）
        - 带后缀代码（如 "600989.SH"）
        
        Args:
            code: 输入的股票代码或名称
            
        Returns:
            标准化的股票代码
        """
        self._ensure_initialized()
        
        try:
            # 尝试从 data_provider 导入标准化函数
            from data_provider.base import normalize_stock_code
            return normalize_stock_code(code)
        except Exception:
            # 简单处理：去除空格，转换为大写
            code = code.strip().upper()
            # 去除常见的后缀
            for suffix in ['.SH', '.SZ', '.BJ']:
                if code.endswith(suffix):
                    code = code[:-3]
            return code
    
    def _convert_result_to_dict(self, result) -> Dict[str, Any]:
        """
        将 AnalysisResult 对象转换为字典
        
        Args:
            result: AnalysisResult 对象
            
        Returns:
            分析结果字典
        """
        return {
            "code": getattr(result, "code", ""),
            "name": getattr(result, "name", ""),
            "sentiment_score": getattr(result, "sentiment_score", 50),
            "operation_advice": getattr(result, "operation_advice", ""),
            "analysis_summary": getattr(result, "analysis_summary", ""),
            "decision_type": getattr(result, "decision_type", "hold"),
            "report_language": getattr(result, "report_language", "zh"),
            "dashboard": getattr(result, "dashboard", {}),
            "raw_data": getattr(result, "raw_data", {}),
        }


class AnalysisResultWrapper:
    """
    分析结果包装器
    
    提供更便捷的属性访问和方法
    """
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
    
    @property
    def code(self) -> str:
        return self._data.get("code", "")
    
    @property
    def name(self) -> str:
        return self._data.get("name", "")
    
    @property
    def sentiment_score(self) -> int:
        return self._data.get("sentiment_score", 50)
    
    @property
    def operation_advice(self) -> str:
        return self._data.get("operation_advice", "")
    
    @property
    def analysis_summary(self) -> str:
        return self._data.get("analysis_summary", "")
    
    @property
    def decision_type(self) -> str:
        return self._data.get("decision_type", "hold")
    
    @property
    def dashboard(self) -> Dict[str, Any]:
        return self._data.get("dashboard", {})
    
    def get_core_conclusion(self) -> Dict[str, Any]:
        """获取核心结论"""
        return self.dashboard.get("core_conclusion", {})
    
    def get_data_perspective(self) -> Dict[str, Any]:
        """获取数据视角（技术面）"""
        return self.dashboard.get("data_perspective", {})
    
    def get_intelligence(self) -> Dict[str, Any]:
        """获取情报面"""
        return self.dashboard.get("intelligence", {})
    
    def get_battle_plan(self) -> Dict[str, Any]:
        """获取作战计划"""
        return self.dashboard.get("battle_plan", {})
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self._data.copy()


# 全局服务实例
_service_instance: Optional[StockAnalyzerService] = None


def get_analyzer_service(skill_config: "SkillConfig") -> StockAnalyzerService:
    """
    获取分析服务实例（单例模式）
    
    Args:
        skill_config: Skill 配置对象
        
    Returns:
        StockAnalyzerService 实例
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = StockAnalyzerService(skill_config)
    return _service_instance


def reset_analyzer_service():
    """重置分析服务实例（用于测试）"""
    global _service_instance
    _service_instance = None
