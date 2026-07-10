import logging

logger = logging.getLogger(__name__)


def _format_currency(amount):
    return f"₹{amount:,.2f}"


def _format_list(items, key, label_key, amount_key):
    lines = []
    for item in items:
        title = item.get(key, "")
        amount = item.get(amount_key, 0)
        lines.append(f"• {title}  —  {_format_currency(amount)}")
    return "\n".join(lines)


def _build_greeting(output):
    return output["text"]


def _build_help(output):
    lines = [output["text"]]
    for cmd in output["commands"]:
        lines.append(f"• {cmd}")
    return "\n".join(lines)


def _build_add_expense_prompt(output):
    return output["text"]


def _build_add_expense_confirm(output):
    preview = output["preview"]
    return (
        f"{output['text']}\n\n"
        f"📝 Preview:\n"
        f"  Amount:      {_format_currency(preview['amount'])}\n"
        f"  Category:    {preview['category']}\n"
        f"  Description: {preview['description'] or '—'}\n"
        f"  Date:        {preview['date']}"
    )


def _build_expense_list(output):
    if not output["expenses"]:
        return "No expenses found for that filter."
    lines = [output["text"]]
    lines.append(_format_list(output["expenses"], "title", "category", "amount"))
    lines.append(f"\n**Total:** {_format_currency(output['total'])}")
    return "\n".join(lines)


def _build_summary(output):
    return (
        f"{output['text']}\n\n"
        f"💰 {output['income']['label']}:      {_format_currency(output['income']['total'])}  _{output['income']['change']}_\n"
        f"📉 {output['expense']['label']}:    {_format_currency(output['expense']['total'])}\n"
        f"⚖️  {output['balance']['label']}:    {_format_currency(output['balance']['total'])}\n"
        f"📊 {output['savings_rate']['label']}:  {output['savings_rate']['value']}%\n\n"
        f"🏆 {output['top_category']['label']}: {output['top_category']['name']} ({_format_currency(output['top_category']['amount'])})"
    )


def _build_add_income_prompt(output):
    return output["text"]


def _build_add_income_confirm(output):
    preview = output["preview"]
    return (
        f"{output['text']}\n\n"
        f"📝 Preview:\n"
        f"  Amount:   {_format_currency(preview['amount'])}\n"
        f"  Source:   {preview['source']}\n"
        f"  Date:     {preview['date']}"
    )


def _build_income_list(output):
    if not output["incomes"]:
        return "No income records found."
    lines = [output["text"]]
    lines.append(_format_list(output["incomes"], "source", "source", "amount"))
    lines.append(f"\n**Total:** {_format_currency(output['total'])}")
    return "\n".join(lines)


def _build_analytics(output):
    lines = [output["text"]]
    for cat in output["category_breakdown"]:
        bar_len = max(1, int(cat["percentage"] / 5))
        bar = "█" * bar_len
        lines.append(f"  {bar} {cat['name']:22s} {_format_currency(cat['amount']):>10s}  ({cat['percentage']}%)")
    lines.append("")
    for tip in output["insights"]:
        lines.append(f"💡 {tip}")
    return "\n".join(lines)


def _build_unknown(output):
    return output["text"]


_BUILDERS = {
    "greeting": _build_greeting,
    "help": _build_help,
    "add_expense_prompt": _build_add_expense_prompt,
    "add_expense_confirm": _build_add_expense_confirm,
    "expense_list": _build_expense_list,
    "summary": _build_summary,
    "add_income_prompt": _build_add_income_prompt,
    "add_income_confirm": _build_add_income_confirm,
    "income_list": _build_income_list,
    "analytics": _build_analytics,
    "unknown": _build_unknown,
}


def build_reply(tool_output):
    if isinstance(tool_output, str):
        return tool_output
    output_type = tool_output.get("type", "unknown")
    builder = _BUILDERS.get(output_type)
    if builder is None:
        logger.warning("No response builder for type '%s'", output_type)
        return tool_output.get("text", "")
    try:
        return builder(tool_output)
    except Exception as e:
        logger.error("Response builder failed for type '%s': %s", output_type, e)
        return tool_output.get("text", "")
