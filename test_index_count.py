"""
测试宽基指数成分股数量是否正确
"""

import pandas as pd
from stock_data import StockDataFetcher
from wide_indexes import filter_stocks_by_indexes, get_wide_indexes

def test_index_constituent_count():
    """测试宽基指数成分股数量是否正确"""

    # 初始化数据获取器
    try:
        fetcher = StockDataFetcher()
        print("数据获取器初始化成功")
    except Exception as e:
        print(f"数据获取器初始化失败: {e}")
        return

    # 获取所有股票列表
    stock_list = fetcher.get_stock_list()
    print(f"获取到 {len(stock_list)} 只股票")

    if stock_list.empty:
        print("没有获取到股票数据，无法测试指数筛选功能")
        return

    # 测试所有宽基指数
    wide_indexes = get_wide_indexes()
    print(f"\n可用的宽基指数: {wide_indexes}")

    # 每个指数的预期最大成分股数量
    expected_max_counts = {
        "科创50": 50,
        "上证50": 50,
        "沪深300": 300,
        "中证500": 500,
        "中证1000": 1000
    }

    for index_name in wide_indexes:
        if index_name == "全选":
            continue  # 全选不需要测试

        print(f"\n=== 测试指数: {index_name} ===")
        print(f"预期最大成分股数量: {expected_max_counts.get(index_name)}")

        # 测试指数筛选
        filtered_stocks = filter_stocks_by_indexes(stock_list, [index_name], fetcher)

        actual_count = len(filtered_stocks)
        print(f"实际筛选结果数量: {actual_count}")

        # 检查实际数量是否符合预期
        expected_max = expected_max_counts.get(index_name, actual_count)
        if actual_count <= expected_max:
            print(f"✓ 成分股数量符合预期（不超过 {expected_max} 只）")
        else:
            print(f"✗ 成分股数量超过预期（{actual_count} > {expected_max}）")

        if not filtered_stocks.empty:
            # 打印前几只股票
            print(filtered_stocks[['ts_code', 'name', 'industry']].head())

def test_simplified_index_constituent_count():
    """测试简化版指数成分股数量是否正确"""

    # 创建一个模拟的股票列表
    # 为每个指数创建足够数量的股票
    # 创建一个模拟的股票列表
    # 为每个指数创建足够数量的股票
    kechuang50_stocks = [f'6880{i:02d}.SH' for i in range(1, 60)]  # 688开头的股票，59只
    shangzheng50_stocks = [f'600{i:03d}.SH' for i in range(1, 60)] + [f'601{i:03d}.SH' for i in range(1, 10)]  # 600, 601开头的股票，68只
    hushang300_stocks = [f'000{i:03d}.SZ' for i in range(1, 310)]  # 深圳股票，309只
    zhongzheng500_stocks = [f'002{i:03d}.SZ' for i in range(1, 510)]  # 中小板股票，509只
    zhongzheng1000_stocks = [f'300{i:03d}.SZ' for i in range(1, 1010)]  # 创业板股票，1009只

    # 合并所有股票
    all_ts_codes = kechuang50_stocks + shangzheng50_stocks + hushang300_stocks[:10]  # 只取部分沪深300股票

    data = {
        'ts_code': all_ts_codes,
        'name': [f'股票{i+1}' for i in range(len(all_ts_codes))],
        'industry': ['半导体']*len(kechuang50_stocks) +
                   ['银行']*len(shangzheng50_stocks) +
                   ['房地产']*len(hushang300_stocks[:10])
    }

    stock_list = pd.DataFrame(data)
    print(f"模拟股票列表: {len(stock_list)} 只股票")

    # 测试简化版指数筛选
    from wide_indexes import get_simplified_index_constituents

    indexes_to_test = ['科创50', '上证50', '沪深300', '中证500', '中证1000']

    for index_name in indexes_to_test:
        print(f"\n=== 测试简化版指数筛选: {index_name} ===")

        simplified_ts_codes = get_simplified_index_constituents(index_name, stock_list)
        filtered_stocks = stock_list[stock_list['ts_code'].isin(simplified_ts_codes)]

        actual_count = len(filtered_stocks)
        print(f"实际筛选结果数量: {actual_count}")

        # 检查实际数量是否符合预期
        expected_max = {
            "科创50": 50,
            "上证50": 50,
            "沪深300": 300,
            "中证500": 500,
            "中证1000": 1000
        }.get(index_name, actual_count)

        if actual_count <= expected_max:
            print(f"✓ 成分股数量符合预期（不超过 {expected_max} 只）")
        else:
            print(f"✗ 成分股数量超过预期（{actual_count} > {expected_max}）")

        if not filtered_stocks.empty:
            print(filtered_stocks[['ts_code', 'name', 'industry']].head())

if __name__ == "__main__":
    print("=== 测试宽基指数成分股数量是否正确 ===\n")

    # 测试简化版（不需要Tushare API）
    print("=== 测试简化版指数筛选 ===")
    test_simplified_index_constituent_count()

    # 测试完整版（需要Tushare API）
    print("\n=== 测试完整版指数筛选（需要Tushare API） ===")
    try:
        test_index_constituent_count()
    except Exception as e:
        print(f"完整版测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== 测试完成 ===\n")
