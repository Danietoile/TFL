import re
import random

# 1. Регулярное выражение (академическое)
REGEX = re.compile(r'^(b(a|(c(bbb|bc)*a(bcc*a)*|ac)*)ac)*$')

def check_regex(word):
    return bool(REGEX.match(word))

# 2. ДКА (пункт 1, 13 состояний Q0–Q12, ловушка Q6)
DFA_START = 'Q1'
DFA_ACCEPT = {'Q0', 'Q1'}
DFA_TRANS = {
    'Q0':  {'a': 'Q12', 'b': 'Q2',  'c': 'Q4'},
    'Q1':  {'a': 'Q6',  'b': 'Q2',  'c': 'Q6'},
    'Q2':  {'a': 'Q10', 'b': 'Q6',  'c': 'Q4'},
    'Q3':  {'a': 'Q12', 'b': 'Q7',  'c': 'Q4'},
    'Q4':  {'a': 'Q3',  'b': 'Q8',  'c': 'Q6'},
    'Q5':  {'a': 'Q3',  'b': 'Q6',  'c': 'Q5'},
    'Q6':  {'a': 'Q6',  'b': 'Q6',  'c': 'Q6'},
    'Q7':  {'a': 'Q6',  'b': 'Q6',  'c': 'Q5'},
    'Q8':  {'a': 'Q6',  'b': 'Q9',  'c': 'Q4'},
    'Q9':  {'a': 'Q6',  'b': 'Q4',  'c': 'Q6'},
    'Q10': {'a': 'Q11', 'b': 'Q6',  'c': 'Q0'},
    'Q11': {'a': 'Q6',  'b': 'Q6',  'c': 'Q1'},
    'Q12': {'a': 'Q6',  'b': 'Q6',  'c': 'Q0'},
}

def check_dfa(word):
    state = DFA_START
    for ch in word:
        state = DFA_TRANS[state][ch]
    return state in DFA_ACCEPT

# 3. НКА (пункт 2, вариант 1 — 12 состояний, без ε)
NFA_START = {'Q1'}
NFA_ACCEPT = {'Q0', 'Q1'}
NFA_TRANS = {
    'Q0':  {'a': {'Q12'}, 'b': {'Q2'},  'c': {'Q4'}},
    'Q1':  {'a': set(),   'b': {'Q2'},  'c': set()},
    'Q2':  {'a': {'Q10'}, 'b': set(),   'c': {'Q4'}},
    'Q3':  {'a': {'Q12'}, 'b': {'Q7'},  'c': {'Q4'}},
    'Q4':  {'a': {'Q3'},  'b': {'Q8'},  'c': set()},
    'Q5':  {'a': {'Q3'},  'b': set(),   'c': {'Q5'}},
    'Q7':  {'a': set(),   'b': set(),   'c': {'Q5'}},
    'Q8':  {'a': set(),   'b': {'Q9'},  'c': {'Q4'}},
    'Q9':  {'a': set(),   'b': {'Q4'},  'c': set()},
    'Q10': {'a': {'Q11'}, 'b': set(),   'c': {'Q0'}},
    'Q11': {'a': set(),   'b': set(),   'c': {'Q1'}},
    'Q12': {'a': set(),   'b': set(),   'c': {'Q0'}},
}

def check_nfa(word):
    states = set(NFA_START)
    for ch in word:
        next_states = set()
        for s in states:
            next_states |= NFA_TRANS[s][ch]
        states = next_states
        if not states:
            return False
    return bool(states & NFA_ACCEPT)

# 4. ПКА (пункт 2, вариант 2 — 14 состояний, с ε-переходами)
PKA_START = 'r0'
PKA_ACCEPT = {'r0'}
PKA_TRANS = {
    'r0': {'a': set(),     'b': set(),     'c': set(),     'eps': {'s0'}},
    's0': {'a': set(),     'b': {'s1'},    'c': set(),     'eps': set()},
    's1': {'a': {'s2'},    'b': set(),     'c': set(),     'eps': {'m0'}},
    's2': {'a': {'s3'},    'b': set(),     'c': set(),     'eps': set()},
    's3': {'a': set(),     'b': set(),     'c': {'s4'},    'eps': set()},
    's4': {'a': set(),     'b': set(),     'c': set(),     'eps': {'r0'}},
    'm0': {'a': {'m1'},    'b': set(),     'c': {'z0'},    'eps': {'s2'}},
    'm1': {'a': set(),     'b': set(),     'c': {'m0'},    'eps': set()},
    'z0': {'a': {'w0'},    'b': {'z1'},    'c': set(),     'eps': set()},
    'z1': {'a': set(),     'b': {'z2'},    'c': {'z0'},    'eps': set()},
    'z2': {'a': set(),     'b': {'z0'},    'c': set(),     'eps': set()},
    'w0': {'a': set(),     'b': {'w1'},    'c': set(),     'eps': {'m0'}},
    'w1': {'a': set(),     'b': set(),     'c': {'w2'},    'eps': set()},
    'w2': {'a': {'w0'},    'b': set(),     'c': {'w2'},    'eps': set()},
}

def eps_closure(states):
    #Вычислить ε-замыкание множества состояний.
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for t in PKA_TRANS[s]['eps']:
            if t not in closure:
                closure.add(t)
                stack.append(t)
    return closure

def check_pka(word):
    states = eps_closure({PKA_START})
    for ch in word:
        next_states = set()
        for s in states:
            next_states |= PKA_TRANS[s][ch]
        states = eps_closure(next_states)
        if not states:
            return False
    return bool(states & PKA_ACCEPT)

# Фазз-тестирование
def generate_random_word(max_len=20):
    length = random.randint(0, max_len)
    return ''.join(random.choice('abc') for _ in range(length))

def generate_targeted_words():
    # Слова, которые точно должны приниматься или отвергаться
    accept = [
        '',          # ε
        'bac',       # b·ε·ac
        'baac',      # b·a·ac
        'bacac',     # b·(ac)·ac
        'bcaac',     # b·(ca)·ac  (Z=ε, W=ε)
        'bcbcaac',   # b·(c·bc·a)·ac
        'bcbbbaac',  # b·(c·bbb·a)·ac
        'bcabcaac',  # b·(ca·bca)·ac
        'bcabccaac', # b·(ca·bcca)·ac
        'bacbac',    # два блока bac
        'baacbaac',  # два блока baac
    ]
    reject = [
        'a', 'b', 'c',
        'abc', 'ba', 'bc',
        'bca', 'bcb', 'bcc',
        'bcbac',     # неполный блок
        'aaa', 'bbb', 'ccc',
    ]
    return accept, reject

def run_tests():
    random.seed(42)
    
    accept_words, reject_words = generate_targeted_words()
    
    # Тестируем целевые слова
    print("=" * 70)
    print("ЦЕЛЕВЫЕ СЛОВА (должны приниматься)")
    print("=" * 70)
    all_ok = True
    for w in accept_words:
        r = check_regex(w)
        d = check_dfa(w)
        n = check_nfa(w)
        p = check_pka(w)
        ok = (r == d == n == p)
        status = "✓" if ok else "✗ MISMATCH"
        display = w if w else 'ε'
        if not ok or not r:
            print(f"  {display:20s}  regex={r}  dfa={d}  nfa={n}  pka={p}  {status}")
            all_ok = False
        else:
            print(f"  {display:20s}  all=True  {status}")
    
    print()
    print("=" * 70)
    print("ЦЕЛЕВЫЕ СЛОВА (должны отвергаться)")
    print("=" * 70)
    for w in reject_words:
        r = check_regex(w)
        d = check_dfa(w)
        n = check_nfa(w)
        p = check_pka(w)
        ok = (r == d == n == p)
        status = "✓" if ok else "✗ MISMATCH"
        if not ok or r:
            print(f"  {w:20s}  regex={r}  dfa={d}  nfa={n}  pka={p}  {status}")
            all_ok = False
        else:
            print(f"  {w:20s}  all=False  {status}")
    
    # Фазз-тестирование
    print()
    print("=" * 70)
    print("ФАЗЗ-ТЕСТИРОВАНИЕ (10000 случайных слов)")
    print("=" * 70)
    
    mismatches = 0
    accepted_count = 0
    total = 10000
    
    for i in range(total):
        w = generate_random_word(max_len=25)
        r = check_regex(w)
        d = check_dfa(w)
        n = check_nfa(w)
        p = check_pka(w)
        
        if r:
            accepted_count += 1
        
        if not (r == d == n == p):
            mismatches += 1
            if mismatches <= 20:
                print(f"  MISMATCH: '{w}'  regex={r}  dfa={d}  nfa={n}  pka={p}")
    
    print(f"\n  Всего слов:       {total}")
    print(f"  Принято (regex):  {accepted_count}")
    print(f"  Расхождений:      {mismatches}")
    
    if mismatches == 0 and all_ok:
        print("\n  ✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ — все 4 распознавателя согласованы.")
    else:
        print("\n  ❌ ОБНАРУЖЕНЫ РАСХОЖДЕНИЯ!")

if __name__ == '__main__':
    run_tests()

