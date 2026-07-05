from flask import Blueprint

import_bp = Blueprint("import", __name__)

from app.statement_import import routes  # noqa: E402, F401
