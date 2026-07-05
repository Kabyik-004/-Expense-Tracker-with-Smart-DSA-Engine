import os

from app.statement_import.parsers.base import BaseParser
from app.statement_import.utils import (
    build_column_map,
    parse_date,
    resolve_debit_credit,
    clean_description,
)


class ExcelParser(BaseParser):

    FORMAT = "excel"
    ALLOWED_EXTENSIONS = {".xlsx", ".xls"}

    def __init__(self):
        self._openpyxl = None
        self._xlrd = None

    def _get_openpyxl(self):
        if self._openpyxl is not None:
            return self._openpyxl
        try:
            import openpyxl
            self._openpyxl = openpyxl
        except ImportError:
            raise ImportError(
                "openpyxl is required to parse .xlsx files. "
                "Install it with: pip install openpyxl"
            )
        return self._openpyxl

    def _get_xlrd(self):
        if self._xlrd is not None:
            return self._xlrd
        try:
            import xlrd
            self._xlrd = xlrd
        except ImportError:
            raise ImportError(
                "xlrd is required to parse .xls files. "
                "Install it with: pip install xlrd"
            )
        return self._xlrd

    def _is_xlsx(self, file_path):
        return file_path.lower().endswith(".xlsx")

    def _parse_xlsx(self, file_path):
        openpyxl = self._get_openpyxl()
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        wb.close()
        return rows

    def _parse_xls(self, file_path):
        xlrd = self._get_xlrd()
        wb = xlrd.open_workbook(file_path)
        ws = wb.sheet_by_index(0)
        rows = []
        for row_idx in range(ws.nrows):
            rows.append(list(ws.row_values(row_idx)))
        return rows

    def _cell_str(self, cell):
        if cell is None:
            return ""
        if isinstance(cell, float):
            if cell == int(cell):
                return str(int(cell))
            return str(cell)
        return str(cell).strip()

    def detect_headers(self, file_path):
        if self._is_xlsx(file_path):
            rows = self._parse_xlsx(file_path)
        else:
            rows = self._parse_xls(file_path)
        if not rows:
            return []
        return [self._cell_str(c) for c in rows[0]]

    def _extract_row(self, row_strs, headers, mapping, row_index):
        date_str = row_strs[mapping["date"]] if mapping.get("date") is not None and mapping["date"] < len(row_strs) else None
        desc_str = row_strs[mapping["description"]] if mapping.get("description") is not None and mapping["description"] < len(row_strs) else None

        debit_str = None
        credit_str = None
        if mapping.get("debit") is not None and mapping["debit"] < len(row_strs):
            debit_str = row_strs[mapping["debit"]]
        if mapping.get("credit") is not None and mapping["credit"] < len(row_strs):
            credit_str = row_strs[mapping["credit"]]

        amount_str = None
        if mapping.get("amount") is not None and mapping["amount"] < len(row_strs):
            amount_str = row_strs[mapping["amount"]]

        ref = None
        if mapping.get("reference") is not None and mapping["reference"] < len(row_strs):
            ref = row_strs[mapping["reference"]]

        date = parse_date(date_str) if date_str else None
        description = clean_description(desc_str) if desc_str else None
        dc = resolve_debit_credit(debit_str, credit_str, amount_str)
        ref_num = str(ref).strip() if ref and str(ref).strip() else None

        raw = {}
        for j, h in enumerate(headers):
            raw[h] = row_strs[j] if j < len(row_strs) else ""

        return self.build_transaction(
            row_index=row_index,
            date=date,
            description=description,
            debit=dc["debit"],
            credit=dc["credit"],
            amount=dc["amount"],
            reference_number=ref_num,
            raw=raw,
        )

    def parse(self, file_path):
        if self._is_xlsx(file_path):
            rows = self._parse_xlsx(file_path)
        else:
            rows = self._parse_xls(file_path)

        if not rows:
            return self.build_result([], self.FORMAT)

        headers = [self._cell_str(c) for c in rows[0]]
        data_rows = rows[1:]

        mapping = build_column_map(headers)

        transactions = []
        for i, row in enumerate(data_rows):
            row_strs = [self._cell_str(c) for c in row]
            if not any(c for c in row_strs):
                continue
            tx = self._extract_row(row_strs, headers, mapping, i)
            transactions.append(tx)

        return self.build_result(
            transactions,
            self.FORMAT,
            metadata={"detected_headers": headers},
        )

    def parse_stream(self, file_stream):
        import tempfile

        ext = ".xlsx"
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(file_stream.read())
            tmp_path = tmp.name

        try:
            return self.parse(tmp_path)
        finally:
            os.unlink(tmp_path)
