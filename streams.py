"""Універсальні ліниві утиліти: нескінченні потоки, take/drop, ковзні вікна."""

from collections import deque
from collections.abc import Callable, Iterable, Iterator
from itertools import accumulate, count, dropwhile, islice, takewhile

# ---------- Нескінченні джерела ----------


def naturals(start: int = 1) -> Iterator[int]:
    """1, 2, 3, ... — делегування itertools.count через yield from."""
    yield from count(start)


def fib_stream() -> Iterator[int]:
    """Нескінченний стрім Фібоначчі: 0, 1, 1, 2, 3, 5, ..."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# ---------- take / drop ----------


def take[T](n: int, it: Iterable[T]) -> list[T]:
    """Перші n елементів. Ітератор просувається рівно на n кроків."""
    if n < 0:
        raise ValueError("n має бути >= 0")
    return list(islice(it, n))


def drop[T](n: int, it: Iterable[T]) -> Iterator[T]:
    """Пропустити перші n елементів і повернути той самий ітератор (ліниво)."""
    if n < 0:
        raise ValueError("n має бути >= 0")
    iterator = iter(it)
    next(islice(iterator, n, n), None)  # «промотати» n елементів
    return iterator


def take_while[T](pred: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    return takewhile(pred, it)


def drop_while[T](pred: Callable[[T], bool], it: Iterable[T]) -> Iterator[T]:
    return dropwhile(pred, it)


# ---------- Ковзні вікна ----------


def sliding_window[T](it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """Вікна розміру k без матеріалізації потоку: пам'ять O(k)."""
    if k <= 0:
        raise ValueError("розмір вікна k має бути > 0")
    return _windows(iter(it), k)


def _windows[T](iterator: Iterator[T], k: int) -> Iterator[tuple[T, ...]]:
    window: deque[T] = deque(islice(iterator, k), maxlen=k)
    if len(window) < k:  # елементів менше, ніж k — жодного вікна
        return
    yield tuple(window)
    for x in iterator:
        window.append(x)  # найстаріший елемент витісняється автоматично
        yield tuple(window)


def moving_average(it: Iterable[float], k: int) -> Iterator[float]:
    return (sum(w) / k for w in sliding_window(it, k))


def prefix_sums(it: Iterable[int]) -> Iterator[int]:
    return accumulate(it)


def chunked[T](it: Iterable[T], size: int) -> Iterator[tuple[T, ...]]:
    """Ліниві пакети фіксованого розміру; останній може бути коротшим."""
    if size <= 0:
        raise ValueError("size має бути > 0")
    iterator = iter(it)
    return iter(lambda: tuple(islice(iterator, size)), ())


# ---------- Для перевірки лінивості ----------


class Counted[T]:
    """Обгортка-ітератор, що рахує, скільки елементів з неї реально взяли."""

    def __init__(self, it: Iterable[T]) -> None:
        self._it = iter(it)
        self.pulled = 0

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        value = next(self._it)  # StopIteration пробрасується далі
        self.pulled += 1
        return value
