"""算盘（suanpan）的档位模型与练习生成。

一根档位上半部 2 颗珠子、下半部 5 颗珠子：
上半部每颗代表 5，下半部每颗代表 1，因此单根档位可表示 0~9。
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List, Tuple

UPPER_BEADS = 2
LOWER_BEADS = 5
DEFAULT_RODS = 13
MIN_RODS = 1
MAX_RODS = 20
MAX_COUNT = 60


class AbacusError(ValueError):
    """算盘参数或数值非法。"""


def _as_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AbacusError("%s 必须是整数" % name)
    return value


@dataclass(frozen=True)
class Rod:
    """单根档位，upper 为靠梁的上珠数，lower 为靠梁的下珠数。"""

    upper: int = 0
    lower: int = 0

    def __post_init__(self) -> None:
        upper = _as_int(self.upper, "upper")
        lower = _as_int(self.lower, "lower")
        if not 0 <= upper <= UPPER_BEADS:
            raise AbacusError("上珠数必须在 0~%d 之间" % UPPER_BEADS)
        if not 0 <= lower <= LOWER_BEADS:
            raise AbacusError("下珠数必须在 0~%d 之间" % LOWER_BEADS)
        if upper * 5 + lower > 9:
            raise AbacusError("一根档位只能表示 0~9")

    @property
    def digit(self) -> int:
        return self.upper * 5 + self.lower

    @classmethod
    def from_digit(cls, digit: int) -> "Rod":
        digit = _as_int(digit, "digit")
        if not 0 <= digit <= 9:
            raise AbacusError("数字必须在 0~9 之间")
        upper = 1 if digit >= 5 else 0
        return cls(upper=upper, lower=digit - upper * 5)

    def to_dict(self) -> dict:
        return {"upper": self.upper, "lower": self.lower, "digit": self.digit}


@dataclass(frozen=True)
class Abacus:
    """若干档位组成的算盘，最右边为个位。"""

    rods: Tuple[Rod, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.rods, tuple):
            raise AbacusError("rods 必须是 Rod 元组")
        if not MIN_RODS <= len(self.rods) <= MAX_RODS:
            raise AbacusError("档位数必须在 %d~%d 之间" % (MIN_RODS, MAX_RODS))
        for rod in self.rods:
            if not isinstance(rod, Rod):
                raise AbacusError("rods 只能包含 Rod")

    def to_number(self) -> int:
        value = 0
        for rod in self.rods:
            value = value * 10 + rod.digit
        return value

    def to_digits(self) -> str:
        return "".join(str(rod.digit) for rod in self.rods)

    def to_dict(self) -> dict:
        return {
            "digits": self.to_digits(),
            "value": self.to_number(),
            "rods": [rod.to_dict() for rod in self.rods],
        }

    @classmethod
    def from_number(cls, value: int, rods: int = DEFAULT_RODS) -> "Abacus":
        value = _as_int(value, "value")
        rods = _as_int(rods, "rods")
        if not MIN_RODS <= rods <= MAX_RODS:
            raise AbacusError("档位数必须在 %d~%d 之间" % (MIN_RODS, MAX_RODS))
        if value < 0:
            raise AbacusError("算盘只能表示非负整数")
        limit = 10 ** rods
        if value >= limit:
            raise AbacusError("数值 %d 超出 %d 档算盘的范围" % (value, rods))
        text = str(value).zfill(rods)
        if len(text) > rods:
            raise AbacusError("数值位数超过档位数")
        return cls(tuple(Rod.from_digit(int(char)) for char in text))


def make_numbers(
    count: int,
    digits: int,
    seed: int = 0,
    unique: bool = True,
) -> List[int]:
    """生成练习用的随机数字。

    digits 为位数（1~6），count 为题目数量。unique 为真时尽量不重复。
    """

    count = _as_int(count, "count")
    digits = _as_int(digits, "digits")
    seed = _as_int(seed, "seed")
    if not 1 <= count <= MAX_COUNT:
        raise AbacusError("题目数量必须在 1~%d 之间" % MAX_COUNT)
    if not 1 <= digits <= 6:
        raise AbacusError("位数必须在 1~6 之间")

    low = 0 if digits == 1 else 10 ** (digits - 1)
    high = 10 ** digits - 1
    rng = random.Random(seed)
    numbers: List[int] = []
    if unique:
        pool_size = high - low + 1
        if count <= pool_size:
            numbers = rng.sample(range(low, high + 1), count)
            return numbers
    seen = set()
    guard = 0
    while len(numbers) < count:
        guard += 1
        if guard > count * 200:
            raise AbacusError("无法生成足够的题目")
        value = rng.randint(low, high)
        if value in seen and unique:
            continue
        seen.add(value)
        numbers.append(value)
    return numbers


def split_number(value: int, rods: int) -> List[int]:
    """把数字按档位拆成从高位到低位的数字列表，长度等于 rods。"""

    value = _as_int(value, "value")
    rods = _as_int(rods, "rods")
    if not MIN_RODS <= rods <= MAX_RODS:
        raise AbacusError("档位数必须在 %d~%d 之间" % (MIN_RODS, MAX_RODS))
    if value < 0:
        raise AbacusError("算盘只能表示非负整数")
    if value >= 10 ** rods:
        raise AbacusError("数值超出档位范围")
    return [int(char) for char in str(value).zfill(rods)]


def total_beads(digits: Iterable[int]) -> int:
    """统计拨出的珠子总数，用于校验与教学提示。"""

    total = 0
    for digit in digits:
        digit = _as_int(digit, "digit")
        if not 0 <= digit <= 9:
            raise AbacusError("数字必须在 0~9 之间")
        total += 1 if digit >= 5 else 0
        total += digit % 5
    return total
