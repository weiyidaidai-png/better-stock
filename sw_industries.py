"""
申万一级行业分类数据
最新的申万一级行业分类（28类）
"""

# 申万一级行业分类列表
SW_INDUSTRIES = [
    "农林牧渔",
    "采掘",
    "化工",
    "钢铁",
    "有色金属",
    "电子",
    "家用电器",
    "食品饮料",
    "纺织服装",
    "轻工制造",
    "医药生物",
    "公用事业",
    "交通运输",
    "房地产",
    "商业贸易",
    "休闲服务",
    "综合",
    "建筑材料",
    "建筑装饰",
    "电气设备",
    "国防军工",
    "计算机",
    "传媒",
    "通信",
    "银行",
    "非银金融",
    "汽车",
    "机械设备"
]

def get_sw_industries():
    """获取申万一级行业列表"""
    return SW_INDUSTRIES.copy()

def is_valid_industry(industry_name):
    """检查行业名称是否属于申万一级行业分类"""
    return industry_name in SW_INDUSTRIES

def filter_stocks_by_industries(stock_list, industries):
    """
    根据行业筛选股票列表

    Args:
        stock_list: pandas DataFrame，包含股票列表数据，必须包含'industry'列
        industries: 行业名称列表，或None/空列表表示不筛选

    Returns:
        pandas DataFrame，筛选后的股票列表
    """
    if not industries or stock_list.empty:
        return stock_list

    # 筛选指定行业的股票
    return stock_list[stock_list['industry'].isin(industries)]

if __name__ == "__main__":
    # 测试功能
    print("申万一级行业分类（28类）：")
    for i, industry in enumerate(get_sw_industries(), 1):
        print(f"{i:2d}. {industry}")

    print(f"\n行业总数：{len(get_sw_industries())}")

    # 测试行业验证
    test_industries = ["电子", "电力设备", "不存在的行业"]
    for industry in test_industries:
        print(f"\n'{industry}' 是否为有效行业：{is_valid_industry(industry)}")