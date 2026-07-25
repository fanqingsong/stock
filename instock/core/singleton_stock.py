#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import concurrent.futures
import instock.core.stockfetch as stf
import instock.core.tablestructure as tbs
import instock.lib.trade_time as trd
from instock.lib.singleton_type import singleton_type

__author__ = 'myh '
__date__ = '2023/3/10 '


# 读取当天股票数据
class stock_data(metaclass=singleton_type):
    def __init__(self, date):
        try:
            self.data = stf.fetch_stocks(date)
        except Exception as e:
            logging.error(f"singleton.stock_data处理异常：{e}")

    def get_data(self):
        return self.data


# 读取股票历史数据
class stock_hist_data(metaclass=singleton_type):
    def __init__(self, date=None, stocks=None, workers=8):
        if stocks is None:
            stocks = self._load_stocks(date)
        if stocks is None:
            self.data = None
            return
        # date 字段可能是 date/datetime/str，统一成字符串给后续缓存路径与区间计算
        date_key = stocks[0][0]
        date_start, is_cache = trd.get_trade_hist_interval(date_key)  # 提高运行效率，只运行一次
        _data = {}
        try:
            # max_workers是None还是没有给出，将默认为机器cup个数*5
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_stock = {executor.submit(stf.fetch_stock_hist, stock, date_start, is_cache): stock for stock
                                   in stocks}
                for future in concurrent.futures.as_completed(future_to_stock):
                    stock = future_to_stock[future]
                    try:
                        __data = future.result()
                        if __data is not None:
                            _data[stock] = __data
                    except Exception as e:
                        logging.error(f"singleton.stock_hist_data处理异常：{stock[1]}代码{e}")
        except Exception as e:
            logging.error(f"singleton.stock_hist_data处理异常：{e}")
        if not _data:
            self.data = None
        else:
            self.data = _data

    @staticmethod
    def _load_stocks(date):
        """优先从已落库的每日股票数据取列表，避免重复全市场抓取。"""
        try:
            import pandas as pd
            import instock.lib.database as mdb
            table = tbs.TABLE_CN_STOCK_SPOT['name']
            cols = list(tbs.TABLE_CN_STOCK_FOREIGN_KEY['columns'])
            sel = '`,`'.join(cols)
            if date is not None and mdb.checkTableIsExist(table):
                date_str = date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date)
                sql = f"SELECT `{sel}` FROM `{table}` WHERE `date` = '{date_str}'"
                _subset = pd.read_sql(sql=sql, con=mdb.engine())
                if _subset is not None and len(_subset.index) > 0:
                    # 统一 date 为字符串，兼容后续 split/缓存逻辑
                    _subset['date'] = _subset['date'].astype(str)
                    return [tuple(x) for x in _subset.values]
        except Exception as e:
            logging.error(f"singleton.stock_hist_data._load_stocks从数据库加载异常：{e}")
        try:
            spot = stock_data(date).get_data()
            if spot is None or len(spot.index) == 0:
                return None
            _subset = spot[list(tbs.TABLE_CN_STOCK_FOREIGN_KEY['columns'])].copy()
            _subset['date'] = _subset['date'].astype(str)
            return [tuple(x) for x in _subset.values]
        except Exception as e:
            logging.error(f"singleton.stock_hist_data._load_stocks处理异常：{e}")
            return None

    def get_data(self):
        return self.data
