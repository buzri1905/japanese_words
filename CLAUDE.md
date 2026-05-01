# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Multi-plugin TRMNL repo. Each subdirectory is one TRMNL private plugin: a `today.json` (what TRMNL polls), a source bank (`vocabulary.json` / `passages.json`), and a `plugin.html` (Liquid markup). Daily content rotates from the bank into `today.json`; once shown, entries are marked with `used_date` so they never repeat.

## Plugins

| Dir | Audience | Level | Cadence | Bank file | today.json shape |
|------|----------|-------|---------|-----------|------------------|
| `mother_jp/` | Mother (Korean speaker, JLPT beginner) | N5 + N4 | 3 words/day (default 2 N5 + 1 N4) | `vocabulary.json` (`words` array) | `{ date, words: [3] }` |
| `my_jp/` | User (N1 holder) | **N1** (challenging) | 3 words/day | `vocabulary.json` (`words` array) | `{ date, words: [3] }` |
| `jp_reading/` | User | N1 (Japanese cooking recipes) | 1 recipe/day | `recipes.json` (`used_recipes` array — title history only) | `{ date, recipe: {...} }` |
| `cn_vocab/` | User | **HSK 4** (with occasional HSK 3 review) | 3 words/day | `vocabulary.json` (`words` array) | `{ date, words: [3] }` |

## Schemas

**Vocab entry** (`mother_jp`, `my_jp`, `cn_vocab` — same shape, different content):
```
{ id, level, word, reading, meaning, example, example_meaning, used_date }
```
- `word`: headword (kanji / hanzi).
- `reading`: kana for Japanese, pinyin for Chinese.
- `meaning`: Korean gloss.
- `example`: sentence with `<ruby>X<rt>Y</rt></ruby>` annotation (furigana for JP, pinyin for CN).
- `example_meaning`: Korean translation of the example.
- `used_date`: `null` until shown, then `YYYY-MM-DD`.

**Recipe today.json shape** (`jp_reading`) — the full recipe is generated fresh each day and only lives here:
```
{ date, recipe: {
    level, title, title_meaning, description, servings,
    ingredients: ["<ruby>...</ruby>", ...],
    steps:       ["<ruby>...</ruby>", ...],
    vocab_notes: [{word,reading,meaning}, ...]
} }
```
- `title`: Japanese dish name (e.g. `親子丼`).
- `title_meaning`: Korean gloss with English-style transliteration if useful (e.g. `오야코동 (닭고기 계란 덮밥)`).
- `description`: 1-sentence intro with furigana. Optional but recommended.
- `servings`: human-readable, e.g. `2人分` / `1人分`.
- `ingredients`: array of raw Japanese strings, each one ingredient + amount, with `<ruby>` on kanji. No Korean per line.
- `steps`: array of Japanese instruction sentences with `<ruby>`. Numbered automatically by the template. No Korean per line.
- `vocab_notes`: 6–10 difficult/cooking-specific terms with Korean meanings. This is the user's lookup strip — pick non-obvious words (avoid `卵` / `水` etc.).

**Recipe history** (`jp_reading/recipes.json`) — only stores titles already shown so we can avoid duplicates:
```
{ used_recipes: [{title, title_meaning, used_date}, ...] }
```
No full-recipe bank — Claude generates a fresh recipe each day.

Recipe cadence: **1 recipe/day**. The user is N1 — keep prose natural, don't over-simplify grammar.

`today.json` always omits `used_date` from the entry it surfaces.

## Daily picking workflow

User says things like **"오늘 단어 골라줘"**, **"단어 업데이트"**, **"오늘 거 뽑아줘"**. **Default plugin: `mother_jp/`** (the long-running one). If the user names another plugin ("내 일본어 골라줘", "중국어 단어 뽑아줘", "일본어 글 골라줘"), operate on that one instead. If ambiguous, ask.

Steps (replace `<plugin>/` with the chosen directory):

1. Determine today's date in **Asia/Seoul** (`TZ=Asia/Seoul date +%Y-%m-%d`). The user is in Korea.
2. **Vocab plugins** (`mother_jp`, `my_jp`, `cn_vocab`):
   1. Read `<plugin>/vocabulary.json`, filter entries where `used_date == null`.
   2. Pick:
      - `mother_jp`: **3 words**, mix **2 N5 + 1 N4** by default.
      - `my_jp`: **3 N1 words**, prefer variety (different parts of speech, not all nouns).
      - `cn_vocab`: **3 words at HSK 4** (with occasional HSK 3 review words sprinkled in).
      Avoid consecutive ids unless the bank is exhausted.
   3. In the bank file, set `used_date` to today for the chosen entries. Use `Edit` per unique line — **never `replace_all` on `"used_date": null`**.
   4. Overwrite `<plugin>/today.json` with the new daily payload (drop `used_date` from entries).
3. **Recipe plugin** (`jp_reading`):
   1. Read `jp_reading/recipes.json` to see which dish titles are already used.
   2. Generate a fresh N1-appropriate Japanese recipe whose `title` is **not** in `used_recipes`. Follow the recipe today.json schema (level, title, title_meaning, description, servings, ingredients, steps, vocab_notes). Keep prose natural, choose 6–10 non-obvious vocab notes.
   3. Overwrite `jp_reading/today.json` with the new recipe.
   4. Append `{title, title_meaning, used_date: today}` to `used_recipes` in `jp_reading/recipes.json`.
4. **Commit and push** so TRMNL polling sees the change:
   ```
   git add <plugin>/today.json <plugin>/<bank>.json
   git commit -m "<plugin> <today>: <summary>"
   git push
   ```
5. Tell the user what was picked so they can verify.

To redo / replace: vocab — revert `used_date` to `null`, re-pick, regenerate today.json. Recipe — remove the appended `used_recipes` entry and regenerate.

When a vocab bank drops below ~10 unused entries, warn the user and offer to add more. (jp_reading has no bank — never runs out.)

## Rendering notes

- Furigana / pinyin annotation is `<ruby>X<rt>Y</rt></ruby>` HTML embedded in the JSON. TRMNL's Liquid `{{ ... }}` does **not** auto-escape, so tags render as HTML. If the user reports tags showing as literal text, switch to `{{ field | raw }}` in the template.
- `mother_jp` and `my_jp` use Japanese-friendly fonts (Noto Sans JP, Hiragino, Yu Gothic).
- `cn_vocab` uses Chinese-friendly fonts (Noto Sans SC, PingFang SC, Microsoft YaHei). Reading is shown in italic to distinguish pinyin from kana visually.
- `jp_reading` is a single-passage layout (title + body + Korean translation + small vocab notes strip at the bottom). Different template from the 3-card vocab plugins.
- Vocab plugins use 3 stacked cards separated by hairlines, ~140 px each. If you grow fonts, verify the example line (with `<ruby>`) doesn't overflow.

## TRMNL platform reference

**Display**
- 800 × 480 px, 1-bit / 2-bit grayscale e-ink (OG device).
- Keep contrast high — avoid grays lighter than ~`#999`. `opacity: 0.65–0.7` renders as readable mid-gray.
- Views: `Full` = whole 800×480 canvas. (Half/Quadrant exist; we use Full.)

**Size/payload limits**
- **Markup template file: 1 MB max.** Practically unlimited.
- **Polling response: no documented hard limit** — keep `today.json` small (KB range).
- **Webhook payload: 2 KB max** — only relevant if a plugin uses the Webhook strategy. Polling has no cap.
- Byte/character length is essentially never the bottleneck. **Pixel height is.**

**Overflow behavior** (framework auto-handles; don't rely on it as primary layout)
- **Content Limiter**: shrinks typography when content exceeds threshold.
- **Clamp Engine**: word-based ellipsis truncation to N lines.
- **Overflow Engine**: column-flow with "and X more" for list content.

**Practical content guidelines (Full view, 800×480)**
- Single-line Japanese with `<ruby>`: ~25 chars before wrap risk.
- Single-line Korean: ~30 chars before wrap.
- 3 stacked cards: ~140 px each is the ceiling.
- 1-passage layout: body area ~280 px after title and translation strip.

**Plugin strategies**
- **Polling** (what we use): TRMNL fetches a JSON URL periodically. Best for content we generate and host (GitHub raw).
- **Webhook**: external service POSTs to TRMNL. 2 KB cap.
- **Static**: markup-only, no dynamic data.

## TRMNL plugin setup (one-time per plugin, done by user)

For each subdirectory:
1. TRMNL → Private Plugins → New Plugin → Strategy: **Polling**.
2. Polling URL: GitHub raw URL of `<plugin>/today.json`. Refresh: ~24h.
3. Markup: paste `<plugin>/plugin.html` into the **Full** view markup field.

**After this restructure**, the existing `mother_jp` plugin needs its polling URL updated from `…/today.json` → `…/mother_jp/today.json`. Until the user does that, the device will keep showing the last cached page or 404.
