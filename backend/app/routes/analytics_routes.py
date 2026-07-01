"""
Analytics routes — /api/analytics/*
Endpoints: spending summaries, trends, DSA-engine insights.
"""

from flask import Blueprint

analytics_bp = Blueprint("analytics", __name__)
