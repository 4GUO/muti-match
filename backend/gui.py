# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, \
    QComboBox
from datetime import datetime
from cfi import cfi22


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.classifier = cfi22()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("医疗器械智能分类系统V1.0.0")
        self.setGeometry(100, 100, 800, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.query_input = QLineEdit(self)
        self.query_input.setPlaceholderText("请输入医疗器械名称")
        layout.addWidget(self.query_input)

        self.search_type = QComboBox(self)
        self.search_type.addItem("智能语义搜索")
        self.search_type.addItem("快速模糊匹配")
        layout.addWidget(self.search_type)

        # 搜索按钮支持回车键

        self.search_button = QPushButton("搜索", self)
        self.search_button.clicked.connect(self.search)
        self.query_input.returnPressed.connect(self.search)
        layout.addWidget(self.search_button)

        self.result_display = QTextEdit(self)
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("准备就绪")

    def search(self):
        query = self.query_input.text().strip()
        if len(query) < self.classifier.config.MIN_QUERY_LEN:
            self.status_bar.showMessage(f"查询太短，请至少输入{self.classifier.config.MIN_QUERY_LEN}个字符")
            return

        self.status_bar.showMessage("搜索中...")
        start_time = datetime.now()

        search_type = self.search_type.currentText()
        if search_type == "快速模糊匹配":
            results = self.classifier.fuzzy_search(query, self.classifier.config.MAX_RESULTS)
        else:
            results = self.classifier.semantic_search(query, self.classifier.config.MAX_RESULTS)

        elapsed = datetime.now() - start_time
        self.display_results(results, elapsed)
        self.status_bar.showMessage("搜索完成")

    def display_results(self, results, elapsed):
        if not results:
            self.result_display.setText("未找到匹配结果，请尝试其他关键词")
            return

        result_text = f"✨ 语义搜索结果（耗时 {elapsed.total_seconds():.2f} 秒）\n"
        result_text += "-" * 90 + "\n"
        result_text += f"{'排名':<5}{'名称':<30}{'分类编码':<15}{'层级':<10}{'匹配度':<10}{'用途描述'}\n"
        result_text += "-" * 90 + "\n"

        for i, item in enumerate(results, 1):
            name = str(item.get('name', '未知名称'))[:28]
            code = str(item.get('code', '未知编码'))
            level = item.get('level', '未知层级')
            score = float(item.get('score', 0))
            description = str(item.get('description', '无描述'))[:100]

            result_text += (
                    str(i) + " " + str(name).ljust(30) +
                    str(code).ljust(15) +
                    str(level).ljust(10) +
                    "{:.2f}".format(score).ljust(10) +
                    str(description)[:100] + "...\n"
            )

        self.result_display.setText(result_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
