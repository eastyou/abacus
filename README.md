# abacus

[![CI](https://github.com/eastyou/abacus/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/abacus/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

把数字画成中国传统算盘（上二下五），生成可直接打印的 A4 读数练习纸。纯标准库、零依赖，适合珠算课与数学拓展课。

## 安装

```bash
pip install -e .
```

## 用法

```bash
# 输出单个数字的算盘 SVG（打印或插入课件）
abacus svg 3806 --rods 4 -o 3806.svg

# 在每根档位下标注数字，便于讲评
abacus svg 3806 --digits

# 生成 8 道三位数读数题
abacus sheet -o 练习.html --count 8 --digits 3

# 固定随机种子，附答案页，可重复生成同一套题
abacus sheet -o 练习.html --count 12 --digits 4 --seed 2026 --answers
```

`sheet` 输出 2 列 × N 行的 A4 版式，每题画一把算盘并留出填写横线；加 `--answers` 会在末尾附加一页参考答案。

## 算盘规则

- 每根档位上半部 2 颗珠子，每颗代表 5；下半部 5 颗，每颗代表 1。
- 靠梁（中间横梁）的珠子才计数，因此单根档位可表示 0~9。
- 最右边为个位，默认 13 档，可表示 0~9999999999999。

## 项目结构

```text
abacus/
├── abacus/
│   ├── __init__.py
│   ├── __main__.py
│   ├── model.py      # 档位与算盘模型、题目生成
│   ├── render.py     # SVG 绘制与 A4 排版
│   └── cli.py        # 命令行入口
├── examples/
│   └── sample.html
└── tests/
    ├── test_model.py
    ├── test_render.py
    └── test_cli.py
```

## 测试

```bash
python -m unittest discover -s tests -v
```

## License

MIT © 2026 eastyou
