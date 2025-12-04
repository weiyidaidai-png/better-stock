<<<<<<< HEAD
import time
import tushare as ts
import pandas as pd
from config import TUSHARE_TOKEN, API_CALL_DELAY
from sw_industries import filter_stocks_by_industries
from wide_indexes import filter_stocks_by_indexes

class StockDataFetcher:
    """股票数据获取器"""

    def __init__(self):
        self.pro = ts.pro_api(TUSHARE_TOKEN)
        self.cache = {}  # 数据缓存，避免重复API调用

    def get_stock_list(self, industries=None, indexes=None):
        """
        获取A股股票列表，支持按行业和宽基指数筛选

        Args:
            industries: 行业名称列表，或None/空列表表示不筛选
            indexes: 宽基指数名称列表，或None/空列表表示不筛选

        Returns:
            pandas DataFrame，包含股票代码、名称和行业信息
        """
        try:
            # 构建缓存键，包含行业和指数参数
            industry_key = "_".join(sorted(industries)) if industries else ""
            index_key = "_".join(sorted(indexes)) if indexes else ""
            cache_key = f'stock_list_{industry_key}_{index_key}'

            if cache_key in self.cache:
                return self.cache[cache_key]

            time.sleep(API_CALL_DELAY)
            df = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,name,industry')
            df = df[df['ts_code'].str.startswith(('6', '0', '3'))]  # 只保留沪深股票

            # 按筛选顺序：先指数筛选，再行业筛选
            # (1) 指数筛选
            filtered_df = filter_stocks_by_indexes(df, indexes, self)

            # (2) 行业筛选
            filtered_df = filter_stocks_by_industries(filtered_df, industries)

            self.cache[cache_key] = filtered_df
            return filtered_df
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return pd.DataFrame()

    def get_daily_data(self, ts_code, start_date=None, end_date=None):
        """获取股票日线数据"""
        try:
            cache_key = f"{ts_code}_{start_date}_{end_date}"
            if cache_key in self.cache:
                return self.cache[cache_key]

            time.sleep(API_CALL_DELAY)
            df = self.pro.daily(ts_code=ts_code, adj='qfq', start_date=start_date, end_date=end_date)

            if df.empty:
                return pd.DataFrame()

            # 转换日期格式并排序
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
            df = df.sort_values('trade_date')

            # 计算5日均线
            df['ma5'] = df['close'].rolling(window=5).mean()

            self.cache[cache_key] = df
            return df
        except Exception as e:
            print(f"获取股票{ts_code}数据失败: {e}")
            return pd.DataFrame()

    def get_recent_data(self, ts_code, days=30):
        """获取股票最近N天的日线数据"""
        try:
            time.sleep(API_CALL_DELAY)
            df = self.pro.daily(ts_code=ts_code, adj='qfq')

            if df.empty:
                return pd.DataFrame()

            # 转换日期格式并排序
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
            df = df.sort_values('trade_date').tail(days)

            # 计算5日均线
            df['ma5'] = df['close'].rolling(window=5).mean()

            return df
        except Exception as e:
            print(f"获取股票{ts_code}最近{days}天数据失败: {e}")
            return pd.DataFrame()

    def clear_cache(self):
        """清除数据缓存"""
        self.cache.clear()

    def get_cache_size(self):
        """获取缓存大小"""
        return len(self.cache)

# 测试用例
if __name__ == "__main__":
    from config import validate_config

    if validate_config():
        fetcher = StockDataFetcher()

        # 测试获取股票列表
        print("获取股票列表...")
        stock_list = fetcher.get_stock_list()
        print(f"获取到 {len(stock_list)} 只股票")

        if not stock_list.empty:
            # 测试获取单只股票数据
            sample_stock = stock_list.iloc[0]['ts_code']
            print(f"\n获取股票 {sample_stock} 数据...")
            daily_data = fetcher.get_daily_data(sample_stock)
            print(f"获取到 {len(daily_data)} 条日线数据")

            if not daily_data.empty:
                print(f"最新收盘价: {daily_data.iloc[-1]['close']:.2f}")
                print(f"最新5日均线: {daily_data.iloc[-1]['ma5']:.2f}")

            # 测试获取最近数据
            print(f"\n获取股票 {sample_stock} 最近20天数据...")
            recent_data = fetcher.get_recent_data(sample_stock, 20)
=======
import time
import tushare as ts
import pandas as pd
from config import TUSHARE_TOKEN, API_CALL_DELAY
from sw_industries import filter_stocks_by_industries

class StockDataFetcher:
    """股票数据获取器"""

    def __init__(self):
        self.pro = ts.pro_api(TUSHARE_TOKEN)
        self.cache = {}  # 数据缓存，避免重复API调用

    def get_stock_list(self, industries=None):
        """
        获取A股股票列表，支持按行业筛选

        Args:
            industries: 行业名称列表，或None/空列表表示不筛选

        Returns:
            pandas DataFrame，包含股票代码、名称和行业信息
        """
        try:
            # 构建缓存键，包含行业参数
            cache_key = f'stock_list_{"_".join(sorted(industries))}' if industries else 'stock_list'

            if cache_key in self.cache:
                return self.cache[cache_key]

            time.sleep(API_CALL_DELAY)
            df = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,name,industry')
            df = df[df['ts_code'].str.startswith(('6', '0', '3'))]  # 只保留沪深股票

            # 按行业筛选
            filtered_df = filter_stocks_by_industries(df, industries)

            self.cache[cache_key] = filtered_df
            return filtered_df
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return pd.DataFrame()

    def get_daily_data(self, ts_code, start_date=None, end_date=None):
        """获取股票日线数据"""
        try:
            cache_key = f"{ts_code}_{start_date}_{end_date}"
            if cache_key in self.cache:
                return self.cache[cache_key]

            time.sleep(API_CALL_DELAY)
            df = self.pro.daily(ts_code=ts_code, adj='qfq', start_date=start_date, end_date=end_date)

            if df.empty:
                return pd.DataFrame()

            # 转换日期格式并排序
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
            df = df.sort_values('trade_date')

            # 计算5日均线
            df['ma5'] = df['close'].rolling(window=5).mean()

            self.cache[cache_key] = df
            return df
        except Exception as e:
            print(f"获取股票{ts_code}数据失败: {e}")
            return pd.DataFrame()

    def get_recent_data(self, ts_code, days=30):
        """获取股票最近N天的日线数据"""
        try:
            time.sleep(API_CALL_DELAY)
            df = self.pro.daily(ts_code=ts_code, adj='qfq')

            if df.empty:
                return pd.DataFrame()

            # 转换日期格式并排序
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
            df = df.sort_values('trade_date').tail(days)

            # 计算5日均线
            df['ma5'] = df['close'].rolling(window=5).mean()

            return df
        except Exception as e:
            print(f"获取股票{ts_code}最近{days}天数据失败: {e}")
            return pd.DataFrame()

    def clear_cache(self):
        """清除数据缓存"""
        self.cache.clear()

    def get_cache_size(self):
        """获取缓存大小"""
        return len(self.cache)

# 测试用例
if __name__ == "__main__":
    from config import validate_config

    if validate_config():
        fetcher = StockDataFetcher()

        # 测试获取股票列表
        print("获取股票列表...")
        stock_list = fetcher.get_stock_list()
        print(f"获取到 {len(stock_list)} 只股票")

        if not stock_list.empty:
            # 测试获取单只股票数据
            sample_stock = stock_list.iloc[0]['ts_code']
            print(f"\n获取股票 {sample_stock} 数据...")
            daily_data = fetcher.get_daily_data(sample_stock)
            print(f"获取到 {len(daily_data)} 条日线数据")

            if not daily_data.empty:
                print(f"最新收盘价: {daily_data.iloc[-1]['close']:.2f}")
                print(f"最新5日均线: {daily_data.iloc[-1]['ma5']:.2f}")

            # 测试获取最近数据
            print(f"\n获取股票 {sample_stock} 最近20天数据...")
            recent_data = fetcher.get_recent_data(sample_stock, 20)
>>>>>>> origin/debug/wide-industries
            print(f"获取到 {len(recent_data)} 条数据")