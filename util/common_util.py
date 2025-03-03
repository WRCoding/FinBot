from pathlib import Path
from typing import Optional


def find_project_root(marker_file='requirements.txt') -> Optional[str]:
    """
    通过查找标记文件来确定项目根目录
    :param marker_file: 标记文件名（如 .git, requirements.txt 等）
    :return: 项目根目录的路径
    """
    current = Path.cwd()
    while current != current.parent:
        if (current / marker_file).exists():
            return current
        current = current.parent
    return None