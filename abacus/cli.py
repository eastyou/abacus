"""命令行入口：生成算盘 SVG 或整页练习纸。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from .model import DEFAULT_RODS, Abacus, AbacusError, make_numbers
from .render import render_abacus_svg, render_sheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="abacus",
        description="算盘读数练习：把数字画成算盘，或生成可打印的 A4 练习纸。",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    svg = sub.add_parser("svg", help="输出单个数字的算盘 SVG")
    svg.add_argument("number", type=int, help="要展示的非负整数")
    svg.add_argument("--rods", type=int, default=DEFAULT_RODS, help="档位数，默认 13")
    svg.add_argument("--digits", action="store_true", help="在每根档位下标注数字")
    svg.add_argument("-o", "--output", help="写入 .svg 文件，缺省打印到终端")

    sheet = sub.add_parser("sheet", help="生成可打印的 A4 练习纸")
    sheet.add_argument("-o", "--output", default="abacus-sheet.html", help="输出 HTML 路径")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--digits", type=int, default=3, help="每题位数，默认 3")
    sheet.add_argument("--rods", type=int, default=DEFAULT_RODS, help="档位数，默认 13")
    sheet.add_argument("--seed", type=int, default=0, help="随机种子，便于复现")
    sheet.add_argument("--answers", action="store_true", help="附加参考答案页")
    sheet.add_argument("--title", default="算盘读数练习", help="练习纸标题")
    return parser


def _write(path: str, content: str) -> int:
    try:
        target = Path(path)
        if target.parent and not target.parent.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
    print("已生成 %s" % path)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "svg":
            abacus = Abacus.from_number(args.number, args.rods)
            content = render_abacus_svg(abacus, show_digits=args.digits)
            if args.output:
                return _write(args.output, content)
            print(content)
            return 0

        if args.command == "sheet":
            numbers = make_numbers(args.count, args.digits, args.seed)
            content = render_sheet(
                numbers,
                rods=args.rods,
                title=args.title,
                answers=args.answers,
            )
            return _write(args.output, content)
    except AbacusError as exc:
        print("参数错误：%s" % exc, file=sys.stderr)
        return 2

    print("未知命令", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
