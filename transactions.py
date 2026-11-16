"""Варіант 6: лінивий потік фінансових транзакцій.

Суми зберігаються як Decimal, щоб уникнути похибок float у грошах.
Жоден крок конвеєра не створює списків: значення обчислюються лише тоді,
коли їх запитує take/islice.
"""

import random
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from decimal import Decimal
from itertools import accumulate, count, takewhile

from streams import drop, sliding_window, take

CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class Transaction:
    id: int
    amount: Decimal  # > 0 — надходження, < 0 — списання
    category: str


INCOME = ("зарплата", "переказ від друга", "кешбек", "повернення коштів")
EXPENSE = ("продукти", "кафе", "транспорт", "комунальні", "підписка")


def transaction_stream(seed: int = 6, start_id: int = 1) -> Iterator[Transaction]:
    """Нескінченний детермінований потік транзакцій (власний генератор з yield)."""
    rng = random.Random(seed)
    for tx_id in count(start_id):
        if rng.random() < 0.45:
            amount = Decimal(rng.randint(10_000, 500_000)) / 100
            category = rng.choice(INCOME)
        else:
            amount = -Decimal(rng.randint(3_000, 150_000)) / 100
            category = rng.choice(EXPENSE)
        yield Transaction(tx_id, amount.quantize(CENT), category)


def from_amounts(amounts: Iterable[int | str | Decimal]) -> Iterator[Transaction]:
    """Скінченний потік із готових сум (для тестів і прикладів)."""
    for tx_id, value in enumerate(amounts, start=1):
        amount = Decimal(value).quantize(CENT)
        yield Transaction(tx_id, amount, "дохід" if amount > 0 else "витрата")


# ---------- Кроки конвеєра ----------


def amounts(txs: Iterable[Transaction]) -> Iterator[Decimal]:
    return (t.amount for t in txs)


def positive(txs: Iterable[Transaction]) -> Iterator[Transaction]:
    """Лише додатні операції (надходження) — generator expression."""
    return (t for t in txs if t.amount > 0)


def running_balance(
    values: Iterable[Decimal], initial: Decimal = Decimal("0.00")
) -> Iterator[Decimal]:
    """Накопичувальний баланс після кожної операції (accumulate)."""
    return drop(1, accumulate(values, initial=initial))


def with_balance(
    txs: Iterable[Transaction], initial: Decimal = Decimal("0.00")
) -> Iterator[tuple[Transaction, Decimal]]:
    """Пари (транзакція, баланс після неї) за один прохід."""
    pairs = ((t, t.amount) for t in txs)
    start = (Transaction(0, Decimal("0.00"), ""), initial)
    totals = accumulate(
        pairs, lambda acc, cur: (cur[0], acc[1] + cur[1]), initial=start
    )
    return drop(1, totals)


def window_sums(values: Iterable[Decimal], k: int) -> Iterator[Decimal]:
    """Ковзні суми за останні k операцій."""
    return (sum(w, Decimal("0.00")) for w in sliding_window(values, k))


def first_window_sums(txs: Iterable[Transaction], k: int, n: int) -> list[Decimal]:
    """Основне завдання: перші n ковзних сум по k надходжень."""
    return take(n, window_sums(amounts(positive(txs)), k))


def deposits_until_goal(
    txs: Iterable[Transaction], goal: Decimal
) -> Iterator[tuple[Transaction, Decimal]]:
    """Надходження з накопиченою сумою, поки сума ще менша за ціль."""
    return takewhile(lambda pair: pair[1] < goal, with_balance(positive(txs)))


def skip_and_take(txs: Iterable[Transaction], skip: int, n: int) -> list[Transaction]:
    return take(n, drop(skip, txs))
