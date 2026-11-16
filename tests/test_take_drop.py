from itertools import count, islice

import pytest

from streams import Counted, drop, drop_while, naturals, take, take_while


def test_take_drop_on_count() -> None:
    xs = count(1)
    assert take(5, xs) == [1, 2, 3, 4, 5]
    assert take(3, xs) == [6, 7, 8]  # ітератор уже просунутий


def test_drop_then_take() -> None:
    assert list(islice(drop(10, count(0)), 3)) == [10, 11, 12]


def test_edge_cases() -> None:
    assert take(0, naturals()) == []
    assert take(5, []) == []
    assert take(10, [1, 2]) == [1, 2]
    assert list(drop(5, [1, 2])) == []
    assert list(drop(0, [1, 2])) == [1, 2]


@pytest.mark.parametrize("bad", [-1, -10])
def test_negative_n_rejected(bad: int) -> None:
    with pytest.raises(ValueError):
        take(bad, [1, 2, 3])
    with pytest.raises(ValueError):
        drop(bad, [1, 2, 3])


def test_takewhile_dropwhile() -> None:
    assert list(take_while(lambda x: x < 5, naturals())) == [1, 2, 3, 4]
    assert take(3, drop_while(lambda x: x <= 0, [-2, -1, 0, 3, -5, 4])) == [3, -5, 4]


def test_take_is_lazy() -> None:
    source = Counted(naturals())
    assert take(4, source) == [1, 2, 3, 4]
    assert source.pulled == 4  # з нескінченного потоку взято рівно 4
