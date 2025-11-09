# bot.py
import json, time, logging
from binance import Client
from strategies.candlestick import get_candle_signal
from strategies.rsi import get_rsi_signal
from strategies.trend import get_trend_signal
from ml_model import MLModel
from risk_manager import RiskManager
from state_manager import StateManager

# Set up logging to file
logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# Load state (positions, balance, etc.)
state = StateManager.load("state.json")
balance = state.get("balance", 10000)  # starting virtual balance
positions = state.get("positions", [])

# Connect to Binance Testnet
api_key = "<YOUR_API_KEY>"  # will be populated by GH Actions
api_secret = "<YOUR_API_SECRET>"
client = Client(api_key, api_secret, testnet=True)  # testnet=True for simulation:contentReference[oaicite:32]{index=32}

# Initialize models and managers
ml = MLModel()
risk = RiskManager(balance)
order_executed = False

try:
    # Fetch latest market data (e.g. recent 100 candles)
    klines = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR, limit=100)
    # Simplest: extract closes for indicators
    closes = [float(k[4]) for k in klines]
    
    # Generate strategy signals
    cs_signal = get_candle_signal(klines)  # e.g. -1,0,1
    rsi_signal = get_rsi_signal(closes)
    trend_signal = get_trend_signal(closes)
    logging.info(f"Signals: candlestick={cs_signal}, RSI={rsi_signal}, trend={trend_signal}")
    
    # Get ML prediction (1=buy, -1=sell, 0=hold)
    ml_signal = ml.predict(closes, [cs_signal, rsi_signal, trend_signal])
    logging.info(f"ML model predicts: {ml_signal}")
    
    # Decide trade: here require agreement of ML and at least one strategy
    if ml_signal == 1 and (cs_signal == 1 or rsi_signal == 1 or trend_signal == 1):
        # Example: go long
        price = closes[-1]
        stop_price = risk.calculate_stop(price, direction=1) 
        qty = risk.calculate_size(price, stop_price)
        # Place market buy order
        order = client.order_market_buy(symbol='BTCUSDT', quantity=qty)
        logging.info(f"Executed BUY {qty} @ market ({price})")
        positions.append({'side': 'LONG', 'entry': price, 'qty': qty, 'stop': stop_price})
        order_executed = True
    elif ml_signal == -1 and (cs_signal == -1 or rsi_signal == -1 or trend_signal == -1):
        # Example: go short (or sell if already long)
        price = closes[-1]
        stop_price = risk.calculate_stop(price, direction=-1)
        qty = risk.calculate_size(price, stop_price)
        order = client.order_market_sell(symbol='BTCUSDT', quantity=qty)
        logging.info(f"Executed SELL {qty} @ market ({price})")
        positions.append({'side': 'SHORT', 'entry': price, 'qty': qty, 'stop': stop_price})
        order_executed = True
    else:
        logging.info("No trade signal this run.")
    
    # Update and save state
    if order_executed:
        balance = float(client.get_asset_balance(asset='USDT')['free'])
        state.update(balance, positions)
    StateManager.save("state.json", state.data)
    logging.info("State saved.")
    
except Exception as e:
    logging.error(f"Error in bot run: {e}", exc_info=True)
    # Save current state before exiting
    StateManager.save("state.json", state.data)
    raise
