"""
简单测试宽基指数成分股数量是否正确
"""

import pandas as pd
from stock_data import StockDataFetcher
from wide_indexes import filter_stocks_by_indexes, get_wide_indexes, get_simplified_index_constituents

def test_simplified_indexes():
    """测试简化版指数筛选功能"""

    print("=== 测试简化版指数筛选功能 ===")

    # 创建一个简单的模拟股票列表
    data = {
        'ts_code': [
            # 科创50股票（688开头）
            '688001.SH', '688002.SH', '688003.SH', '688004.SH', '688005.SH',
            '688006.SH', '688007.SH', '688008.SH', '688009.SH', '688010.SH',
            '688011.SH', '688012.SH', '688013.SH', '688014.SH', '688015.SH',
            '688016.SH', '688017.SH', '688018.SH', '688019.SH', '688020.SH',
            '688021.SH', '688022.SH', '688023.SH', '688024.SH', '688025.SH',
            '688026.SH', '688027.SH', '688028.SH', '688029.SH', '688030.SH',
            '688031.SH', '688032.SH', '688033.SH', '688034.SH', '688035.SH',
            '688036.SH', '688037.SH', '688038.SH', '688039.SH', '688040.SH',

            # 上证50股票（600, 601开头）
            '600000.SH', '600036.SH', '601318.SH', '600030.SH', '600009.SH',
            '600519.SH', '600276.SH', '601166.SH', '601328.SH', '600016.SH',
            '600104.SH', '600837.SH', '601668.SH', '601628.SH', '601988.SH',
            '600028.SH', '601288.SH', '601939.SH', '601857.SH', '601186.SH',
            '601601.SH', '600690.SH', '600585.SH', '600340.SH', '601818.SH',
            '601688.SH', '600050.SH', '600196.SH', '601390.SH', '601899.SH',
            '601088.SH', '601998.SH', '600703.SH', '600019.SH', '600887.SH',

            # 其他股票
            '000001.SZ', '000002.SZ', '000858.SZ', '000063.SZ', '000069.SZ'
        ],
        'name': [f'股票{i+1}' for i in range(105)],
        'industry': ['半导体']*40 + ['银行']*50 + ['其他']*15
    }

    stock_list = pd.DataFrame(data)
    print(f"模拟股票列表: {len(stock_list)} 只股票")

    # 测试各个指数
    test_cases = [
        ("科创50", 50),
        ("上证50", 50),
        ("沪深300", 300),
        ("中证500", 500),
        ("中证1000", 1000)
    ]

    for index_name, expected_max in test_cases:
        print(f"\n测试指数: {index_name}")
        print(f"预期最大数量: {expected_max}")

        # 测试简化版指数筛选
        result = get_simplified_index_constituents(index_name, stock_list)
        actual_count = len(result)

        print(f"实际筛选数量: {actual_count}")

        if actual_count <= expected_max:
            print(f"测试通过: 数量符合预期")
        else:
            print(f"测试失败: 数量超过预期")

def test_real_tushare_data():
    """测试真实的Tushare数据"""

    print("\n=== 测试真实的Tushare数据 ===")

    try:
        # 初始化数据获取器
        fetcher = StockDataFetcher()
        print("数据获取器初始化成功")

        # 获取所有股票列表
        stock_list = fetcher.get_stock_list()
        print(f"获取到 {len(stock_list)} 只股票")

        if stock_list.empty:
            print("没有获取到股票数据")
            return

        # 测试各个指数
        test_cases = [
            ("科创50", 50),
            ("上证50", 50),
            ("沪深300", 300),
            ("中证500", 500),
            ("中证1000", 1000)
        ]

        for index_name, expected_max in test_cases:
            print(f"\n测试指数: {index_name}")
            print(f"预期最大数量: {expected_max}")

            # 测试指数筛选
            filtered_stocks = filter_stocks_by_indexes(stock_list, [index_name], fetcher)
            actual_count = len(filtered_stocks)

            print(f"实际筛选数量: {actual_count}")

            if actual_count <= expected_max:
                print(f"测试通过: 数量符合预期")
            else:
                print(f"测试失败: 数量超过预期")

            if actual_count > 0 and actual_count <= 10:
                print(filtered_stocks[['ts_code', 'name', 'industry']])

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simplified_indexes()
    test_real_tushare_data()
    print("\n=== 所有测试完成 ===\n")
