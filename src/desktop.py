"""PyQt6桌面入口 - 启动Web图形界面"""
import sys
import threading
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """主函数"""
    try:
        from PyQt6.QtCore import QUrl, QTimer
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        print("错误: PyQt6-WebEngine 未安装")
        print("请运行: pip install PyQt6 PyQt6-WebEngine")
        print("\n或者使用浏览器访问: http://localhost:8765")
        print("启动Flask服务: python -m src.gui.app")
        return

    from src.gui.app import create_app

    app = QApplication(sys.argv)
    app.setApplicationName("公文写作助手")

    # 在后台线程启动Flask服务
    flask_app = create_app()
    server_thread = threading.Thread(
        target=lambda: flask_app.run(
            host="127.0.0.1",
            port=8765,
            debug=False,
            use_reloader=False,
            threaded=True
        ),
        daemon=True
    )
    server_thread.start()

    # 等待服务器启动
    import time
    time.sleep(1)

    # 创建浏览器窗口
    view = QWebEngineView()
    view.setWindowTitle("公文写作助手")
    view.resize(1200, 800)

    # 加载页面
    url = QUrl("http://127.0.0.1:8765")
    view.load(url)

    # 显示窗口
    view.show()

    # 启动事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
