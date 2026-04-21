from __future__ import annotations

import argparse
from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LOG_ROOT = ROOT / "logs" / "daily"
OUTPUT_ROOT = ROOT / "slides" / "outlines"

SECTION_NAMES = [
    "今日の問い",
    "今日やったこと",
    "得られたこと",
    "スライド化メモ",
    "困りごと",
    "次にやること",
    "参照・成果物",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a slide-ready outline from daily logs.")
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
    foci: list[str] = []
    questions: list[str] = []
    actions: list[str] = []
    findings: list[str] = []
    slide_notes: list[str] = []
    blockers: list[str] = []
    next_steps: list[str] = []
    artifacts: list[str] = []

    for path, meta, sections in logs:
        themes.extend(normalize_list(meta.get("themes", [])))
        focus = str(meta.get("focus", "")).strip()
        if focus:
            foci.append(focus)
        questions.extend(sections["今日の問い"])
        actions.extend(sections["今日やったこと"])
        findings.extend(sections["得られたこと"])
        slide_notes.extend(sections["スライド化メモ"])
        blockers.extend(sections["困りごと"])
        next_steps.extend(sections["次にやること"])
        artifacts.extend(sections["参照・成果物"])
        artifacts.append(path.as_posix().replace(ROOT.as_posix() + "/", ""))

    outline = [
        f"# {args.title}",
        "",
        f"- 期間: {start.isoformat()} から {end.isoformat()}",
        f"- 対象ログ数: {len(logs)}",
        f"- テーマ: {', '.join(unique_keep_order(themes)) or '未設定'}",
        "",
        "## この期間の主題",
    ]

    for item in unique_keep_order(foci) or ["主題未記入"]:
        outline.append(f"- {item}")

    outline.extend(["", "## 問い", *[f"- {item}" for item in unique_keep_order(questions) or ["問い未記入"]]])
    outline.extend(["", "## 実施したこと", *[f"- {item}" for item in unique_keep_order(actions) or ["記録なし"]]])
    outline.extend(["", "## 得られたこと", *[f"- {item}" for item in unique_keep_order(findings) or ["記録なし"]]])
    outline.extend(["", "## スライドに載せる材料", *[f"- {item}" for item in unique_keep_order(slide_notes) or ["記録なし"]]])
    outline.extend(["", "## 詰まりどころ", *[f"- {item}" for item in unique_keep_order(blockers) or ["特記事項なし"]]])
    outline.extend(["", "## 次の一手", *[f"- {item}" for item in unique_keep_order(next_steps) or ["未記入"]]])
    outline.extend(["", "## 参照元", *[f"- {item}" for item in unique_keep_order(artifacts)]])
    outline.append("")

    output_path = Path(args.output) if args.output else default_output_path(end)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(outline), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
