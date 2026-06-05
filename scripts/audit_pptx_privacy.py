#!/usr/bin/env python3
"""Audit PPTX files for privacy-sensitive OOXML parts and keyword leaks."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path


BLOCKED_PREFIXES = (
    "docProps/",
    "customXml/",
    "ppt/notesSlides/",
    "ppt/notesMasters/",
    "ppt/comments/",
    "ppt/commentAuthors",
    "ppt/tags/",
    "ppt/embeddings/",
    "ppt/charts/",
    "ppt/diagrams/",
    "ppt/handoutMasters/",
    "ppt/printerSettings/",
)

DEFAULT_KEYWORDS = (
    "范学勇",
    "郭永红",
    "旋翼",
    "鸟爪",
    "手翼",
    "尺度律",
    "实验室",
    "联系方式",
    "邮箱",
    "手机",
    "电话",
    "基金",
    "202509",
    "202510",
)


def audit(path: Path, keywords: tuple[str, ...]) -> list[str]:
    findings: list[str] = []
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        blocked = [name for name in names if name.startswith(BLOCKED_PREFIXES)]
        if blocked:
            findings.append(f"blocked parts present: {blocked[:8]} count={len(blocked)}")

        slides = [
            name
            for name in names
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]
        if len(slides) != 1:
            findings.append(f"expected exactly 1 blank slide, found {len(slides)}")

        text_chunks: list[str] = []
        for name in names:
            if name.endswith((".xml", ".rels")):
                text_chunks.append(zf.read(name).decode("utf-8", "ignore"))
        haystack = "\n".join(text_chunks)
        hits = [keyword for keyword in keywords if keyword in haystack]
        if hits:
            findings.append(f"keyword hits: {hits}")
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--keyword", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    keywords = tuple(args.keyword) if args.keyword else DEFAULT_KEYWORDS
    failed = False
    for root in args.paths:
        files = [root] if root.is_file() else sorted(root.rglob("*.pptx"))
        for pptx in files:
            findings = audit(pptx, keywords)
            if findings:
                failed = True
                print(f"FAIL {pptx}")
                for finding in findings:
                    print(f"  - {finding}")
            else:
                print(f"OK {pptx}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
