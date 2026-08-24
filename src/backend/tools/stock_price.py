def get_stock_price(ticker):
    stock_prices = {
        "NVDA": 180.75,
        "GOOGL": 195.30,
        "AAPL": 230.50,
        "MSFT": 510.25,
        "AMZN": 220.40,
        "TSM": 240.10,
        "AVGO": 310.60,
        "2222": 8.20,
        "SPCX": 420.00,
        "META": 760.20,
    }

    return stock_prices.get(ticker.upper(),0.0)