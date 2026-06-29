#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 批量拆图工具 — 按页拆分图片 PDF 为独立 PNG 图片

功能
  扫描指定目录下的所有 PDF 文件，将每一页渲染为高分辨率 PNG 图片，
  按「原文件名_序号.png」的命名规范存入输出目录。

  默认输出目录为每个 PDF 所在的源目录（图片紧邻 PDF）；
  也可通过 -o 指定统一输出目录。

技术特点
  - 基于 PyMuPDF（fitz），纯 Python 绑定，无需安装 Poppler 等系统依赖
  - 3 倍缩放矩阵渲染，输出约 216–300 DPI 的高清图片
  - 自动化目录创建、严格错误隔离、全量日志输出

运行方式
  python -m pdf_splitter                       # 扫描当前目录下的所有 PDF，图片放在 PDF 旁边
  python -m pdf_splitter -d ./my_pdfs          # 扫描指定目录
  python -m pdf_splitter -d ./my_pdfs -o ./out # 指定统一输出目录
  python -m pdf_splitter --zoom 4.0            # 4 倍渲染（更高 DPI）
  python -m pdf_splitter --verbose             # 显示详细日志
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# ──────────────────────────────────────────────────
# 第三方依赖（需提前安装）：pip install -r requirements.txt
# ──────────────────────────────────────────────────
try:
    import fitz  # PyMuPDF
except ImportError:
    print("缺少依赖：PyMuPDF。请执行：pip install -r requirements.txt")
    sys.exit(1)


# ═══════════════════════════════════════════════════
# 日志配置
# ═══════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("pdf_splitter")


# ═══════════════════════════════════════════════════
# 核心函数
# ═══════════════════════════════════════════════════

# ── 常量 ──
DEFAULT_INPUT_DIR = "."   # 默认扫描当前目录
RENDER_ZOOM = 3.0          # 渲染缩放倍数（≈ 216–300 DPI）
OUTPUT_EXT = ".png"        # 输出图片格式


def ensure_directory(path: Path) -> Path:
    """
    确保目标目录存在，不存在则自动创建。

    Args:
        path: 目录路径。

    Returns:
        相同的 Path 对象。
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def collect_pdf_files(input_dir: Path, recursive: bool = False) -> list[Path]:
    """
    扫描指定目录，收集所有 .pdf 文件（不区分大小写），并按文件名排序。

    Args:
        input_dir: 待扫描的目录。
        recursive: 是否递归扫描子目录。

    Returns:
        排序后的 PDF 文件路径列表。
    """
    if not input_dir.is_dir():
        logger.warning("输入目录不存在，已自动创建：%s", input_dir)
        ensure_directory(input_dir)
        return []

    if recursive:
        pattern = "**/*.pdf"
    else:
        pattern = "*.pdf"

    pdf_files = sorted(
        [p for p in input_dir.glob(pattern) if p.suffix.lower() == ".pdf"]
    )
    logger.info("在 %s 中发现 %d 个 PDF 文件", input_dir, len(pdf_files))
    return pdf_files


def split_pdf_to_images(
    pdf_path: Path,
    output_dir: Path | None,
    zoom: float = RENDER_ZOOM,
) -> int:
    """
    将单个 PDF 文件的每一页渲染为 PNG 图片。

    Args:
        pdf_path:   PDF 文件路径。
        output_dir: 输出图片目录。设为 None 时自动使用 PDF 所在目录。
        zoom:       渲染缩放倍数（Matrix 比例，默认 3.0）。

    Returns:
        成功导出的页数。失败返回 0。

    Raises:
        不抛出异常 —— 所有异常会被捕获并记录日志，保证调用方流程不中断。
    """
    # ── 确定输出目录：未指定则输出到 PDF 所在目录 ──
    if output_dir is None:
        resolved_output = pdf_path.parent.resolve()
    else:
        resolved_output = output_dir
    ensure_directory(resolved_output)

    try:
        # ── 打开 PDF ──
        doc = fitz.open(str(pdf_path))

        # 检查 PDF 是否已加密
        if doc.is_encrypted:
            logger.error("跳过加密文件（无法解密）：%s", pdf_path.name)
            doc.close()
            return 0

        # ── 文件清册 ──
        stem = pdf_path.stem                  # 不含后缀的文件名
        page_count = doc.page_count

        # 0 页 PDF → 直接跳过
        if page_count == 0:
            logger.warning("跳过空文件（0 页）：%s", pdf_path.name)
            doc.close()
            return 0

        # 序号最少双位数对齐（01, 02, ..., 99, 100...）
        seq_min_width = max(2, len(str(page_count)))

        logger.info("开始处理：%s（共 %d 页）", pdf_path.name, page_count)

        # ── 逐页渲染 ──
        success_count = 0
        for page_num in range(page_count):
            page = doc[page_num]
            # 极端情况下损坏 PDF 的页码可能为空
            if page is None:
                logger.warning("  第 %d 页为空，跳过", page_num + 1)
                continue

            # 高分辨率矩阵：zoom 倍缩放
            matrix = fitz.Matrix(zoom, zoom)
            pixmap = page.get_pixmap(matrix=matrix)

            # 生成输出文件名：原文件名_序号.png
            seq = str(page_num + 1).zfill(seq_min_width)
            out_name = f"{stem}_{seq}{OUTPUT_EXT}"
            out_path = resolved_output / out_name

            # 保存图片
            pixmap.save(str(out_path))
            success_count += 1

            # 及时释放 pixmap 内存（处理大文件时防止 OOM）
            pixmap = None  # noqa: F841 — 主动释放前确认

            logger.debug("  第 %d/%d 页 → %s", page_num + 1, page_count, out_name)

        doc.close()
        logger.info("  完成：%s → 导出 %d/%d 页", pdf_path.name, success_count, page_count)
        return success_count

    except Exception as exc:
        # 使用 %r 避免 exc 消息中的 % 字符与 logging 格式化冲突
        logger.error("处理失败：%s（原因：%r）", pdf_path.name, exc)
        return 0


def run_batch(
    input_dir: Path,
    output_dir: Path | None,
    zoom: float = RENDER_ZOOM,
    recursive: bool = False,
) -> None:
    """
    批量处理指定目录下的所有 PDF 文件。

    Args:
        input_dir:  输入目录（存放 PDF）。
        output_dir: 输出目录。None 表示每个 PDF 输出到自身所在目录。
        zoom:       渲染缩放倍数。
        recursive:  是否递归扫描子目录。
    """
    pdf_files = collect_pdf_files(input_dir, recursive)

    if not pdf_files:
        logger.warning("未找到 PDF 文件，无需处理。")
        return

    total_pdfs = len(pdf_files)
    total_pages = 0
    success_pdfs = 0
    failed_pdfs = 0

    logger.info("=" * 50)
    logger.info("批量处理开始 —— 共 %d 个 PDF 文件", total_pdfs)
    if output_dir:
        logger.info("输出目录：%s", output_dir)
    else:
        logger.info("输出模式：每个 PDF 输出到自身所在目录")
    logger.info("渲染倍率：%.1f 倍", zoom)
    logger.info("=" * 50)

    for idx, pdf_path in enumerate(pdf_files, start=1):
        logger.info("[%d/%d] 正在处理：%s", idx, total_pdfs, pdf_path.name)
        pages = split_pdf_to_images(pdf_path, output_dir, zoom)
        if pages > 0:
            total_pages += pages
            success_pdfs += 1
        else:
            failed_pdfs += 1

    # ── 汇总 ──
    logger.info("=" * 50)
    logger.info("批量处理完成")
    logger.info("  成功：%d 个 PDF（共 %d 页）", success_pdfs, total_pages)
    if failed_pdfs > 0:
        logger.warning("  失败（已跳过）：%d 个 PDF", failed_pdfs)
    if output_dir:
        logger.info("  输出目录：%s", output_dir)
    logger.info("=" * 50)


# ═══════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════

def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="PDF 批量拆图工具 — 按页拆分图片 PDF 为独立的 PNG 图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python -m pdf_splitter                                 # 扫描当前目录\n"
            "  python -m pdf_splitter -d ./my_pdfs                   # 扫描指定目录\n"
            "  python -m pdf_splitter -d ./my_pdfs -r                # 递归扫描子目录\n"
            "  python -m pdf_splitter -d ./my_pdfs -o ./out          # 统一输出到 ./out\n"
            "  python -m pdf_splitter --zoom 4.0                     # 4 倍渲染（更高 DPI）\n"
            "  python -m pdf_splitter --verbose                      # 显示详细日志\n"
        ),
    )
    parser.add_argument(
        "-d", "--input-dir",
        default=DEFAULT_INPUT_DIR,
        help=f"PDF 输入目录（默认：当前目录）",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="PNG 输出目录（不指定则图片放在 PDF 源文件所在目录）",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="递归扫描输入目录的所有子目录",
    )
    parser.add_argument(
        "--zoom",
        type=float,
        default=RENDER_ZOOM,
        help=f"渲染缩放倍数（默认：{RENDER_ZOOM}，范围 1.0–10.0，值越大图片分辨率越高）",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="输出详细调试日志",
    )
    return parser.parse_args()


def main() -> None:
    """主入口：解析参数并执行批量拆分。"""
    args = parse_args()

    # ── 日志级别 ──
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("详细日志模式已启用")

    # ── 路径标准化 ──
    # 以当前工作目录为基准（而非脚本所在目录），使得 -d . 直观地扫描当前目录
    cwd = Path.cwd().resolve()
    input_dir = (cwd / args.input_dir).resolve()

    output_dir: Path | None = None
    if args.output_dir:
        output_dir = (cwd / args.output_dir).resolve()

    # ── 参数校验 ──
    if args.zoom < 1.0:
        logger.warning("缩放倍数 %.1f 过低，自动调整为 1.0", args.zoom)
        args.zoom = 1.0
    if args.zoom > 10.0:
        logger.warning("缩放倍数 %.1f 过高，自动调整为 10.0", args.zoom)
        args.zoom = 10.0

    logger.info("输入目录：%s", input_dir)
    if output_dir:
        logger.info("输出目录：%s", output_dir)
    else:
        logger.info("输出模式：每个 PDF 输出到自身所在目录（未指定 -o）")
    logger.info("渲染倍率：%.1f 倍", args.zoom)

    # ── 执行 ──
    run_batch(input_dir, output_dir, args.zoom, args.recursive)


# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    main()
