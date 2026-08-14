# -*- coding: utf-8 -*-
"""Excel -> JSON converter with type coercion."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .loader import WorkbookData
from .schema import TableSpec, coerce


def convert_workbook(wb: WorkbookData, specs: Dict[str, TableSpec]) -> Dict[str, Any]:
    """Convert each sheet to a JSON-serializable structure.

    Returns {sheet_name: {"columns": [...], "rows": [ {col: value}, ... ]}}.
    Values are coerced to declared types when a spec exists; otherwise kept raw.
    """
    result: Dict[str, Any] = {}
    for sheet in wb.sheets:
        spec = specs.get(sheet.name)
        converted_rows = []
        for row in sheet.rows:
            out_row: Dict[str, Any] = {}
            for col, val in row.items():
                if spec and col in spec.types:
                    out_row[col] = coerce(val, spec.types[col])
                else:
                    out_row[col] = val
            converted_rows.append(out_row)
        result[sheet.name] = {"columns": sheet.columns, "rows": converted_rows}
    return result


def write_json(data: Dict[str, Any], out_dir: str, filename: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path
