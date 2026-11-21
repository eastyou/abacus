"""命令行测试：参数解析、文件输出与错误码。"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from abacus.cli import main


class SvgCommandTest(unittest.TestCase):
    def test_prints_svg_to_stdout(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = main(["svg", "123"])
        self.assertEqual(code, 0)
        self.assertIn("<svg", buffer.getvalue())

    def test_writes_svg_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out" / "demo.svg"
            code = main(["svg", "3806", "--rods", "4", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())
            self.assertIn("<svg", target.read_text(encoding="utf-8"))

    def test_negative_number_exit_code(self) -> None:
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            code = main(["svg", "-5"])
        self.assertEqual(code, 2)
        self.assertIn("参数错误", error.getvalue())

    def test_overflow_exit_code(self) -> None:
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            code = main(["svg", "1000", "--rods", "3"])
        self.assertEqual(code, 2)


class SheetCommandTest(unittest.TestCase):
    def test_writes_sheet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sheet.html"
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = main(["sheet", "-o", str(target), "--count", "4", "--digits", "2"])
            self.assertEqual(code, 0)
            html = target.read_text(encoding="utf-8")
            self.assertEqual(html.count("<svg"), 4)
            self.assertIn("已生成", buffer.getvalue())

    def test_seed_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "a.html"
            second = Path(tmp) / "b.html"
            main(["sheet", "-o", str(first), "--seed", "9", "--answers"])
            main(["sheet", "-o", str(second), "--seed", "9", "--answers"])
            self.assertEqual(
                first.read_text(encoding="utf-8"),
                second.read_text(encoding="utf-8"),
            )

    def test_answers_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sheet.html"
            main(["sheet", "-o", str(target), "--answers", "--count", "2"])
            self.assertIn("参考答案", target.read_text(encoding="utf-8"))

    def test_invalid_count(self) -> None:
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            code = main(["sheet", "--count", "0"])
        self.assertEqual(code, 2)
        self.assertIn("题目数量", error.getvalue())

    def test_invalid_digits(self) -> None:
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            code = main(["sheet", "--digits", "9"])
        self.assertEqual(code, 2)

    def test_custom_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sheet.html"
            main(["sheet", "-o", str(target), "--title", "珠算小测"])
            self.assertIn("珠算小测", target.read_text(encoding="utf-8"))


class ParserTest(unittest.TestCase):
    def test_missing_command_exits(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                main([])

    def test_help_exits_zero(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                main(["--help"])
        self.assertEqual(caught.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
