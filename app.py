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
        symbol = request.form['symbol']
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")

        if not data.empty:
            price = round(data['Close'][0], 2)
            stock_data = {
                'symbol': symbol.upper(),
                'price': price
            }
        else:
            stock_data = {
                'symbol': symbol.upper(),
                'price': "Invalid stock symbol"
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