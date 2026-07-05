import re
from datetime import datetime

from app import db
from app.models.expense import Expense


def _tokenize(text):
    if not text:
        return set()
    return set(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def _jaccard_similarity(a, b):
    tokens_a = _tokenize(a)
    tokens_b = _tokenize(b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def _amount_tolerance(a, b, tolerance=0.01):
    if a is None or b is None:
        return False
    return abs(a - b) <= tolerance


def _normalize_date(date_val):
    if date_val is None:
        return None
    if isinstance(date_val, datetime):
        return date_val.date()
    if isinstance(date_val, str):
        try:
            return datetime.strptime(date_val, "%Y-%m-%d").date()
        except ValueError:
            return None
    return date_val


def detect_duplicates(transactions, user_id):
    if not transactions or not user_id:
        return []

    existing = Expense.query.filter_by(user_id=user_id).all()

    existing_by_date = {}
    for exp in existing:
        d = exp.date
        if d not in existing_by_date:
            existing_by_date[d] = []
        existing_by_date[d].append(exp)

    results = []
    for tx in transactions:
        tx_date = _normalize_date(tx.get("date"))
        tx_amount = tx.get("amount")
        tx_desc = tx.get("description", "")

        matches = []

        if tx_date in existing_by_date:
            candidates = existing_by_date[tx_date]
            for exp in candidates:
                score = 0
                reasons = []

                if _amount_tolerance(tx_amount, exp.amount):
                    score += 40
                    reasons.append(f"Amount matches ₹{exp.amount:,.2f}")

                sim = _jaccard_similarity(tx_desc, exp.title or "")
                if sim >= 0.5:
                    score += int(sim * 30)
                    reasons.append(f"Description similarity {(sim * 100):.0f}%")

                if tx_desc and exp.description:
                    desc_sim = _jaccard_similarity(tx_desc, exp.description)
                    if desc_sim >= 0.5:
                        score += int(desc_sim * 20)
                        reasons.append(f"Description match {(desc_sim * 100):.0f}%")

                if score >= 40:
                    matches.append({
                        "expense_id": exp.id,
                        "expense_title": exp.title,
                        "expense_amount": exp.amount,
                        "expense_date": exp.date.isoformat() if exp.date else None,
                        "expense_category_id": exp.category_id,
                        "score": min(score, 100),
                        "reasons": reasons,
                    })

        matches.sort(key=lambda m: m["score"], reverse=True)

        results.append({
            "row_index": tx.get("row_index"),
            "duplicate": len(matches) > 0,
            "match_count": len(matches),
            "best_score": matches[0]["score"] if matches else 0,
            "matches": matches[:3],
        })

    return results


def attach_duplicates_to_preview(preview_result, user_id):
    transactions = preview_result.get("transactions", [])
    duplicates = detect_duplicates(transactions, user_id)

    dup_map = {d["row_index"]: d for d in duplicates}

    for tx in transactions:
        info = dup_map.get(tx.get("row_index"))
        if info and info["duplicate"]:
            tx["duplicate"] = True
            tx["duplicate_count"] = info["match_count"]
            tx["duplicate_best_score"] = info["best_score"]
            tx["duplicate_matches"] = info["matches"]
            tx["duplicate_action"] = "import"  # default; user can change to skip/replace
        else:
            tx["duplicate"] = False

    preview_result["duplicate_count"] = sum(1 for d in duplicates if d["duplicate"])
    preview_result["duplicates"] = duplicates
