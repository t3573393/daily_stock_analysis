# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill - 配置管理模块
===================================

职责：
1. 支持从智能体配置文件加载配置
2. 支持从环境变量加载配置（向后兼容）
3. 配置优先级：运行时参数 > 智能体配置文件 > 环境变量 > 默认值
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: str = "openai"
    api_key: str = ""
    model: str = "gpt-4o"
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class DataSourceConfig:
    """数据源配置"""
    primary: str = "akshare"
    fallback: Optional[str] = None
    tushare_token: Optional[str] = None
    akshare_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationConfig:
    """通知配置"""
    enabled: bool = False
    channels: list = field(default_factory=list)


@dataclass
class AnalysisConfig:
    """分析参数配置"""
    default_report_type: str = "full"  # full / simple
    news_window: int = 7  # 新闻时间窗口（天）
    language: str = "zh"  # zh / en
    enable_backtest: bool = True
    enable_portfolio: bool = True


@dataclass
class SkillConfig:
    """Skill 完整配置"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    data_source: DataSourceConfig = field(default_factory=DataSourceConfig)
    notification: NotificationConfig = field(default_factory=NotificationConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)


class ConfigManager:
    """
    配置管理器
    
    支持多种配置来源（优先级从高到低）：
    1. 运行时传入的配置字典
    2. 智能体配置文件（~/.config/claude/stock_analyzer.yaml）
    3. 环境变量
    4. 默认值
    """
    
    DEFAULT_CONFIG_PATHS = [
        Path.home() / ".config" / "claude" / "stock_analyzer.yaml",
        Path.home() / ".config" / "stock_analyzer.yaml",
        Path.cwd() / "stock_analyzer.yaml",
        Path.cwd() / ".claude" / "stock_analyzer.yaml",
    ]
    
    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为 None 则自动搜索默认路径
            config_dict: 运行时配置字典，优先级最高
        """
        self._config = SkillConfig()
        self._config_path = config_path
        self._config_dict = config_dict or {}
        self._loaded = False
    
    def load(self) -> SkillConfig:
        """
        加载配置
        
        Returns:
            SkillConfig: 加载后的配置对象
        """
        if self._loaded:
            return self._config
        
        # 1. 加载默认值（已在 __init__ 中设置）
        logger.debug("加载默认配置")
        
        # 2. 从环境变量加载
        self._load_from_env()
        
        # 3. 从配置文件加载
        self._load_from_file()
        
        # 4. 从运行时字典加载（优先级最高）
        self._load_from_dict()
        
        self._loaded = True
        return self._config
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        logger.debug("从环境变量加载配置")
        
        # LLM 配置
        if os.getenv("LLM_PROVIDER"):
            self._config.llm.provider = os.getenv("LLM_PROVIDER")
        if os.getenv("LLM_API_KEY"):
            self._config.llm.api_key = os.getenv("LLM_API_KEY")
        if os.getenv("LLM_MODEL"):
            self._config.llm.model = os.getenv("LLM_MODEL")
        if os.getenv("LLM_BASE_URL"):
            self._config.llm.base_url = os.getenv("LLM_BASE_URL")
        if os.getenv("LLM_TEMPERATURE"):
            try:
                self._config.llm.temperature = float(os.getenv("LLM_TEMPERATURE"))
            except ValueError:
                pass
        if os.getenv("LLM_MAX_TOKENS"):
            try:
                self._config.llm.max_tokens = int(os.getenv("LLM_MAX_TOKENS"))
            except ValueError:
                pass
        
        # 数据源配置
        if os.getenv("DATA_SOURCE_PRIMARY"):
            self._config.data_source.primary = os.getenv("DATA_SOURCE_PRIMARY")
        if os.getenv("DATA_SOURCE_FALLBACK"):
            self._config.data_source.fallback = os.getenv("DATA_SOURCE_FALLBACK")
        if os.getenv("TUSHARE_TOKEN"):
            self._config.data_source.tushare_token = os.getenv("TUSHARE_TOKEN")
        
        # 分析配置
        if os.getenv("ANALYSIS_REPORT_TYPE"):
            self._config.analysis.default_report_type = os.getenv("ANALYSIS_REPORT_TYPE")
        if os.getenv("ANALYSIS_NEWS_WINDOW"):
            try:
                self._config.analysis.news_window = int(os.getenv("ANALYSIS_NEWS_WINDOW"))
            except ValueError:
                pass
        if os.getenv("ANALYSIS_LANGUAGE"):
            self._config.analysis.language = os.getenv("ANALYSIS_LANGUAGE")
    
    def _load_from_file(self):
        """从配置文件加载"""
        config_path = self._find_config_file()
        if not config_path:
            logger.debug("未找到配置文件")
            return
        
        logger.debug(f"从配置文件加载: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data or 'stock_analyzer' not in data:
                logger.warning(f"配置文件格式不正确: {config_path}")
                return
            
            config_data = data['stock_analyzer']
            
            # LLM 配置
            if 'llm' in config_data:
                llm_data = config_data['llm']
                if 'provider' in llm_data:
                    self._config.llm.provider = llm_data['provider']
                if 'api_key' in llm_data:
                    self._config.llm.api_key = llm_data['api_key']
                if 'model' in llm_data:
                    self._config.llm.model = llm_data['model']
                if 'base_url' in llm_data:
                    self._config.llm.base_url = llm_data['base_url']
                if 'temperature' in llm_data:
                    self._config.llm.temperature = llm_data['temperature']
                if 'max_tokens' in llm_data:
                    self._config.llm.max_tokens = llm_data['max_tokens']
            
            # 数据源配置
            if 'data_source' in config_data:
                ds_data = config_data['data_source']
                if 'primary' in ds_data:
                    self._config.data_source.primary = ds_data['primary']
                if 'fallback' in ds_data:
                    self._config.data_source.fallback = ds_data['fallback']
                if 'tushare_token' in ds_data:
                    self._config.data_source.tushare_token = ds_data['tushare_token']
                if 'akshare_config' in ds_data:
                    self._config.data_source.akshare_config = ds_data['akshare_config']
            
            # 通知配置
            if 'notification' in config_data:
                notif_data = config_data['notification']
                if 'enabled' in notif_data:
                    self._config.notification.enabled = notif_data['enabled']
                if 'channels' in notif_data:
                    self._config.notification.channels = notif_data['channels']
            
            # 分析配置
            if 'analysis' in config_data:
                analysis_data = config_data['analysis']
                if 'default_report_type' in analysis_data:
                    self._config.analysis.default_report_type = analysis_data['default_report_type']
                if 'news_window' in analysis_data:
                    self._config.analysis.news_window = analysis_data['news_window']
                if 'language' in analysis_data:
                    self._config.analysis.language = analysis_data['language']
                if 'enable_backtest' in analysis_data:
                    self._config.analysis.enable_backtest = analysis_data['enable_backtest']
                if 'enable_portfolio' in analysis_data:
                    self._config.analysis.enable_portfolio = analysis_data['enable_portfolio']
                    
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
    
    def _load_from_dict(self):
        """从运行时字典加载（最高优先级）"""
        if not self._config_dict:
            return
        
        logger.debug("从运行时字典加载配置")
        
        # 这里可以实现深度合并逻辑
        # 简化版本：直接覆盖顶层配置
        if 'llm' in self._config_dict:
            for key, value in self._config_dict['llm'].items():
                if hasattr(self._config.llm, key):
                    setattr(self._config.llm, key, value)
        
        if 'data_source' in self._config_dict:
            for key, value in self._config_dict['data_source'].items():
                if hasattr(self._config.data_source, key):
                    setattr(self._config.data_source, key, value)
        
        if 'notification' in self._config_dict:
            for key, value in self._config_dict['notification'].items():
                if hasattr(self._config.notification, key):
                    setattr(self._config.notification, key, value)
        
        if 'analysis' in self._config_dict:
            for key, value in self._config_dict['analysis'].items():
                if hasattr(self._config.analysis, key):
                    setattr(self._config.analysis, key, value)
    
    def _find_config_file(self) -> Optional[Path]:
        """查找配置文件"""
        # 优先使用用户指定的路径
        if self._config_path:
            path = Path(self._config_path).expanduser().resolve()
            if path.exists():
                return path
            return None
        
        # 搜索默认路径
        for path in self.DEFAULT_CONFIG_PATHS:
            path = path.expanduser().resolve()
            if path.exists():
                return path
        
        return None
    
    def get_config(self) -> SkillConfig:
        """获取配置（自动加载）"""
        if not self._loaded:
            self.load()
        return self._config
    
    def to_dict(self) -> Dict:
        """将配置转换为字典"""
        return asdict(self.get_config())
    
    def validate(self) -> tuple[bool, list]:
        """
        验证配置有效性
        
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        config = self.get_config()
        
        # 验证 LLM API Key
        if not config.llm.api_key:
            errors.append("LLM API Key 未设置")
        
        # 验证 LLM Provider
        valid_providers = ["openai", "anthropic", "gemini", "vertex_ai", "deepseek", "ollama"]
        if config.llm.provider not in valid_providers:
            errors.append(f"不支持的 LLM Provider: {config.llm.provider}")
        
        # 验证数据源
        valid_sources = ["akshare", "tushare", "baostock", "efinance", "yfinance"]
        if config.data_source.primary not in valid_sources:
            errors.append(f"不支持的数据源: {config.data_source.primary}")
        
        # 验证报告类型
        if config.analysis.default_report_type not in ["full", "simple"]:
            errors.append(f"不支持的报告类型: {config.analysis.default_report_type}")
        
        # 验证语言
        if config.analysis.language not in ["zh", "en"]:
            errors.append(f"不支持的语言: {config.analysis.language}")
        
        return len(errors) == 0, errors


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager(
    config_path: Optional[str] = None,
    config_dict: Optional[Dict] = None
) -> ConfigManager:
    """
    获取全局配置管理器实例
    
    Args:
        config_path: 配置文件路径
        config_dict: 运行时配置字典
        
    Returns:
        ConfigManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path=config_path, config_dict=config_dict)
    return _config_manager


def get_config(config_path: Optional[str] = None) -> SkillConfig:
    """
    获取配置对象的快捷方法
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        SkillConfig: 配置对象
    """
    return get_config_manager(config_path).get_config()


def reset_config():
    """重置全局配置（用于测试）"""
    global _config_manager
    _config_manager = None
