import re

def extract_sector_summary(raw_text):
    summary_match = re.search(r"\*\*1\. Sector & View Summary:\*\*[\s\n]*(.+?)\n---", raw_text, re.DOTALL)
    return summary_match.group(1).strip() if summary_match else "Sector summary not found."

def parse_strategies(raw_text):
    strategies = []
    number_pat = re.compile(r"[-+]?\d*\.?\d+")

    def extract_value(text, key, pct=False):
        m = re.search(rf"{key}\s*[:：]\s*([\d.:]+)", text, flags=re.I)
        if not m:
            return 0
        raw = m.group(1).replace(":", ".")
        val = number_pat.search(raw)
        if not val:
            return 0
        return float(val.group()) if not pct else float(val.group())

    for block in raw_text.split('---'):
        if "Strategy" not in block:
            continue
        clean = block.replace("**", "").replace("###", "").replace("-", "").strip()
        name_match = re.search(r"Strategy\s*:\s*(.+?)\n", clean, flags=re.I)
        explanation_match = re.search(r"Explanation\s*:\s*(.+?)\n", clean, flags=re.I)
        if not name_match or not explanation_match:
            continue
        name = name_match.group(1).strip()
        explanation = explanation_match.group(1).strip()
        strategies.append({
            "name": name,
            "explanation": explanation,
            "popularity": extract_value(clean, "Popularity", pct=True),
            "avg_return": extract_value(clean, "Average Return", pct=True),
            "sharpe_ratio": extract_value(clean, "Sharpe Ratio"),
            "win_rate": extract_value(clean, "Win Rate", pct=True),
            "max_drawdown": extract_value(clean, "Max Drawdown", pct=True),
            "profit_factor": extract_value(clean, "Profit Factor"),
            "volatility": extract_value(clean, "Volatility", pct=True),
            "risk_reward_ratio": extract_value(clean, "Expectancy"),
            "trade_frequency": extract_value(clean, "Trade Frequency")
        })
    return strategies

def build_response_summary(strategies):
    response_summary = ""
    for s in strategies:
        response_summary += f"\n### {s['name']}\n"
        response_summary += f"- **Explanation**: {s['explanation']}\n"
        response_summary += f"- **Popularity**: {s['popularity']}%\n"
        response_summary += f"- **Average Return**: {s['avg_return']}%\n"
        response_summary += f"- **Sharpe Ratio**: {s['sharpe_ratio']}\n"
        response_summary += f"- **Win Rate**: {s['win_rate']}%\n"
        response_summary += f"- **Max Drawdown**: {s['max_drawdown']}%\n"
        response_summary += f"- **Profit Factor**: {s['profit_factor']}\n"
        response_summary += f"- **Volatility**: {s['volatility']}%\n"
        response_summary += f"- **Expectancy**: {s['risk_reward_ratio']}\n"
        response_summary += f"- **Trade Frequency**: {s['trade_frequency']} trades/month\n"
    return response_summary 