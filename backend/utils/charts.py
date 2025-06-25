import plotly.graph_objs as go

def generate_plotly_charts(strategies):
    charts = {}

    def make_chart(metric, title, yaxis):
        fig = go.Figure([go.Bar(x=[s['name'] for s in strategies], y=[s[metric] for s in strategies])])
        fig.update_layout(title=title, xaxis_title='Strategy', yaxis_title=yaxis)
        return fig

    metrics = {
        "popularity": "Strategy Popularity (%)",
        "avg_return": "Average Return (%)",
        "sharpe_ratio": "Sharpe Ratio",
        "win_rate": "Win Rate (%)",
        "max_drawdown": "Max Drawdown (%)",
        "profit_factor": "Profit Factor",
        "volatility": "Volatility (%)",
        "expectancy": "Risk-Reward Ratio",
        "trade_frequency": "Trade Frequency (trades/month)"
    }

    for key, title in metrics.items():
        charts[key] = make_chart(key, title, title.split(" (")[0])

    return charts 