# pdf-splitter-to-png

> PDF 批量拆图工具 — 按页拆分图片 PDF 为独立 PNG 图片。基于 PyMuPDF，纯 Python 实现，无需额外安装 Poppler 等系统依赖。

[![Build & Release](https://github.com/AuOwen807/pdf-splitter-to-png/actions/workflows/release.yml/badge.svg)](https://github.com/AuOwen807/pdf-splitter-to-png/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%2010-lightgrey)

---

## 功能特点

- **批量处理** — 遍历指定目录下的所有 PDF 文件，自动转换
- **高清晰度** — 3 倍缩放矩阵渲染（≈ 216–300 DPI），确保 OCR 清晰度
- **灵活输出** — 可统一输出到指定目录，也可让图片紧邻源 PDF 存放
- **递归扫描** — 支持递归扫描子目录
- **严格命名** — `原文件名_序号.png` 格式，序号最少双位对齐
- **自动创建目录** — 输入/输出目录不存在时自动创建
- **健壮异常处理** — 单个 PDF 损坏或加密不影响整批任务
- **纯 Python** — 无需安装 Poppler 等系统级依赖

## 快速开始

### 方式一：下载可执行文件（推荐）

1. 前往 [Releases](https://github.com/AuOwen807/pdf-splitter-to-png/releases) 页面
2. 下载最新版本的 `pdf-splitter-to-png-windows-x64.exe`
3. 将 `.exe` 放到有 PDF 的文件夹中双击运行

> **无需任何安装** — PyMuPDF 已内置在 exe 中

### 方式二：Python 环境运行

```bash
# 1. 克隆仓库
git clone https://github.com/AuOwen807/pdf-splitter-to-png.git
cd pdf-splitter-to-png

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python -m pdf_splitter
```

## 使用示例

```bash
# 扫描当前目录所有 PDF，图片放在每个 PDF 旁边
python -m pdf_splitter

# 扫描指定目录
python -m pdf_splitter -d ./我的PDF

# 递归扫描子目录
python -m pdf_splitter -d ./我的PDF -r

# 统一输出到指定目录
python -m pdf_splitter -d ./我的PDF -o ./汇总输出

# 4 倍渲染（更高 DPI）
python -m pdf_splitter -d ./我的PDF --zoom 4.0

# 显示详细日志
python -m pdf_splitter --verbose
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `-d, --input-dir` | PDF 输入目录（默认：当前目录） |
| `-o, --output-dir` | PNG 输出目录（不指定则图片放在源 PDF 所在目录） |
| `-r, --recursive` | 递归扫描子目录 |
| `--zoom` | 渲染缩放倍数（默认：3.0，范围 1.0–10.0） |
| `--verbose` | 输出详细调试日志 |

## 输出目录行为说明

```
# 不指定 -o：图片跟随源 PDF
pdf_inputs/
├── 一楼/签证单A.pdf
│   ├── 签证单A_01.png
│   └── 签证单A_02.png
└── 签证单C.pdf
    ├── 签证单C_01.png
    ├── 签证单C_02.png
    └── 签证单C_03.png

# 指定 -o：统一输出
python -m pdf_splitter -d pdf_inputs -o 汇总输出
汇总输出/
├── 签证单A_01.png
├── 签证单A_02.png
├── 签证单C_01.png
├── 签证单C_02.png
└── 签证单C_03.png
```

## 项目结构

```
pdf-splitter-to-png/
├── .github/workflows/release.yml   # GitHub Actions CI/CD
├── src/pdf_splitter/               # 源代码
│   ├── __init__.py                 # 包定义
│   ├── __main__.py                 # 入口：python -m
│   └── cli.py                      # 核心逻辑
├── pyproject.toml                  # 项目配置
├── requirements.txt                # 运行依赖
├── requirements-dev.txt            # 构建/开发依赖
├── LICENSE                         # MIT 许可
├── CHANGELOG.md                    # 版本变更日志
└── README.md                       # 本文件
```

## 技术栈

- **PyMuPDF (fitz)** — PDF 渲染引擎（纯 Python，无需系统依赖）
- **PyInstaller** — 打包为独立 Windows 可执行文件
- **GitHub Actions** — CI/CD 自动构建与发布

## 许可

[MIT License](LICENSE) © 2026 auowen807
