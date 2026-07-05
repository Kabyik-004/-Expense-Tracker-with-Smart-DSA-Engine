from app.statement_import.parsers.registry import ParserRegistry
from app.statement_import.categorizer import CategorizerRegistry


def parse_file(file_path, categorize=True, password=None):
    try:
        parser = ParserRegistry.get_parser(file_path)
        result = parser.parse(file_path, password=password)
    except Exception as e:
        return {"error": f"Failed to parse file: {e}", "transactions": [], "report": {}, "metadata": {}}
    if categorize:
        try:
            _categorize_result(result)
        except Exception as e:
            result["error"] = f"Categorization failed: {e}"
    return result


def parse_stream(file_stream, filename, categorize=True):
    parser = ParserRegistry.get_parser(filename)
    result = parser.parse_stream(file_stream)
    if categorize:
        _categorize_result(result)
    return result


def categorize_transaction(description):
    return CategorizerRegistry.categorize(description)


def categorize_transactions(descriptions):
    return CategorizerRegistry.categorize_batch(descriptions)


def _categorize_result(parse_result):
    for tx in parse_result.get("transactions", []):
        desc = tx.get("description", "")
        result = CategorizerRegistry.categorize(desc)
        tx["suggested_category"] = result.category_name
        tx["category_confidence"] = result.confidence
        tx["category_method"] = result.method
    # also add categorization summary to report
    report = parse_result.get("report", {})
    categories = {}
    for tx in parse_result.get("transactions", []):
        cat = tx.get("suggested_category", "Other")
        categories[cat] = categories.get(cat, 0) + 1
    report["category_summary"] = categories


def detect_headers(file_path):
    parser = ParserRegistry.get_parser(file_path)
    return parser.detect_headers(file_path)


def get_supported_extensions():
    return ParserRegistry.get_supported_extensions()


def list_parsers():
    return ParserRegistry.list_parsers()


def register_bank_parser(bank_id, extension, parser_instance):
    ParserRegistry.register_bank_parser(bank_id, extension, parser_instance)


SUPPORTED_BANKS = [
    {
        "id": "hdfc",
        "name": "HDFC Bank",
        "formats": ["CSV"],
        "headers": ["Date", "Narration", "Chq./Ref.No.", "Value Dated", "Withdrawal Amt.", "Deposit Amt.", "Closing Balance"],
    },
    {
        "id": "icici",
        "name": "ICICI Bank",
        "formats": ["CSV"],
        "headers": ["Date", "Value Date", "Narration", "Ref No./Cheque No.", "Debit", "Credit", "Balance"],
    },
    {
        "id": "sbi",
        "name": "State Bank of India",
        "formats": ["CSV"],
        "headers": ["Txn Date", "Value Date", "Description", "Ref No./Cheque No.", "Debit", "Credit", "Balance"],
    },
    {
        "id": "axis",
        "name": "Axis Bank",
        "formats": ["CSV"],
        "headers": ["Transaction Date", "Value Date", "Description", "Cheque No.", "Debit", "Credit", "Balance"],
    },
    {
        "id": "kotak",
        "name": "Kotak Mahindra Bank",
        "formats": ["CSV"],
        "headers": ["Date", "Narration", "Chq/Ref No", "Value Dt", "Withdrawal", "Deposit", "Balance"],
    },
    {
        "id": "yes",
        "name": "Yes Bank",
        "formats": ["CSV"],
        "headers": ["Transaction Date", "Particulars", "Debit", "Credit", "Balance"],
    },
]

ALLOWED_EXTENSIONS = {".csv", ".pdf", ".xlsx", ".xls"}
MAX_FILE_SIZE = 15 * 1024 * 1024

FORMAT_MAP = {
    ".csv": "csv",
    ".pdf": "pdf",
    ".xlsx": "xlsx",
    ".xls": "xls",
}


def get_supported_banks():
    return SUPPORTED_BANKS
