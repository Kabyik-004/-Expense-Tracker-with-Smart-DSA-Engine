from abc import ABC, abstractmethod


class BaseParser(ABC):

    FORMAT = None
    ALLOWED_EXTENSIONS = set()

    @abstractmethod
    def parse(self, file_path):
        pass

    @abstractmethod
    def parse_stream(self, file_stream):
        pass

    @abstractmethod
    def detect_headers(self, file_path):
        pass

    def empty_transaction(self, row_index, raw, errors=None):
        return {
            "row_index": row_index,
            "valid": False,
            "date": None,
            "description": None,
            "amount": None,
            "credit": None,
            "debit": None,
            "reference_number": None,
            "errors": errors or ["Unknown error"],
            "raw": raw,
        }

    def build_transaction(self, row_index, date, description, debit, credit, amount, reference_number, raw):
        errors = []
        if date is None:
            errors.append("Missing or unparseable date")
        if description is None or not description.strip():
            errors.append("Missing description")
        if amount is None:
            errors.append("Could not determine amount")

        valid = len(errors) == 0
        return {
            "row_index": row_index,
            "valid": valid,
            "date": date,
            "description": (description or "").strip(),
            "amount": amount,
            "credit": credit,
            "debit": debit,
            "reference_number": reference_number,
            "errors": errors if errors else None,
            "raw": raw,
        }

    def build_result(self, transactions, parser_name, metadata=None):
        total = len(transactions)
        valid = [t for t in transactions if t.get("valid")]
        invalid = [t for t in transactions if not t.get("valid")]

        report = {
            "total_rows": total,
            "valid_rows": len(valid),
            "invalid_rows": len(invalid),
            "errors": [
                {"row": t["row_index"], "errors": t.get("errors", [])}
                for t in invalid
            ],
        }

        result = {
            "transactions": valid,
            "report": report,
            "metadata": {
                "parser": parser_name,
                "detected_bank": None,
                "detected_headers": None,
            },
        }
        if metadata:
            result["metadata"].update(metadata)
        return result
