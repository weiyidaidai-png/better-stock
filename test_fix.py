"""
测试修复后的指数成分股数量问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_data import StockDataFetcher
from wide_indexes import filter_stocks_by_indexes

def test_index_fix():
    """测试修复后的指数成分股数量问题"""

    print("测试修复后的指数成分股数量问题")
    print("=" * 50)

    try:
        # 初始化数据获取器
        fetcher = StockDataFetcher()
        print("✓ 数据获取器初始化成功")

        # 获取所有股票列表
        stock_list = fetcher.get_stock_list()
        print(f"✓ 获取到 {len(stock_list)} 只股票")

        if stock_list.empty:
            print("✗ 没有获取到股票数据")
            return

        # 测试各个指数的成分股数量
        indexes_to_test = ['科创50', '上证50', '沪深300', '中证500', '中证1000']
        expected_max_counts = {
            '科创50': 50,
            '上证50': 50,
            '沪深300': 300,
            '中证500': 500,
            '中证1000': 1000
        }

        for index_name in indexes_to_test:
            print(f"\n测试指数: {index_name}")
            print(f"预期最大成分股数量: {expected_max_counts[index_name]}")

            # 获取指数成分股
            filtered_stocks = filter_stocks_by_indexes(stock_list, [index_name], fetcher)
            actual_count = len(filtered_stocks)

            print(f"实际获取的成分股数量: {actual_count}")

            if actual_count <= expected_max_counts[index_name]:
                print(f"✓ 测试通过: 成分股数量在合理范围内")
            else:
                print(f"✗ 测试失败: 成分股数量超过预期最大值")

            # 如果有成分股，打印几只示例
            if actual_count > 0 and actual_count <= 5:
                print("成分股示例:")
                print(filtered_stocks[['ts_code', 'name', 'industry']])
            elif actual_count > 5:
                print(f"共 {actual_count} 只成分股，显示前5只:")
                print(filtered_stocks[['ts_code', 'name', 'industry']].head())

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_index_fix()
    print("\n" + "=" * 50)
    print("测试完成")
