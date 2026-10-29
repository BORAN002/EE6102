# EE6102 · 双语复习 / Bilingual Study Notes

A bilingual study website based on all five supplied Sample Quiz PDFs.

根据全部五份 Sample Quiz 整理的中英文复习网站。

**Website / 在线访问:** https://boran002.github.io/EE6102/

**Repository / 源码:** https://github.com/BORAN002/EE6102

- 115 questions: 27 / 20 / 15 / 35 / 18 across Parts 1–5.
- 44 expanded concept lessons with explanations, examples, common distinctions and linked questions.
- Three knowledge views: Understand, Memorize and Vocabulary.
- 132 full bilingual sentences to memorize, with optional hidden Chinese translations for self-testing.
- 182 distinct vocabulary terms with Chinese meanings and bilingual definitions.
- 314 bundled English audio clips for sentences and vocabulary, with 0.75× / 1× / 1.25× playback and sentence queues.
- English, Chinese and bilingual display.
- Review mode highlights the marked source answer in bold.
- Practice mode hides answers until submission, with explanations, mistakes and bookmarks.
- Progress is stored only in the current browser's local storage.
- Source PDFs are available with question-level page links.

## Content policy

Answer keys reproduce the marked source answers. The original materials contain several ambiguous or technically inaccurate answers. These are explicitly explained in bilingual source notes; they are not silently changed. In particular, Part 5 Q17 is scored as D according to the source, while its note explains why signature detection (B) fits the question's wording.

Option order is retained. Obvious labels are normalized; Part 3 Q12 has five options and a duplicated source letter, documented in its note. Explanations, Chinese translations and concept summaries are study aids, not additional text from the original PDFs.

## Run locally

From this folder:

```sh
python3 -m http.server 8080
```

Then open http://localhost:8080. No build or dependency installation is required.

## Validate

```sh
python3 scripts/validate-content.py
node --check app.js
node --check knowledge.js
node --test scripts/study-audio.test.mjs
```

The content validator checks completeness, bilingual fields, source keys, PDF availability, bidirectional concept associations, audio references and audio file hashes. The audio tests cover playback queues, switching tracks, cancellation and failure handling. GitHub Pages publishes the root of the `main` branch; `.nojekyll` disables Jekyll processing.

## Regenerate pronunciation audio

Audio is synthesized in US English with the macOS Samantha voice. Visitors play ordinary M4A files; no speech service, account or browser speech-synthesis support is required. Clips load only when requested.

After editing vocabulary or memorization sentences, run this authoring command on macOS (requires `say` and `afconvert`):

```sh
python3 scripts/generate-audio.py
python3 scripts/validate-content.py
```

Use `--parts 3 4` to regenerate selected chapters. A vocabulary entry can set `say` to spell out an abbreviation. The manifest records the spoken text, voice and file checksum.
