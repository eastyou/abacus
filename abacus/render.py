"""把算盘画成 SVG，并排版成可打印的 A4 练习纸。"""

from __future__ import annotations

import html
from typing import Iterable, List, Sequence

from .model import (
    DEFAULT_RODS,
    LOWER_BEADS,
    UPPER_BEADS,
    Abacus,
    AbacusError,
    Rod,
)

BEAD_RX = 9.0
BEAD_RY = 4.4
ROD_GAP = 22.0
FRAME_LEFT = 24.0
BAR_Y = 82.0


def _fmt(value: float) -> str:
    text = "%.1f" % value
    return text[:-2] if text.endswith(".0") else text


def bead_positions(rod: Rod) -> List[tuple]:
    """返回一根档位上所有珠子的圆心坐标 (x 偏移, y, 是否靠梁)。

    x 偏移由调用方补上档位横坐标；上珠与下珠各 2 颗、5 颗始终画出来，
    只有位置不同，这样图案与真实算盘一致。
    """

    positions: List[tuple] = []
    for index in range(UPPER_BEADS):
        if index < rod.upper:
            positions.append((0.0, BAR_Y - 12.0 * (index + 1), True))
        else:
            positions.append((0.0, 26.0 + 12.0 * (index - rod.upper), False))
    for index in range(LOWER_BEADS):
        if index < rod.lower:
            positions.append((0.0, BAR_Y + 14.0 * (index + 1), True))
        else:
            positions.append((0.0, 172.0 - 14.0 * (index - rod.lower), False))
    return positions


def render_abacus_svg(abacus: Abacus, show_digits: bool = False) -> str:
    """生成单把算盘的 SVG 字符串。"""

    if not isinstance(abacus, Abacus):
        raise AbacusError("abacus 必须是 Abacus 实例")
    count = len(abacus.rods)
    width = 2 * FRAME_LEFT + (count - 1) * ROD_GAP + 2 * BEAD_RX + 6.0
    height = 212.0 if show_digits else 200.0

    parts: List[str] = []
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" '
        'viewBox="0 0 %s %s" role="img" aria-label="算盘">'
        % (_fmt(width), _fmt(height), _fmt(width), _fmt(height))
    )
    parts.append(
        '<rect x="6" y="8" width="%s" height="184" rx="6" ry="6" '
        'fill="#fbf5e6" stroke="#8b6b3d" stroke-width="2"/>'
        % _fmt(width - 12)
    )
    parts.append(
        '<line x1="10" y1="%s" x2="%s" y2="%s" stroke="#8b6b3d" '
        'stroke-width="2.5"/>' % (_fmt(BAR_Y), _fmt(width - 10), _fmt(BAR_Y))
    )

    for index, rod in enumerate(abacus.rods):
        x = FRAME_LEFT + index * ROD_GAP
        parts.append(
            '<line x1="%s" y1="16" x2="%s" y2="186" stroke="#b9a27b" '
            'stroke-width="1.6"/>' % (_fmt(x), _fmt(x))
        )
        for _, y, active in bead_positions(rod):
            fill = "#c0392b" if active else "#e8d9bd"
            stroke = "#8b2f24" if active else "#b9a27b"
            parts.append(
                '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" '
                'stroke="%s" stroke-width="1"/>'
                % (_fmt(x), _fmt(y), _fmt(BEAD_RX), _fmt(BEAD_RY), fill, stroke)
            )
        if show_digits:
            parts.append(
                '<text x="%s" y="206" text-anchor="middle" font-size="12" '
                'font-family="monospace" fill="#5a4325">%d</text>'
                % (_fmt(x), rod.digit)
            )

    parts.append("</svg>")
    return "".join(parts)


def render_sheet(
    numbers: Sequence[int],
    rods: int = DEFAULT_RODS,
    title: str = "算盘读数练习",
    answers: bool = False,
) -> str:
    """把一组数字排版成 A4 练习纸，每道题画一把算盘。"""

    if not numbers:
        raise AbacusError("至少需要一道题")
    if not 1 <= rods <= 20:
        raise AbacusError("档位数必须在 1~20 之间")
    safe_title = html.escape(title)
    cards: List[str] = []
    for index, value in enumerate(numbers, start=1):
        abacus = Abacus.from_number(value, rods)
        svg = render_abacus_svg(abacus)
        cards.append(
            '<div class="card"><div class="no">%d</div>%s'
            '<div class="line">答案：<span class="blank"></span></div></div>'
            % (index, svg)
        )
    answer_block = ""
    if answers:
        items = "".join(
            '<li><span class="ans-no">%d.</span> %d</li>' % (i, value)
            for i, value in enumerate(numbers, start=1)
        )
        answer_block = (
            '<section class="answers"><h2>参考答案</h2><ol class="ans-list">%s'
            "</ol></section>" % items
        )

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<style>
  @page { size: A4; margin: 10mm; }
  * { box-sizing: border-box; }
  body { margin: 0; background: #f0eee9; color: #2b2b2b;
         font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif; }
  .sheet { width: 190mm; margin: 0 auto; background: #fff; padding: 8mm;
           box-shadow: 0 2px 12px rgba(0,0,0,.12); }
  h1 { font-size: 20px; margin: 0 0 2mm; letter-spacing: 1px; }
  .hint { font-size: 12px; color: #666; margin-bottom: 4mm; }
  .meta { font-size: 12px; color: #444; display: flex; gap: 8mm;
          margin-bottom: 4mm; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm; }
  .card { border: 1px solid #ddd; border-radius: 3px; padding: 2mm 2mm 3mm;
          position: relative; break-inside: avoid; page-break-inside: avoid; }
  .card .no { position: absolute; top: 2mm; left: 2mm; font-size: 12px;
              color: #999; }
  .card svg { display: block; width: 100%%; height: auto; margin-top: 2mm; }
  .line { font-size: 13px; margin-top: 1mm; text-align: center; }
  .blank { display: inline-block; min-width: 38mm;
           border-bottom: 1px solid #333; height: 16px; }
  .answers { margin-top: 6mm; page-break-before: always; }
  .answers h2 { font-size: 16px; margin: 0 0 3mm; }
  .ans-list { columns: 4; font-size: 13px; padding-left: 5mm; }
  .ans-list li { margin-bottom: 2mm; }
  .ans-no { color: #999; }
  @media print { body { background: #fff; } .sheet { box-shadow: none;
                 width: auto; padding: 0; } }
</style>
</head>
<body>
<div class="sheet">
  <h1>%s</h1>
  <div class="hint">看算盘上靠梁的珠子，把表示的数字写在横线上。</div>
  <div class="meta"><span>姓名：____________</span><span>班级：____________</span>
    <span>日期：____________</span></div>
  <div class="grid">%s</div>
  %s
</div>
</body>
</html>
""" % (safe_title, safe_title, "".join(cards), answer_block)
