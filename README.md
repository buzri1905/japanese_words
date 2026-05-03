# japanese_words

TRMNL 사설 플러그인 모음. 매일 단어/레시피를 자동 로테이션해서 e-ink 디바이스에 띄웁니다.

## 플러그인

| 디렉토리 | 대상 | 레벨 | 하루 분량 |
|----------|------|------|-----------|
| `mother_jp/` | 어머니 (한국어 화자, JLPT 입문) | N5 + N4 | 단어 3개 |
| `my_jp/` | 본인 (N1 보유) | N1 (도전용) | 단어 3개 |
| `cn_vocab/` | 본인 | HSK 4 (HSK 3 복습 섞임) | 단어 3개 |
| `jp_reading/` | 본인 | N1 일본 요리 레시피 | 레시피 1개 |

각 디렉토리에 `today.json` (TRMNL이 폴링하는 데이터)과 `plugin.html` (Liquid 마크업)이 있고, 단어 뱅크는 `vocabulary.json` 또는 `recipes.json`.

## 브라우저에서 미리보기

`today.html`은 같은 폴더의 `today.json`을 JS로 fetch해서 800×480 디바이스 프레임으로 렌더합니다. raw.githack 링크로 바로 열 수 있어요:

- 어머니 일본어 — https://raw.githack.com/buzri1905/japanese_words/main/mother_jp/today.html
- 나의 일본어 (N1) — https://raw.githack.com/buzri1905/japanese_words/main/my_jp/today.html
- 중국어 (HSK 4) — https://raw.githack.com/buzri1905/japanese_words/main/cn_vocab/today.html
- 일본 요리 레시피 — https://raw.githack.com/buzri1905/japanese_words/main/jp_reading/today.html

today.json만 갱신하면 미리보기에도 자동 반영됩니다 (raw.githack CDN 캐시 때문에 약간 지연될 수 있음).
