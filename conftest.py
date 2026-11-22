"""pytest 配置：把仓库根加入 sys.path，使顶层包可导入。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
