from __future__ import annotations

import argparse
from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LOG_ROOT = ROOT / "logs" / "daily"
OUTPUT_ROOT = ROOT / "slides" / "outlines"

SECTION_FOCUS = "\u4eca\u65e5\u306e\u7126\u70b9"
SECTION_QUESTION = "\u4eca\u65e5\u306e\u554f\u3044"
SECTION_ACTIONS = "\u4eca\u65e5\u3084\u3063\u305f\u3053\u3068"
SECTION_FINDINGS = "\u5f97\u3089\u308c\u305f\u3053\u3068"
SECTION_SLIDE_NOTES = "\u30b9\u30e9\u30a4\u30c9\u5316\u30e1\u30e2"
SECTION_BLOCKERS = "\u56f0\u308a\u3054\u3068"
SECTION_NEXT_STEPS = "\u6b21\u306b\u3084\u308b\u3053\u3068"
SECTION_ARTIFACTS = "\u53c2\u7167\u30fb\u6210\u679c\u7269"

SECTION_NAMES = [
    SECTION_FOCUS,
    SECTION_QUESTION,
    SECTION_ACTIONS,
    SECTION_FINDINGS,
    SECTION_SLIDE_NOTES,
    SECTION_BLOCKERS,
    SECTION_NEXT_STEPS,
    SECTION_ARTIFACTS,
]


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


def parse_sections(body: str) -> dict[str, list[str]]:
    sections: OrderedDict[str, list[str]] = OrderedDict((name, []) for name in SECTION_NAMES)
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


def unique_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output


def collect_logs(start: date, end: date) -> list[tuple[Path, dict[str, object], dict[str, list[str]]]]:
    collected: list[tuple[Path, dict[str, object], dict[str, list[str]]]] = []
    for path in sorted(LOG_ROOT.glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        raw_date = str(meta.get("date", path.stem))
        try:
            log_date = parse_date(raw_date)
        except ValueError:
            continue
        if start <= log_date <= end:
            collected.append((path, meta, parse_sections(body)))
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
    frontmatter_focus: list[str] = []
    daily_focus: list[str] = []
    actions: list[str] = []
    findings: list[str] = []
    slide_notes: list[str] = []
    blockers: list[str] = []
    next_steps: list[str] = []
    artifacts: list[str] = []

    for path, meta, sections in logs:
        themes.extend(normalize_list(meta.get("themes", [])))

        focus_value = str(meta.get("focus", "")).strip()
        if focus_value:
            frontmatter_focus.append(focus_value)

        daily_focus.extend(sections[SECTION_FOCUS])
        daily_focus.extend(sections[SECTION_QUESTION])
        actions.extend(sections[SECTION_ACTIONS])
        findings.extend(sections[SECTION_FINDINGS])
        slide_notes.extend(sections[SECTION_SLIDE_NOTES])
        blockers.extend(sections[SECTION_BLOCKERS])
        next_steps.extend(sections[SECTION_NEXT_STEPS])
        artifacts.extend(sections[SECTION_ARTIFACTS])
        artifacts.append(path.as_posix().replace(ROOT.as_posix() + "/", ""))

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

    for item in unique_keep_order(frontmatter_focus) or ["Focus not recorded"]:
        outline.append(f"- {item}")

    outline.extend(["", "## Daily Focus Notes", *[f"- {item}" for item in unique_keep_order(daily_focus) or ["No focus recorded"]]])
    outline.extend(["", "## What We Did", *[f"- {item}" for item in unique_keep_order(actions) or ["No activity recorded"]]])
    outline.extend(["", "## Key Takeaways", *[f"- {item}" for item in unique_keep_order(findings) or ["No finding recorded"]]])
    outline.extend(["", "## Slide-Ready Notes", *[f"- {item}" for item in unique_keep_order(slide_notes) or ["No slide note recorded"]]])
    outline.extend(["", "## Blockers", *[f"- {item}" for item in unique_keep_order(blockers) or ["No blocker recorded"]]])
    outline.extend(["", "## Next Steps", *[f"- {item}" for item in unique_keep_order(next_steps) or ["No next step recorded"]]])
    outline.extend(["", "## Sources", *[f"- {item}" for item in unique_keep_order(artifacts)]])
    outline.append("")

    output_path = Path(args.output) if args.output else default_output_path(end)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(outline), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
