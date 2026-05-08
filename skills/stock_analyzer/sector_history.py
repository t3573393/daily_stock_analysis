# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill - 历史数据存储模块
===================================

功能：
1. 存储热点板块历史数据
2. 追踪板块排名变化趋势
3. 计算热度变化趋势
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class SectorSnapshot:
    """板块快照"""
    date: str
    name: str
    code: str
    change_percent: float
    turnover_rate: float
    heat_score: float
    rank: int
    trend: str


class SectorHistoryStore:
    """
    板块历史数据存储
    
    管理热点板块的历史数据，支持：
    - 快照保存
    - 趋势计算
    - 数据导出
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化存储
        
        Args:
            storage_path: 存储路径，默认 ~/.claude/skills/stock_analyzer/data/
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / ".claude" / "skills" / "stock_analyzer" / "data"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.history_file = self.storage_path / "sector_history.json"
        self.trend_file = self.storage_path / "sector_trends.json"
        
        self._history: Dict[str, List[SectorSnapshot]] = {}
        self._trends: Dict[str, Dict] = {}
        
        self._load()
    
    def _load(self):
        """加载历史数据"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history = {
                        k: [SectorSnapshot(**s) for s in v] 
                        for k, v in data.items()
                    }
                logger.info(f"已加载历史数据: {len(self._history)} 天")
            except Exception as e:
                logger.error(f"加载历史数据失败: {e}")
                self._history = {}
        
        if self.trend_file.exists():
            try:
                with open(self.trend_file, 'r', encoding='utf-8') as f:
                    self._trends = json.load(f)
            except Exception as e:
                logger.error(f"加载趋势数据失败: {e}")
                self._trends = {}
    
    def _save(self):
        """保存数据"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    k: [asdict(s) for s in v] 
                    for k, v in self._history.items()
                }, f, ensure_ascii=False, indent=2)
            
            with open(self.trend_file, 'w', encoding='utf-8') as f:
                json.dump(self._trends, f, ensure_ascii=False, indent=2)
            
            logger.debug("数据已保存")
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
    
    def add_snapshot(self, date: str, sectors: List[Dict[str, Any]]):
        """
        添加板块快照
        
        Args:
            date: 日期 (YYYY-MM-DD)
            sectors: 板块数据列表
        """
        if date in self._history:
            self._history[date] = []
        
        snapshots = []
        for rank, sector in enumerate(sectors, 1):
            snapshot = SectorSnapshot(
                date=date,
                name=sector.get("name", ""),
                code=sector.get("code", ""),
                change_percent=sector.get("change_percent", 0),
                turnover_rate=sector.get("turnover_rate", 0),
                heat_score=sector.get("heat_score", 0),
                rank=rank,
                trend=sector.get("trend", "stable")
            )
            snapshots.append(snapshot)
        
        self._history[date] = snapshots
        self._calculate_trends()
        self._save()
    
    def _calculate_trends(self):
        """计算趋势数据"""
        if not self._history:
            return
        
        dates = sorted(self._history.keys())
        
        for sector_name in self._get_all_sector_names():
            scores = []
            changes = []
            ranks = []
            
            for date in dates:
                sector_data = self._history[date]
                found = next((s for s in sector_data if s.name == sector_name), None)
                if found:
                    scores.append(found.heat_score)
                    changes.append(found.change_percent)
                    ranks.append(found.rank)
            
            if len(scores) >= 2:
                # 计算趋势
                score_trend = "rising" if scores[-1] > scores[0] else "falling"
                avg_change = sum(changes) / len(changes)
                rank_change = ranks[-1] - ranks[0] if len(ranks) >= 2 else 0
                
                self._trends[sector_name] = {
                    "dates": dates,
                    "scores": scores,
                    "changes": changes,
                    "ranks": ranks,
                    "score_trend": score_trend,
                    "avg_change": avg_change,
                    "rank_change": rank_change,
                    "current_score": scores[-1] if scores else 0,
                    "current_rank": ranks[-1] if ranks else 0,
                    "score_change": scores[-1] - scores[0] if len(scores) >= 2 else 0,
                    "change_change": changes[-1] - changes[0] if len(changes) >= 2 else 0
                }
    
    def _get_all_sector_names(self) -> set:
        """获取所有板块名称"""
        names = set()
        for snapshots in self._history.values():
            for s in snapshots:
                names.add(s.name)
        return names
    
    def get_sector_trend(self, sector_name: str, days: int = 30) -> Optional[Dict]:
        """
        获取板块趋势
        
        Args:
            sector_name: 板块名称
            days: 追踪天数
            
        Returns:
            趋势数据
        """
        return self._trends.get(sector_name)
    
    def get_multi_sector_trends(self, sector_names: List[str], days: int = 30) -> Dict[str, Dict]:
        """获取多个板块趋势"""
        return {
            name: self._trends.get(name) 
            for name in sector_names 
            if name in self._trends
        }
    
    def get_historical_scores(self, sector_name: str, days: int = 30) -> List[Dict]:
        """
        获取板块历史热度数据
        
        Returns:
            [{date, score, change, rank}, ...]
        """
        dates = sorted(self._history.keys())[-days:]
        result = []
        
        for date in dates:
            sector_data = self._history[date]
            found = next((s for s in sector_data if s.name == sector_name), None)
            if found:
                result.append({
                    "date": date,
                    "score": found.heat_score,
                    "change": found.change_percent,
                    "rank": found.rank
                })
        
        return result
    
    def get_all_sectors_scores(self, date: str) -> List[Dict]:
        """获取指定日期所有板块热度"""
        if date not in self._history:
            return []
        
        return [
            {
                "name": s.name,
                "code": s.code,
                "score": s.heat_score,
                "change": s.change_percent,
                "rank": s.rank,
                "trend": s.trend
            }
            for s in sorted(self._history[date], key=lambda x: x.rank)
        ]
    
    def get_trending_up(self, limit: int = 10) -> List[Dict]:
        """获取热度上升最快的板块"""
        trending = []
        for name, data in self._trends.items():
            trending.append({
                "name": name,
                "score_change": data.get("score_change", 0),
                "rank_change": data.get("rank_change", 0),
                "current_score": data.get("current_score", 0),
                "avg_change": data.get("avg_change", 0)
            })
        
        return sorted(trending, key=lambda x: x["score_change"], reverse=True)[:limit]
    
    def get_trending_down(self, limit: int = 10) -> List[Dict]:
        """获取热度下降最快的板块"""
        trending = []
        for name, data in self._trends.items():
            trending.append({
                "name": name,
                "score_change": data.get("score_change", 0),
                "rank_change": data.get("rank_change", 0),
                "current_score": data.get("current_score", 0),
                "avg_change": data.get("avg_change", 0)
            })
        
        return sorted(trending, key=lambda x: x["score_change"])[:limit]
    
    def get_new_hot_sectors(self, days: int = 7) -> List[str]:
        """获取新晋热点板块"""
        dates = sorted(self._history.keys())
        if len(dates) < 2:
            return []
        
        recent_dates = dates[-days:]
        old_set = set()
        new_set = set()
        
        for i, date in enumerate(recent_dates):
            sectors = self._history[date]
            if i == 0:
                old_set = {s.name for s in sectors[:20]}
            new_set = {s.name for s in sectors[:20]}
        
        return list(new_set - old_set)
    
    def get_fading_sectors(self, days: int = 7) -> List[str]:
        """获取退潮板块"""
        dates = sorted(self._history.keys())
        if len(dates) < 2:
            return []
        
        recent_dates = dates[-days:]
        old_set = set()
        new_set = set()
        
        for i, date in enumerate(recent_dates):
            sectors = self._history[date]
            if i == 0:
                old_set = {s.name for s in sectors[:20]}
            new_set = {s.name for s in sectors[:20]}
        
        return list(old_set - new_set)
    
    def export_trend_data(self) -> Dict[str, Any]:
        """导出趋势数据"""
        return {
            "export_date": datetime.now().isoformat(),
            "total_sectors": len(self._trends),
            "trending_up": self.get_trending_up(),
            "trending_down": self.get_trending_down(),
            "new_hot": self.get_new_hot_sectors(),
            "fading": self.get_fading_sectors(),
            "trends": self._trends
        }
    
    def get_dates(self) -> List[str]:
        """获取所有日期"""
        return sorted(self._history.keys())
    
    def clear_old_data(self, keep_days: int = 90):
        """清理旧数据"""
        dates = sorted(self._history.keys())
        cutoff = (datetime.now() - timedelta(days=keep_days)).strftime("%Y-%m-%d")
        
        old_dates = [d for d in dates if d < cutoff]
        for d in old_dates:
            del self._history[d]
        
        if old_dates:
            self._calculate_trends()
            self._save()
            logger.info(f"已清理 {len(old_dates)} 天的旧数据")
