"""
测试宽基指数筛选功能
"""

import pandas as pd
from stock_data import StockDataFetcher
from wide_indexes import filter_stocks_by_indexes, get_wide_indexes

def test_index_filter():
    """测试宽基指数筛选功能"""

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

    for index_name in wide_indexes:
        if index_name == "全选":
            continue  # 全选不需要测试

        print(f"\n测试指数: {index_name}")

        # 测试指数筛选
        filtered_stocks = filter_stocks_by_indexes(stock_list, [index_name], fetcher)

        print(f"筛选结果: {len(filtered_stocks)} 只股票")

        if not filtered_stocks.empty:
            # 打印前几只股票
            print(filtered_stocks[['ts_code', 'name', 'industry']].head())
        else:
            print("警告: 没有筛选出任何股票，可能是指数成分股数据获取失败")

def test_simplified_index_filter():
    """测试简化版指数筛选功能"""

    # 创建一个模拟的股票列表
    data = {
        'ts_code': [
            '600000.SH', '600036.SH', '601318.SH',  # 上证50成分股
            '688001.SH', '688002.SH', '688003.SH',  # 科创50成分股
            '000001.SZ', '000002.SZ', '000858.SZ',  # 沪深300成分股
            '002001.SZ', '002002.SZ', '002003.SZ',  # 中证500成分股
            '300001.SZ', '300002.SZ', '300003.SZ'   # 中证1000成分股
        ],
        'name': [
            '浦发银行', '招商银行', '中国平安',  # 上证50成分股
            '华兴源创', '睿创微纳', '天准科技',  # 科创50成分股
            '平安银行', '万科A', '五粮液',        # 沪深300成分股
            '新和成', '浙江医药', '恒瑞医药',     # 中证500成分股
            '特锐德', '神州泰岳', '乐普医疗'     # 中证1000成分股
        ],
        'industry': [
            '银行', '银行', '保险',            # 上证50成分股
            '半导体', '半导体', '半导体',        # 科创50成分股
            '银行', '房地产', '食品饮料',        # 沪深300成分股
            '化工', '医药生物', '医药生物',     # 中证500成分股
            '电气设备', '计算机', '医药生物'     # 中证1000成分股
        ]
    }

    stock_list = pd.DataFrame(data)
    print(f"模拟股票列表: {len(stock_list)} 只股票")

    # 测试简化版指数筛选
    from wide_indexes import get_simplified_index_constituents

    indexes_to_test = ['科创50', '上证50', '沪深300', '中证500', '中证1000']

    for index_name in indexes_to_test:
        print(f"\n测试简化版指数筛选: {index_name}")

        simplified_ts_codes = get_simplified_index_constituents(index_name, stock_list)
        filtered_stocks = stock_list[stock_list['ts_code'].isin(simplified_ts_codes)]

        print(f"筛选结果: {len(filtered_stocks)} 只股票")
        print(filtered_stocks[['ts_code', 'name', 'industry']])

if __name__ == "__main__":
    print("=== 测试宽基指数筛选功能 ===\n")

    # 测试简化版（不需要Tushare API）
    print("=== 测试简化版指数筛选 ===\n")
    test_simplified_index_filter()

    # 测试完整版（需要Tushare API）
    print("\n=== 测试完整版指数筛选（需要Tushare API） ===\n")
    try:
        test_index_filter()
    except Exception as e:
        print(f"完整版测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== 测试完成 ===\n")
