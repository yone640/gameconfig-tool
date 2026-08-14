# -*- coding: utf-8 -*-
"""Shared test helpers: build in-memory xlsx files."""
from __future__ import annotations

import os
import tempfile

from openpyxl import Workbook


def make_xlsx(rows_by_sheet, dirpath=None, filename="table.xlsx"):
    """Create a temp .xlsx; rows_by_sheet: {sheet_name: [header, ...rows]}."""
    wb = Workbook()
    wb.remove(wb.active)
    for name, rows in rows_by_sheet.items():
        ws = wb.create_sheet(title=name)
        for r in rows:
            ws.append(r)
    if dirpath is None:
        dirpath = tempfile.mkdtemp()
    path = os.path.join(dirpath, filename)
    wb.save(path)
    return path
