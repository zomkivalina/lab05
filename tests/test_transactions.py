from decimal import Decimal

import pytest

from streams import Counted, take
from transactions import (
    Transaction,
    amounts,
    deposits_until_goal,
    first_window_sums,
    from_amounts,
    positive,
    running_balance,
    skip_and_take,
    transaction_stream,
    window_sums,
    with_balance,
)

D = Decimal
AMOUNTS = [100, -30, 200, -50, 300, 400, -10, 500]


def test_positive_filters_only_income() -> None:
    assert list(amounts(positive(from_amounts(AMOUNTS)))) == [
        D(100),
        D(200),
        D(300),
        D(400),
        D(500),
    ]


def test_running_balance_all_operations() -> None:
    balances = list(running_balance(amounts(from_amounts(AMOUNTS))))
    assert balances == [D(x) for x in (100, 70, 270, 220, 520, 920, 910, 1410)]


def test_running_balance_initial() -> None:
    assert list(running_balance([D(10), D(-5)], initial=D(100))) == [D(110), D(105)]


def test_with_balance_pairs() -> None:
    pairs = list(with_balance(from_amounts([50, -20])))
    assert [(t.id, b) for t, b in pairs] == [(1, D(50)), (2, D(30))]


def test_first_window_sums() -> None:
    # надходження: 100, 200, 300, 400, 500 -> вікна по 3
    assert first_window_sums(from_amounts(AMOUNTS), k=3, n=2) == [D(600), D(900)]
    assert first_window_sums(from_amounts(AMOUNTS), k=3, n=10) == [
        D(600),
        D(900),
        D(1200),
    ]


def test_edge_cases() -> None:
    assert first_window_sums(from_amounts([]), k=2, n=5) == []
    assert first_window_sums(from_amounts([-1, -2]), k=1, n=5) == []
    assert first_window_sums(from_amounts(AMOUNTS), k=6, n=3) == []  # k > len
    assert first_window_sums(transaction_stream(), k=3, n=0) == []
    with pytest.raises(ValueError):
        list(window_sums([D(1)], 0))


def test_pipeline_is_lazy_on_infinite_stream() -> None:
    source = Counted(from_amounts(AMOUNTS))
    first_window_sums(source, k=2, n=1)
    assert source.pulled == 3  # 100, -30, 200 — і жодного елемента більше

    infinite = Counted(transaction_stream())
    sums = first_window_sums(infinite, k=3, n=5)
    assert len(sums) == 5
    deposits_needed = 3 + 5 - 1
    assert infinite.pulled < 50  # потік нескінченний, але взято лише потрібне
    assert sum(1 for _ in positive(take(infinite.pulled, transaction_stream()))) == (
        deposits_needed
    )


def test_deposits_until_goal() -> None:
    got = [
        (t.amount, total)
        for t, total in deposits_until_goal(from_amounts(AMOUNTS), D(700))
    ]
    assert got == [(D(100), D(100)), (D(200), D(300)), (D(300), D(600))]


def test_stream_is_deterministic_and_typed() -> None:
    first = take(20, transaction_stream(seed=1))
    assert first == take(20, transaction_stream(seed=1))
    assert all(isinstance(t, Transaction) for t in first)
    assert all(t.amount == t.amount.quantize(D("0.01")) for t in first)
    assert [t.id for t in skip_and_take(transaction_stream(), 5, 3)] == [6, 7, 8]


def test_generator_is_exhausted_after_use() -> None:
    gen = positive(from_amounts([1, 2]))
    assert list(gen) and list(gen) == []
