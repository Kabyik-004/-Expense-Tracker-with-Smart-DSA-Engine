import os

from app.statement_import.parsers.csv_parser import CSVParser
from app.statement_import.parsers.pdf_parser import PDFParser
from app.statement_import.parsers.excel_parser import ExcelParser


class ParserRegistry:
    _parsers = {}
    _initialized = False

    @classmethod
    def _init(cls):
        if cls._initialized:
            return
        cls.register(CSVParser())
        cls.register(PDFParser())
        cls.register(ExcelParser())
        cls._initialized = True

    @classmethod
    def register(cls, parser_instance):
        for ext in parser_instance.ALLOWED_EXTENSIONS:
            cls._parsers[ext.lower()] = parser_instance

    @classmethod
    def get_parser(cls, file_path):
        cls._init()
        ext = os.path.splitext(file_path)[1].lower()
        parser = cls._parsers.get(ext)
        if parser is None:
            allowed = ", ".join(sorted(cls._parsers.keys()))
            raise ValueError(
                f"No parser registered for extension '{ext}'. "
                f"Supported extensions: {allowed}"
            )
        return parser

    @classmethod
    def get_supported_extensions(cls):
        cls._init()
        return set(cls._parsers.keys())

    @classmethod
    def list_parsers(cls):
        cls._init()
        seen = set()
        result = []
        for ext, parser in cls._parsers.items():
            parser_cls = type(parser).__name__
            if parser_cls not in seen:
                seen.add(parser_cls)
                result.append({
                    "name": parser_cls,
                    "format": parser.FORMAT,
                    "extensions": sorted(parser.ALLOWED_EXTENSIONS),
                })
        return result

    @classmethod
    def register_bank_parser(cls, bank_id, extension, parser_instance):
        cls._init()
        key = f"bank:{bank_id}:{extension.lower()}"
        cls._parsers[key] = parser_instance
