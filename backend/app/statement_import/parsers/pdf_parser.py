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

    def _extract_all_text(self, pdf):
        for page in pdf.pages:
            t = page.extract_text(x_tolerance=3, y_tolerance=3)
            if t:
                return t, "tolerance"
        for page in pdf.pages:
            t = page.extract_text(layout=True)
            if t:
                return t, "layout"
        for page in pdf.pages:
            words = page.extract_words(x_tolerance=3)
            if words:
                lines = {}
                for w in words:
                    line_key = round(w["top"], 0)
                    lines.setdefault(line_key, []).append(w["text"])
                text = "\n".join(" ".join(lines[k]) for k in sorted(lines))
                return text, "words"
        return "", None

    def _parse_text_fallback(self, file_path, password=None):
        pdfplumber = self._get_library()
        with self._open_pdf(file_path, password=password) as pdf:
            full_text, _ = self._extract_all_text(pdf)

        if not full_text.strip():
            return [], {"parser_mode": "text_fallback", "error": "No extractable text found in PDF"}

        date_pat = r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"
        date_text_pat = r"\b(\d{1,2}[/-][A-Za-z]{3}[/-]\d{2,4})\b"
        amount_pat = r"([+-]?\s*[\d,]+\.\d{1,2})"

        header_keywords = {"date", "narration", "description", "particulars", "debit", "credit",
                           "deposit", "withdrawal", "balance", "closing", "chq", "ref", "transaction",
                           "opening", "value dated", "page", "statement"}

        lines = [l.strip() for l in full_text.split("\n") if l.strip()]

        groups = []
        current = []
        for line in lines:
            has_date = bool(re.findall(date_pat, line) or re.findall(date_text_pat, line))
            low = line.lower()
            is_header = sum(1 for kw in header_keywords if kw in low) >= 3 or len(line.split()) <= 1
            if has_date and not is_header and current:
                groups.append(current)
                current = [line]
            elif has_date and not is_header:
                current = [line]
            elif current:
                current.append(line)
        if current:
            groups.append(current)

        transactions = []
        row_index = 0
        for group in groups:
            amount_line = None
            desc_lines = []
            for line in reversed(group):
                amounts = re.findall(amount_pat, line)
                if amounts:
                    amount_line = line
                    break
                desc_lines.insert(0, line)
            if amount_line is None:
                continue
            amounts = re.findall(amount_pat, amount_line)
            if not amounts:
                continue

            desc = " ".join(desc_lines) if desc_lines else " ".join(group)
            desc = re.sub(r"\s{2,}", " ", desc).strip()

            date_str = (re.findall(date_pat, group[0]) or re.findall(date_text_pat, group[0]))[0]
            date = parse_date(date_str)
            if not date:
                continue

            for a in amounts:
                desc = desc.replace(a, "")
            for pat in (date_pat, date_text_pat):
                desc = re.sub(pat, "", desc, count=1)
            desc = re.sub(r"\s{2,}", " ", desc).strip()
            desc = clean_description(desc)

            vals = [float(a.replace(",", "")) for a in amounts]
            debit = None
            credit = None
            amount = None

            if len(vals) == 1:
                a = vals[0]
                if a < 0:
                    debit = abs(a)
                    amount = abs(a)
                else:
                    debit = a
                    amount = a
            elif len(vals) == 2:
                tx_val = vals[0]
                if tx_val < 0:
                    debit = abs(tx_val)
                else:
                    debit = tx_val
                amount = abs(tx_val)
            else:
                tx_vals = vals[:-1]
                for v in tx_vals:
                    if v < 0:
                        debit = abs(v)
                    else:
                        credit = v
                amount = max(abs(v) for v in tx_vals) if tx_vals else abs(vals[-1])

            tx = self.build_transaction(
                row_index=row_index,
                date=date,
                description=desc,
                debit=debit,
                credit=credit,
                amount=amount,
                reference_number=None,
                raw={"group": group},
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

        if not transactions or not any(t.get("valid") for t in transactions):
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
