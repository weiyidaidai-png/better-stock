<<<<<<< HEAD
"""
申万一级行业分类数据
最新的申万一级行业分类（28类）
"""
import pandas as pd

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

# Tushare行业名称到申万行业分类的映射表
TUSHARE_TO_SW_MAPPING = {
    # 计算机相关
    "计算机应用": "计算机",
    "计算机设备": "计算机",
    "软件开发": "计算机",
    "软件服务": "计算机",

    # 农林牧渔相关
    "农业": "农林牧渔",
    "林业": "农林牧渔",
    "畜牧业": "农林牧渔",
    "渔业": "农林牧渔",
    "农产品加工": "农林牧渔",

    # 电子相关
    "电子信息": "电子",
    "电子制造": "电子",
    "半导体": "电子",
    "集成电路": "电子",
    "光学光电子": "电子",
    "电子元件": "电子",

    # 其他常见映射
    "通信设备": "通信",
    "通信服务": "通信",
    "传媒娱乐": "传媒",
    "互联网": "传媒",
    "汽车制造": "汽车",
    "汽车零部件": "汽车",
    "机械设备": "机械设备",
    "机械制造": "机械设备",
    "电气设备": "电气设备",
    "电力设备": "电气设备",
    "医疗器械": "医药生物",
    "医药制造": "医药生物",
    "医疗服务": "医药生物",
    "化学制药": "医药生物",
    "生物制品": "医药生物",
    "食品加工": "食品饮料",
    "饮料制造": "食品饮料",
    "白酒": "食品饮料",
    "啤酒": "食品饮料",
    "家电制造": "家用电器",
    "纺织制造": "纺织服装",
    "服装家纺": "纺织服装",
    "化工原料": "化工",
    "化学制品": "化工",
    "石油化工": "化工",
    "钢铁": "钢铁",
    "有色金属": "有色金属",
    "煤炭开采": "采掘",
    "石油开采": "采掘",
    "房地产开发": "房地产",
    "建筑工程": "建筑装饰",
    "建筑材料": "建筑材料",
    "交通运输": "交通运输",
    "仓储物流": "交通运输",
    "银行": "银行",
    "证券": "非银金融",
    "保险": "非银金融",
    "多元金融": "非银金融",
    "公用事业": "公用事业",
    "环保工程": "公用事业",
    "商业贸易": "商业贸易",
    "零售": "商业贸易",
    "餐饮": "休闲服务",
    "旅游": "休闲服务",
    "酒店": "休闲服务",
    "综合": "综合",
    "国防军工": "国防军工",
    "航空航天": "国防军工"
}

def _map_tushare_to_sw_industry(industry):
    """将Tushare行业名称映射到申万行业分类"""
    if pd.isna(industry):
        return None

    # 先尝试精确匹配
    if industry in TUSHARE_TO_SW_MAPPING:
        return TUSHARE_TO_SW_MAPPING[industry]

    # 尝试模糊匹配（包含关键词）
    for tushare_industry, sw_industry in TUSHARE_TO_SW_MAPPING.items():
        if tushare_industry in industry or industry in tushare_industry:
            return sw_industry

    # 如果没有匹配到，返回原行业名称
    return industry

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

    # 创建一个临时列，存储映射后的申万行业名称
    temp_df = stock_list.copy()
    temp_df['sw_industry'] = temp_df['industry'].apply(_map_tushare_to_sw_industry)

    # 筛选指定行业的股票（包括那些映射后匹配的股票）
    # 同时保留那些行业为NaN或无法映射的股票，如果用户选择了"未知行业"或类似选项
    # 注意：这里我们假设当用户选择所有行业时，会包含所有股票，包括行业未知的

    # 检查是否用户选择了所有行业（28个申万一级行业）
    all_industries_selected = set(industries) == set(SW_INDUSTRIES)

    if all_industries_selected:
        # 如果选择了所有行业，返回所有股票，包括那些行业为NaN的
        return stock_list
    else:
        # 否则，筛选那些映射后的行业在指定行业列表中的股票
        # 同时处理那些行业为NaN的情况 - 这些股票不会被筛选到，除非有特殊处理
        filtered_df = temp_df[temp_df['sw_industry'].isin(industries)]

        # 返回原始DataFrame的列（去除临时列）
        return filtered_df[stock_list.columns]

if __name__ == "__main__":
    # 测试功能
    print("申万一级行业分类（28类）：")
    for i, industry in enumerate(get_sw_industries(), 1):
        print(f"{i:2d}. {industry}")

    print(f"\n行业总数：{len(get_sw_industries())}")

    # 测试行业验证
    test_industries = ["电子", "电力设备", "不存在的行业"]
    for industry in test_industries:
=======
"""
申万一级行业分类数据
最新的申万一级行业分类（28类）
"""
import pandas as pd

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

# Tushare行业名称到申万行业分类的映射表
TUSHARE_TO_SW_MAPPING = {
    # 计算机相关
    "计算机应用": "计算机",
    "计算机设备": "计算机",
    "软件开发": "计算机",
    "软件服务": "计算机",

    # 农林牧渔相关
    "农业": "农林牧渔",
    "林业": "农林牧渔",
    "畜牧业": "农林牧渔",
    "渔业": "农林牧渔",
    "农产品加工": "农林牧渔",

    # 电子相关
    "电子信息": "电子",
    "电子制造": "电子",
    "半导体": "电子",
    "集成电路": "电子",
    "光学光电子": "电子",
    "电子元件": "电子",

    # 其他常见映射
    "通信设备": "通信",
    "通信服务": "通信",
    "传媒娱乐": "传媒",
    "互联网": "传媒",
    "汽车制造": "汽车",
    "汽车零部件": "汽车",
    "机械设备": "机械设备",
    "机械制造": "机械设备",
    "电气设备": "电气设备",
    "电力设备": "电气设备",
    "医疗器械": "医药生物",
    "医药制造": "医药生物",
    "医疗服务": "医药生物",
    "化学制药": "医药生物",
    "生物制品": "医药生物",
    "食品加工": "食品饮料",
    "饮料制造": "食品饮料",
    "白酒": "食品饮料",
    "啤酒": "食品饮料",
    "家电制造": "家用电器",
    "纺织制造": "纺织服装",
    "服装家纺": "纺织服装",
    "化工原料": "化工",
    "化学制品": "化工",
    "石油化工": "化工",
    "钢铁": "钢铁",
    "有色金属": "有色金属",
    "煤炭开采": "采掘",
    "石油开采": "采掘",
    "房地产开发": "房地产",
    "建筑工程": "建筑装饰",
    "建筑材料": "建筑材料",
    "交通运输": "交通运输",
    "仓储物流": "交通运输",
    "银行": "银行",
    "证券": "非银金融",
    "保险": "非银金融",
    "多元金融": "非银金融",
    "公用事业": "公用事业",
    "环保工程": "公用事业",
    "商业贸易": "商业贸易",
    "零售": "商业贸易",
    "餐饮": "休闲服务",
    "旅游": "休闲服务",
    "酒店": "休闲服务",
    "综合": "综合",
    "国防军工": "国防军工",
    "航空航天": "国防军工"
}

def _map_tushare_to_sw_industry(industry):
    """将Tushare行业名称映射到申万行业分类"""
    if pd.isna(industry):
        return None

    # 先尝试精确匹配
    if industry in TUSHARE_TO_SW_MAPPING:
        return TUSHARE_TO_SW_MAPPING[industry]

    # 尝试模糊匹配（包含关键词）
    for tushare_industry, sw_industry in TUSHARE_TO_SW_MAPPING.items():
        if tushare_industry in industry or industry in tushare_industry:
            return sw_industry

    # 如果没有匹配到，返回原行业名称
    return industry

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

    # 创建一个临时列，存储映射后的申万行业名称
    temp_df = stock_list.copy()
    temp_df['sw_industry'] = temp_df['industry'].apply(_map_tushare_to_sw_industry)

    # 筛选指定行业的股票（包括那些映射后匹配的股票）
    # 同时保留那些行业为NaN或无法映射的股票，如果用户选择了"未知行业"或类似选项
    # 注意：这里我们假设当用户选择所有行业时，会包含所有股票，包括行业未知的

    # 检查是否用户选择了所有行业（28个申万一级行业）
    all_industries_selected = set(industries) == set(SW_INDUSTRIES)

    if all_industries_selected:
        # 如果选择了所有行业，返回所有股票，包括那些行业为NaN的
        return stock_list
    else:
        # 否则，筛选那些映射后的行业在指定行业列表中的股票
        # 同时处理那些行业为NaN的情况 - 这些股票不会被筛选到，除非有特殊处理
        filtered_df = temp_df[temp_df['sw_industry'].isin(industries)]

        # 返回原始DataFrame的列（去除临时列）
        return filtered_df[stock_list.columns]

if __name__ == "__main__":
    # 测试功能
    print("申万一级行业分类（28类）：")
    for i, industry in enumerate(get_sw_industries(), 1):
        print(f"{i:2d}. {industry}")

    print(f"\n行业总数：{len(get_sw_industries())}")

    # 测试行业验证
    test_industries = ["电子", "电力设备", "不存在的行业"]
    for industry in test_industries:
>>>>>>> origin/debug/wide-industries
        print(f"\n'{industry}' 是否为有效行业：{is_valid_industry(industry)}")