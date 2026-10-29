"""Validate quiz completeness, bilingual content, answers and concept links."""
import hashlib
import json
import re
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

manifest = json.loads((ROOT / 'audio/manifest.json').read_text())
audio_paths = set()
terms = set()
total_questions = total_concepts = total_sentences = 0

def audio_clip(value):
    path = value.get('audio', '')
    assert re.fullmatch(r'audio/en/[a-f0-9]{20}\.m4a', path), path
    clip = (ROOT / path).read_bytes()
    assert len(clip) > 1000 and clip[4:8] == b'ftyp', path
    assert hashlib.sha256(clip).hexdigest() == manifest[path]['sha256'], path
    text = value.get('say') or value.get('en') or value.get('term')
    text = text.replace('’', "'").replace('–', '-').replace('—', ', ')
    assert manifest[path]['text'] == text, (path, text)
    audio_paths.add(path)
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
        assert len(c['lesson']) >= 2, cid
        for paragraph in c['lesson']:
            bilingual(paragraph)
        bilingual(c['example'])
        bilingual(c['pitfall'])
        assert len(c['statements']) == 3, cid
        for sentence in c['statements']:
            bilingual(sentence)
            audio_clip(sentence)
            total_sentences += 1
        assert len(c['vocabulary']) >= 4, cid
        for word in c['vocabulary']:
            assert word['term'].strip() and word['zh'].strip(), cid
            bilingual(word['definition'])
            audio_clip(word)
            terms.add(word['term'].lower())
        assert c['questionIds']
        for qnum in c['questionIds']:
            assert qnum in questions, (cid, qnum)
            assert cid in questions[qnum]['conceptIds'], (cid, qnum)
    assert (ROOT / f'sources/part-{number}.pdf').read_bytes().startswith(b'%PDF-')
    total_questions += len(questions)
    total_concepts += len(concepts)
    print(f'Part {number}: {len(questions)} questions, {len(concepts)} concepts; validated')
assert total_questions == 115
assert total_concepts == 44 and total_sentences == 132
assert audio_paths == set(manifest), 'Unreferenced or missing audio'
print(f'PASS: {total_questions} questions, {total_concepts} bilingual concepts, '
      f'{total_sentences} sentences, {len(terms)} terms and {len(audio_paths)} audio clips.')
