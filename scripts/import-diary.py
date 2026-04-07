#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


SOURCE_DIR = Path("/Users/admin/Downloads/老薛的晨间日记 markdown")
OUTPUT_DIR = Path("content/posts/diary")
DEFAULT_YEAR = 2026


def parse_args():
    parser = argparse.ArgumentParser(description="Import morning diary markdown files.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--year", type=int, help="Import a specific year, e.g. 2026")
    group.add_argument("--all", action="store_true", help="Import all diary files")
    parser.add_argument("--dry-run", action="store_true", help="Print planned work only")
    return parser.parse_args()


def split_front_matter(text, source_path):
    if not text.startswith("---\n"):
        raise ValueError(f"{source_path}: missing front matter")

    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"{source_path}: unclosed front matter")

    front_matter = text[4:end].strip()
    body = text[end + len("\n---") :]
    if body.startswith("\r\n"):
        body = body[2:]
    elif body.startswith("\n"):
        body = body[1:]

    if not body.strip():
        raise ValueError(f"{source_path}: empty body")

    return parse_simple_yaml(front_matter), body


def parse_simple_yaml(front_matter):
    values = {}
    for line in front_matter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def strip_markdown(text):
    text = text.strip()
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text)
    text = re.sub(r"^\s*[-*+]\s+", "", text)
    text = re.sub(r"^\s*>\s?", "", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"[*_~]+", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def first_nonempty_line(body):
    for line in body.splitlines():
        clean = strip_markdown(line)
        if clean:
            return clean
    return ""


def make_title(body):
    title = first_nonempty_line(body)
    if not title:
        raise ValueError("empty title")
    if len(title) > 50:
        return title[:50] + "..."
    return title


def make_summary(body):
    plain_lines = []
    for line in body.splitlines():
        clean = strip_markdown(line)
        if clean:
            plain_lines.append(clean)
    summary = re.sub(r"\s+", " ", " ".join(plain_lines)).strip()
    if len(summary) > 100:
        return summary[:100] + "..."
    return summary


def yaml_string(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_post(source_path, front_matter, body):
    date_value = front_matter.get("date") or source_path.stem
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_value):
        raise ValueError(f"{source_path}: invalid date {date_value!r}")

    year = date_value[:4]
    title = make_title(body)
    summary = make_summary(body)
    output_front_matter = "\n".join(
        [
            "---",
            f"title: {yaml_string(title)}",
            f"date: {date_value}T06:30:00+08:00",
            "draft: false",
            f'tags: ["晨间日记", "{year}"]',
            'categories: ["晨间日记"]',
            f"summary: {yaml_string(summary)}",
            "ShowToc: false",
            "---",
            "",
        ]
    )
    return output_front_matter + body


def iter_sources(args):
    pattern = "*.md" if args.all else f"{args.year or DEFAULT_YEAR}-*.md"
    return sorted(SOURCE_DIR.glob(pattern))


def main():
    args = parse_args()
    if not SOURCE_DIR.exists():
        print(f"Source directory not found: {SOURCE_DIR}", file=sys.stderr)
        return 1

    sources = iter_sources(args)
    if not sources:
        print("成功 0 篇、跳过 0 篇、错误 0 篇")
        return 0

    success = 0
    skipped = 0
    errors = 0
    if not args.dry_run:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for source_path in sources:
        try:
            text = source_path.read_text(encoding="utf-8")
            front_matter, body = split_front_matter(text, source_path)
            rendered = render_post(source_path, front_matter, body)
            output_path = OUTPUT_DIR / source_path.name
            if args.dry_run:
                print(f"DRY-RUN {source_path.name} -> {output_path}")
            else:
                output_path.write_text(rendered, encoding="utf-8")
            success += 1
        except ValueError as exc:
            skipped += 1
            print(f"SKIP {exc}", file=sys.stderr)
        except Exception as exc:
            errors += 1
            print(f"ERROR {source_path}: {exc}", file=sys.stderr)

    print(f"成功 {success} 篇、跳过 {skipped} 篇、错误 {errors} 篇")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
