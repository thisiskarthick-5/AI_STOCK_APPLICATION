from flask import Flask, render_template, request, jsonify
import yfinance as yf

app = Flask(__name__)

# List of popular stock symbols (mix of global and Indian)
POPULAR_STOCKS = [
    "TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NFLX",
    "SBIN.NS", "BHARTIARTL.NS", "WIPRO.NS", "HCLTECH.NS", "MARUTI.NS",
    "TATAMOTORS.NS", "ITC.NS", "HINDUNILVR.NS", "ASIANPAINT.NS", "AXISBANK.NS"
]

@app.route('/', methods=['GET', 'POST'])
def index():
    stock_data = None

    if request.method == 'POST':
        symbol = request.form['symbol'].upper()
        stock = yf.Ticker(symbol)
        # Fetch 1 month of history for chart visualization
        history = stock.history(period="1mo")

        if not history.empty:
            # Extract current price
            current_price = round(history['Close'][-1], 2)
            
            # Extract historical data for Chart.js
            dates = history.index.strftime('%Y-%m-%d').tolist()
            prices = [round(p, 2) for p in history['Close'].tolist()]
            
            stock_data = {
                'symbol': symbol,
                'price': current_price,
                'history_dates': dates,
                'history_prices': prices
            }
        else:
            stock_data = {
                'symbol': symbol,
                'price': "Invalid stock symbol or no data available"
            }

    return render_template('index.html', stock_data=stock_data)

@app.route('/suggest')
def suggest():
    query = request.args.get('q', '').upper()
    if not query:
        return jsonify([])
    
    suggestions = [s for s in POPULAR_STOCKS if query in s.upper()]
    return jsonify(suggestions[:10])

if __name__ == '__main__':
    app.run(debug=True)