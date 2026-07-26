#!/usr/bin/env python3
"""
뱅크에서 오늘의 단어를 뽑아 today.json을 갱신하는 스크립트 (AI 불필요).

CLAUDE.md의 "Daily picking workflow"를 그대로 구현한다:
  - vocabulary.json에서 used_date == null 인 항목만 후보로
  - 레벨 구성대로 뽑고, 뽑은 항목에 used_date=오늘(Asia/Seoul) 기록
  - today.json 을 새 payload로 덮어씀 (used_date 필드는 제외)

사용법:
  python3 pick_words.py                # mother_jp (N5 2 + N4 1)
  python3 pick_words.py my_jp          # N1 3개
  python3 pick_words.py cn_vocab       # HSK4 3개
  python3 pick_words.py --push         # 뽑고 git add/commit/push 까지

레시피 플러그인(jp_reading)은 매번 새로 생성해야 하므로 대상이 아니다.
"""
import json
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent

# 플러그인별 뽑기 규칙: level -> 뽑을 개수. None 이면 레벨 무관 총 3개.
PLUGINS = {
    "mother_jp": {"N5": 2, "N4": 1},
    "my_jp":     {"N1": 3},
    "cn_vocab":  {"HSK4": 3},   # 필요시 HSK3 복습은 수동으로
}


def today_seoul() -> str:
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")


def no_consecutive_ids(chosen) -> bool:
    ids = sorted(c["id"] for c in chosen)
    return all(b - a > 1 for a, b in zip(ids, ids[1:]))


def pick(candidates, n, tries=200):
    """가능하면 연속 id를 피해서 n개 뽑기. 후보가 부족하면 있는 만큼."""
    if len(candidates) <= n:
        return list(candidates)
    for _ in range(tries):
        sample = random.sample(candidates, n)
        if no_consecutive_ids(sample):
            return sample
    return random.sample(candidates, n)  # 못 피하면 그냥


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    push = "--push" in sys.argv[1:]
    plugin = args[0] if args else "mother_jp"

    if plugin not in PLUGINS:
        sys.exit(f"알 수 없는 플러그인: {plugin} (가능: {', '.join(PLUGINS)})")

    pdir = BASE / plugin
    bank_path = pdir / "vocabulary.json"
    today_path = pdir / "today.json"
    date = today_seoul()

    bank = json.loads(bank_path.read_text(encoding="utf-8"))
    words = bank["words"]

    chosen = []
    for level, count in PLUGINS[plugin].items():
        pool = [w for w in words if w["level"] == level and w.get("used_date") is None]
        if len(pool) < count:
            print(f"⚠️  {level} 미사용 단어가 {len(pool)}개뿐입니다 (요청 {count}개). "
                  f"뱅크 보충이 필요할 수 있어요.")
        chosen.extend(pick(pool, count))

    if not chosen:
        sys.exit("뽑을 단어가 없습니다. 뱅크를 확인하세요.")

    # 뱅크에 used_date 기록
    chosen_ids = {w["id"] for w in chosen}
    for w in words:
        if w["id"] in chosen_ids:
            w["used_date"] = date

    bank_path.write_text(
        json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # today.json (used_date 제외)
    payload = {
        "date": date,
        "words": [{k: v for k, v in w.items() if k != "used_date"} for w in chosen],
    }
    today_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"[{plugin}] {date} 오늘의 단어:")
    for w in chosen:
        print(f"  - {w['level']} {w['word']} ({w['reading']}) — {w['meaning']}")

    unused_left = sum(1 for w in words if w.get("used_date") is None)
    print(f"남은 미사용 단어: {unused_left}개")
    if unused_left < 10:
        print("⚠️  미사용 단어가 10개 미만입니다. 뱅크를 보충하세요.")

    if push:
        rel_today = f"{plugin}/today.json"
        rel_bank = f"{plugin}/vocabulary.json"
        summary = ", ".join(w["word"] for w in chosen)
        subprocess.run(["git", "-C", str(BASE), "add", rel_today, rel_bank], check=True)
        subprocess.run(
            ["git", "-C", str(BASE), "commit", "-m", f"{plugin} {date}: {summary}"],
            check=True,
        )
        subprocess.run(["git", "-C", str(BASE), "push"], check=True)
        print("git push 완료.")


if __name__ == "__main__":
    main()
