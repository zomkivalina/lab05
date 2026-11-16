"""Демонстрація: база (Фібоначчі, take/drop, accumulate) і варіант 6."""

import operator
from decimal import Decimal
from itertools import accumulate

from streams import (
    Counted,
    drop,
    fib_stream,
    moving_average,
    naturals,
    sliding_window,
    take,
)
from transactions import (
    deposits_until_goal,
    first_window_sums,
    positive,
    transaction_stream,
    with_balance,
)


def money(x: Decimal) -> str:
    return f"{x:>11,.2f}".replace(",", " ")


def base_demo() -> None:
    print("=== БАЗОВА ЧАСТИНА ===")
    print(f"fib_stream, перші 10:          {take(10, fib_stream())}")
    print(f"пропустити 5, взяти 8:         {take(8, drop(5, fib_stream()))}")
    sums = take(10, map(sum, sliding_window(naturals(), 3)))
    print(f"суми вікон по 3 з naturals():  {sums}")
    print(f"рухоме середнє [1..6], k=2:    {list(moving_average(range(1, 7), 2))}")
    print(f"префіксні суми [1,2,3,4]:      {list(accumulate([1, 2, 3, 4]))}")
    print(
        f"префіксні добутки [1,2,3,4]:   {list(accumulate([1, 2, 3, 4], operator.mul))}"
    )
    print(f"максимум префікса [3,1,4,1,5]: {list(accumulate([3, 1, 4, 1, 5], max))}")


def variant_demo() -> None:
    print("\n=== ВАРІАНТ 6: ПОТІК ТРАНЗАКЦІЙ (нескінченний, seed=6) ===")
    print(f"{'ID':>3}  {'Категорія':<18} {'Сума':>11}  {'Баланс':>11}")
    for tx, bal in take(12, with_balance(transaction_stream())):
        print(f"{tx.id:>3}  {tx.category:<18} {money(tx.amount)}  {money(bal)}")

    print("\nЛише надходження та накопичений баланс надходжень:")
    for tx, total in take(6, with_balance(positive(transaction_stream()))):
        print(f"{tx.id:>3}  {tx.category:<18} {money(tx.amount)}  {money(total)}")

    print("\nПерші 5 ковзних сум по 3 надходженнях:")
    source = Counted(transaction_stream())
    for i, s in enumerate(first_window_sums(source, k=3, n=5), start=1):
        print(f"  вікно {i}: {money(s)} грн")
    print(f"  транзакцій взято з нескінченного потоку: {source.pulled}")

    goal = Decimal("20000")
    print(f"\nНадходження, поки накопичено менше {money(goal).strip()} грн:")
    for tx, total in deposits_until_goal(transaction_stream(), goal):
        print(f"  #{tx.id:<3} +{money(tx.amount).strip():>9} -> {money(total)}")


if __name__ == "__main__":
    base_demo()
    variant_demo()
