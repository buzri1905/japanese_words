# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

TRMNL private plugin that displays **3 Japanese vocabulary words per day** for the user's mother, a JLPT N5/N4 beginner learner. Korean is her native language. Words are pre-listed in `vocabulary.json`; once shown they are marked with `used_date` so they never repeat.

## Files

- `vocabulary.json` — master word bank (60 entries: 40 N5 + 20 N4). Entry schema: `id`, `level` (`N5`/`N4`), `word`, `reading` (kana of the headword), `meaning` (Korean), `example` (Japanese sentence with `<ruby>kanji<rt>kana</rt></ruby>` furigana), `example_meaning` (Korean translation), `used_date` (`null` until shown, then `YYYY-MM-DD`).
- `today.json` — what TRMNL polls. Shape: `{ "date": "YYYY-MM-DD", "words": [3 entries] }`. Each entry mirrors a vocabulary row minus `used_date`.
- `plugin.html` — TRMNL Liquid template. Iterates `words` with `{% for w in words %}` and renders each as a row (word + reading + meaning + level on top, furigana example + Korean translation below).

## Daily picking workflow

The user (or their mother) will say things like "오늘 단어 골라줘", "단어 업데이트", "오늘 거 뽑아줘". Do this:

1. Determine today's date in **Asia/Seoul** (`TZ=Asia/Seoul date +%Y-%m-%d`). The user is in Korea.
2. Read `vocabulary.json`, filter to entries where `used_date == null`.
3. Pick **3 words**. Default mix: **2 N5 + 1 N4** for progressive learning. If only one level has unused entries left, draw from what remains. Prefer variety (don't pick three consecutive ids unless that's all that's left).
4. In `vocabulary.json`, set `used_date` to today's date for the 3 chosen entries (use `Edit` with each entry's unique line — never `replace_all` on `"used_date": null`).
5. Overwrite `today.json` with `{ "date": <today>, "words": [<the 3 picks, dropping the used_date field>] }`.
6. **Commit and push to GitHub** so TRMNL can poll the new content. Run `git add today.json vocabulary.json && git commit -m "<today>: <word1>, <word2>, <word3>" && git push`. Without this, TRMNL keeps showing yesterday's words.
7. Tell the user which 3 were picked (word, reading, meaning) so they can verify.

To redo / replace a word: revert that entry's `used_date` to `null` in `vocabulary.json`, pick a different one, update `today.json`, then commit and push again.

When the bank runs low (< ~10 unused entries), warn the user and offer to add more N5/N4 words.

## Rendering notes

- Furigana is `<ruby>kanji<rt>kana</rt></ruby>` HTML embedded in the JSON `example` field. TRMNL's Liquid output (`{{ ... }}`) does **not** auto-escape, so the tags render correctly. If the user reports the tags showing as literal text on the device, change `{{ w.example }}` in `plugin.html` to `{{ w.example | raw }}`.
- Display target: 800×480 monochrome e-ink. Keep contrast high — avoid grays lighter than ~`#999`. The current template uses `opacity: 0.65–0.7` for de-emphasis, which renders as readable mid-gray.
- Layout is 3 stacked cards separated by hairlines. Each card is ~140 px tall — if you grow font sizes, verify the example line (which has `<ruby>` adding vertical space) doesn't overflow.

## TRMNL plugin setup (one-time, done by user)

1. TRMNL → Private Plugins → New Plugin → Strategy: **Polling**.
2. Polling URL: wherever `today.json` is hosted (GitHub raw, S3, etc.). Refresh interval: ~24h.
3. Markup: paste `plugin.html` contents into the **Full** view markup field.
