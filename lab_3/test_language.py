#!/usr/bin/env python3
"""
Автоматическое тестирование языка L = {w1 a^n w2 | (|w1|=n ∨ |w2|<n) & wi ∈ {a,b}*}
"""
import itertools

def in_language_naive(s):
    """Проверяет принадлежность строки s языку L полным перебором всех разбиений."""
    m = len(s)
    if not all(c in 'ab' for c in s):
        return False
    for i in range(m):              # позиция начала блока a^n
        for n in range(1, m - i + 1):  # длина блока
            # Проверяем, что s[i:i+n] — все 'a'
            if all(s[j] == 'a' for j in range(i, i + n)):
                w1_len = i
                w2_len = m - i - n
                if w1_len == n or w2_len < n:
                    return True
    return False


def in_L1(s):
    """Проверка L1: ∃ n≥1 такое, что s[n..2n-1] все 'a'."""
    m = len(s)
    for n in range(1, m // 2 + 1):
        if 2 * n <= m and all(s[j] == 'a' for j in range(n, 2 * n)):
            return True
    return False


def in_L2(s):
    """Проверка L2: ∃ блок a^n, после которого < n символов."""
    m = len(s)
    for i in range(m):
        for n in range(1, m - i + 1):
            if all(s[j] == 'a' for j in range(i, i + n)):
                w2_len = m - i - n
                if w2_len < n:
                    return True
    return False


def grammar_generates(s):
    """
    Проверка порождения грамматикой через рекурсивный спуск с мемоизацией (алгоритм Эрли).
    Упрощённая версия: проверяем, может ли S породить s.
    """
    memo = {}
    
    def matches(nonterm, start, end):
        """Может ли нетерминал nonterm породить s[start:end]?"""
        key = (nonterm, start, end)
        if key in memo:
            return memo[key]
        
        memo[key] = False  # предотвращаем бесконечную рекурсию
        result = False
        substr = s[start:end]
        length = end - start
        
        if nonterm == 'S':
            result = matches('S1', start, end) or matches('S2', start, end)
        
        elif nonterm == 'S1':
            # S1 -> T R: split into T and R
            for mid in range(start + 2, end + 1):  # T generates >= 2 symbols
                if matches('T', start, mid) and matches('R', mid, end):
                    result = True
                    break
        
        elif nonterm == 'S2':
            # S2 -> Q U: split into Q and U
            for mid in range(start + 1, end + 1):  # Q generates >= 1 symbol
                if matches('Q', start, mid) and matches('U', mid, end):
                    result = True
                    break
        
        elif nonterm == 'T':
            if length >= 2:
                # T -> aa | ba
                if length == 2 and substr[1] == 'a' and substr[0] in 'ab':
                    result = True
                # T -> aTa | bTa
                elif length >= 3 and substr[0] in 'ab' and substr[-1] == 'a':
                    if matches('T', start + 1, end - 1):
                        result = True
        
        elif nonterm == 'R':
            # R -> ε | aR | bR
            if length == 0:
                result = True
            elif length >= 1 and substr[0] in 'ab':
                result = matches('R', start + 1, end)
        
        elif nonterm == 'Q':
            # Q -> a | aQ | bQ
            if length == 1 and substr[0] == 'a':
                result = True
            elif length >= 2 and substr[0] in 'ab':
                result = matches('Q', start + 1, end)
        
        elif nonterm == 'U':
            # U -> ε | aUa | aUb
            if length == 0:
                result = True
            elif length >= 2 and substr[0] == 'a' and substr[-1] in 'ab':
                result = matches('U', start + 1, end - 1)
        
        memo[key] = result
        return result
    
    return matches('S', 0, len(s))


# ============ ТЕСТИРОВАНИЕ ============

print("=" * 70)
print("ТЕСТИРОВАНИЕ ЯЗЫКА L")
print("=" * 70)

# Тест 1: проверка конкретных примеров
print("\n--- Тест 1: Конкретные примеры ---\n")
test_cases = [
    ("", False, "Пустая строка"),
    ("a", True, "n=1, w2=ε, |w2|=0<1"),
    ("b", False, "Нет букв a"),
    ("aa", True, "n=1, w1=a, |w1|=1=n"),
    ("ab", False, "n=1, i=0: |w1|=0≠1, |w2|=1≥1"),
    ("ba", True, "n=1, w1=b, |w1|=1=n"),
    ("bb", False, "Нет букв a"),
    ("aab", True, "n=1, w1=a, |w1|=1=n"),
    ("abb", False, "n=1, i=0: |w1|=0≠1, |w2|=2≥1"),
    ("bba", True, "n=1, w2=ε, |w2|=0<1"),
    ("bab", True, "n=1, w1=b, |w1|=1=n"),
    ("abab", False, "Все разложения не подходят"),
    ("abba", True, "Последняя a: n=1, |w2|=0<1"),
    ("aabb", True, "n=1, w1=a, |w1|=1=n"),
    ("bbab", False, "Поз. 1=b; блок a на поз.2: |w2|=1≥1"),
    ("abbb", False, "n=1, i=0: |w1|=0≠1, |w2|=3≥1"),
    ("aabbb", True, "n=1, w1=a, |w1|=1=n"),
    ("aaabb", True, "n=1, w1=a, |w1|=1=n"),
    ("baaab", True, "n=1, поз.1=a: |w1|=1=n"),
    ("bbabb", False, "Поз.1=b; блок a на поз.2: |w1|=2≠1, |w2|=2≥1"),
]

all_pass = True
for s, expected, reason in test_cases:
    naive = in_language_naive(s)
    grammar = grammar_generates(s)
    l1 = in_L1(s)
    l2 = in_L2(s)
    union = l1 or l2
    
    status_naive = "✓" if naive == expected else "✗"
    status_grammar = "✓" if grammar == expected else "✗"
    status_union = "✓" if union == expected else "✗"
    
    if naive != expected or grammar != expected or union != expected:
        all_pass = False
        print(f"  ОШИБКА: '{s}' ожидание={expected}, наивный={naive}, грамматика={grammar}, L1∪L2={union}")
    else:
        print(f"  {status_naive} '{s or 'ε':6s}' → {'∈L' if expected else '∉L'} | Наив={naive}, Грамм={grammar}, L1∪L2={union} | {reason}")

print(f"\n  Результат: {'ВСЕ ТЕСТЫ ПРОЙДЕНЫ ✓' if all_pass else 'ЕСТЬ ОШИБКИ ✗'}")

# Тест 2: Полный перебор всех строк длины ≤ 7
print("\n--- Тест 2: Полный перебор (сравнение наивного с грамматикой) ---\n")

total_tested = 0
total_errors = 0
stats = []

for length in range(0, 8):
    total = 2 ** length if length > 0 else 1
    count_in_L = 0
    errors = 0
    
    strings = [''] if length == 0 else [''.join(bits) for bits in itertools.product('ab', repeat=length)]
    
    for s in strings:
        naive = in_language_naive(s)
        grammar = grammar_generates(s)
        
        if naive != grammar:
            errors += 1
            if errors <= 3:
                print(f"  РАСХОЖДЕНИЕ: '{s}' наивный={naive}, грамматика={grammar}")
        
        if naive:
            count_in_L += 1
    
    total_tested += len(strings)
    total_errors += errors
    pct = count_in_L / len(strings) * 100 if strings else 0
    stats.append((length, count_in_L, len(strings), pct))
    print(f"  Длина {length}: {count_in_L}/{len(strings)} строк в L ({pct:.1f}%), ошибок: {errors}")

print(f"\n  Всего протестировано: {total_tested} строк, ошибок: {total_errors}")
print(f"  {'ВСЕ СОВПАДАЮТ ✓' if total_errors == 0 else 'ЕСТЬ РАСХОЖДЕНИЯ ✗'}")

# Тест 3: Проверка L1 ∪ L2 = naive
print("\n--- Тест 3: Проверка L = L1 ∪ L2 (полный перебор) ---\n")

errors_union = 0
for length in range(0, 8):
    strings = [''] if length == 0 else [''.join(bits) for bits in itertools.product('ab', repeat=length)]
    for s in strings:
        naive = in_language_naive(s)
        l1 = in_L1(s)
        l2 = in_L2(s)
        union = l1 or l2
        if naive != union:
            errors_union += 1
            if errors_union <= 5:
                print(f"  РАСХОЖДЕНИЕ: '{s}' наивный={naive}, L1={l1}, L2={l2}, L1∪L2={union}")

print(f"  Ошибок: {errors_union}")
print(f"  {'L = L1 ∪ L2 ПОДТВЕРЖДЕНО ✓' if errors_union == 0 else 'ЕСТЬ РАСХОЖДЕНИЯ ✗'}")

# Тест 4: Строки НЕ в L
print("\n--- Тест 4: Все строки НЕ в L (длины ≤ 7) ---\n")
not_in_L = []
for length in range(0, 8):
    strings = [''] if length == 0 else [''.join(bits) for bits in itertools.product('ab', repeat=length)]
    for s in strings:
        if not in_language_naive(s):
            not_in_L.append(s)

print(f"  Количество строк вне L (длины ≤ 7): {len(not_in_L)}")
print(f"  Примеры: {not_in_L[:30]}")
if len(not_in_L) > 30:
    print(f"  ... и ещё {len(not_in_L) - 30}")

print("\n" + "=" * 70)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 70)
