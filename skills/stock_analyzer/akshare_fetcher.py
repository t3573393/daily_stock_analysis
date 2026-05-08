# -*- coding: utf-8 -*-
"""
===================================
Stock Analyzer Skill - Akshare 数据获取模块
===================================

基于 akshare 的数据获取实现。
当安装 akshare 后自动启用。

安装: pip install akshare
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# 检查 akshare 是否可用
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    logger.warning("akshare 未安装，部分功能将不可用。安装方式: pip install akshare")


class AkshareDataFetcher:
    """
    Akshare 数据获取器
    
    提供股票数据获取功能。
    """
    
    def __init__(self):
        if not AKSHARE_AVAILABLE:
            raise ImportError("akshare 未安装，请先安装: pip install akshare")
        
        self.ak = ak
        logger.info("AkshareDataFetcher 初始化成功")
    
    def get_stock_realtime(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票实时数据
        
        Args:
            stock_code: 股票代码 (如 "600519")
            
        Returns:
            实时数据字典
        """
        try:
            # 东方财富实时行情
            df = self.ak.stock_zh_a_spot_em()
            
            # 匹配股票
            stock = df[df['代码'] == stock_code]
            if stock.empty:
                return None
            
            row = stock.iloc[0]
            return {
                "code": row['代码'],
                "name": row['名称'],
                "price": float(row['最新价']),
                "change": float(row['涨跌幅']),
                "volume": float(row['成交量']),
                "amount": float(row['成交额']),
                "high": float(row['最高']),
                "low": float(row['最低']),
                "open": float(row['今开']),
                "prev_close": float(row['昨收']),
            }
        except Exception as e:
            logger.error(f"获取实时数据失败: {e}")
            return None
    
    def get_stock_history(
        self, 
        stock_code: str, 
        period: str = "daily",
        adjust: str = "qfq"
    ) -> Optional[List[Dict]]:
        """
        获取股票历史数据
        
        Args:
            stock_code: 股票代码
            period: 周期 ("daily", "weekly", "monthly")
            adjust: 复权类型 ("qfq", "hfq", "")
            
        Returns:
            历史数据列表
        """
        try:
            df = self.ak.stock_zh_a_hist(
                symbol=stock_code,
                period=period,
                start_date="20200101",
                end_date="20500101",
                adjust=adjust
            )
            
            if df is None or df.empty:
                return None
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    "date": row['日期'],
                    "open": float(row['开盘']),
                    "high": float(row['最高']),
                    "low": float(row['最低']),
                    "close": float(row['收盘']),
                    "volume": float(row['成交量']),
                    "amount": float(row['成交额']),
                    "change": float(row['涨跌幅']) if '涨跌幅' in row else 0,
                })
            
            return result
        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            return None
    
    def get_sector_rankings(self, n: int = 50) -> Tuple[List[Dict], List[Dict]]:
        """
        获取板块排名
        
        Args:
            n: 返回数量
            
        Returns:
            (热门板块列表, 冷门板块列表)
        """
        try:
            # 行业板块涨跌
            df = self.ak.stock_board_industry_name_em()
            
            if df is None or df.empty:
                return [], []
            
            # 按涨跌幅排序
            df_sorted = df.sort_values('涨跌幅', ascending=False)
            
            top_sectors = []
            bottom_sectors = []
            
            for _, row in df_sorted.head(n).iterrows():
                top_sectors.append({
                    "板块名称": row['板块名称'],
                    "板块代码": row.get('板块代码', ''),
                    "涨跌幅": float(row['涨跌幅']),
                    "换手率": float(row.get('换手率', 0)),
                    "成交量": float(row.get('成交量', 0)),
                    "成交额": float(row.get('成交额', 0)),
                    "上涨家数": int(row.get('上涨家数', 0)),
                    "下跌家数": int(row.get('下跌家数', 0)),
                    "lead_stocks": []
                })
            
            for _, row in df_sorted.tail(n).iterrows():
                bottom_sectors.append({
                    "板块名称": row['板块名称'],
                    "板块代码": row.get('板块代码', ''),
                    "涨跌幅": float(row['涨跌幅']),
                    "换手率": float(row.get('换手率', 0)),
                    "成交量": float(row.get('成交量', 0)),
                    "成交额": float(row.get('成交额', 0)),
                    "上涨家数": int(row.get('上涨家数', 0)),
                    "下跌家数": int(row.get('下跌家数', 0)),
                    "lead_stocks": []
                })
            
            return top_sectors, bottom_sectors
            
        except Exception as e:
            logger.error(f"获取板块排名失败: {e}")
            return [], []
    
    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股票信息字典
        """
        try:
            df = self.ak.stock_individual_info_em(symbol=stock_code)
            
            if df is None or df.empty:
                return None
            
            info = {}
            for _, row in df.iterrows():
                info[row['item']] = row['value']
            
            return {
                "code": stock_code,
                "name": info.get('股票简称', ''),
                "industry": info.get('行业', ''),
                "market": info.get('上市时间', ''),
                "total_shares": info.get('总股本', ''),
                "float_shares": info.get('流通股本', ''),
            }
        except Exception as e:
            logger.error(f"获取股票信息失败: {e}")
            return None
    
    def get_market_index(self) -> Optional[Dict[str, Any]]:
        """
        获取大盘指数
        
        Returns:
            指数数据字典
        """
        try:
            df = self.ak.stock_zh_index_spot_em()
            
            # 过滤主要指数
            indices = ['上证指数', '深证成指', '创业板指', '科创50']
            
            result = {}
            for _, row in df.iterrows():
                if row['名称'] in indices:
                    result[row['名称']] = {
                        "code": row['代码'],
                        "name": row['名称'],
                        "price": float(row['最新价']),
                        "change": float(row['涨跌幅']),
                        "volume": float(row['成交量']),
                        "amount": float(row['成交额']),
                    }
            
            return result
        except Exception as e:
            logger.error(f"获取大盘指数失败: {e}")
            return None


def get_akshare_fetcher() -> Optional[AkshareDataFetcher]:
    """
    获取 Akshare 数据获取器
    
    Returns:
        AkshareDataFetcher 实例，如果 akshare 未安装返回 None
    """
    if not AKSHARE_AVAILABLE:
        logger.warning("akshare 未安装，无法创建数据获取器")
        return None
    
    return AkshareDataFetcher()
