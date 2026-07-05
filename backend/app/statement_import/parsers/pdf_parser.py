import os
import re

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

    def _parse_text_fallback(self, file_path, password=None):
        pdfplumber = self._get_library()
        with self._open_pdf(file_path, password=password) as pdf:
            all_text = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    all_text.append(t)
        full_text = "\n".join(all_text)

        date_pat = r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"
        amount_pat = r"([+-]?\s*[\d,]+\.\d{2})"

        transactions = []
        row_index = 0
        for line in full_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            dates = re.findall(date_pat, line)
            amounts = re.findall(amount_pat, line)
            if not dates or not amounts:
                continue
            date = parse_date(dates[0])
            if not date:
                continue
            desc = re.sub(date_pat, "", line, count=1).strip()
            for a in amounts:
                desc = desc.replace(a, "")
            desc = re.sub(r"\s{2,}", " ", desc).strip()
            desc = clean_description(desc)

            amount = None
            debit = None
            credit = None
            parsed = []
            for a_str in amounts:
                a = float(a_str.replace(",", ""))
                parsed.append(a)
            if len(parsed) == 1:
                a = parsed[0]
                if a < 0:
                    debit = abs(a)
                    amount = abs(a)
                else:
                    debit = a
                    amount = a
            elif len(parsed) >= 2:
                negs = [abs(a) for a in parsed if a < 0]
                poss = [a for a in parsed if a >= 0]
                if negs and len(negs) == 1:
                    debit = negs[0]
                    amount = negs[0]
                    if poss:
                        credit = poss[0]
                        amount = poss[0] if amount is None else max(amount, poss[0])
                elif len(poss) >= 2:
                    debit = poss[0]
                    amount = poss[0]
                    credit = None
                else:
                    debit = parsed[0] if parsed[0] >= 0 else abs(parsed[0])
                    amount = abs(parsed[0])

            tx = self.build_transaction(
                row_index=row_index,
                date=date,
                description=desc,
                debit=debit,
                credit=credit,
                amount=amount,
                reference_number=None,
                raw={"line": line},
            )
            transactions.append(tx)
            row_index += 1

        return transactions, {"parser_mode": "text_fallback"}

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

        headers, rows = self._merge_tables(tables) if tables else ([], [])
        header_strs = [str(h).strip() if h else "" for h in headers]

        mapping = build_column_map(header_strs)

        transactions = []
        for i, row in enumerate(rows):
            row = [str(c).strip() if c else "" for c in row]
            if not any(c for c in row):
                continue
            tx = self._extract_row(row, header_strs, mapping, i)
            transactions.append(tx)

        if not transactions:
            text_tx, extra_meta = self._parse_text_fallback(file_path, password=password)
            if text_tx:
                transactions = text_tx
                header_strs = ["text_fallback"]

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
