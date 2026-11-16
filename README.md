# Лабораторна робота №5. Ліниві обчислення: генератори та itertools

**Студентка:** Зьомків А. І., група ФЕП-21
**Варіант:** 6 — «Потік фінансових транзакцій»

## Завдання варіанту
Лінивий потік сум транзакцій: відфільтрувати додатні операції, рахувати
накопичувальний баланс і перші N ковзних сум.
Інструменти: generator expression, `accumulate`, `islice`, `sliding_window`.

## Що реалізовано
**`streams.py` (база):** `naturals`, `fib_stream` (нескінченні генератори),
`take` / `drop` (з перевіркою n < 0), обгортки `take_while` / `drop_while`,
`sliding_window` на `deque(maxlen=k)` (пам'ять O(k), `ValueError` для k ≤ 0),
`moving_average`, `prefix_sums`, ліниві пакети `chunked` та `Counted` —
ітератор-лічильник для перевірки лінивості.

**`transactions.py` (варіант 6):**
- `Transaction` — frozen dataclass, суми в `Decimal` (без похибок float);
- `transaction_stream(seed)` — нескінченний детермінований генератор (`yield` + `count`);
- `from_amounts` — скінченний потік для тестів;
- `positive` — лише надходження (generator expression);
- `running_balance`, `with_balance` — накопичувальний баланс через `accumulate`;
- `window_sums`, `first_window_sums` — перші N ковзних сум по k надходженнях;
- `deposits_until_goal` — надходження, поки накопичено менше цілі (`takewhile`);
- `skip_and_take` — пропустити m транзакцій і взяти n.

Жоден крок не матеріалізує потік: списки з'являються лише у фінальному `take`.

## На що звернути увагу
- **Лінивість.** `first_window_sums(transaction_stream(), k=3, n=5)` бере з
  нескінченного потоку рівно стільки транзакцій, скільки потрібно до 7-го
  надходження (3 + 5 − 1); це перевіряє тест через `Counted`.
- **Вичерпання.** Генератор проходиться один раз — для повторного проходу треба
  створити новий (`transaction_stream()` ще раз).
- **Нескінченні потоки** завжди закінчуються `take` / `islice` / `takewhile`.

## Структура
```
lab05/
├── streams.py         # універсальні ліниві утиліти
├── transactions.py    # варіант 6
├── main.py            # демонстрація
├── tests/             # test_fib_stream, test_take_drop, test_sliding_window,
│                      # test_accumulate, test_transactions
├── pyproject.toml, mypy.ini, requirements.txt, .gitignore
```
Потрібен Python 3.12+ (узагальнені функції `def take[T](...)`).

## Запуск
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt

pytest -q
python main.py
mypy .
black --check .
ruff check .
```
