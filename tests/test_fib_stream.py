from itertools import islice

from streams import drop, fib_stream, take


def test_first_10() -> None:
    assert list(islice(fib_stream(), 10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_with_take_and_drop() -> None:
    assert take(8, drop(5, fib_stream())) == [5, 8, 13, 21, 34, 55, 89, 144]


def test_recurrence_holds_far_away() -> None:
    a, b, c = take(3, drop(200, fib_stream()))
    assert a + b == c


def test_each_call_is_a_new_stream() -> None:
    s = fib_stream()
    assert take(3, s) == [0, 1, 1]
    assert take(3, s) == [2, 3, 5]  # той самий генератор продовжує
    assert take(3, fib_stream()) == [0, 1, 1]  # новий — з початку
