"""模型层测试：档位、编码解码与题目生成。"""

from __future__ import annotations

import unittest

from abacus.model import (
    Abacus,
    AbacusError,
    Rod,
    make_numbers,
    split_number,
    total_beads,
)


class RodTest(unittest.TestCase):
    def test_zero_rod(self) -> None:
        rod = Rod()
        self.assertEqual(rod.digit, 0)

    def test_five_uses_one_upper_bead(self) -> None:
        rod = Rod.from_digit(5)
        self.assertEqual((rod.upper, rod.lower), (1, 0))

    def test_nine_uses_upper_and_four_lower(self) -> None:
        rod = Rod.from_digit(9)
        self.assertEqual((rod.upper, rod.lower), (1, 4))

    def test_all_digits_roundtrip(self) -> None:
        for digit in range(10):
            self.assertEqual(Rod.from_digit(digit).digit, digit)

    def test_digit_below_five(self) -> None:
        rod = Rod.from_digit(3)
        self.assertEqual((rod.upper, rod.lower), (0, 3))

    def test_reject_negative_upper(self) -> None:
        with self.assertRaises(AbacusError):
            Rod(upper=-1)

    def test_reject_excess_upper(self) -> None:
        with self.assertRaises(AbacusError):
            Rod(upper=3)

    def test_reject_excess_lower(self) -> None:
        with self.assertRaises(AbacusError):
            Rod(lower=6)

    def test_reject_over_nine(self) -> None:
        with self.assertRaises(AbacusError):
            Rod(upper=2, lower=0)

    def test_reject_non_integer(self) -> None:
        with self.assertRaises(AbacusError):
            Rod(upper=True)  # type: ignore[arg-type]

    def test_from_digit_rejects_ten(self) -> None:
        with self.assertRaises(AbacusError):
            Rod.from_digit(10)

    def test_from_digit_rejects_negative(self) -> None:
        with self.assertRaises(AbacusError):
            Rod.from_digit(-1)

    def test_to_dict(self) -> None:
        data = Rod.from_digit(7).to_dict()
        self.assertEqual(data, {"upper": 1, "lower": 2, "digit": 7})


class AbacusTest(unittest.TestCase):
    def test_encode_zero(self) -> None:
        self.assertEqual(Abacus.from_number(0, 3).to_digits(), "000")

    def test_encode_3806(self) -> None:
        abacus = Abacus.from_number(3806, 4)
        self.assertEqual(abacus.to_digits(), "3806")
        self.assertEqual([rod.digit for rod in abacus.rods], [3, 8, 0, 6])

    def test_roundtrip_numbers(self) -> None:
        for value in (0, 1, 9, 10, 99, 1234, 9999):
            self.assertEqual(Abacus.from_number(value, 4).to_number(), value)

    def test_leading_zeros_preserved(self) -> None:
        abacus = Abacus.from_number(42, 5)
        self.assertEqual(abacus.to_digits(), "00042")

    def test_reject_negative_number(self) -> None:
        with self.assertRaises(AbacusError):
            Abacus.from_number(-1)

    def test_reject_overflow(self) -> None:
        with self.assertRaises(AbacusError):
            Abacus.from_number(1000, 3)

    def test_accept_maximum(self) -> None:
        self.assertEqual(Abacus.from_number(999, 3).to_digits(), "999")

    def test_reject_zero_rods(self) -> None:
        with self.assertRaises(AbacusError):
            Abacus.from_number(1, 0)

    def test_reject_too_many_rods(self) -> None:
        with self.assertRaises(AbacusError):
            Abacus.from_number(1, 21)

    def test_requires_tuple(self) -> None:
        with self.assertRaises(AbacusError):
            Abacus([Rod.from_digit(1)])  # type: ignore[arg-type]

    def test_rejects_non_rod(self) -> None:
        with self.assertRaises(AbacusError):
            Abacus((1,))  # type: ignore[arg-type]

    def test_to_dict_shape(self) -> None:
        data = Abacus.from_number(38, 2).to_dict()
        self.assertEqual(data["digits"], "38")
        self.assertEqual(data["value"], 38)
        self.assertEqual(len(data["rods"]), 2)


class HelperTest(unittest.TestCase):
    def test_split_number(self) -> None:
        self.assertEqual(split_number(405, 4), [0, 4, 0, 5])

    def test_split_number_overflow(self) -> None:
        with self.assertRaises(AbacusError):
            split_number(1234, 3)

    def test_total_beads(self) -> None:
        self.assertEqual(total_beads([0, 1, 5, 9]), 0 + 1 + 1 + 5)

    def test_total_beads_rejects_invalid(self) -> None:
        with self.assertRaises(AbacusError):
            total_beads([12])

    def test_make_numbers_reproducible(self) -> None:
        first = make_numbers(8, 3, seed=7)
        second = make_numbers(8, 3, seed=7)
        self.assertEqual(first, second)

    def test_make_numbers_unique(self) -> None:
        numbers = make_numbers(20, 2, seed=1)
        self.assertEqual(len(set(numbers)), 20)

    def test_make_numbers_digit_length(self) -> None:
        for value in make_numbers(30, 4, seed=3):
            self.assertGreaterEqual(value, 1000)
            self.assertLessEqual(value, 9999)

    def test_make_numbers_single_digit_allows_zero(self) -> None:
        numbers = make_numbers(10, 1, seed=0)
        self.assertTrue(all(0 <= value <= 9 for value in numbers))

    def test_make_numbers_rejects_bad_count(self) -> None:
        with self.assertRaises(AbacusError):
            make_numbers(0, 2)

    def test_make_numbers_rejects_bad_digits(self) -> None:
        with self.assertRaises(AbacusError):
            make_numbers(3, 7)


if __name__ == "__main__":
    unittest.main()
