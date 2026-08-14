# -*- coding: utf-8 -*-
"""Report generation: console summary + markdown detail report."""
from __future__ import annotations

import os
from typing import Dict, List

from .validator import Issue, ValidationResult


def console_summary(results: Dict[str, ValidationResult]) -> str:
    lines = []
    total_errors = 0
    total_warnings = 0
    for path, res in results.items():
        errs = len(res.errors)
        warns = len([i for i in res.issues if i.level == "warning"])
        total_errors += errs
        total_warnings += warns
        status = "OK " if res.ok else "FAIL"
        lines.append(f"[{status}] {os.path.basename(path)}: {errs} error(s), {warns} warning(s)")
    lines.append(f"TOTAL: {total_errors} error(s), {total_warnings} warning(s)")
    return "\n".join(lines)


def markdown_report(results: Dict[str, ValidationResult]) -> str:
    lines = ["# 配置表校验报告", ""]
    for path, res in results.items():
        lines.append(f"## {os.path.basename(path)}")
        lines.append("")
        if not res.issues:
            lines.append("无问题。")
            lines.append("")
            continue
        lines.append("| 级别 | 规则 | Sheet | 行 | 列 | 说明 |")
        lines.append("|---|---|---|---|---|---|")
        for issue in sorted(res.issues, key=lambda i: (i.sheet, i.row)):
            lines.append(f"| {issue.level} | {issue.rule} | {issue.sheet} | {issue.row} | {issue.column} | {issue.message} |")
        lines.append("")
    return "\n".join(lines)


def write_markdown_report(results: Dict[str, ValidationResult], out_path: str) -> str:
    text = markdown_report(results)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    return out_path
