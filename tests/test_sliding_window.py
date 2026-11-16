import pytest

from streams import Counted, chunked, moving_average, naturals, sliding_window, take


def test_windows_basic() -> None:
    assert list(sliding_window([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]


def test_window_sums() -> None:
    assert list(map(sum, sliding_window(range(5), 2))) == [1, 3, 5, 7]


def test_edge_cases() -> None:
    assert list(sliding_window([], 2)) == []
    assert list(sliding_window([1, 2], 3)) == []  # k > довжини
    assert list(sliding_window([1, 2], 2)) == [(1, 2)]
    assert list(sliding_window("ab", 1)) == [("a",), ("b",)]


@pytest.mark.parametrize("k", [0, -1])
def test_bad_window_size(k: int) -> None:
    with pytest.raises(ValueError):
        sliding_window([1, 2, 3], k)


def test_infinite_source_and_laziness() -> None:
    source = Counted(naturals())
    sums = take(10, map(sum, sliding_window(source, 3)))
    assert sums == [6, 9, 12, 15, 18, 21, 24, 27, 30, 33]
    assert source.pulled == 12  # 10 вікон по 3 = 10 + 3 - 1 елементів


def test_moving_average() -> None:
    assert list(moving_average([2, 4, 6, 8], 2)) == [3.0, 5.0, 7.0]
    assert list(moving_average([1, 2], 5)) == []


def test_chunked() -> None:
    assert list(chunked(range(7), 3)) == [(0, 1, 2), (3, 4, 5), (6,)]
    assert list(chunked([], 3)) == []
    assert take(2, chunked(naturals(), 2)) == [(1, 2), (3, 4)]
    with pytest.raises(ValueError):
        chunked([1], 0)
