"""python -m pdf_splitter 入口"""
import sys
from pathlib import Path

# 将 src 目录加入 sys.path，支持 python -m pdf_splitter 直接运行
_src_dir = Path(__file__).resolve().parent.parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from pdf_splitter.cli import main

main()
