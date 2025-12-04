"""
启动脚本 - 启动A股股票均线差异筛选工具
"""

import os
import sys
import webbrowser
import time

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_config():
    """检查配置"""
    from config import validate_config

    if not validate_config():
        print("错误：请先在 config.py 中配置您的 tushare API token")
        print("您可以在 https://tushare.pro/register 免费注册获取")
        input("按回车键退出...")
        sys.exit(1)

def start_server():
    """启动服务器"""
    print("=" * 50)
    print("A股股票均线差异筛选工具")
    print("=" * 50)
    print()

    # 检查配置
    check_config()

    print("正在启动Flask服务器...")
    print()

    try:
        # 导入并运行Flask应用
        from app import app

        # 自动打开浏览器
        print("服务器将在 http://localhost:5000 启动")
        print("正在打开浏览器...")
        time.sleep(1)
        webbrowser.open('http://localhost:5000')

        print()
        print("按 Ctrl+C 停止服务器")
        print("=" * 50)
        print()

        # 运行Flask应用
        app.run(debug=False)

    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装所有依赖包：")
        print("pip install flask pandas tushare requests python-dateutil numpy")
        input("按回车键退出...")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print("服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"启动服务器失败: {e}")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    start_server()