import os


def get_project_root():
    current_file = os.path.abspath(__file__)  # 获取当前脚本文件的绝对路径
    project_root = os.path.dirname(current_file)
    return project_root


DB_PATH = os.path.join(get_project_root(), "database.db")
