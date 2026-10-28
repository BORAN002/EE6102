"""Validate quiz completeness, bilingual content, answers and concept links."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNTS = [27, 20, 15, 35, 18]
PAGES = [9, 6, 5, 11, 6]
KEYS = [
    [0,0,2,0,0,0,0,3,0,0,0,4,0,0,0,0,0,1,4,1,1,0,0,1,0,1,0],
    [3,3,1,2,0,2,2,3,0,2,0,2,0,0,0,0,0,3,0,0],
    [1,1,0,0,0,0,0,2,1,0,0,2,0,0,1],
    [1,2,0,1,2,0,1,3,2,3,1,1,1,1,0,0,0,3,0,0,1,0,3,1,0,0,0,0,2,1,1,0,2,1,0],
    [3,2,0,0,0,0,0,0,0,0,0,1,0,1,0,2,3,3],
]

def bilingual(value):
    assert isinstance(value, dict)
    for lang in ('en', 'zh'):
        assert isinstance(value.get(lang), str) and value[lang].strip(), value

total_questions = total_concepts = 0
for number, expected in enumerate(COUNTS, 1):
    part = json.loads((ROOT / f'data/part-{number}.json').read_text())
    assert part['id'] == number
    bilingual(part['title'])
    bilingual(part['subtitle'])
    assert len(part['questions']) == expected
    assert [q['number'] for q in part['questions']] == list(range(1, expected + 1))
    assert [q['answer'] for q in part['questions']] == KEYS[number-1]
    concepts = {c['id']: c for c in part['concepts']}
    assert len(concepts) == len(part['concepts'])
    questions = {q['number']: q for q in part['questions']}
    for q in part['questions']:
        assert q['id'] == f'p{number}-q{q["number"]}'
        assert 1 <= q['page'] <= PAGES[number-1]
        bilingual(q['prompt'])
        bilingual(q['explanation'])
        assert 2 <= len(q['options']) <= 5
        assert 0 <= q['answer'] < len(q['options'])
        for option in q['options']:
            bilingual(option)
        if q.get('note'):
            bilingual(q['note'])
        assert q['conceptIds']
        for cid in q['conceptIds']:
            assert cid in concepts, (q['id'], cid)
            assert q['number'] in concepts[cid]['questionIds'], (q['id'], cid)
    for cid, c in concepts.items():
        for field in ('title', 'body', 'memory'):
            bilingual(c[field])
        assert c['questionIds']
        for qnum in c['questionIds']:
            assert qnum in questions, (cid, qnum)
            assert cid in questions[qnum]['conceptIds'], (cid, qnum)
    assert (ROOT / f'sources/part-{number}.pdf').read_bytes().startswith(b'%PDF-')
    total_questions += len(questions)
    total_concepts += len(concepts)
    print(f'Part {number}: {len(questions)} questions, {len(concepts)} concepts; validated')
assert total_questions == 115
print(f'PASS: {total_questions} questions and {total_concepts} bilingual concepts.')
