"""
Budget Optimizer Service
DSA algorithms: Dynamic Programming (Knapsack variant), Greedy
Used for suggesting optimal budget allocations across categories.
"""


def knapsack_optimize(categories, total_budget):
    """
    0/1 Knapsack DP to select categories that maximize priority within budget.

    Args:
        categories: list of dicts with keys 'name', 'budget_limit', 'priority' (1-10)
        total_budget: total budget to allocate

    Returns:
        dict with 'selected' categories, 'total_allocated', 'total_priority'
    """
    n = len(categories)
    weights = [min(c.get("budget_limit", 0) or 0, total_budget) for c in categories]
    values = [c.get("priority", 5) for c in categories]

    dp = [[0] * (int(total_budget) + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(int(total_budget) + 1):
            if int(weights[i - 1]) <= w:
                dp[i][w] = max(
                    values[i - 1] + dp[i - 1][w - int(weights[i - 1])],
                    dp[i - 1][w],
                )
            else:
                dp[i][w] = dp[i - 1][w]

    selected = []
    w = int(total_budget)
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(categories[i - 1])
            w -= int(weights[i - 1])

    return {
        "selected": list(reversed(selected)),
        "total_allocated": total_budget - w,
        "total_priority": dp[n][int(total_budget)],
    }


def greedy_budget_allocation(categories, total_budget):
    """
    Greedy budget allocation by priority/weight ratio.
    Allocates budget to highest priority categories first.
    """
    scored = []
    for cat in categories:
        budget = cat.get("budget_limit", 0) or 0
        priority = cat.get("priority", 1)
        ratio = priority / budget if budget > 0 else float("inf")
        scored.append((ratio, cat))

    scored.sort(key=lambda x: x[0], reverse=True)
    allocated = []
    remaining = total_budget

    for ratio, cat in scored:
        needed = cat.get("budget_limit", 0) or 0
        if needed <= remaining:
            allocated.append(cat)
            remaining -= needed
        if remaining <= 0:
            break

    return allocated
