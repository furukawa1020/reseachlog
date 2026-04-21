from __future__ import annotations

import argparse
from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LOG_ROOT = ROOT / "logs" / "daily"
OUTPUT_ROOT = ROOT / "slides" / "outlines"

OLD_SECTION_ACTIONS = "今日やったこと"
OLD_SECTION_FINDINGS = "得られたこと"
OLD_SECTION_BLOCKERS = "困りごと"
OLD_SECTION_NEXT_STEPS = "次にやること"
OLD_SECTION_ARTIFACTS = "参照・成果物"
OLD_SECTION_SLIDE_NOTES = "スライド化メモ"

SECTION_THIS_WEEK = "前回からの活動 Works in this week"
SECTION_THIS_WEEK_RESEARCH = "研究概要 Research works"
SECTION_THIS_WEEK_OTHER = "その他 Other works"
SECTION_MEMOS = "振り返り・反省事項 Memos"
SECTION_NEXT_WEEK = "次回までの活動予定 Works in upcoming week"
SECTION_NEXT_WEEK_RESEARCH = "研究活動 Research works"
SECTION_NEXT_WEEK_OTHER = "その他 Other works"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a slide-outline draft from daily logs.")
    parser.add_argument("--from", dest="date_from", required=True, help="Start date in YYYY-MM-DD.")
    parser.add_argument("--to", dest="date_to", required=True, help="End date in YYYY-MM-DD.")
    parser.add_argument("--title", required=True, help="Title for the outline.")
    parser.add_argument("--output", help="Optional output path.")
    return parser.parse_args()


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_front_matter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text

    lines = text.splitlines()
    front_lines: list[str] = []
    body_start = 0
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            body_start = index + 1
            break
        front_lines.append(lines[index])

    data: dict[str, object] = {}
    current_key: str | None = None
    current_list: list[str] | None = None

    for raw_line in front_lines:
        if not raw_line.strip():
            continue

        if raw_line.startswith("  - ") and current_key:
            if current_list is None:
                current_list = []
                data[current_key] = current_list
            current_list.append(raw_line[4:].strip())
            continue

        current_list = None
        if ":" not in raw_line:
            continue

        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key

        if value:
            data[key] = value
        else:
            data[key] = []
            current_list = data[key]  # type: ignore[assignment]

    body = "\n".join(lines[body_start:])
    return data, body


def parse_old_sections(body: str) -> dict[str, list[str]]:
    section_names = [
        OLD_SECTION_ACTIONS,
        OLD_SECTION_FINDINGS,
        OLD_SECTION_BLOCKERS,
        OLD_SECTION_NEXT_STEPS,
        OLD_SECTION_ARTIFACTS,
        OLD_SECTION_SLIDE_NOTES,
    ]
    sections: OrderedDict[str, list[str]] = OrderedDict((name, []) for name in section_names)
    current: str | None = None

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            heading = line[3:].strip()
            current = heading if heading in sections else None
            continue

        if current is None:
            continue

        stripped = line.strip()
        if not stripped:
            continue

        cleaned = re.sub(r"^[-*]\s*", "", stripped)
        sections[current].append(cleaned)

    return sections


def parse_weekly_report_sections(body: str) -> dict[str, list[str]]:
    sections = {
        "this_week_research": [],
        "this_week_other": [],
        "memos": [],
        "next_week_research": [],
        "next_week_other": [],
    }

    current_h2: str | None = None
    current_h3: str | None = None

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            current_h2 = line[3:].strip()
            current_h3 = None
            continue
        if line.startswith("### "):
            current_h3 = line[4:].strip()
            continue

        stripped = line.strip()
        if not stripped or not stripped.startswith("- "):
            continue

        item = stripped[2:].strip()
        if not item:
            continue

        if current_h2 == SECTION_THIS_WEEK and current_h3 == SECTION_THIS_WEEK_RESEARCH:
            sections["this_week_research"].append(item)
        elif current_h2 == SECTION_THIS_WEEK and current_h3 == SECTION_THIS_WEEK_OTHER:
            sections["this_week_other"].append(item)
        elif current_h2 == SECTION_THIS_WEEK and current_h3 == SECTION_MEMOS:
            sections["memos"].append(item)
        elif current_h2 == SECTION_NEXT_WEEK and current_h3 == SECTION_NEXT_WEEK_RESEARCH:
            sections["next_week_research"].append(item)
        elif current_h2 == SECTION_NEXT_WEEK and current_h3 == SECTION_NEXT_WEEK_OTHER:
            sections["next_week_other"].append(item)

    return sections


def unique_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output


def collect_logs(start: date, end: date) -> list[tuple[Path, dict[str, object], str]]:
    collected: list[tuple[Path, dict[str, object], str]] = []
    for path in sorted(LOG_ROOT.glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        raw_date = str(meta.get("date", path.stem))
        try:
            log_date = parse_date(raw_date)
        except ValueError:
            continue
        if start <= log_date <= end:
            collected.append((path, meta, body))
    return collected


def normalize_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def default_output_path(end: date) -> Path:
    year_dir = OUTPUT_ROOT / str(end.year)
    year_dir.mkdir(parents=True, exist_ok=True)
    return year_dir / f"{end.isoformat()}-slide-outline.md"


def main() -> int:
    args = parse_args()
    start = parse_date(args.date_from)
    end = parse_date(args.date_to)
    logs = collect_logs(start, end)

    if not logs:
        raise SystemExit("No logs found in the requested date range.")

    themes: list[str] = []
    main_focus: list[str] = []
    this_week_research: list[str] = []
    this_week_other: list[str] = []
    memos: list[str] = []
    next_week_research: list[str] = []
    next_week_other: list[str] = []
    old_actions: list[str] = []
    old_findings: list[str] = []
    old_blockers: list[str] = []
    old_next_steps: list[str] = []
    artifacts: list[str] = []

    for path, meta, body in logs:
        themes.extend(normalize_list(meta.get("themes", [])))

        focus_value = str(meta.get("focus", "")).strip()
        if focus_value:
            main_focus.append(focus_value)

        weekly_sections = parse_weekly_report_sections(body)
        this_week_research.extend(weekly_sections["this_week_research"])
        this_week_other.extend(weekly_sections["this_week_other"])
        memos.extend(weekly_sections["memos"])
        next_week_research.extend(weekly_sections["next_week_research"])
        next_week_other.extend(weekly_sections["next_week_other"])

        old_sections = parse_old_sections(body)
        old_actions.extend(old_sections[OLD_SECTION_ACTIONS])
        old_findings.extend(old_sections[OLD_SECTION_FINDINGS])
        old_blockers.extend(old_sections[OLD_SECTION_BLOCKERS])
        old_next_steps.extend(old_sections[OLD_SECTION_NEXT_STEPS])
        artifacts.extend(old_sections[OLD_SECTION_ARTIFACTS])
        artifacts.append(path.as_posix().replace(ROOT.as_posix() + "/", ""))

    what_we_did = unique_keep_order(this_week_research + old_actions)
    other_works = unique_keep_order(this_week_other)
    memo_items = unique_keep_order(memos + old_findings + old_blockers)
    next_steps = unique_keep_order(next_week_research + next_week_other + old_next_steps)

    outline = [
        f"# {args.title}",
        "",
        f"- Period: {start.isoformat()} to {end.isoformat()}",
        f"- Source logs: {len(logs)}",
        f"- Themes: {', '.join(unique_keep_order(themes)) or 'Unspecified'}",
        "- Note: This is a draft aggregated from research logs. If the source logs are in Japanese, polish the bullets into presentation English before use.",
        "",
        "## Main Focus",
    ]

    for item in unique_keep_order(main_focus) or ["Focus not recorded"]:
        outline.append(f"- {item}")

    outline.extend(["", "## Research Works This Period", *[f"- {item}" for item in what_we_did or ["No research activity recorded"]]])
    outline.extend(["", "## Other Works", *[f"- {item}" for item in other_works or ["No other work recorded"]]])
    outline.extend(["", "## Memos and Reflections", *[f"- {item}" for item in memo_items or ["No memo recorded"]]])
    outline.extend(["", "## Planned Next Steps", *[f"- {item}" for item in next_steps or ["No next step recorded"]]])
    outline.extend(["", "## Sources", *[f"- {item}" for item in unique_keep_order(artifacts)]])
    outline.append("")

    output_path = Path(args.output) if args.output else default_output_path(end)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(outline), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

