import pandas as pd
from stock_data import StockDataFetcher
from sw_industries import get_sw_industries, is_valid_industry

class StockAnalyzer:
    """股票分析器"""

    def __init__(self, fetcher=None):
        self.fetcher = fetcher or StockDataFetcher()

    def calculate_ma_diff(self, ts_code, long_period=20, short_period=5):
        """计算单只股票的均线差异"""
        try:
            # 获取最近足够多的数据
            days_needed = max(long_period, short_period) + 10  # 确保有足够数据计算均线
            df = self.fetcher.get_recent_data(ts_code, days_needed)

            # 自动跳过时间不足的股票
            if df.empty or len(df) < max(long_period, short_period):
                # print(f"跳过股票 {ts_code}: 数据不足 (需要 {max(long_period, short_period)} 天，实际 {len(df)} 天)")
                return None

            # 计算长期均值（最近long_period天的平均值）
            recent_data = df.tail(long_period)
            long_mean = recent_data['close'].mean()

            # 计算短期均值（最近short_period天的平均值）
            latest_short_data = df.tail(short_period)
            short_mean = latest_short_data['close'].mean()

            # 计算差异百分比
            diff_percent = ((short_mean - long_mean) / long_mean) * 100

            return {
                'ts_code': ts_code,
                'long_mean': long_mean,
                'short_mean': short_mean,
                'diff_percent': diff_percent,
                'latest_close': recent_data['close'].iloc[-1],
                'short_period': short_period
            }
        except Exception as e:
            print(f"分析股票{ts_code}失败: {e}")
            return None

    def analyze_stocks(self, stock_list=None, long_period=20, diff_threshold=5, short_period=5, pre_industries=None):
        """
        批量分析股票，支持行业预筛选

        Args:
            stock_list: 股票列表DataFrame，若为None则自动获取
            long_period: 长期均值周期（天）
            diff_threshold: 差异百分比阈值
            short_period: 短期均值周期（天）
            pre_industries: 行业预筛选列表，或None表示不筛选

        Returns:
            pandas DataFrame，包含分析结果，增加行业字段
        """
        if stock_list is None:
            stock_list = self.fetcher.get_stock_list(pre_industries)

        if stock_list.empty:
            return pd.DataFrame()

        results = []
        total = len(stock_list)

        print(f"开始分析 {total} 只股票...")

        for i, (_, stock) in enumerate(stock_list.iterrows()):
            ts_code = stock['ts_code']
            name = stock['name']
            industry = stock.get('industry', '未知行业')

            if (i + 1) % 10 == 0:
                print(f"已分析 {i + 1}/{total} 只股票")

            result = self.calculate_ma_diff(ts_code, long_period, short_period)

            if result:
                result['name'] = name
                result['industry'] = industry  # 添加行业信息
                results.append(result)

        # 转换为DataFrame
        df = pd.DataFrame(results)

        if df.empty:
            return df

        # 筛选差异大于阈值的股票
        df = df[df['diff_percent'].abs() > diff_threshold]

        # 按差异百分比绝对值从大到小排序
        df = df.sort_values('diff_percent', key=lambda x: x.abs(), ascending=False)

        # 保留需要的列并排序，增加行业列
        df = df[['ts_code', 'name', 'industry', 'diff_percent', 'latest_close', 'long_mean', 'short_mean', 'short_period']]

        print(f"分析完成，找到 {len(df)} 只符合条件的股票")

        return df

    def filter_results_by_industries(self, results_df, post_industries=None):
        """
        对分析结果进行行业后筛选

        Args:
            results_df: 分析结果DataFrame
            post_industries: 行业后筛选列表，或None表示不筛选

        Returns:
            pandas DataFrame，筛选后的结果
        """
        if results_df.empty or not post_industries:
            return results_df

        # 筛选指定行业的股票
        filtered_df = results_df[results_df['industry'].isin(post_industries)]

        print(f"行业后筛选完成，找到 {len(filtered_df)} 只符合条件的股票")
        return filtered_df

    def get_available_industries(self, results_df=None):
        """
        获取可用的行业列表

        Args:
            results_df: 分析结果DataFrame，若为None则返回所有申万一级行业

        Returns:
            list，行业名称列表
        """
        if results_df is None or results_df.empty:
            return get_sw_industries()

        # 从结果中提取行业并去重排序
        industries = sorted(results_df['industry'].dropna().unique())
        return industries

    def get_stock_details(self, ts_code, days=60):
        """获取股票详细数据（用于绘制图表）"""
        try:
            df = self.fetcher.get_recent_data(ts_code, days)

            if df.empty:
                return None

            # 计算移动平均线
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            df['ma30'] = df['close'].rolling(window=30).mean()

            # 转换为字典格式，方便JSON序列化
            data = {
                'trade_dates': df['trade_date'].dt.strftime('%Y-%m-%d').tolist(),
                'close_prices': df['close'].tolist(),
                'ma5': df['ma5'].tolist(),
                'ma20': df['ma20'].tolist(),
                'ma30': df['ma30'].tolist(),
                'latest_data': {
                    'close': df['close'].iloc[-1],
                    'ma5': df['ma5'].iloc[-1],
                    'ma20': df['ma20'].iloc[-1],
                    'ma30': df['ma30'].iloc[-1]
                }
            }

            return data
        except Exception as e:
            print(f"获取股票{ts_code}详情失败: {e}")
            return None

    def filter_top_diff_stocks(self, df, top_n=10):
        """筛选差异最大的前N只股票"""
        if df.empty:
            return df

        # 按差异百分比绝对值排序
        df = df.sort_values('diff_percent', key=lambda x: x.abs(), ascending=False)
        return df.head(top_n)

    def get_stock_stats(self, df):
        """获取筛选结果的统计信息"""
        if df.empty:
            return {}

        stats = {
            'total_count': len(df),
            'avg_diff_percent': df['diff_percent'].mean(),
            'max_diff_percent': df['diff_percent'].max(),
            'min_diff_percent': df['diff_percent'].min(),
            'positive_count': len(df[df['diff_percent'] > 0]),
            'negative_count': len(df[df['diff_percent'] < 0])
        }

        return stats

# 测试用例
if __name__ == "__main__":
    from config import validate_config

    if validate_config():
        analyzer = StockAnalyzer()

        # 测试分析单只股票
        print("测试分析单只股票...")
        result = analyzer.calculate_ma_diff('000001.SZ', 20)
        if result:
            print(f"股票: {result['ts_code']}")
            print(f"长期均值: {result['long_mean']:.2f}")
            print(f"最新5日均线: {result['latest_ma5']:.2f}")
            print(f"差异百分比: {result['diff_percent']:.2f}%")

        # 测试批量分析（只分析前5只股票）
        print("\n测试批量分析（前5只股票）...")
        stock_list = analyzer.fetcher.get_stock_list().head(5)
        result_df = analyzer.analyze_stocks(stock_list, 20, 3)

        if not result_df.empty:
            print("\n筛选结果:")
            print(result_df.to_string(index=False))

            # 测试统计信息
            stats = analyzer.get_stock_stats(result_df)
            print("\n统计信息:")
            for key, value in stats.items():
                print(f"{key}: {value}")

        # 测试获取股票详情
        print("\n测试获取股票详情...")
        details = analyzer.get_stock_details('000001.SZ', 30)
        if details:
            print(f"获取到 {len(details['trade_dates'])} 天数据")
            print(f"最新收盘价: {details['latest_data']['close']:.2f}")
            print(f"最新5日均线: {details['latest_data']['ma5']:.2f}")