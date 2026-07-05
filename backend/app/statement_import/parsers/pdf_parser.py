import os

from app.statement_import.parsers.base import BaseParser
from app.statement_import.utils import (
    build_column_map,
    find_column,
    parse_date,
    resolve_debit_credit,
    clean_description,
)


class PDFParser(BaseParser):

    FORMAT = "pdf"
    ALLOWED_EXTENSIONS = {".pdf"}

    def __init__(self):
        self._pdfplumber = None

    def _get_library(self):
        if self._pdfplumber is not None:
            return self._pdfplumber
        try:
            import pdfplumber
            self._pdfplumber = pdfplumber
        except ImportError:
            raise ImportError(
                "pdfplumber is required to parse PDF files. "
                "Install it with: pip install pdfplumber"
            )
        return self._pdfplumber

    def _extract_tables(self, pdf):
        tables = []
        for page in pdf.pages:
            page_tables = page.extract_tables()
            for table in page_tables:
                if table and len(table) > 1:
                    tables.append(table)
        return tables

    def _merge_tables(self, tables):
        if not tables:
            return [], []
        headers = tables[0][0] if tables[0] else []
        merged = []
        for table in tables:
            if table and len(table) > 1:
                for row in table[1:]:
                    merged.append(row)
        return headers, merged

    def _open_pdf(self, file_path, password=None):
        pdfplumber = self._get_library()
        kwargs = {}
        if password:
            kwargs["password"] = password
        return pdfplumber.open(file_path, **kwargs)

    def detect_headers(self, file_path, password=None):
        pdfplumber = self._get_library()
        with self._open_pdf(file_path, password=password) as pdf:
            tables = self._extract_tables(pdf)
            if not tables:
                return []
            headers, _ = self._merge_tables(tables)
            return [str(h).strip() if h else "" for h in headers]

    def _extract_row(self, row, header_strs, mapping, row_index):
        date_str = row[mapping["date"]] if mapping.get("date") is not None and mapping["date"] < len(row) else None
        desc_str = row[mapping["description"]] if mapping.get("description") is not None and mapping["description"] < len(row) else None

        debit_str = None
        credit_str = None
        if mapping.get("debit") is not None and mapping["debit"] < len(row):
            debit_str = row[mapping["debit"]]
        if mapping.get("credit") is not None and mapping["credit"] < len(row):
            credit_str = row[mapping["credit"]]

        amount_str = None
        if mapping.get("amount") is not None and mapping["amount"] < len(row):
            amount_str = row[mapping["amount"]]

        ref = None
        if mapping.get("reference") is not None and mapping["reference"] < len(row):
            ref = row[mapping["reference"]]

        date = parse_date(str(date_str)) if date_str else None
        description = clean_description(str(desc_str)) if desc_str else None
        dc = resolve_debit_credit(debit_str, credit_str, amount_str)
        ref_num = str(ref).strip() if ref and str(ref).strip() else None

        raw = {}
        for j, h in enumerate(header_strs):
            raw[h] = row[j] if j < len(row) else ""

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

    def parse(self, file_path, password=None):
        pdfplumber = self._get_library()
        try:
            with self._open_pdf(file_path, password=password) as pdf:
                tables = self._extract_tables(pdf)
                num_pages = len(pdf.pages)
        except Exception as e:
            err_str = str(e).lower()
            if "password" in err_str or "encrypt" in err_str or "not a pdf" in err_str or "cannot be opened" in err_str:
                raise
            return self.build_result(
                [], self.FORMAT,
                metadata={"error": str(e), "total_pages": 0},
            )

        if not tables:
            return self.build_result(
                [], self.FORMAT,
                metadata={"detected_headers": [], "total_pages": num_pages},
            )

        headers, rows = self._merge_tables(tables)
        header_strs = [str(h).strip() if h else "" for h in headers]

        if not rows and pdfplumber:
            with self._open_pdf(file_path, password=password) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        for line in text.split("\n"):
                            line = line.strip()
                            if line:
                                rows.append([line])

        mapping = build_column_map(header_strs)

        transactions = []
        for i, row in enumerate(rows):
            row = [str(c).strip() if c else "" for c in row]
            if not any(c for c in row):
                continue
            tx = self._extract_row(row, header_strs, mapping, i)
            transactions.append(tx)

        return self.build_result(
            transactions,
            self.FORMAT,
            metadata={
                "detected_headers": header_strs,
                "total_pages": num_pages,
            },
        )

    def parse_stream(self, file_stream, password=None):
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_stream.read())
            tmp_path = tmp.name

        try:
            return self.parse(tmp_path, password=password)
        finally:
            os.unlink(tmp_path)
