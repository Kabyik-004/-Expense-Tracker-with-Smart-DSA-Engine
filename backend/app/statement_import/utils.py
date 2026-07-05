import re
from datetime import datetime


DATE_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d/%m/%y",
    "%d-%m-%y",
    "%m/%d/%Y",
    "%m-%d-%Y",
    "%d %b %Y",
    "%d %B %Y",
    "%b %d %Y",
    "%B %d %Y",
    "%d-%b-%Y",
    "%d-%B-%Y",
    "%Y%m%d",
]

COLUMN_SIGNATURES = {
    "date": [
        "date", "transaction date", "txn date", "txn_date",
        "posting date", "value date", "value dated",
        "transaction_date", "posting_date", "value_date",
    ],
    "description": [
        "narration", "description", "particulars", "details",
        "remarks", "memo", "payee", "merchant", "transaction details",
        "transaction_description",
    ],
    "debit": [
        "debit", "debit amount", "debit_amt", "withdrawal",
        "withdrawal amt.", "withdrawal amount", "dr",
        "withdrawal_amt", "debit_amt",
    ],
    "credit": [
        "credit", "credit amount", "credit_amt", "deposit",
        "deposit amt.", "deposit amount", "cr",
        "deposit_amt", "credit_amt",
    ],
    "amount": [
        "amount", "transaction amount", "txn amount", "value",
        "sum", "total", "amount_inr", "transaction_amount",
    ],
    "reference": [
        "chq./ref.no.", "chq/ref no", "ref no./cheque no.",
        "cheque no.", "ref no", "chq./ref", "reference",
        "cheque number", "chq/ref", "ref number", "transaction ref",
        "ref_no", "cheque_no", "reference_number",
    ],
    "balance": [
        "balance", "closing balance", "running balance",
        "available balance", "closing_balance", "current balance",
    ],
    "type": [
        "type", "transaction type", "dr/cr", "debit/credit",
        "mode", "txn_type", "transaction_type",
    ],
}


def _normalise_header(name):
    return name.strip().lower().replace("_", " ").replace(".", "").replace("-", " ")


def find_column(headers, field):
    normalised = [_normalise_header(h) for h in headers]
    for sig in COLUMN_SIGNATURES.get(field, []):
        sig_normal = _normalise_header(sig)
        for i, h in enumerate(normalised):
            if h == sig_normal or h.startswith(sig_normal) or sig_normal in h:
                return i
    return None


def build_column_map(headers):
    return {
        field: find_column(headers, field)
        for field in COLUMN_SIGNATURES
    }


BANK_COLUMN_MAP = {
    "hdfc": {
        "date": "Date",
        "description": "Narration",
        "debit": "Withdrawal Amt.",
        "credit": "Deposit Amt.",
        "reference": "Chq./Ref.No.",
        "balance": "Closing Balance",
    },
    "icici": {
        "date": "Date",
        "description": "Narration",
        "debit": "Debit",
        "credit": "Credit",
        "reference": "Ref No./Cheque No.",
        "balance": "Balance",
    },
    "sbi": {
        "date": "Txn Date",
        "description": "Description",
        "debit": "Debit",
        "credit": "Credit",
        "reference": "Ref No./Cheque No.",
        "balance": "Balance",
    },
    "axis": {
        "date": "Transaction Date",
        "description": "Description",
        "debit": "Debit",
        "credit": "Credit",
        "reference": "Cheque No.",
        "balance": "Balance",
    },
    "kotak": {
        "date": "Date",
        "description": "Narration",
        "debit": "Withdrawal",
        "credit": "Deposit",
        "reference": "Chq/Ref No",
        "balance": "Balance",
    },
    "yes": {
        "date": "Transaction Date",
        "description": "Particulars",
        "debit": "Debit",
        "credit": "Credit",
        "reference": None,
        "balance": None,
    },
}


def resolve_bank_name(bank_id):
    from app.statement_import.parser import SUPPORTED_BANKS
    for bank in SUPPORTED_BANKS:
        if bank["id"] == bank_id:
            return bank["name"]
    return bank_id


def parse_date(date_str):
    if not date_str or not isinstance(date_str, str):
        return None
    cleaned = date_str.strip()
    if not cleaned:
        return None
    cleaned = re.sub(r'\s+', ' ', cleaned)
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_amount(amount_str):
    if amount_str is None:
        return None
    if isinstance(amount_str, (int, float)):
        return round(float(amount_str), 2)
    cleaned = str(amount_str).strip().upper()
    if not cleaned:
        return None
    cleaned = cleaned.replace(",", "").replace(" ", "")
    negative = False
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = cleaned[1:-1]
        negative = True
    if cleaned.startswith("-"):
        cleaned = cleaned[1:]
        negative = True
    try:
        val = float(cleaned)
        if negative:
            val = -val
        return round(val, 2)
    except (ValueError, TypeError):
        return None


def resolve_debit_credit(debit_val, credit_val, amount_val):
    debit = parse_amount(debit_val)
    credit = parse_amount(credit_val)

    if debit is not None and credit is not None:
        if debit > 0 and credit == 0:
            return {"debit": debit, "credit": 0.0, "amount": debit}
        if credit > 0 and debit == 0:
            return {"debit": 0.0, "credit": credit, "amount": credit}
        return {"debit": debit, "credit": credit, "amount": max(debit, credit)}

    if debit is not None and debit > 0:
        return {"debit": debit, "credit": 0.0, "amount": debit}

    if credit is not None and credit > 0:
        return {"debit": 0.0, "credit": credit, "amount": credit}

    if amount_val is not None:
        parsed = parse_amount(amount_val)
        if parsed is not None:
            if parsed < 0:
                return {"debit": abs(parsed), "credit": 0.0, "amount": abs(parsed)}
            return {"debit": 0.0, "credit": parsed, "amount": parsed}

    return {"debit": None, "credit": None, "amount": None}


def extract_cell(row_dict, key, headers_map):
    idx = headers_map.get(key)
    if idx is None:
        return None
    values = list(row_dict.values())
    if idx < len(values):
        return values[idx]
    return None


def extract_cell_by_name(row_dict, column_name):
    if column_name is None:
        return None
    return row_dict.get(column_name)


def clean_description(desc_str):
    if not desc_str or not isinstance(desc_str, str):
        return ""
    return re.sub(r'\s+', ' ', desc_str.strip())
