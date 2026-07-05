from app.statement_import.categorizer.rule_based import RuleBasedCategorizer


class CategorizerRegistry:
    _categorizer = None

    @classmethod
    def get_categorizer(cls):
        if cls._categorizer is None:
            cls._categorizer = RuleBasedCategorizer()
        return cls._categorizer

    @classmethod
    def set_categorizer(cls, categorizer_instance):
        cls._categorizer = categorizer_instance

    @classmethod
    def categorize(cls, description):
        return cls.get_categorizer().categorize(description)

    @classmethod
    def categorize_batch(cls, descriptions):
        return cls.get_categorizer().categorize_batch(descriptions)
