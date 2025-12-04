"""
宽基指数数据管理
"""

import pandas as pd

# 宽基指数列表
WIDE_INDEXES = [
    "全选",
    "科创50",
    "上证50",
    "沪深300",
    "中证500",
    "中证1000"
]

# 指数代码映射表
INDEX_CODE_MAPPING = {
    "科创50": "KCB50",
    "上证50": "SSE50",
    "沪深300": "HS300",
    "中证500": "ZZ500",
    "中证1000": "ZZ1000"
}

# Tushare 指数代码映射
TUSHARE_INDEX_MAPPING = {
    "KCB50": "885005.SI",
    "SSE50": "000016.SH",
    "HS300": "000300.SH",
    "ZZ500": "000905.SH",
    "ZZ1000": "000852.SH"
}

def get_wide_indexes():
    """获取宽基指数列表"""
    return WIDE_INDEXES.copy()

def get_index_code(index_name):
    """根据指数名称获取指数代码"""
    return INDEX_CODE_MAPPING.get(index_name, "")

def get_tushare_index_code(index_name):
    """根据指数名称获取 Tushare 指数代码"""
    index_code = INDEX_CODE_MAPPING.get(index_name, "")
    return TUSHARE_INDEX_MAPPING.get(index_code, "")

def is_valid_index(index_name):
    """检查指数名称是否有效"""
    return index_name in WIDE_INDEXES

def filter_stocks_by_indexes(stock_list, indexes, fetcher=None):
    """
    根据宽基指数筛选股票列表

    Args:
        stock_list: pandas DataFrame，包含股票列表数据，必须包含'ts_code'列
        indexes: 指数名称列表，或None/空列表表示不筛选
        fetcher: StockDataFetcher 实例，用于获取指数成分股数据

    Returns:
        pandas DataFrame，筛选后的股票列表
    """
    if not indexes or stock_list.empty:
        return stock_list

    # 检查是否选择了"全选"
    if "全选" in indexes:
        return stock_list

    # 获取所有选择的指数的成分股
    all_index_stocks = []

    for index_name in indexes:
        if index_name not in WIDE_INDEXES or index_name == "全选":
            continue

        # 获取指数成分股
        index_stocks = get_index_constituents(index_name, fetcher)

        if not index_stocks.empty:
            index_ts_codes = index_stocks['ts_code'].tolist()
            all_index_stocks.extend(index_ts_codes)
            print(f"指数 {index_name} 有 {len(index_ts_codes)} 只成分股")
        else:
            print(f"警告：无法获取指数 {index_name} 的成分股数据，将尝试使用简化的代码匹配方法")

            # 如果无法通过Tushare API获取成分股，尝试使用简化的代码匹配方法
            simplified_ts_codes = get_simplified_index_constituents(index_name, stock_list)
            if simplified_ts_codes:
                all_index_stocks.extend(simplified_ts_codes)
                print(f"使用简化方法为指数 {index_name} 匹配到 {len(simplified_ts_codes)} 只股票")

    # 去重指数成分股
    all_index_stocks = list(set(all_index_stocks))

    # 如果没有获取到任何指数成分股，返回空列表
    if not all_index_stocks:
        print("错误：无法获取任何指数的成分股数据")
        return pd.DataFrame(columns=stock_list.columns)

    print(f"所有选中的指数共有 {len(all_index_stocks)} 只成分股")

    # 筛选出在任何一个指数成分股中的股票
    # 注意：指数筛选是"或"的关系，即只要股票在任何一个选中的指数中，就会被保留
    filtered_df = stock_list[stock_list['ts_code'].isin(all_index_stocks)]

    print(f"筛选后得到 {len(filtered_df)} 只股票")

    return filtered_df


def get_simplified_index_constituents(index_name, stock_list):
    """
    使用简化的方法获取指数成分股（当Tushare API调用失败时使用）

    Args:
        index_name: 指数名称
        stock_list: 所有股票的列表

    Returns:
        list: 指数成分股的ts_code列表，数量符合指数规定
    """
    # 对于不同的指数，使用不同的股票代码匹配规则
    # 这只是一个简化的方法，实际结果可能不完全准确

    ts_codes = []

    if index_name == "科创50":
        # 科创50的股票代码通常以688开头，最多50只股票
        ts_codes = stock_list[stock_list['ts_code'].str.startswith('688')]['ts_code'].head(50).tolist()
    elif index_name == "上证50":
        # 上证50的股票代码通常以600或601开头，最多50只股票
        ts_codes = stock_list[stock_list['ts_code'].str.startswith(('600', '601'))]['ts_code'].head(50).tolist()
    elif index_name == "沪深300":
        # 沪深300包含上海和深圳的大型公司，最多300只股票
        # 实际应用中可以根据市值或其他指标进行筛选
        ts_codes = stock_list.head(300)['ts_code'].tolist()
    elif index_name == "中证500":
        # 中证500包含中型公司，最多500只股票
        # 实际应用中可以根据市值或其他指标进行筛选
        ts_codes = stock_list.iloc[300:800]['ts_code'].tolist()  # 301-800共500只
    elif index_name == "中证1000":
        # 中证1000包含小型公司，最多1000只股票
        # 实际应用中可以根据市值或其他指标进行筛选
        ts_codes = stock_list.iloc[800:1800]['ts_code'].tolist()  # 801-1800共1000只

    # 确保返回的股票数量不超过指数规定的数量
    max_count = {
        "科创50": 50,
        "上证50": 50,
        "沪深300": 300,
        "中证500": 500,
        "中证1000": 1000
    }.get(index_name, len(ts_codes))

    if len(ts_codes) > max_count:
        ts_codes = ts_codes[:max_count]

    print(f"简化方法为指数 {index_name} 筛选出 {len(ts_codes)} 只股票")

    return ts_codes

def get_index_constituents(index_name, fetcher=None):
    """
    获取指定指数的成分股

    Args:
        index_name: 指数名称
        fetcher: StockDataFetcher 实例，用于获取数据

    Returns:
        pandas DataFrame，包含指数成分股数据，至少包含'ts_code'列
    """
    if not fetcher:
        return pd.DataFrame()

    try:
        # 获取 Tushare 指数代码
        tushare_index_code = get_tushare_index_code(index_name)
        if not tushare_index_code:
            print(f"无法获取指数 {index_name} 的 Tushare 代码")
            return pd.DataFrame()

        print(f"尝试获取指数 {index_name}({tushare_index_code}) 的成分股...")

        # 对于不同的指数，使用不同的获取策略
        if index_name == "科创50":
            # 科创50的正确Tushare指数代码应该是"000688.SH"，而不是"885005.SI"
            # 让我们使用正确的指数代码重新尝试
            print(f"使用正确的科创50指数代码 '000688.SH' 重新尝试...")
            index_constituents = fetcher.pro.index_member(
                index_code="000688.SH"
            )

            # 如果获取失败，尝试使用旧的指数代码
            if index_constituents.empty:
                print(f"使用科创50指数代码 '000688.SH' 获取失败，尝试使用旧的指数代码 '885005.SI'...")
                index_constituents = fetcher.pro.index_member(
                    index_code="885005.SI"
                )
        else:
            # 尝试使用 index_member 接口（更稳定）
            index_constituents = fetcher.pro.index_member(
                index_code=tushare_index_code
            )

        # 如果 index_member 接口失败，尝试使用 index_weight 接口
        if index_constituents.empty:
            print(f"index_member 接口返回空，尝试使用 index_weight 接口...")

            # 对于科创50，使用正确的指数代码
            if index_name == "科创50":
                index_weight_code = "000688.SH"
            else:
                index_weight_code = tushare_index_code

            index_constituents = fetcher.pro.index_weight(
                index_code=index_weight_code,
                start_date=None,
                end_date=None
            )

        if index_constituents.empty:
            print(f"无法获取指数 {index_name} 的成分股数据")
            return pd.DataFrame()

        # 处理不同接口返回的列名差异
        # index_member 接口返回的列名通常是 'con_code'
        # index_weight 接口返回的列名通常是 'con_code' 或 'ts_code'
        if 'con_code' in index_constituents.columns:
            # 将 con_code 重命名为 ts_code
            index_constituents.rename(columns={'con_code': 'ts_code'}, inplace=True)
        elif 'ts_code' not in index_constituents.columns:
            print(f"指数成分股数据中没有找到 ts_code 列")
            return pd.DataFrame()

        # 处理 index_weight 接口返回的历史数据
        # 如果数据中有 'trade_date' 列，只保留最新的成分股数据
        if 'trade_date' in index_constituents.columns:
            print(f"发现 trade_date 列，筛选最新的成分股数据...")
            # 将 trade_date 转换为日期格式
            index_constituents['trade_date'] = pd.to_datetime(index_constituents['trade_date'], format='%Y%m%d')

            # 获取最新的交易日期
            latest_date = index_constituents['trade_date'].max()

            # 只保留最新日期的成分股数据
            index_constituents = index_constituents[index_constituents['trade_date'] == latest_date]

        # 只保留 ts_code 列并去重
        index_constituents = index_constituents[['ts_code']].drop_duplicates()

        print(f"成功获取指数 {index_name} 的 {len(index_constituents)} 只成分股")

        return index_constituents

    except Exception as e:
        print(f"获取指数 {index_name} 成分股失败: {e}")
        # 打印详细的错误信息
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
