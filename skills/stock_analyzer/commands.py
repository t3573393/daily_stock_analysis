# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill - 命令解析和处理
===================================

职责：
1. 解析用户输入的命令
2. 路由到对应的处理函数
3. 处理参数和选项
4. 返回格式化后的响应
"""

import re
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Command:
    """命令对象"""
    name: str
    args: List[str]
    options: Dict[str, Any]
    raw_input: str


class CommandParser:
    """
    命令解析器
    
    解析用户输入，提取命令、参数和选项。
    """
    
    # 支持的命令
    COMMANDS = {
        "analyze": ["/analyze", "分析", "股票分析", "查看"],
        "market": ["/market", "大盘", "市场", "复盘", "market review"],
        "portfolio": ["/portfolio", "组合", "持仓", "portfolio"],
        "backtest": ["/backtest", "回测", "策略", "backtest"],
        "help": ["/help", "帮助", "help", "?"],
    }
    
    def __init__(self):
        pass
    
    def parse(self, user_input: str) -> Optional[Command]:
        """
        解析用户输入
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            Command 对象，如果无法解析返回 None
        """
        if not user_input or not user_input.strip():
            return None
        
        user_input = user_input.strip()
        
        # 尝试匹配命令
        for cmd_name, aliases in self.COMMANDS.items():
            for alias in aliases:
                if user_input.lower().startswith(alias.lower()):
                    # 提取参数部分
                    remaining = user_input[len(alias):].strip()
                    args, options = self._parse_args_and_options(remaining)
                    
                    return Command(
                        name=cmd_name,
                        args=args,
                        options=options,
                        raw_input=user_input
                    )
        
        # 如果没有匹配到命令，尝试智能识别
        return self._smart_parse(user_input)
    
    def _parse_args_and_options(self, text: str) -> Tuple[List[str], Dict[str, Any]]:
        """
        解析参数和选项
        
        Args:
            text: 参数字符串
            
        Returns:
            (参数列表, 选项字典)
        """
        args = []
        options = {}
        
        if not text:
            return args, options
        
        # 简单的选项解析（--key value 或 --key=value）
        # 先提取选项
        option_pattern = r'--(\w+)(?:=|\s+)([^\s]+)'
        matches = re.findall(option_pattern, text)
        
        for key, value in matches:
            # 尝试转换类型
            if value.lower() in ('true', 'yes'):
                options[key] = True
            elif value.lower() in ('false', 'no'):
                options[key] = False
            elif value.isdigit():
                options[key] = int(value)
            elif self._is_float(value):
                options[key] = float(value)
            else:
                options[key] = value
        
        # 移除选项后的文本作为参数
        clean_text = re.sub(option_pattern, '', text).strip()
        
        # 按逗号、空格分隔参数
        if clean_text:
            # 先尝试按逗号分隔（适合多股票）
            if ',' in clean_text:
                args = [a.strip() for a in clean_text.split(',') if a.strip()]
            else:
                args = clean_text.split()
        
        return args, options
    
    def _smart_parse(self, user_input: str) -> Optional[Command]:
        """
        智能解析（当没有明确命令时）
        
        根据内容特征推测用户意图。
        """
        user_input_lower = user_input.lower()
        
        # 大盘相关关键词
        market_keywords = ['大盘', '市场', '指数', '上证', '深证', '创业板', 'a股', '行情']
        if any(kw in user_input_lower for kw in market_keywords):
            return Command(
                name="market",
                args=[user_input],
                options={},
                raw_input=user_input
            )
        
        # 股票代码模式（6位数字）
        stock_pattern = r'\b(\d{6})\b'
        stock_matches = re.findall(stock_pattern, user_input)
        if stock_matches:
            return Command(
                name="analyze",
                args=stock_matches,
                options={},
                raw_input=user_input
            )
        
        # 股票名称（简单判断：2-4个汉字）
        name_pattern = r'([\u4e00-\u9fa5]{2,4})'
        name_matches = re.findall(name_pattern, user_input)
        if name_matches:
            return Command(
                name="analyze",
                args=name_matches,
                options={},
                raw_input=user_input
            )
        
        return None
    
    def _is_float(self, value: str) -> bool:
        """检查是否为浮点数"""
        try:
            float(value)
            return True
        except ValueError:
            return False


class CommandHandler:
    """
    命令处理器
    
    处理解析后的命令，调用相应的服务。
    """
    
    def __init__(self, skill_instance: "StockAnalyzerSkill"):
        """
        初始化命令处理器
        
        Args:
            skill_instance: StockAnalyzerSkill 实例
        """
        self.skill = skill_instance
        self.parser = CommandParser()
    
    def handle(self, user_input: str) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            处理结果文本
        """
        # 解析命令
        command = self.parser.parse(user_input)
        
        if command is None:
            return self._get_help_message()
        
        # 路由到对应处理器
        handlers = {
            "analyze": self._handle_analyze,
            "market": self._handle_market,
            "portfolio": self._handle_portfolio,
            "backtest": self._handle_backtest,
            "help": self._handle_help,
        }
        
        handler = handlers.get(command.name)
        if handler:
            try:
                return handler(command)
            except Exception as e:
                logger.error(f"处理命令 {command.name} 失败: {e}")
                return f"❌ 处理失败: {str(e)}"
        
        return self._get_help_message()
    
    def _handle_analyze(self, command: Command) -> str:
        """处理分析命令"""
        if not command.args:
            return "❌ 请提供要分析的股票代码或名称\n\n示例:\n- /analyze 600989\n- /analyze 茅台\n- /analyze 600989,000001,300750"
        
        # 检查是否为多股票
        if len(command.args) == 1 and ',' in command.args[0]:
            # 逗号分隔的多股票
            stock_codes = [c.strip() for c in command.args[0].split(',') if c.strip()]
        else:
            stock_codes = command.args
        
        # 检查选项
        full_report = command.options.get('full', True)
        comparison_mode = command.options.get('compare', len(stock_codes) > 1)
        
        if len(stock_codes) == 1:
            # 单股分析
            return self.skill.analyze_stock(stock_codes[0], full_report=full_report)
        else:
            # 多股分析
            return self.skill.analyze_stocks(stock_codes, comparison_mode=comparison_mode)
    
    def _handle_market(self, command: Command) -> str:
        """处理大盘命令"""
        return self.skill.perform_market_review()
    
    def _handle_portfolio(self, command: Command) -> str:
        """处理投资组合命令"""
        portfolio_name = command.args[0] if command.args else "我的组合"
        
        # 这里可以从配置或参数中获取组合股票列表
        # 简化版本：提示用户输入股票
        if not command.args or len(command.args) < 2:
            return f"📊 **{portfolio_name}**\n\n请提供组合中的股票代码，例如:\n`/portfolio {portfolio_name} 600989,000001,300750`"
        
        # 解析股票列表
        stock_codes = []
        for arg in command.args[1:]:
            if ',' in arg:
                stock_codes.extend([c.strip() for c in arg.split(',')])
            else:
                stock_codes.append(arg)
        
        return self.skill.analyze_portfolio(stock_codes, portfolio_name)
    
    def _handle_backtest(self, command: Command) -> str:
        """处理回测命令"""
        if len(command.args) < 2:
            return "❌ 请提供策略名称和股票代码\n\n示例:\n- /backtest 均线金叉 600519\n- /backtest 趋势跟踪 000001"
        
        strategy_name = command.args[0]
        stock_code = command.args[1]
        
        return self.skill.backtest_strategy(strategy_name, stock_code)
    
    def _handle_help(self, command: Command) -> str:
        """处理帮助命令"""
        return self._get_help_message()
    
    def _get_help_message(self) -> str:
        """获取帮助信息"""
        return """📊 **Stock Analyzer 股票分析助手**

**可用命令:**

1️⃣ **股票分析** `/analyze`
   - 单股: `/analyze 600989` 或 `/analyze 茅台`
   - 多股: `/analyze 600989,000001,300750`
   - 简版: `/analyze 600989 --full=false`

2️⃣ **大盘复盘** `/market`
   - 查看: `/market` 或 `大盘`

3️⃣ **投资组合** `/portfolio`
   - 分析: `/portfolio 我的组合 600989,000001`

4️⃣ **策略回测** `/backtest`
   - 回测: `/backtest 均线金叉 600519`

5️⃣ **帮助** `/help`
   - 显示本帮助信息

**智能识别:**
直接输入股票代码（如 `600989`）或股票名称（如 `茅台`）即可自动分析。

**注意事项:**
- 股票代码支持 6 位数字格式
- 多股票用逗号分隔
- 分析结果仅供参考，不构成投资建议
"""


class StockAnalyzerSkill:
    """
    股票分析 Skill 主类
    
    整合配置、分析服务和格式化器，提供统一的接口。
    """
    
    def __init__(
        self, 
        config_path: Optional[str] = None,
        config_dict: Optional[Dict] = None
    ):
        """
        初始化 Skill
        
        Args:
            config_path: 配置文件路径
            config_dict: 运行时配置字典
        """
        # 延迟导入避免循环依赖
        from .config import get_config_manager, SkillConfig
        from .analyzer import get_analyzer_service
        from .formatter import get_formatter
        
        # 加载配置
        self.config_manager = get_config_manager(config_path, config_dict)
        self.config: SkillConfig = self.config_manager.get_config()
        
        # 验证配置
        is_valid, errors = self.config_manager.validate()
        if not is_valid:
            error_msg = "\n".join([f"- {e}" for e in errors])
            raise ValueError(f"配置验证失败:\n{error_msg}")
        
        # 初始化服务
        self.analyzer_service = get_analyzer_service(self.config)
        self.formatter = get_formatter(
            language=self.config.analysis.language,
            simple_mode=self.config.analysis.default_report_type == "simple"
        )
        
        # 初始化命令处理器
        self.command_handler = CommandHandler(self)
        
        logger.info("StockAnalyzerSkill 初始化完成")
    
    def process(self, user_input: str) -> str:
        """
        处理用户输入（主入口）
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            处理结果文本
        """
        return self.command_handler.handle(user_input)
    
    def analyze_stock(self, stock_code: str, full_report: bool = True) -> str:
        """
        分析单只股票
        
        Args:
            stock_code: 股票代码或名称
            full_report: 是否生成完整报告
            
        Returns:
            格式化后的分析报告
        """
        try:
            result = self.analyzer_service.analyze_single_stock(
                stock_code, 
                full_report=full_report
            )
            
            if result is None:
                return f"❌ 无法分析股票 `{stock_code}`\n\n可能原因:\n- 股票代码不存在\n- 数据源暂时不可用\n- 该股票已退市"
            
            return self.formatter.format_single_stock_report(result)
            
        except Exception as e:
            logger.error(f"分析股票失败: {e}")
            return f"❌ 分析失败: {str(e)}"
    
    def analyze_stocks(
        self, 
        stock_codes: List[str], 
        comparison_mode: bool = False
    ) -> str:
        """
        分析多只股票
        
        Args:
            stock_codes: 股票代码列表
            comparison_mode: 是否启用对比模式
            
        Returns:
            格式化后的分析报告
        """
        try:
            results = self.analyzer_service.analyze_multiple_stocks(
                stock_codes,
                full_report=False  # 多股分析使用简要报告
            )
            
            if not results:
                return "❌ 无法获取分析结果，请检查股票代码是否正确。"
            
            return self.formatter.format_multiple_stocks_report(
                results, 
                comparison_mode=comparison_mode
            )
            
        except Exception as e:
            logger.error(f"分析多股失败: {e}")
            return f"❌ 分析失败: {str(e)}"
    
    def perform_market_review(self) -> str:
        """
        执行大盘复盘
        
        Returns:
            格式化后的复盘报告
        """
        try:
            report = self.analyzer_service.perform_market_review()
            
            if report is None:
                return "❌ 无法获取大盘复盘报告，请检查数据源配置。"
            
            return self.formatter.format_market_review_report(report)
            
        except Exception as e:
            logger.error(f"大盘复盘失败: {e}")
            return f"❌ 大盘复盘失败: {str(e)}"
    
    def analyze_portfolio(
        self, 
        stock_codes: List[str], 
        portfolio_name: str = "我的组合"
    ) -> str:
        """
        分析投资组合
        
        Args:
            stock_codes: 组合中的股票代码列表
            portfolio_name: 组合名称
            
        Returns:
            格式化后的组合分析报告
        """
        try:
            results = self.analyzer_service.analyze_multiple_stocks(
                stock_codes,
                full_report=False
            )
            
            if not results:
                return "❌ 无法分析组合，请检查股票代码。"
            
            return self.formatter.format_portfolio_report(results, portfolio_name)
            
        except Exception as e:
            logger.error(f"分析组合失败: {e}")
            return f"❌ 组合分析失败: {str(e)}"
    
    def backtest_strategy(self, strategy_name: str, stock_code: str) -> str:
        """
        回测策略
        
        Args:
            strategy_name: 策略名称
            stock_code: 股票代码
            
        Returns:
            格式化后的回测报告
        """
        # 回测功能需要进一步实现
        # 这里返回一个占位符
        return f"""📊 **策略回测**

策略: {strategy_name}
标的: {stock_code}

⚠️ 回测功能需要配置回测引擎，当前版本暂未实现。

请使用项目原生的回测功能：
```bash
python main.py --mode backtest --strategy {strategy_name} --code {stock_code}
```
"""


# 便捷函数

def create_skill(
    config_path: Optional[str] = None,
    config_dict: Optional[Dict] = None
) -> StockAnalyzerSkill:
    """
    创建 Skill 实例
    
    Args:
        config_path: 配置文件路径
        config_dict: 运行时配置字典
        
    Returns:
        StockAnalyzerSkill 实例
    """
    return StockAnalyzerSkill(config_path, config_dict)


def analyze(stock_code: str, config_path: Optional[str] = None) -> str:
    """
    快速分析单只股票的便捷函数
    
    Args:
        stock_code: 股票代码
        config_path: 配置文件路径
        
    Returns:
        分析报告文本
    """
    skill = create_skill(config_path)
    return skill.analyze_stock(stock_code)


def market_review(config_path: Optional[str] = None) -> str:
    """
    快速获取大盘复盘的便捷函数
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        复盘报告文本
    """
    skill = create_skill(config_path)
    return skill.perform_market_review()
