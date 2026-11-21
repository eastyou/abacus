"""渲染层测试：SVG 珠子数量、靠梁状态与练习纸排版。"""

from __future__ import annotations

import unittest

from abacus.model import Abacus
from abacus.render import bead_positions, render_abacus_svg, render_sheet


class SvgTest(unittest.TestCase):
    def test_svg_root(self) -> None:
        svg = render_abacus_svg(Abacus.from_number(123, 4))
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))

    def test_bead_count_matches_rods(self) -> None:
        svg = render_abacus_svg(Abacus.from_number(12345, 5))
        self.assertEqual(svg.count("<ellipse"), 7 * 5)

    def test_active_bead_count(self) -> None:
        abacus = Abacus.from_number(96, 2)
        svg = render_abacus_svg(abacus)
        expected = sum(rod.upper + rod.lower for rod in abacus.rods)
        self.assertEqual(svg.count('fill="#c0392b"'), expected)

    def test_zero_has_no_active_beads(self) -> None:
        svg = render_abacus_svg(Abacus.from_number(0, 3))
        self.assertEqual(svg.count('fill="#c0392b"'), 0)

    def test_digit_labels_toggle(self) -> None:
        plain = render_abacus_svg(Abacus.from_number(42, 2))
        labeled = render_abacus_svg(Abacus.from_number(42, 2), show_digits=True)
        self.assertNotIn("<text", plain)
        self.assertEqual(labeled.count("<text"), 2)

    def test_width_scales_with_rods(self) -> None:
        narrow = render_abacus_svg(Abacus.from_number(1, 3))
        wide = render_abacus_svg(Abacus.from_number(1, 13))
        narrow_width = narrow.split('width="')[1].split('"')[0]
        wide_width = wide.split('width="')[1].split('"')[0]
        self.assertLess(float(narrow_width), float(wide_width))

    def test_bead_positions_count(self) -> None:
        abacus = Abacus.from_number(5, 1)
        positions = bead_positions(abacus.rods[0])
        self.assertEqual(len(positions), 7)

    def test_active_beads_closer_to_bar(self) -> None:
        rod = Abacus.from_number(5, 1).rods[0]
        positions = bead_positions(rod)
        active = [pos for pos in positions if pos[2]]
        self.assertEqual(len(active), 1)
        self.assertLess(abs(active[0][1] - 82.0), 20.0)


class SheetTest(unittest.TestCase):
    def test_sheet_has_all_cards(self) -> None:
        html = render_sheet([12, 34, 56], rods=3)
        self.assertEqual(html.count('<div class="card">'), 3)
        self.assertEqual(html.count("<svg"), 3)

    def test_sheet_contains_title(self) -> None:
        html = render_sheet([7], title="三年级珠算")
        self.assertIn("三年级珠算", html)

    def test_sheet_escapes_title(self) -> None:
        html = render_sheet([7], title="<script>x</script>")
        self.assertNotIn("<script>x</script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_answers_hidden_by_default(self) -> None:
        html = render_sheet([3806], rods=4)
        self.assertNotIn("参考答案", html)
        self.assertNotIn("3806", html)

    def test_answers_page(self) -> None:
        html = render_sheet([3806, 42], rods=4, answers=True)
        self.assertIn("参考答案", html)
        self.assertIn("3806", html)
        self.assertIn("42", html)

    def test_empty_numbers_rejected(self) -> None:
        with self.assertRaises(ValueError):
            render_sheet([])

    def test_invalid_rods_rejected(self) -> None:
        with self.assertRaises(ValueError):
            render_sheet([1], rods=0)

    def test_sheet_is_chinese_html(self) -> None:
        html = render_sheet([9])
        self.assertIn('lang="zh-CN"', html)
        self.assertIn("@page", html)

    def test_print_media_rule(self) -> None:
        html = render_sheet([9])
        self.assertIn("@media print", html)


if __name__ == "__main__":
    unittest.main()
