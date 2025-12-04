"""
测试脚本 - 验证股票筛选工具的基本功能
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import validate_config, DEFAULT_LONG_PERIOD, DEFAULT_DIFF_THRESHOLD
from stock_data import StockDataFetcher
from stock_analyzer import StockAnalyzer

def test_config():
    """测试配置"""
    print("测试配置...")
    if validate_config():
        print("✓ 配置验证通过")
        return True
    else:
        print("✗ 配置验证失败，请检查tushare API token")
        return False

def test_stock_data():
    """测试股票数据获取"""
    print("\n测试股票数据获取...")
    fetcher = StockDataFetcher()

    # 测试获取股票列表
    stock_list = fetcher.get_stock_list()
    if not stock_list.empty:
        print(f"✓ 获取到 {len(stock_list)} 只股票")
        return stock_list
    else:
        print("✗ 无法获取股票列表")
        return None

def test_stock_analysis(stock_list):
    """测试股票分析功能"""
    print("\n测试股票分析功能...")
    analyzer = StockAnalyzer()

    # 测试分析单只股票
    sample_stock = stock_list.iloc[0]['ts_code']
    print(f"分析股票: {sample_stock}")

    result = analyzer.calculate_ma_diff(sample_stock, DEFAULT_LONG_PERIOD)
    if result:
        print(f"✓ 股票分析成功")
        print(f"  长期均值: {result['long_mean']:.2f}")
        print(f"  最新5日均线: {result['latest_ma5']:.2f}")
        print(f"  差异百分比: {result['diff_percent']:.2f}%")
        return True
    else:
        print("✗ 股票分析失败")
        return False

def test_batch_analysis(stock_list):
    """测试批量分析功能"""
    print("\n测试批量分析功能（前3只股票）...")
    analyzer = StockAnalyzer()

    # 只分析前3只股票
    test_list = stock_list.head(3)
    result_df = analyzer.analyze_stocks(test_list, DEFAULT_LONG_PERIOD, DEFAULT_DIFF_THRESHOLD)

    if not result_df.empty:
        print(f"✓ 批量分析成功")
        print(f"  找到 {len(result_df)} 只符合条件的股票")
        print("\n分析结果:")
        print(result_df.to_string(index=False))
        return True
    else:
        print(f"✗ 批量分析完成，但未找到符合条件的股票")
        return True  # 没有找到股票也是正常情况

def test_stock_details(stock_list):
    """测试股票详情获取"""
    print("\n测试股票详情获取...")
    analyzer = StockAnalyzer()

    sample_stock = stock_list.iloc[0]['ts_code']
    details = analyzer.get_stock_details(sample_stock, 30)

    if details:
        print(f"✓ 获取股票详情成功")
        print(f"  获取到 {len(details['trade_dates'])} 天数据")
        print(f"  最新收盘价: {details['latest_data']['close']:.2f}")
        print(f"  最新5日均线: {details['latest_data']['ma5']:.2f}")
        return True
    else:
        print("✗ 获取股票详情失败")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("A股股票均线差异筛选工具 - 功能测试")
    print("=" * 50)

    # 测试步骤
    tests = [
        ("配置验证", test_config),
        ("股票数据获取", test_stock_data),
        ("股票分析功能", test_stock_analysis, {"stock_list": None}),
        ("批量分析功能", test_batch_analysis, {"stock_list": None}),
        ("股票详情获取", test_stock_details, {"stock_list": None})
    ]

    passed = 0
    failed = 0
    stock_list = None

    for test_name, test_func, *args in tests:
        try:
            if test_name == "股票数据获取":
                stock_list = test_func()
                if stock_list is not None:
                    passed += 1
                else:
                    failed += 1
            elif test_name in ["股票分析功能", "批量分析功能", "股票详情获取"]:
                if stock_list is not None:
                    if test_func(stock_list):
                        passed += 1
                    else:
                        failed += 1
                else:
                    print(f"跳过测试: {test_name} (依赖股票数据)")
            else:
                if test_func():
                    passed += 1
                else:
                    failed += 1
        except Exception as e:
            print(f"✗ {test_name} 失败: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"测试结果: 成功 {passed}, 失败 {failed}")
    print("=" * 50)

    if passed == len(tests) or (passed >= 3 and failed <= 2):
        print("\n🎉 基本功能测试通过！")
        print("您可以运行 app.py 启动Web服务了")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查配置和网络连接")
        return False

if __name__ == "__main__":
    main()