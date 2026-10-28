# EE6102 · 双语复习 / Bilingual Study Notes

A bilingual study website based on all five supplied Sample Quiz PDFs.

根据全部五份 Sample Quiz 整理的中英文复习网站。

**Website / 在线访问:** https://boran002.github.io/EE6102/

**Repository / 源码:** https://github.com/BORAN002/EE6102

- 115 questions: 27 / 20 / 15 / 35 / 18 across Parts 1–5.
- 44 concept notes, with definitions, memory sentences and linked questions.
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
```

The content validator checks completeness, bilingual fields, source keys, PDF availability and bidirectional concept associations. GitHub Pages publishes the root of the `main` branch; `.nojekyll` disables Jekyll processing.
