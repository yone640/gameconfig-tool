# -*- coding: utf-8 -*-
"""Validator: check config tables against schema rules.

Reference-integrity checks use a GLOBAL index built across every workbook in
the directory, so cross-file references (heroes.xlsx -> items.xlsx) work.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .loader import WorkbookData
from .schema import TableSpec, coerce


@dataclass
class Issue:
    level: str          # "error" | "warning"
    rule: str           # e.g. "required", "unique", "type", "enum", "range", "ref"
    sheet: str
    row: int            # 1-based data row number in the source sheet
    column: str
    message: str


@dataclass
class ValidationResult:
    issues: List[Issue] = field(default_factory=list)

    @property
    def errors(self) -> List[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False


def _unique_columns(spec: TableSpec) -> List[str]:
    if isinstance(spec.unique, list):
        return list(spec.unique)
    return [spec.unique] if spec.unique else []


def _collect_indexes(wbs: List[WorkbookData], specs: Dict[str, TableSpec]) -> Tuple[
        Dict[str, Dict[str, Tuple[str, int]]], Dict[str, List[Issue]]]:
    """Build {sheet -> {unique_key -> (file_path, row)}} and per-file duplicate issues."""
    index: Dict[str, Dict[str, Tuple[str, int]]] = {}
    per_file: Dict[str, List[Issue]] = {wb.path: [] for wb in wbs}
    for wb in wbs:
        for sheet in wb.sheets:
            spec = specs.get(sheet.name)
            if not spec:
                continue
            cols = _unique_columns(spec)
            if not cols:
                continue
            table_idx = index.setdefault(sheet.name, {})
            for row_no, row in enumerate(sheet.rows, start=2):
                key_parts = [repr(row[c]) for c in cols if c in row]
                if not key_parts:
                    continue
                key = "|".join(key_parts)
                if key in table_idx:
                    prev_file, prev_row = table_idx[key]
                    per_file[wb.path].append(Issue(
                        "error", "unique", sheet.name, row_no, ",".join(cols),
                        f"duplicate unique key {key!r} (first seen in "
                        f"{os.path.basename(prev_file)} row {prev_row})"))
                else:
                    table_idx[key] = (wb.path, row_no)
    return index, per_file


def validate_all(wbs: List[WorkbookData], specs: Dict[str, TableSpec]) -> Dict[str, ValidationResult]:
    """Validate every workbook; returns {file_path: ValidationResult}."""
    index, unique_issues = _collect_indexes(wbs, specs)
    results: Dict[str, ValidationResult] = {}
    for wb in wbs:
        issues: List[Issue] = list(unique_issues.get(wb.path, []))
        for sheet in wb.sheets:
            spec = specs.get(sheet.name)
            if not spec:
                continue
            for row_no, row in enumerate(sheet.rows, start=2):
                for col, raw in row.items():
                    if spec.columns and col not in spec.columns:
                        continue
                    # required
                    if col in spec.required and _is_blank(raw):
                        issues.append(Issue(
                            "error", "required", sheet.name, row_no, col,
                            "required column is empty"))
                    # type
                    if col in spec.types and not _is_blank(raw):
                        try:
                            coerce(raw, spec.types[col])
                        except ValueError as e:
                            issues.append(Issue(
                                "error", "type", sheet.name, row_no, col,
                                f"type mismatch: {e}"))
                    # enum
                    if col in spec.enums and not _is_blank(raw):
                        allowed = spec.enums[col]
                        raw_str = str(raw).strip()
                        if raw_str not in allowed:
                            issues.append(Issue(
                                "error", "enum", sheet.name, row_no, col,
                                f"value {raw_str!r} not in {allowed}"))
                    # range
                    if col in spec.ranges and not _is_blank(raw):
                        try:
                            v = float(raw)
                            rng = spec.ranges[col]
                            if "min" in rng and v < rng["min"]:
                                issues.append(Issue(
                                    "error", "range", sheet.name, row_no, col,
                                    f"value {v} below min {rng['min']}"))
                            if "max" in rng and v > rng["max"]:
                                issues.append(Issue(
                                    "error", "range", sheet.name, row_no, col,
                                    f"value {v} above max {rng['max']}"))
                        except (TypeError, ValueError):
                            pass  # non-numeric handled by type rule
                    # reference integrity (global index)
                    for ref in spec.refs:
                        if ref.get("column") == col and not _is_blank(raw):
                            target_index = index.get(ref.get("table", ""))
                            key_str = str(raw).strip()
                            if target_index is None:
                                if ref.get("table") in specs:
                                    issues.append(Issue(
                                        "error", "ref", sheet.name, row_no, col,
                                        f"referenced table {ref.get('table')!r} has no rows in any workbook"))
                                else:
                                    issues.append(Issue(
                                        "warning", "ref", sheet.name, row_no, col,
                                        f"referenced table {ref.get('table')!r} has no spec"))
                            elif key_str not in target_index:
                                issues.append(Issue(
                                    "error", "ref", sheet.name, row_no, col,
                                    f"dangling reference: {key_str!r} not found in {ref.get('table')}"))
        results[wb.path] = ValidationResult(issues=issues)
    return results
