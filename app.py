from flask import Flask, render_template, request, jsonify
import threading
import time
from stock_analyzer import StockAnalyzer
from sw_industries import get_sw_industries
from wide_indexes import get_wide_indexes
from config import validate_config, DEFAULT_LONG_PERIOD, DEFAULT_DIFF_THRESHOLD, \
    DEFAULT_SHORT_PERIOD, DEFAULT_SHORT_PERIOD_UNIT, DEFAULT_LONG_PERIOD_UNIT, \
    MONTH_TO_TRADING_DAYS, DAYS_IN_YEAR, MAX_LONG_YEARS

app = Flask(__name__)

# 全局变量
analyzer = None
analysis_result = None  # 存储原始分析结果
filtered_result = None  # 存储行业后筛选结果
analysis_status = 'idle'  # idle, running, completed, error
analysis_progress = 0
current_pre_industries = None  # 当前使用的预筛选行业
current_pre_indexes = None  # 当前使用的预筛选宽基指数

def initialize_analyzer():
    """初始化股票分析器"""
    global analyzer
    if validate_config():
        analyzer = StockAnalyzer()
        return True
    else:
        return False

def background_analysis(stock_list, long_period, diff_threshold, short_period):
    """后台分析股票"""
    global analysis_result, filtered_result, analysis_status, analysis_progress

    try:
        analysis_status = 'running'
        analysis_progress = 0

        if analyzer is None:
            if not initialize_analyzer():
                raise Exception("无法初始化股票分析器，请检查tushare API token配置")

        # 开始分析
        total = len(stock_list)
        results = []

        for i, (_, stock) in enumerate(stock_list.iterrows()):
            ts_code = stock['ts_code']
            name = stock['name']
            industry = stock.get('industry', '未知行业')

            # 更新进度（确保进度平滑更新）
            current_progress = int((i + 1) / total * 100)
            if current_progress != analysis_progress:
                analysis_progress = current_progress

            # 分析单只股票
            result = analyzer.calculate_ma_diff(ts_code, long_period, short_period)

            if result:
                result['name'] = name
                result['industry'] = industry  # 添加行业信息
                results.append(result)

        # 处理分析结果
        import pandas as pd
        df = pd.DataFrame(results)

        if not df.empty:
            # 筛选差异大于阈值的股票
            df = df[df['diff_percent'].abs() > diff_threshold]

            # 按差异百分比绝对值从大到小排序
            df = df.sort_values('diff_percent', key=lambda x: x.abs(), ascending=False)

            # 保留需要的列并排序，增加行业列
            df = df[['ts_code', 'name', 'industry', 'diff_percent', 'latest_close', 'long_mean', 'short_mean', 'short_period']]

        analysis_result = df
        filtered_result = df  # 初始时过滤结果与原始结果相同
        analysis_status = 'completed'

    except Exception as e:
        print(f"分析失败: {e}")
        analysis_status = 'error'
        analysis_result = str(e)
        filtered_result = None

def convert_to_days(period, unit):
    """将周期转换为天数"""
    if unit == 'day':
        return period
    elif unit == 'month':
        return period * MONTH_TO_TRADING_DAYS
    elif unit == 'year':
        return period * DAYS_IN_YEAR
    return period

@app.route('/')
def index():
    """首页"""
    # 获取申万一级行业列表
    sw_industries = get_sw_industries()
    # 获取宽基指数列表
    wide_indexes = get_wide_indexes()

    return render_template('index.html',
                         default_long_period=DEFAULT_LONG_PERIOD,
                         default_long_unit=DEFAULT_LONG_PERIOD_UNIT,
                         default_short_period=DEFAULT_SHORT_PERIOD,
                         default_short_unit=DEFAULT_SHORT_PERIOD_UNIT,
                         default_diff_threshold=DEFAULT_DIFF_THRESHOLD,
                         sw_industries=sw_industries,
                         wide_indexes=wide_indexes)

@app.route('/api/configure', methods=['POST'])
def configure():
    """配置分析参数并开始分析"""
    global analysis_result, filtered_result, analysis_status, analysis_progress, current_pre_industries

    try:
        # 获取参数
        long_period = int(request.form.get('long_period', DEFAULT_LONG_PERIOD))
        long_period_unit = request.form.get('long_period_unit', DEFAULT_LONG_PERIOD_UNIT)
        short_period = int(request.form.get('short_period', DEFAULT_SHORT_PERIOD))
        short_period_unit = request.form.get('short_period_unit', DEFAULT_SHORT_PERIOD_UNIT)
        diff_threshold = float(request.form.get('diff_threshold', DEFAULT_DIFF_THRESHOLD))

        # 获取行业预筛选参数
        pre_industries = request.form.getlist('pre_industries[]')
        # 处理空列表情况
        pre_industries = pre_industries if pre_industries and pre_industries != [''] else None

        # 获取宽基指数预筛选参数
        pre_indexes = request.form.getlist('pre_indexes[]')
        # 处理空列表情况
        pre_indexes = pre_indexes if pre_indexes and pre_indexes != [''] else None

        # 单位转换为天数
        long_period_days = convert_to_days(long_period, long_period_unit)
        short_period_days = convert_to_days(short_period, short_period_unit)

        # 验证参数
        max_long_days = MAX_LONG_YEARS * DAYS_IN_YEAR
        if long_period_days < 5 or long_period_days > max_long_days:
            return jsonify({'success': False, 'message': f'长期周期应在5天到{MAX_LONG_YEARS}年之间'})

        if short_period_days < 1 or short_period_days > long_period_days:
            return jsonify({'success': False, 'message': '短期周期应大于0且小于长期周期'})

        if diff_threshold < 0 or diff_threshold > 100:
            return jsonify({'success': False, 'message': '差异阈值应在0-100之间'})

        # 初始化分析器
        if analyzer is None:
            if not initialize_analyzer():
                return jsonify({'success': False, 'message': '无法初始化股票分析器，请检查tushare API token配置'})

        # 获取股票列表，支持行业和宽基指数预筛选
        stock_list = analyzer.fetcher.get_stock_list(pre_industries, pre_indexes)
        if stock_list.empty:
            return jsonify({'success': False, 'message': '无法获取股票列表或所选行业/指数无股票数据'})

        # 重置状态
        analysis_result = None
        filtered_result = None
        analysis_status = 'running'
        analysis_progress = 0
        current_pre_industries = pre_industries
        current_pre_indexes = pre_indexes

        # 启动后台分析线程
        thread = threading.Thread(target=background_analysis, args=(stock_list, long_period_days, diff_threshold, short_period_days))
        thread.daemon = True
        thread.start()

        return jsonify({'success': True, 'total_stocks': len(stock_list),
                       'long_period_days': long_period_days,
                       'short_period_days': short_period_days,
                       'pre_industries': pre_industries or [],
                       'pre_indexes': pre_indexes or []})

    except Exception as e:
        return jsonify({'success': False, 'message': f'配置失败: {str(e)}'})

@app.route('/api/status')
def get_status():
    """获取分析状态"""
    global analysis_status, analysis_progress

    return jsonify({
        'status': analysis_status,
        'progress': analysis_progress
    })

@app.route('/api/results')
def get_results():
    """获取分析结果"""
    global filtered_result, analysis_status

    if analysis_status != 'completed':
        return jsonify({'success': False, 'message': '分析尚未完成'})

    if filtered_result is None or filtered_result.empty:
        return jsonify({'success': False, 'message': '没有找到符合条件的股票'})

    # 计算统计信息
    total_count = len(filtered_result)
    up_count = len(filtered_result[filtered_result['diff_percent'] > 0])
    down_count = len(filtered_result[filtered_result['diff_percent'] < 0])
    avg_diff = filtered_result['diff_percent'].mean()

    # 转换为JSON格式
    results = {
        'stocks': filtered_result.to_dict('records'),
        'count': total_count,
        'statistics': {
            'total': total_count,
            'up': up_count,
            'down': down_count,
            'avg_diff': float(avg_diff)
        }
    }

    return jsonify({'success': True, 'data': results})

@app.route('/api/filter_by_industries', methods=['POST'])
def filter_by_industries():
    """按行业后筛选分析结果"""
    global analysis_result, filtered_result, analysis_status

    if analysis_status != 'completed':
        return jsonify({'success': False, 'message': '分析尚未完成'})

    if analysis_result is None or analysis_result.empty:
        return jsonify({'success': False, 'message': '没有可筛选的股票数据'})

    try:
        # 获取后筛选行业参数
        post_industries = request.json.get('post_industries', [])
        post_industries = post_industries if post_industries else None

        # 进行行业后筛选
        filtered_result = analyzer.filter_results_by_industries(analysis_result, post_industries)

        # 返回筛选结果
        if filtered_result.empty:
            return jsonify({'success': True, 'message': '没有找到符合行业条件的股票'})

        # 计算统计信息
        total_count = len(filtered_result)
        up_count = len(filtered_result[filtered_result['diff_percent'] > 0])
        down_count = len(filtered_result[filtered_result['diff_percent'] < 0])
        avg_diff = filtered_result['diff_percent'].mean()

        results = {
            'stocks': filtered_result.to_dict('records'),
            'count': total_count,
            'statistics': {
                'total': total_count,
                'up': up_count,
                'down': down_count,
                'avg_diff': float(avg_diff)
            }
        }

        return jsonify({'success': True, 'data': results})

    except Exception as e:
        return jsonify({'success': False, 'message': f'行业筛选失败: {str(e)}'})

@app.route('/api/available_industries')
def get_available_industries():
    """获取可用的行业列表"""
    global analysis_result

    try:
        if analysis_result is None or analysis_result.empty:
            # 如果没有分析结果，返回所有申万一级行业
            industries = get_sw_industries()
        else:
            # 从分析结果中提取可用行业
            industries = sorted(analysis_result['industry'].dropna().unique())

        return jsonify({'success': True, 'data': industries})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取行业列表失败: {str(e)}'})

@app.route('/api/stock_details/<ts_code>')
def get_stock_details(ts_code):
    """获取股票详细数据"""
    try:
        if analyzer is None:
            if not initialize_analyzer():
                return jsonify({'success': False, 'message': '无法初始化股票分析器'})

        details = analyzer.get_stock_details(ts_code, 60)
        if details is None:
            return jsonify({'success': False, 'message': '无法获取股票详情'})

        return jsonify({'success': True, 'data': details})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取股票详情失败: {str(e)}'})

@app.route('/api/stock_list')
def get_stock_list():
    """获取股票列表（用于搜索）"""
    try:
        if analyzer is None:
            if not initialize_analyzer():
                return jsonify({'success': False, 'message': '无法初始化股票分析器'})

        stock_list = analyzer.fetcher.get_stock_list()
        if stock_list.empty:
            return jsonify({'success': False, 'message': '无法获取股票列表'})

        # 转换为JSON格式
        stocks = stock_list[['ts_code', 'name']].to_dict('records')

        return jsonify({'success': True, 'data': stocks})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取股票列表失败: {str(e)}'})

@app.route('/api/reset')
def reset_analysis():
    """重置分析状态"""
    global analysis_result, filtered_result, analysis_status, analysis_progress, current_pre_industries, current_pre_indexes

    analysis_result = None
    filtered_result = None
    analysis_status = 'idle'
    analysis_progress = 0
    current_pre_industries = None
    current_pre_indexes = None

    return jsonify({'success': True, 'message': '分析状态已重置'})

if __name__ == '__main__':
    # 初始化分析器
    initialize_analyzer()

    print("A股股票均线差异筛选工具已启动")
    print("请访问 http://localhost:5000")
    print("首次使用请在 config.py 中配置您的 tushare API token")

    app.run(debug=True)

