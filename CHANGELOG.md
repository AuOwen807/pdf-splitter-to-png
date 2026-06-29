# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-06-29

### Added
- 初始版本发布
- 批量处理 PDF 文件，逐页导出为 PNG 图片
- 基于 PyMuPDF（fitz），纯 Python 绑定，无需 Poppler
- 3 倍缩放矩阵渲染（≈ 216–300 DPI）
- 灵活输出：`-o` 指定统一目录，不指定则图片跟随源 PDF
- 递归扫描子目录（`-r` 参数）
- 严格命名规则：`原文件名_序号.png`（序号最少双位对齐）
- 自动创建目录
- 单文件损坏/加密/0 页时跳过，整批不中断
- 支持自定义输入目录、输出目录、渲染倍率、递归扫描
- 内存管理：每页渲染后主动释放 pixmap，防止大文件 OOM
- 空页检查：损坏 PDF 中页码为空时跳过
- `requirements-dev.txt` 分离构建依赖
- 详细日志与汇总报告
- GitHub Actions CI/CD：自动编译 Windows 可执行文件
