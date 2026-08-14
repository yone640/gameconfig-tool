# -*- coding: utf-8 -*-
"""Command-line entry point for gameconfig-tool."""
from __future__ import annotations

import argparse
import sys
from typing import List

from .converter import convert_workbook, write_json
from .loader import load_directory
from .report import console_summary, write_markdown_report
from .schema import load_schema
from .validator import validate_all


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gameconfig",
        description="Game designer config table converter & validator (Excel -> JSON)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_conv = sub.add_parser("convert", help="convert Excel config tables to JSON")
    p_conv.add_argument("dir", help="directory containing .xlsx config tables")
    p_conv.add_argument("-o", "--out", default="out", help="output directory (default: out/)")
    p_conv.add_argument("--schema", default=None, help="optional schema.json to coerce types")

    p_val = sub.add_parser("validate", help="validate config tables against schema")
    p_val.add_argument("dir", help="directory containing .xlsx config tables")
    p_val.add_argument("--schema", required=True, help="schema.json path")
    p_val.add_argument("--report", default="report.md", help="markdown report output path")

    return parser


def _cmd_convert(args: argparse.Namespace) -> int:
    wbs = load_directory(args.dir)
    if not wbs:
        print(f"no .xlsx files found in {args.dir}")
        return 1
    specs = load_schema(args.schema) if args.schema else {}
    for wb in wbs:
        data = convert_workbook(wb, specs)
        base = wb.path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]
        name = base.rsplit(".", 1)[0] + ".json"
        path = write_json(data, args.out, name)
        sheet_info = ", ".join(f"{s.name}({len(s.rows)}行)" for s in wb.sheets)
        print(f"converted {base} -> {path} [{sheet_info}]")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    wbs = load_directory(args.dir)
    if not wbs:
        print(f"no .xlsx files found in {args.dir}")
        return 1
    specs = load_schema(args.schema)
    results = validate_all(wbs, specs)
    print(console_summary(results))
    write_markdown_report(results, args.report)
    print(f"report written to {args.report}")
    return 0 if all(r.ok for r in results.values()) else 1


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "convert":
        return _cmd_convert(args)
    if args.command == "validate":
        return _cmd_validate(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
