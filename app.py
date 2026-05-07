from flask import Flask, render_template, request, jsonify
import yfinance as yf

app = Flask(__name__)

# Popular stock symbols (Indian .NS and global)
POPULAR_STOCKS = [
    "TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "BHARTIARTL.NS", "WIPRO.NS", "HCLTECH.NS", "MARUTI.NS",
    "TATAMOTORS.NS", "ITC.NS", "HINDUNILVR.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NFLX", "NVDA", "AMD"
]


@app.route('/', methods=['GET', 'POST'])
def index():
    stock_data = None
    error = None

    if request.method == 'POST':
        # --- 1. Input Validation ---
        symbol = request.form.get('symbol', '').strip().upper()

        if not symbol:
            error = "Please enter a stock symbol."
        else:
            try:
                # --- 2. Data Fetching ---
                stock = yf.Ticker(symbol)
                history = stock.history(period="1mo")

                # --- 4. Edge Case: No data returned ---
                if history.empty:
                    error = f"No data found for symbol '{symbol}'. Please check the symbol and try again."
                else:
                    # --- 3. Data Processing ---
                    # Format dates as YYYY-MM-DD strings
                    dates = history.index.strftime('%Y-%m-%d').tolist()

                    # Round all price values to 2 decimal places
                    close_prices  = [round(p, 2) for p in history['Close'].tolist()]
                    open_prices   = [round(p, 2) for p in history['Open'].tolist()]
                    high_prices   = [round(p, 2) for p in history['High'].tolist()]
                    low_prices    = [round(p, 2) for p in history['Low'].tolist()]
                    volumes       = [int(v)       for v in history['Volume'].tolist()]

                    current_price = close_prices[-1]
                    prev_price    = close_prices[-2] if len(close_prices) > 1 else current_price
                    price_change  = round(current_price - prev_price, 2)
                    change_pct    = round((price_change / prev_price) * 100, 2) if prev_price else 0

                    # Detect currency: Indian stocks use ₹, others use $
                    currency = '₹' if symbol.endswith('.NS') or symbol.endswith('.BO') else '$'

                    stock_data = {
                        'symbol':         symbol,
                        'price':          current_price,
                        'price_change':   price_change,
                        'change_pct':     change_pct,
                        'currency':       currency,
                        'high_52w':       round(max(high_prices), 2),
                        'low_52w':        round(min(low_prices), 2),
                        'avg_volume':     int(sum(volumes) / len(volumes)),
                        'history_dates':  dates,
                        'history_close':  close_prices,
                        'history_open':   open_prices,
                        'history_high':   high_prices,
                        'history_low':    low_prices,
                        'history_volume': volumes,
                    }

            except Exception as e:
                # --- 8. Backend crash prevention ---
                error = f"An error occurred while fetching data for '{symbol}'. Please try again."

    return render_template('index.html', stock_data=stock_data, error=error)


@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    symbol = symbol.strip().upper()
    try:
        stock = yf.Ticker(symbol)
        history = stock.history(period="1mo")
        if history.empty:
            return jsonify({'error': 'No data found'}), 404
        
        dates = history.index.strftime('%Y-%m-%d').tolist()
        close_prices = [round(p, 2) for p in history['Close'].tolist()]
        high_prices = [round(p, 2) for p in history['High'].tolist()]
        
        current_price = close_prices[-1]
        prev_price = close_prices[-2] if len(close_prices) > 1 else current_price
        price_change = round(current_price - prev_price, 2)
        change_pct = round((price_change / prev_price) * 100, 2) if prev_price else 0
        currency = '₹' if symbol.endswith('.NS') or symbol.endswith('.BO') else '$'
        
        return jsonify({
            'symbol': symbol,
            'price': current_price,
            'change_pct': change_pct,
            'currency': currency,
            'high_30d': round(max(high_prices), 2),
            'history_dates': dates,
            'history_close': close_prices
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/suggest')
def suggest():
    query = request.args.get('q', '').strip().upper()
    if not query:
        return jsonify([])
    suggestions = [s for s in POPULAR_STOCKS if query in s]
    return jsonify(suggestions[:10])


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)