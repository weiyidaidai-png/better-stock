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
        print(f"[指数筛选] 未指定指数或股票列表为空，返回全部股票")
        return stock_list

    # 检查是否选择了"全选"
    if "全选" in indexes:
        print(f"[指数筛选] 选择了'全选'，返回全部股票")
        return stock_list

    # 获取所有选择的指数的成分股
    all_index_stocks = []
    api_failed_indexes = []

    for index_name in indexes:
        if index_name not in WIDE_INDEXES or index_name == "全选":
            print(f"[指数筛选] 跳过无效指数：{index_name}")
            continue

        print(f"\n[指数筛选] 开始处理指数：{index_name}")
        # 获取指数成分股
        index_stocks = get_index_constituents(index_name, fetcher)

        if not index_stocks.empty:
            index_ts_codes = index_stocks['ts_code'].tolist()
            all_index_stocks.extend(index_ts_codes)
            print(f"[指数筛选] 指数 {index_name} 获取成功，有 {len(index_ts_codes)} 只成分股")
            print(f"[指数筛选] 前5只成分股：{index_ts_codes[:5]}")
        else:
            print(f"[指数筛选] 警告：无法获取指数 {index_name} 的成分股数据")
            api_failed_indexes.append(index_name)

    # 去重指数成分股
    all_index_stocks = list(set(all_index_stocks))

    # 如果没有获取到任何指数成分股，返回空列表
    if not all_index_stocks:
        error_msg = f"[指数筛选] 错误：无法获取任何指数的成分股数据"
        if api_failed_indexes:
            error_msg += f"，API调用失败的指数：{api_failed_indexes}"
        print(error_msg)
        return pd.DataFrame(columns=stock_list.columns)

    print(f"\n[指数筛选汇总]")
    print(f"- 所有选中的指数共有 {len(all_index_stocks)} 只成分股（去重后）")

    if api_failed_indexes:
        print(f"- 注意：以下指数API调用失败，未包含其成分股：{api_failed_indexes}")

    # 筛选出在任何一个指数成分股中的股票
    # 注意：指数筛选是"或"的关系，即只要股票在任何一个选中的指数中，就会被保留
    filtered_df = stock_list[stock_list['ts_code'].isin(all_index_stocks)]

    print(f"- 筛选后得到 {len(filtered_df)} 只股票")
    print(f"- 筛选结果前5只股票：{filtered_df['ts_code'].tolist()[:5]}")

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

def validate_index_constituents(index_name, constituents, expected_count=None):
    """
    验证指数成分股的准确性

    Args:
        index_name: 指数名称
        constituents: 成分股DataFrame，必须包含'ts_code'列
        expected_count: 预期的成分股数量（可选）

    Returns:
        dict: 验证结果，包含以下字段：
            - valid: 是否通过验证
            - message: 验证结果信息
            - issues: 发现的问题列表（如果有）
    """
    results = {
        'valid': True,
        'message': '验证通过',
        'issues': []
    }

    print(f"[指数验证] 开始验证指数 {index_name} 的成分股")
    print(f"[指数验证] 成分股数量：{len(constituents)}")

    if constituents.empty:
        results['valid'] = False
        results['message'] = '成分股数据为空'
        results['issues'].append('成分股数据为空')
        return results

    # 检查是否包含ts_code列
    if 'ts_code' not in constituents.columns:
        results['valid'] = False
        results['message'] = '成分股数据中没有ts_code列'
        results['issues'].append('缺少ts_code列')
        return results

    # 验证成分股数量是否符合预期
    if expected_count is not None:
        actual_count = len(constituents)
        if actual_count != expected_count:
            results['valid'] = False
            results['message'] = f"成分股数量不符合预期（预期：{expected_count}，实际：{actual_count}）"
            results['issues'].append(f"数量不符：预期{expected_count}，实际{actual_count}")

    # 对于特定指数，进行额外验证
    if index_name == "上证50":
        # 上证50成分股应该主要是上海证券交易所的股票（600、601、603开头）
        # 注意：现在上证50也包含一些科创板股票（688开头）
        valid_prefixes = ('600', '601', '603', '688')
        valid_stocks = constituents[constituents['ts_code'].str.startswith(valid_prefixes)]
        invalid_stocks = constituents[~constituents['ts_code'].str.startswith(valid_prefixes)]

        print(f"[指数验证] 上证50中有效市场股票数量：{len(valid_stocks)}")
        print(f"[指数验证] 上证50中无效市场股票数量：{len(invalid_stocks)}")

        if len(invalid_stocks) > 0:
            results['valid'] = False
            results['issues'].append(f"包含无效市场股票：{invalid_stocks['ts_code'].tolist()}")

    elif index_name == "科创50":
        # 科创50成分股应该是科创板股票（688开头）
        star_stocks = constituents[constituents['ts_code'].str.startswith('688')]
        non_star_stocks = constituents[~constituents['ts_code'].str.startswith('688')]

        print(f"[指数验证] 科创50中科创板股票数量：{len(star_stocks)}")
        print(f"[指数验证] 科创50中非科创板股票数量：{len(non_star_stocks)}")

        if len(non_star_stocks) > 0:
            results['valid'] = False
            results['issues'].append(f"包含非科创板股票：{non_star_stocks['ts_code'].tolist()}")

    # 检查是否有重复的股票代码
    duplicate_ts_codes = constituents[constituents.duplicated('ts_code', keep=False)]['ts_code'].tolist()
    if duplicate_ts_codes:
        results['valid'] = False
        results['issues'].append(f"包含重复股票代码：{list(set(duplicate_ts_codes))}")

    # 更新验证结果消息
    if results['valid']:
        results['message'] = f"指数 {index_name} 成分股验证通过，共 {len(constituents)} 只成分股"
    else:
        results['message'] = f"指数 {index_name} 成分股验证失败，发现 {len(results['issues'])} 个问题"

    print(f"[指数验证] 验证结果：{results['message']}")
    if not results['valid']:
        print(f"[指数验证] 发现的问题：{results['issues']}")

    return results


def get_index_constituents(index_name, fetcher=None):
    """
    获取指定指数的成分股

    Args:
        index_name: 指数名称
        fetcher: StockDataFetcher 实例，用于获取数据

    Returns:
        pandas DataFrame，包含指数成分股数据，至少包含'ts_code'列
    """
    print(f"[指数成分股获取] 开始获取指数 {index_name} 的成分股")

    if not fetcher:
        print(f"[指数成分股获取] 错误：未提供数据获取器实例")
        return pd.DataFrame()

    try:
        # 获取 Tushare 指数代码
        tushare_index_code = get_tushare_index_code(index_name)
        if not tushare_index_code:
            print(f"[指数成分股获取] 错误：无法获取指数 {index_name} 的 Tushare 代码")
            return pd.DataFrame()

        print(f"[指数成分股获取] 指数 {index_name} 对应的 Tushare 代码：{tushare_index_code}")

        # 对于不同的指数，使用不同的获取策略
        if index_name == "科创50":
            # 科创50的正确Tushare指数代码应该是"000688.SH"，而不是"885005.SI"
            # 让我们使用正确的指数代码重新尝试
            print(f"[指数成分股获取] 科创50特殊处理：使用正确指数代码 '000688.SH'")
            index_constituents = fetcher.pro.index_member(
                index_code="000688.SH"
            )
            print(f"[指数成分股获取] 使用 '000688.SH' 获取结果数量：{len(index_constituents)}")

            # 如果获取失败，尝试使用旧的指数代码
            if index_constituents.empty:
                print(f"[指数成分股获取] 使用 '000688.SH' 获取失败，尝试旧代码 '885005.SI'")
                index_constituents = fetcher.pro.index_member(
                    index_code="885005.SI"
                )
                print(f"[指数成分股获取] 使用 '885005.SI' 获取结果数量：{len(index_constituents)}")
        else:
            # 尝试使用 index_member 接口（更稳定）
            print(f"[指数成分股获取] 尝试使用 index_member 接口获取数据")
            index_constituents = fetcher.pro.index_member(
                index_code=tushare_index_code
            )
            print(f"[指数成分股获取] index_member 接口返回数量：{len(index_constituents)}")

        # 如果 index_member 接口失败，尝试使用 index_weight 接口
        if index_constituents.empty:
            print(f"[指数成分股获取] index_member 接口返回空，尝试使用 index_weight 接口")

            # 对于科创50，使用正确的指数代码
            if index_name == "科创50":
                index_weight_code = "000688.SH"
            else:
                index_weight_code = tushare_index_code

            print(f"[指数成分股获取] 使用 index_weight 接口，指数代码：{index_weight_code}")
            index_constituents = fetcher.pro.index_weight(
                index_code=index_weight_code,
                start_date=None,
                end_date=None
            )
            print(f"[指数成分股获取] index_weight 接口返回数量：{len(index_constituents)}")

        if index_constituents.empty:
            print(f"[指数成分股获取] 错误：无法获取指数 {index_name} 的成分股数据，所有接口均返回空")
            return pd.DataFrame()

        # 处理不同接口返回的列名差异
        # index_member 接口返回的列名通常是 'con_code'
        # index_weight 接口返回的列名通常是 'con_code' 或 'ts_code'
        print(f"[指数成分股获取] 原始数据列名：{list(index_constituents.columns)}")

        if 'con_code' in index_constituents.columns:
            # 将 con_code 重命名为 ts_code
            print(f"[指数成分股获取] 将 'con_code' 列重命名为 'ts_code'")
            index_constituents.rename(columns={'con_code': 'ts_code'}, inplace=True)
        elif 'ts_code' not in index_constituents.columns:
            print(f"[指数成分股获取] 错误：指数成分股数据中没有找到 'ts_code' 列")
            return pd.DataFrame()

        # 处理 index_weight 接口返回的历史数据
        # 如果数据中有 'trade_date' 列，只保留最新的成分股数据
        if 'trade_date' in index_constituents.columns:
            print(f"[指数成分股获取] 发现 'trade_date' 列，筛选最新的成分股数据")
            print(f"[指数成分股获取] 原始数据包含 {len(index_constituents)} 条历史记录")

            # 将 trade_date 转换为日期格式
            index_constituents['trade_date'] = pd.to_datetime(index_constituents['trade_date'], format='%Y%m%d')

            # 获取最新的交易日期
            latest_date = index_constituents['trade_date'].max()
            print(f"[指数成分股获取] 最新的交易日期：{latest_date.strftime('%Y-%m-%d')}")

            # 只保留最新日期的成分股数据
            index_constituents = index_constituents[index_constituents['trade_date'] == latest_date]
            print(f"[指数成分股获取] 筛选后保留 {len(index_constituents)} 条最新记录")

        # 只保留 ts_code 列并去重
        index_constituents = index_constituents[['ts_code']].drop_duplicates()
        print(f"[指数成分股获取] 去重后最终成分股数量：{len(index_constituents)}")

        if len(index_constituents) > 0:
            print(f"[指数成分股获取] 前5只成分股代码：{index_constituents['ts_code'].tolist()[:5]}")

        # 验证指数成分股的准确性
        expected_counts = {
            "科创50": 50,
            "上证50": 50,
            "沪深300": 300,
            "中证500": 500,
            "中证1000": 1000
        }
        expected_count = expected_counts.get(index_name)
        validation_result = validate_index_constituents(index_name, index_constituents, expected_count)

        if not validation_result['valid']:
            print(f"[指数成分股获取] 警告：指数 {index_name} 成分股验证失败")

        return index_constituents

    except Exception as e:
        print(f"[指数成分股获取] 异常：获取指数 {index_name} 成分股失败 - {type(e).__name__}: {str(e)}")
        # 打印详细的错误信息
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
