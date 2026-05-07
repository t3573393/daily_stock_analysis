---
name: "stock_analyzer"
description: "AI驱动的股票分析助手。支持单股/多股分析、大盘复盘、投资组合管理和策略回测。生成人类可读的分析报告，适合在聊天界面直接展示。"
version: "1.0.0"
author: "Dragon Stock Analyzer Team"
---

# Stock Analyzer Skill

AI驱动的股票分析助手，提供专业的股票分析、市场复盘和投资建议。

## 功能概览

| 功能 | 命令示例 | 说明 |
|------|---------|------|
| **单股分析** | `/analyze 600989` 或 `/analyze 茅台` | 分析指定股票的完整报告 |
| **多股对比** | `/analyze 600989,000001,300750` | 分析并对比多只股票 |
| **大盘复盘** | `/market` 或 `/market 今日复盘` | 市场整体分析和复盘 |
| **投资组合** | `/portfolio` 或 `/portfolio 我的自选股` | 分析投资组合表现 |
| **策略回测** | `/backtest 均线金叉 600519` | 验证交易策略有效性 |

## 配置方式

### 1. 智能体配置文件（推荐）

在智能体配置目录创建 `stock_analyzer.yaml`：

```yaml
# ~/.config/claude/stock_analyzer.yaml
stock_analyzer:
  llm:
    provider: openai
    api_key: sk-your-api-key
    model: gpt-4o
    
  data_source:
    primary: akshare
    tushare_token: your-tushare-token
    
  analysis:
    default_report_type: full
    news_window: 7
    language: zh
```

### 2. 环境变量

```bash
# .env 文件
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-api-key
LLM_MODEL=gpt-4o
TUSHARE_TOKEN=your-tushare-token
```

## 输出格式

分析报告包含以下部分：

1. **📊 核心结论** - 一句话总结 + 操作建议（买入/持有/观望/卖出）
2. **📈 技术面分析** - 趋势状态、价格位置、量能分析、筹码结构
3. **📰 市场情报** - 相关新闻、风险警报、积极催化剂
4. **🎯 操作策略** - 狙击点（买入/卖出目标价）、仓位策略、风险控制清单

## 使用示例

### 单股分析

```
用户: /analyze 600989
助手: 
📊 **宝丰能源 (600989) 分析报告**

🎯 核心结论
信号: 谨慎看多 | 建议: 轻仓试探

📈 技术面
- 趋势: 中期上升通道，短期回调至支撑位
- 价格位置: 当前价格处于布林带中轨附近
- 量能: 近期缩量回调，抛压减轻
- 筹码: 主力筹码集中，散户筹码松动

📰 情报面
- 积极因素: 煤制烯烃项目投产，产能释放
- 风险因素: 原材料价格波动，行业周期性

🎯 操作策略
- 买入区间: 14.5-15.0元
- 止损位: 13.8元 (-7%)
- 目标位: 17.5元 (+15%)
- 仓位建议: 不超过总仓位10%
```

### 大盘复盘

```
用户: /market
助手:
📊 **2026-05-07 A股市场复盘**

🎯 市场情绪: 谨慎乐观 (情绪指数: 62/100)

📈 指数表现
- 上证指数: 3,245.67 (+0.45%)
- 深证成指: 10,234.56 (+0.78%)
- 创业板指: 2,156.78 (+1.23%)

🔥 热点板块
1. 新能源 (+3.2%) - 政策利好刺激
2. 半导体 (+2.8%) - 国产替代加速
3. 医药 (+1.5%) - 创新药获批

⚠️ 风险提示
- 北向资金净流出 15.6亿
- 成交量较昨日萎缩 12%

💡 明日策略
建议关注新能源产业链回调机会，控制仓位在60%以内。
```

## 技术架构

```
skills/stock_analyzer/
├── SKILL.md              # 本文件
├── __init__.py           # 包入口
├── config.py             # 配置管理（支持智能体配置文件）
├── analyzer.py           # 核心分析服务封装
├── formatter.py          # 对话式输出格式化
├── commands.py           # 命令解析和处理
└── example_config.yaml   # 示例配置文件
```

## 依赖要求

- Python 3.10+
- 项目根目录的 `requirements.txt` 依赖
- 有效的 LLM API Key
- （可选）Tushare Token 获取更完整数据

## 集成说明

### 在 Claude Code 中使用

1. 将本 skill 复制到 `.claude/skills/stock_analyzer/`
2. 配置 API Key 和数据源
3. 在对话中使用 `/analyze`, `/market`, `/portfolio`, `/backtest` 命令

### 在其他智能体中使用

本 skill 设计为独立 Python 包，可以在任何支持 Python 的智能体框架中使用：

```python
from skills.stock_analyzer import StockAnalyzerSkill

skill = StockAnalyzerSkill(config_path="~/.config/my_agent/stock_analyzer.yaml")
result = skill.analyze_stock("600989")
print(result)
```

## 注意事项

1. **数据延迟**: 股票数据可能有15分钟延迟，非实时行情
2. **风险提示**: AI分析仅供参考，不构成投资建议
3. **API限制**: 注意 LLM API 和数据源的调用限制
4. **合规性**: 使用本 skill 请遵守当地金融监管要求
