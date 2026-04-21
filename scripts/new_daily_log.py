from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "templates" / "daily-log.md"
LOG_ROOT = ROOT / "logs" / "daily"


def build_block(items: list[str], fallback: str) -> str:
    values = [item.strip() for item in items if item.strip()]
    if not values:
        values = [fallback]
    return "\n".join(f"  - {value}" for value in values)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a daily research log.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Log date in YYYY-MM-DD.")
    parser.add_argument("--theme", nargs="*", default=["H1"], help="Themes such as H1 H2 H3.")
    parser.add_argument("--focus", default="今日の主題を書く", help="Main focus for the day.")
    parser.add_argument("--tags", nargs="*", default=["research-log"], help="Optional tags.")
    parser.add_argument("--force", action="store_true", help="Overwrite if the file exists.")
    args = parser.parse_args()

    year = args.date[:4]
    log_dir = LOG_ROOT / year
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{args.date}.md"

    if log_path.exists() and not args.force:
        print(log_path)
        return 0

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    content = (
        template.replace("{{DATE}}", args.date)
        .replace("{{THEMES_BLOCK}}", build_block(args.theme, "H1"))
        .replace("{{FOCUS}}", args.focus)
        .replace("{{TAGS_BLOCK}}", build_block(args.tags, "research-log"))
    )

    log_path.write_text(content, encoding="utf-8")
    print(log_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

