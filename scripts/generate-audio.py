"""Generate bundled English term/sentence audio with macOS system TTS.

Requires say and afconvert. Generation does not contact an external TTS service.
Existing clips are reused when voice, rate and spoken text match.
"""
import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE = 'Samantha'
RATE = 165
parser = argparse.ArgumentParser()
parser.add_argument('--parts', type=int, nargs='+', default=[1, 2, 3, 4, 5])
args = parser.parse_args()
out = ROOT / 'audio/en'
out.mkdir(parents=True, exist_ok=True)
manifest_path = ROOT / 'audio/manifest.json'
manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
jobs = {}
parts = []
for number in args.parts:
    path = ROOT / f'data/part-{number}.json'
    data = json.loads(path.read_text())
    for concept in data['concepts']:
        assert concept.get('statements') and concept.get('vocabulary'), concept['id']
        for item in concept['statements'] + concept['vocabulary']:
            text = item.get('say') or item.get('en') or item['term']
            text = text.replace('’', "'").replace('–', '-').replace('—', ', ')
            digest = hashlib.sha256(f'{VOICE}|{RATE}|{text}'.encode()).hexdigest()[:20]
            item['audio'] = f'audio/en/{digest}.m4a'
            jobs[item['audio']] = text
    parts.append((path, data))

def generate(job):
    relative, text = job
    destination = ROOT / relative
    if not destination.exists():
        with tempfile.TemporaryDirectory(prefix='ee6102-audio-') as temp:
            speech = Path(temp) / 'speech.txt'
            speech.write_text(text)
            intermediate = Path(temp) / 'speech.aiff'
            subprocess.run(['say', '-v', VOICE, '-r', str(RATE), '-o', str(intermediate), '-f', str(speech)], check=True, capture_output=True)
            subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac', '-b', '48000', str(intermediate), str(destination)], check=True, capture_output=True)
    assert destination.stat().st_size > 1000, relative
    return relative, {'text': text, 'voice': VOICE, 'wordsPerMinute': RATE, 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()}

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for relative, metadata in pool.map(generate, jobs.items()):
        manifest[relative] = metadata
for path, data in parts:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
# Keep unchanged chapters when regenerating a subset, but drop obsolete entries.
referenced = set()
for path in (ROOT / 'data').glob('part-*.json'):
    for concept in json.loads(path.read_text())['concepts']:
        for item in concept.get('statements', []) + concept.get('vocabulary', []):
            if item.get('audio'):
                referenced.add(item['audio'])
manifest = {path: metadata for path, metadata in manifest.items() if path in referenced}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(f'Prepared {len(jobs)} English audio clips for parts {args.parts}.')
