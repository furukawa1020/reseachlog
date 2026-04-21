from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DAILY_TEMPLATE_PATH = ROOT / "templates" / "daily-log.md"
WEEKLY_REPORT_TEMPLATE_PATH = ROOT / "templates" / "daily-weekly-report.md"
DAILY_LOG_ROOT = ROOT / "logs" / "daily"
WEEKLY_REPORT_ROOT = ROOT / "logs" / "daily_weekly_report"


def build_block(items: list[str], fallback: str) -> str:
    values = [item.strip() for item in items if item.strip()]
    if not values:
        values = [fallback]
    return "\n".join(f"  - {value}" for value in values)


def render_template(template_path: Path, log_date: str, themes: list[str], focus: str, tags: list[str]) -> str:
    template = template_path.read_text(encoding="utf-8")
    return (
        template.replace("{{DATE}}", log_date)
        .replace("{{THEMES_BLOCK}}", build_block(themes, "H1"))
        .replace("{{FOCUS}}", focus)
        .replace("{{TAGS_BLOCK}}", build_block(tags, "research-log"))
    )


def build_output_path(root: Path, log_date: str) -> Path:
    year = log_date[:4]
    output_dir = root / year
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{log_date}.md"


def write_if_needed(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create daily log files.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Log date in YYYY-MM-DD.")
    parser.add_argument("--theme", nargs="*", default=["H1"], help="Themes such as H1 H2 H3.")
    parser.add_argument("--focus", default="その日の重点を書く", help="Main focus for the day.")
    parser.add_argument("--tags", nargs="*", default=["research-log"], help="Optional tags.")
    parser.add_argument("--force", action="store_true", help="Overwrite if the file exists.")
    args = parser.parse_args()

    daily_path = build_output_path(DAILY_LOG_ROOT, args.date)
    weekly_report_path = build_output_path(WEEKLY_REPORT_ROOT, args.date)

    daily_content = render_template(DAILY_TEMPLATE_PATH, args.date, args.theme, args.focus, args.tags)
    weekly_report_content = render_template(
        WEEKLY_REPORT_TEMPLATE_PATH,
        args.date,
        args.theme,
        args.focus,
        args.tags,
    )

    write_if_needed(daily_path, daily_content, args.force)
    write_if_needed(weekly_report_path, weekly_report_content, args.force)

    print(daily_path)
    print(weekly_report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

