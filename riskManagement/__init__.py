from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel


class QVBoxLayoutExample(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QVBoxLayout 示例")
        self.resize(300, 200)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)  # 设置页边距

        label = QLabel("示例文本")
        main_layout.addWidget(label)

        container_widget = QWidget()
        container_widget.setLayout(main_layout)

        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication([])
    window = QVBoxLayoutExample()
    window.show()
    app.exec()