def get_latest_financial_metric(ticker, metric):
    ticker = ticker.upper()
    metric = metric.lower()

    financials = {
        "NVDA": {
            "revenue": 208.70,
            "net_income": 120.10,
            "eps": 4.52,
        },
        "GOOGL": {
            "revenue": 402.84,
            "net_income": 132.17,
            "eps": 8.96,
        },
        "AAPL": {
            "revenue": 416.16,
            "net_income": 112.01,
            "eps": 7.46,
        },
        "MSFT": {
            "revenue": 281.72,
            "net_income": 101.83,
            "eps": 13.64,
        },
        "AMZN": {
            "revenue": 716.92,
            "net_income": 77.67,
            "eps": 7.20,
        },
        "TSM": {
            "revenue": 90.20,
            "net_income": 36.80,
            "eps": 7.10,
        },
        "AVGO": {
            "revenue": 59.90,
            "net_income": 18.30,
            "eps": 4.80,
        },
        "2222": {
            "revenue": 480.00,
            "net_income": 105.00,
            "eps": 0.50,
        },
        "SPCX": {
            "revenue": 15.50,
            "net_income": 3.20,
            "eps": 1.10,
        },
        "META": {
            "revenue": 200.97,
            "net_income": 78.84,
            "eps": 29.50,
        },
    }

    return financials.get(ticker, {}).get(metric, 0.0)