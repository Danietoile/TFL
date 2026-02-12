import re
import random
import time
import matplotlib.pyplot as plt

# Регулярное выражение 
REGEX = r"^((?:a|b)+)((?:a|b)+)((?:a|b)+)\2\3(\1\1)+$"
_pattern = re.compile(REGEX)

def oracle_regex(s: str) -> bool:
    """Оракул: принадлежность языку через Python-regex (для коротких тестов)."""
    return _pattern.fullmatch(s) is not None

def _is_square_segment(s: str, start: int, length: int) -> bool:
    """Проверка, что s[start:start+length] = TT, где |T|>=2."""
    if length < 4 or length % 2 != 0:
        return False
    half = length // 2
    for i in range(half):
        if s[start + i] != s[start + half + i]:
            return False
    return True

def _is_repeat_ww(s: str, start: int, w: str) -> bool:
    """Проверка, что суффикс s[start:] равен (ww)^k для некоторого k>=1."""
    m = len(w)
    period = 2 * m
    rem = len(s) - start
    if rem < period or rem % period != 0:
        return False
    pat = w + w
    for i in range(rem):
        if s[start + i] != pat[i % period]:
            return False
    return True

#НАИВНЫЙ ПАРСЕР (рекурсивный с возвратами)

def parse_naive(s: str) -> bool:
    n = len(s)
    if n < 7:
        return False
    for ch in s:
        if ch not in "ab":
            return False

    def choose_y(pos: int, w: str, x: str) -> bool:
        m = len(w)
        p = len(x)
        for end_y in range(pos + 1, n):
            q = end_y - pos

            # Нужно место на x + y + хотя бы одно ww
            if n - end_y < p + q + 2 * m:
                break

            y = s[pos:end_y]
            if s[end_y:end_y + p] != x:
                continue
            if s[end_y + p:end_y + p + q] != y:
                continue

            tail_start = end_y + p + q
            if _is_repeat_ww(s, tail_start, w):
                return True
        return False

    def choose_x(pos: int, w: str) -> bool:
        m = len(w)
        for end_x in range(pos + 1, n):
            p = end_x - pos

            # После x нужно минимум: y (>=1) + x + y (>=1) + ww
            if n - end_x < (p + 2) + 2 * m:
                break

            x = s[pos:end_x]
            if choose_y(end_x, w, x):
                return True
        return False

    # Выбор w
    max_m = (n - 4) // 3  # из условия n >= m + 4 + 2m
    for m in range(1, max_m + 1):
        if n - m < 4 + 2 * m:
            break
        w = s[:m]
        if choose_x(m, w):
            return True

    return False

#ОПТИМИЗИРОВАННЫЙ ПАРСЕР

def parse_fast(s: str) -> bool:
    n = len(s)
    if n < 7:
        return False
    for ch in s:
        if ch not in "ab":
            return False

    max_m = (n - 4) // 3
    for m in range(1, max_m + 1):
        w = s[:m]
        period = 2 * m

        # tail_start = n - period*k, k>=1
        tail_start = n - period
        while tail_start >= m + 4:
            mid_len = tail_start - m
            if mid_len % 2 == 0 and _is_square_segment(s, m, mid_len):
                if _is_repeat_ww(s, tail_start, w):
                    return True
            tail_start -= period

    return False

#ГЕНЕРАТОРЫ ДЛЯ ТЕСТОВ

def gen_positive_exact(length: int, rng: random.Random) -> str:
    """Генерирует слово ровно заданной длины, принадлежащее языку (если длина допустима)."""
    if length < 7 or (length % 2 == 0 and length < 10):
        raise ValueError("Для языка недостижима такая длина (минимум 7, а чётные минимум 10).")

    for _ in range(20000):
        m_max = (length - 4) // 3
        m = rng.randint(1, m_max)

        max_k = (length - m - 4) // (2 * m)
        if max_k < 1:
            continue
        k = rng.randint(1, max_k)

        rem = length - m * (2 * k + 1)
        if rem < 4 or rem % 2 != 0:
            continue
        t = rem // 2
        if t < 2:
            continue

        p = rng.randint(1, t - 1)
        q = t - p

        w = "".join(rng.choice("ab") for _ in range(m))
        x = "".join(rng.choice("ab") for _ in range(p))
        y = "".join(rng.choice("ab") for _ in range(q))

        s = w + x + y + x + y + (w + w) * k
        if len(s) == length:
            return s

    # Детерминированная конструкция
    if length % 2 == 1:
        m = 1
    else:
        m = 2
    k = 1
    rem = length - m * (2 * k + 1)
    t = rem // 2
    w = "a" * m
    x = "a"
    y = "b" * (t - 1)
    s = w + x + y + x + y + (w + w) * k
    return s

def gen_negative_exact(length: int, rng: random.Random) -> str:
    """Генерирует слово заданной длины, НЕ принадлежащее языку."""
    while True:
        s = "".join(rng.choice("ab") for _ in range(length))
        if not parse_fast(s):
            return s

#ФАЗЗ-ТЕСТ

def fuzz_test(num_tests: int = 3000, max_len: int = 60, seed: int = 0) -> None:
    rng = random.Random(seed)

    # Случайные слова
    for _ in range(num_tests):
        L = rng.randint(0, max_len)
        s = "".join(rng.choice("ab") for _ in range(L))
        a = parse_naive(s)
        b = parse_fast(s)
        c = oracle_regex(s) if L <= 40 else b  # длинные строки не гоняем через regex-оракул
        if a != b or b != c:
            print("Несовпадение!")
            print("s =", s)
            print("naive =", a, "fast =", b, "regex =", c)
            return

    # Слова из языка (точные длины)
    for L in range(7, max_len + 1):
        if L % 2 == 0 and L < 10:
            continue
        s = gen_positive_exact(L, rng)
        a = parse_naive(s)
        b = parse_fast(s)
        c = oracle_regex(s) if L <= 40 else b
        if a != b or b != c:
            print("Несовпадение на положительном примере!")
            print("L =", L)
            print("s =", s)
            print("naive =", a, "fast =", b, "regex =", c)
            return

    print("Фазз-тест пройден: парсеры эквивалентны на случайных тестах.")

#БЕНЧМАРК И ГРАФИКИ

def _avg_time(func, samples):
    t0 = time.perf_counter()
    for s in samples:
        func(s)
    t1 = time.perf_counter()
    return (t1 - t0) / len(samples)

def benchmark_and_plot(lengths, seed: int = 1):
    rng = random.Random(seed)

    naive_in, fast_in = [], []
    naive_out, fast_out = [], []

    for L in lengths:
        if L % 2 == 0 and L < 10:
            continue

        if L <= 200:
            cnt = 30
        elif L <= 400:
            cnt = 20
        else:
            cnt = 10

        pos_samples = [gen_positive_exact(L, rng) for _ in range(cnt)]
        neg_samples = [gen_negative_exact(L, rng) for _ in range(cnt)]

        naive_in.append(_avg_time(parse_naive, pos_samples))
        fast_in.append(_avg_time(parse_fast, pos_samples))

        naive_out.append(_avg_time(parse_naive, neg_samples))
        fast_out.append(_avg_time(parse_fast, neg_samples))

    xs = [L for L in lengths if not (L % 2 == 0 and L < 10)]

    # График 1: слова из языка
    plt.figure()
    plt.plot(xs, naive_in, marker="o", label="Наивный парсер")
    plt.plot(xs, fast_in, marker="o", label="Оптимизированный парсер")
    plt.yscale("log")
    plt.grid(True)
    plt.title("Сравнение времени работы парсеров\n(слова, принадлежащие языку)")
    plt.xlabel("Длина слова")
    plt.ylabel("Время выполнения (секунды, лог. шкала)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("comparison_in.png", dpi=200)

    # График 2: слова не из языка
    plt.figure()
    plt.plot(xs, naive_out, marker="o", label="Наивный парсер")
    plt.plot(xs, fast_out, marker="o", label="Оптимизированный парсер")
    plt.yscale("log")
    plt.grid(True)
    plt.title("Сравнение времени работы парсеров\n(слова, не принадлежащие языку)")
    plt.xlabel("Длина слова")
    plt.ylabel("Время выполнения (секунды, лог. шкала)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("comparison_out.png", dpi=200)

    plt.show()

# Запуск 
fuzz_test(num_tests=2000, max_len=80, seed=0)
benchmark_and_plot([50,100,150,200,250,300,350,400,450,500], seed=1)