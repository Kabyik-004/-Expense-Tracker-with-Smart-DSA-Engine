"""
Analytics routes — /api/analytics/*
Endpoints: spending summaries, trends, DSA-engine insights.
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.controllers.analytics_controller import (
    analytics_overview,
    category_analytics,
    time_series_analytics,
    dashboard_analytics,
)

analytics_bp = Blueprint("analytics", __name__)


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================


@analytics_bp.route("/overview", methods=["GET"])
@jwt_required()
def get_overview():
    """
    Get analytics overview: totals, balance, extremes.
    
    Returns:
    - total_expense: Sum of all expenses
    - total_income: Sum of all income
    - balance: Income - Expense
    - highest_expense: Largest single expense
    - lowest_expense: Smallest single expense
    - average_expense: Average expense amount
    
    Time Complexity: O(n) - scans all expenses
    """
    user_id = int(get_jwt_identity())
    return analytics_overview(user_id)


@analytics_bp.route("/categories", methods=["GET"])
@jwt_required()
def get_category_analysis():
    """
    Get category breakdown: most used, top 5, distribution.
    
    Returns:
    - most_used_category: Category with most expenses
    - top_5_categories: Top 5 by total amount
    - category_distribution: All categories with percentages
    
    Time Complexity: O(n) - aggregates all expenses
    """
    user_id = int(get_jwt_identity())
    return category_analytics(user_id)


@analytics_bp.route("/time-series", methods=["GET"])
@jwt_required()
def get_time_series():
    """
    Get time-based breakdown: daily, weekly, monthly.
    
    Returns:
    - daily: {YYYY-MM-DD: {total, count}}
    - weekly: {YYYY-Www: {total, count}}
    - monthly: {YYYY-MM: {total, count}}
    
    Time Complexity: O(n) - groups all expenses by time
    """
    user_id = int(get_jwt_identity())
    return time_series_analytics(user_id)


@analytics_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard():
    """
    Get complete analytics dashboard with all metrics.
    
    Returns:
    - summary: total_expense, total_income, balance
    - extremes: highest, lowest, average expense
    - categories: most_used, top_5, distribution
    - time_series: daily, weekly, monthly breakdown
    
    This is the comprehensive view combining all analytics.
    
    Time Complexity: O(n) - comprehensive scan
    """
    user_id = int(get_jwt_identity())
    return dashboard_analytics(user_id)
