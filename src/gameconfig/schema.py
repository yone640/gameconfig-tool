# -*- coding: utf-8 -*-
"""Schema parsing and per-cell validation rules."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TableSpec:
    """Spec for one table (sheet)."""
    name: str
    columns: List[str] = field(default_factory=list)
    types: Dict[str, str] = field(default_factory=dict)       # col -> int|float|str|bool
    required: List[str] = field(default_factory=list)
    unique: List[str] = field(default_factory=list)           # column name or list of columns
    enums: Dict[str, List[str]] = field(default_factory=dict)  # col -> allowed values
    ranges: Dict[str, Dict[str, float]] = field(default_factory=dict)  # col -> {min,max}
    refs: List[Dict[str, str]] = field(default_factory=list)  # [{column, table, key}]


def load_schema(path: str) -> Dict[str, TableSpec]:
    """Load schema.json into {sheet_name: TableSpec}."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    specs: Dict[str, TableSpec] = {}
    for name, cfg in raw.items():
        specs[name] = TableSpec(
            name=name,
            columns=cfg.get("columns", []),
            types=cfg.get("types", {}),
            required=cfg.get("required", []),
            unique=cfg.get("unique", []),
            enums=cfg.get("enums", {}),
            ranges=cfg.get("ranges", {}),
            refs=cfg.get("refs", []),
        )
    return specs


def coerce(value: Any, type_name: str) -> Any:
    """Coerce a raw cell value to the declared type; raises ValueError."""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        raise ValueError("empty value")
    if type_name == "int":
        if isinstance(value, bool):
            raise ValueError(f"expected int, got bool")
        return int(float(value))
    if type_name == "float":
        return float(value)
    if type_name == "str":
        return str(value).strip()
    if type_name == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            low = value.strip().lower()
            if low in ("true", "1", "yes"):
                return True
            if low in ("false", "0", "no"):
                return False
        raise ValueError(f"expected bool, got {value!r}")
    raise ValueError(f"unknown type {type_name!r}")
