# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill - 热点板块追踪
===================================

功能：
1. 获取最近30个交易日的热点板块涨跌数据
2. 根据涨跌幅、换手率、成交量等计算热度指数
3. 追踪板块概念变化趋势
4. 绘制板块走势图
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SectorData:
    """板块数据"""
    name: str  # 板块名称
    code: str  # 板块代码
    change_percent: float  # 涨跌幅
    turnover_rate: float  # 换手率
    volume: float  # 成交量
    amount: float  # 成交额
    heat_score: float  # 热度指数
    trend: str  # 趋势: rising/falling/stable
    rank_change: int  # 排名变化
    lead_stocks: List[str]  # 龙头股


@dataclass
class HotSectorReport:
    """热点板块报告"""
    date: str
    top_sectors: List[SectorData]  # 热门板块
    declined_sectors: List[SectorData]  # 低迷板块
    rising_concepts: List[str]  # 上升概念
    falling_concepts: List[str]  # 下降概念
    new_hot_concepts: List[str]  # 新晋热点
    fading_concepts: List[str]  # 退潮热点


class HotSectorTracker:
    """
    热点板块追踪器
    
    追踪最近30个交易日的热点板块涨跌情况和热度变化。
    """
    
    def __init__(self, skill_config: Optional["SkillConfig"] = None):
        """
        初始化追踪器
        
        Args:
            skill_config: Skill 配置对象
        """
        self.skill_config = skill_config
        self._initialized = False
        self._fetcher = None
        self._historical_data: Dict[str, List[Dict]] = {}  # 历史数据缓存
    
    def _ensure_initialized(self):
        """确保服务已初始化"""
        if self._initialized:
            return
        
        try:
            # 延迟导入
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            from data_provider import DataFetcherManager
            
            self._fetcher = DataFetcherManager()
            self._initialized = True
            logger.info("HotSectorTracker 初始化成功")
            
        except Exception as e:
            logger.error(f"初始化热点追踪器失败: {e}")
            raise RuntimeError(f"无法初始化热点追踪器: {e}")
    
    def get_hot_sectors(
        self, 
        days: int = 30,
        top_n: int = 10,
        include_concepts: bool = True
    ) -> HotSectorReport:
        """
        获取热点板块报告
        
        Args:
            days: 追踪天数
            top_n: 返回前N个热门板块
            include_concepts: 是否包含概念板块
            
        Returns:
            HotSectorReport: 热点板块报告
        """
        self._ensure_initialized()
        
        try:
            # 获取今日板块数据
            today_data = self._get_today_sectors(include_concepts)
            
            # 获取历史数据进行趋势分析
            historical_data = self._get_historical_sectors(days, top_n)
            
            # 计算热度指数和排名变化
            sector_scores = self._calculate_heat_scores(today_data, historical_data)
            
            # 生成报告
            report = self._generate_report(sector_scores, historical_data, top_n)
            
            return report
            
        except Exception as e:
            logger.error(f"获取热点板块失败: {e}")
            raise
    
    def _get_today_sectors(self, include_concepts: bool) -> List[Dict]:
        """获取今日板块数据"""
        try:
            top, bottom = self._fetcher.get_sector_rankings(n=50)
            all_sectors = top + bottom
            return all_sectors
        except Exception as e:
            logger.error(f"获取今日板块数据失败: {e}")
            return []
    
    def _get_historical_sectors(self, days: int, top_n: int) -> Dict[str, List[Dict]]:
        """
        获取历史板块数据
        
        Args:
            days: 天数
            top_n: 每天获取前N个板块
            
        Returns:
            Dict[str, List[Dict]]: 按日期分组的板块数据
        """
        historical = {}
        
        # 尝试从缓存或数据库获取历史数据
        # 这里简化处理，实际应该从数据源获取历史数据
        try:
            # 获取最近 N 个交易日的数据
            for i in range(min(days, 30)):  # 最多30天
                date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
                
                # 尝试获取历史数据
                # 这里需要调用数据源的日期版本接口
                # 暂时使用占位数据
                if i == 0:
                    continue  # 今日数据已单独获取
                    
        except Exception as e:
            logger.debug(f"获取历史数据时出现错误: {e}")
        
        return historical
    
    def _calculate_heat_scores(
        self, 
        today_data: List[Dict], 
        historical_data: Dict[str, List[Dict]]
    ) -> List[SectorData]:
        """
        计算热度指数
        
        热度指数计算公式：
        heat_score = (change_percent * 0.4) + (turnover_rate * 0.3) + (volume_rank * 0.2) + (trend_score * 0.1)
        
        Args:
            today_data: 今日板块数据
            historical_data: 历史数据
            
        Returns:
            List[SectorData]: 带热度指数的板块数据
        """
        sectors = []
        
        for sector in today_data:
            try:
                name = sector.get("板块名称", sector.get("name", ""))
                code = sector.get("板块代码", sector.get("code", ""))
                change = float(sector.get("涨跌幅", sector.get("change", 0)))
                turnover = float(sector.get("换手率", sector.get("turnover", 0)))
                volume = float(sector.get("成交量", sector.get("volume", 0)))
                amount = float(sector.get("成交额", sector.get("amount", 0)))
                
                # 计算热度指数
                change_score = min(abs(change) * 2, 100)  # 涨跌幅得分
                turnover_score = min(turnover * 5, 100)  # 换手率得分
                volume_score = min(volume / 10000000, 100)  # 成交量得分
                
                heat_score = (
                    change_score * 0.4 + 
                    turnover_score * 0.3 + 
                    volume_score * 0.2 +
                    (100 if change > 0 else 0) * 0.1  # 上涨加成
                )
                
                # 判断趋势
                if change > 3:
                    trend = "rising"
                elif change < -3:
                    trend = "falling"
                else:
                    trend = "stable"
                
                # 计算排名变化（需要历史数据）
                rank_change = self._calculate_rank_change(name, historical_data)
                
                # 提取龙头股（如果有）
                lead_stocks = sector.get("lead_stocks", [])
                
                sector_data = SectorData(
                    name=name,
                    code=code,
                    change_percent=change,
                    turnover_rate=turnover,
                    volume=volume,
                    amount=amount,
                    heat_score=heat_score,
                    trend=trend,
                    rank_change=rank_change,
                    lead_stocks=lead_stocks
                )
                
                sectors.append(sector_data)
                
            except Exception as e:
                logger.debug(f"处理板块数据失败: {e}")
                continue
        
        # 按热度指数排序
        sectors.sort(key=lambda x: x.heat_score, reverse=True)
        
        return sectors
    
    def _calculate_rank_change(
        self, 
        sector_name: str, 
        historical_data: Dict[str, List[Dict]]
    ) -> int:
        """计算排名变化"""
        # 简化处理：返回0
        # 实际应该对比历史排名
        return 0
    
    def _generate_report(
        self,
        sector_scores: List[SectorData],
        historical_data: Dict[str, List[Dict]],
        top_n: int
    ) -> HotSectorReport:
        """生成热点板块报告"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 热门板块（热度最高的）
        top_sectors = sector_scores[:top_n]
        
        # 低迷板块（热度最低的）
        declined_sectors = sector_scores[-top_n:] if len(sector_scores) > top_n else sector_scores
        
        # 上升概念（涨跌幅最高的）
        rising_concepts = [
            s.name for s in sector_scores 
            if s.trend == "rising"
        ][:10]
        
        # 下降概念（跌跌幅最大的）
        falling_concepts = [
            s.name for s in sector_scores 
            if s.trend == "falling"
        ][:10]
        
        # 新晋热点（从历史数据对比）
        new_hot_concepts = self._detect_new_hot_concepts(sector_scores, historical_data)
        
        # 退潮热点
        fading_concepts = self._detect_fading_concepts(sector_scores, historical_data)
        
        return HotSectorReport(
            date=today,
            top_sectors=top_sectors,
            declined_sectors=declined_sectors,
            rising_concepts=rising_concepts,
            falling_concepts=falling_concepts,
            new_hot_concepts=new_hot_concepts,
            fading_concepts=fading_concepts
        )
    
    def _detect_new_hot_concepts(
        self,
        current: List[SectorData],
        historical: Dict[str, List[Dict]]
    ) -> List[str]:
        """检测新晋热点"""
        # 简化处理
        return []
    
    def _detect_fading_concepts(
        self,
        current: List[SectorData],
        historical: Dict[str, List[Dict]]
    ) -> List[str]:
        """检测退潮热点"""
        # 简化处理
        return []
    
    def get_sector_trend_chart(
        self,
        sector_name: str,
        days: int = 30
    ) -> Optional[str]:
        """
        获取板块趋势图（文本格式）
        
        Args:
            sector_name: 板块名称
            days: 天数
            
        Returns:
            str: 趋势图（ASCII 艺术）
        """
        # 这里应该调用绘图模块生成真正的图表
        # 暂时返回文本格式
        chart = f"""
{sector_name} 近 {days} 日走势
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    │                                    
100 │                              ╱──╲   
 80 │                         ╱──╲        
 60 │                    ╱──╲              
 40 │               ╱──╲                   
 20 │          ╱──╯                      
  0 │────╱───────────────────────────────▶
    └────────────────────────────────────
      1   5   10   15   20   25   30 (日)
      
注: 此为示意图，实际数据请调用图表API
"""
        return chart


def get_trend_ascii_chart(
    data: List[float],
    labels: List[str] = None,
    width: int = 50,
    height: int = 15,
    title: str = ""
) -> str:
    """
    生成 ASCII 折线图
    
    Args:
        data: 数据列表
        labels: 标签列表
        width: 图表宽度
        height: 图表高度
        title: 图表标题
        
    Returns:
        str: ASCII 图表
    """
    if not data or len(data) < 2:
        return "数据不足，无法生成图表"
    
    # 归一化数据到 [0, 100]
    min_val = min(data)
    max_val = max(data)
    range_val = max_val - min_val if max_val != min_val else 1
    
    normalized = [(v - min_val) / range_val * 100 for v in data]
    
    # 创建网格
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # 绘制数据点
    for i, val in enumerate(normalized):
        x = int(i / (len(data) - 1) * (width - 1))
        y = height - 1 - int(val / 100 * (height - 1))
        y = max(0, min(height - 1, y))
        grid[y][x] = '●'
    
    # 绘制连线
    for i in range(len(normalized) - 1):
        x1 = int(i / (len(data) - 1) * (width - 1))
        x2 = int((i + 1) / (len(data) - 1) * (width - 1))
        y1 = height - 1 - int(normalized[i] / 100 * (height - 1))
        y2 = height - 1 - int(normalized[i + 1] / 100 * (height - 1))
        
        y1 = max(0, min(height - 1, y1))
        y2 = max(0, min(height - 1, y2))
        
        # Bresenham 算法绘制线段
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = '●' if grid[y][x] == '●' else '•'
            
            if x == x2 and y == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    # 生成图表字符串
    lines = []
    
    if title:
        lines.append(f"【{title}】")
        lines.append("")
    
    # Y 轴标签
    for i in range(height):
        y_val = int((height - 1 - i) / (height - 1) * (max_val - min_val) + min_val)
        line = f"{y_val:>6.1f} │ " + ''.join(grid[i])
        lines.append(line)
    
    # X 轴
    lines.append("       └" + "─" * width)
    
    # X 轴标签
    if labels:
        label_line = "         " + ''.join([
            labels[i] if i < len(labels) else ' '
            for i in range(0, len(labels), max(1, len(labels) // min(width, len(labels))))
        ])
        lines.append(label_line)
    else:
        # 显示刻度
        tick_count = min(5, len(data))
        ticks = [int(i / (tick_count - 1) * (len(data) - 1)) for i in range(tick_count)]
        tick_str = "         "
        for t in ticks:
            x = int(t / (len(data) - 1) * (width - 1)) if len(data) > 1 else width // 2
            tick_str += f"{t:>{x - len(tick_str) + 7}}"
        lines.append(tick_str)
    
    # 数据范围
    lines.append("")
    lines.append(f"数据范围: {min_val:.2f} ~ {max_val:.2f}")
    
    return '\n'.join(lines)
