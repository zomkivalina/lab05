import operator
from itertools import accumulate

from streams import naturals, prefix_sums, take


def test_accumulate_sum_prod() -> None:
    assert list(accumulate([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(accumulate([1, 2, 3, 4], operator.mul)) == [1, 2, 6, 24]


def test_running_max_and_initial() -> None:
    assert list(accumulate([3, 1, 4, 1, 5], max)) == [3, 3, 4, 4, 5]
    assert list(accumulate([1, 2], initial=100)) == [100, 101, 103]


def test_prefix_sums_on_infinite_stream() -> None:
    assert take(5, prefix_sums(naturals())) == [1, 3, 6, 10, 15]  # трикутні числа


def test_empty() -> None:
    assert list(prefix_sums([])) == []
