import csv
import os

from app.statement_import.parsers.base import BaseParser
from app.statement_import.utils import (
    BANK_COLUMN_MAP,
    build_column_map,
    find_column,
    parse_date,
    resolve_debit_credit,
    clean_description,
    extract_cell_by_name,
)


class CSVParser(BaseParser):

    FORMAT = "csv"
    ALLOWED_EXTENSIONS = {".csv"}
    SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

    def _detect_encoding(self, file_path):
        import chardet

        with open(file_path, "rb") as f:
            raw = f.read(8192)
        result = chardet.detect(raw)
        return result.get("encoding", "utf-8")

    def _read_rows(self, file_path, encoding=None):
        if encoding is None:
            encoding = self._detect_encoding(file_path)
        with open(file_path, encoding=encoding, newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        return rows

    def _read_dicts(self, file_path, encoding=None):
        if encoding is None:
            encoding = self._detect_encoding(file_path)
        with open(file_path, encoding=encoding, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return rows

    def detect_headers(self, file_path):
        rows = self._read_rows(file_path)
        if not rows:
            return []
        return [h.strip() for h in rows[0]]

    def _build_mapping(self, headers, bank_id):
        bank_map = BANK_COLUMN_MAP.get(bank_id)
        if bank_map:
            mapping = {}
            for field, col_name in bank_map.items():
                if col_name:
                    mapping[field] = find_column(headers, field)
            return mapping
        return build_column_map(headers)

    def _extract_row(self, row_dict, headers, mapping, row_index):
        date_str = extract_cell_by_name(row_dict, headers[mapping["date"]]) if mapping.get("date") is not None and mapping["date"] < len(headers) else None
        desc_str = extract_cell_by_name(row_dict, headers[mapping["description"]]) if mapping.get("description") is not None and mapping["description"] < len(headers) else None

        debit_str = None
        credit_str = None
        if mapping.get("debit") is not None and mapping["debit"] < len(headers):
            debit_str = extract_cell_by_name(row_dict, headers[mapping["debit"]])
        if mapping.get("credit") is not None and mapping["credit"] < len(headers):
            credit_str = extract_cell_by_name(row_dict, headers[mapping["credit"]])

        amount_str = None
        if mapping.get("amount") is not None and mapping["amount"] < len(headers):
            amount_str = extract_cell_by_name(row_dict, headers[mapping["amount"]])

        ref = None
        if mapping.get("reference") is not None and mapping["reference"] < len(headers):
            ref = extract_cell_by_name(row_dict, headers[mapping["reference"]])

        date = parse_date(date_str)
        description = clean_description(desc_str)
        dc = resolve_debit_credit(debit_str, credit_str, amount_str)
        ref_num = str(ref).strip() if ref and str(ref).strip() else None

        return self.build_transaction(
            row_index=row_index,
            date=date,
            description=description,
            debit=dc["debit"],
            credit=dc["credit"],
            amount=dc["amount"],
            reference_number=ref_num,
            raw=dict(row_dict),
        )

    def _extract_stream_row(self, row_dict, row_index):
        keys = list(row_dict.keys())
        mapping = build_column_map(keys)

        date_str = row_dict.get(keys[mapping["date"]]) if mapping.get("date") is not None and mapping["date"] < len(keys) else None
        desc_str = row_dict.get(keys[mapping["description"]]) if mapping.get("description") is not None and mapping["description"] < len(keys) else None

        debit_str = None
        credit_str = None
        if mapping.get("debit") is not None and mapping["debit"] < len(keys):
            debit_str = row_dict.get(keys[mapping["debit"]])
        if mapping.get("credit") is not None and mapping["credit"] < len(keys):
            credit_str = row_dict.get(keys[mapping["credit"]])

        amount_str = None
        if mapping.get("amount") is not None and mapping["amount"] < len(keys):
            amount_str = row_dict.get(keys[mapping["amount"]])

        ref = None
        if mapping.get("reference") is not None and mapping["reference"] < len(keys):
            ref = row_dict.get(keys[mapping["reference"]])

        date = parse_date(date_str)
        description = clean_description(desc_str)
        dc = resolve_debit_credit(debit_str, credit_str, amount_str)
        ref_num = str(ref).strip() if ref and str(ref).strip() else None

        return self.build_transaction(
            row_index=row_index,
            date=date,
            description=description,
            debit=dc["debit"],
            credit=dc["credit"],
            amount=dc["amount"],
            reference_number=ref_num,
            raw=dict(row_dict),
        )

    def parse(self, file_path):
        raw_rows = self._read_rows(file_path)
        if not raw_rows:
            return self.build_result([], self.FORMAT)

        headers = [h.strip() for h in raw_rows[0]]
        data_rows = raw_rows[1:]

        bank = _detect_bank_by_headers(headers)
        bank_id = bank["id"] if bank else None
        mapping = self._build_mapping(headers, bank_id)

        transactions = []
        for i, row in enumerate(data_rows):
            if not row or not any(cell.strip() for cell in row):
                continue
            row_dict = {}
            for j, h in enumerate(headers):
                row_dict[h] = row[j].strip() if j < len(row) else ""
            tx = self._extract_row(row_dict, headers, mapping, i)
            transactions.append(tx)

        return self.build_result(
            transactions,
            self.FORMAT,
            metadata={
                "detected_bank": bank_id,
                "detected_headers": headers,
            },
        )

    def parse_stream(self, file_stream):
        import codecs

        reader = csv.DictReader(codecs.getreader("utf-8-sig")(file_stream))
        rows = list(reader)
        if not rows:
            return self.build_result([], self.FORMAT)

        transactions = []
        for i, row in enumerate(rows):
            if not any(v.strip() for v in row.values() if v):
                continue
            tx = self._extract_stream_row(row, i)
            transactions.append(tx)

        return self.build_result(transactions, self.FORMAT)


_SUPPORTED_BANK_HEADERS = [
    {
        "id": "hdfc",
        "name": "HDFC Bank",
        "headers": ["Date", "Narration", "Chq./Ref.No.", "Value Dated", "Withdrawal Amt.", "Deposit Amt.", "Closing Balance"],
    },
    {
        "id": "icici",
        "name": "ICICI Bank",
        "headers": ["Date", "Value Date", "Narration", "Ref No./Cheque No.", "Debit", "Credit", "Balance"],
    },
    {
        "id": "sbi",
        "name": "State Bank of India",
        "headers": ["Txn Date", "Value Date", "Description", "Ref No./Cheque No.", "Debit", "Credit", "Balance"],
    },
    {
        "id": "axis",
        "name": "Axis Bank",
        "headers": ["Transaction Date", "Value Date", "Description", "Cheque No.", "Debit", "Credit", "Balance"],
    },
    {
        "id": "kotak",
        "name": "Kotak Mahindra Bank",
        "headers": ["Date", "Narration", "Chq/Ref No", "Value Dt", "Withdrawal", "Deposit", "Balance"],
    },
    {
        "id": "yes",
        "name": "Yes Bank",
        "headers": ["Transaction Date", "Particulars", "Debit", "Credit", "Balance"],
    },
]


def _detect_bank_by_headers(headers):
    normalized_input = [h.strip().lower() for h in headers]
    for bank in _SUPPORTED_BANK_HEADERS:
        normalized_bank = [h.lower() for h in bank["headers"]]
        if normalized_input == normalized_bank:
            return bank
        score = sum(1 for h in normalized_bank if h in normalized_input)
        if score >= len(normalized_bank) * 0.7:
            return bank
    return None
