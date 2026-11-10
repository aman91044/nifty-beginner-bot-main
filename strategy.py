import time
import json
import os
import webbrowser
from datetime import datetime
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws

import config

STATE_FILE = "state.json"

# ==========================================
# STATE MANAGEMENT
# ==========================================
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "status": "WAITING",
        "live_price": 0.0,
        "session_high": -1,
        "session_low": 999999,
        "trade": None
    }

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"Error saving state: {e}")

# Load initial state
state = load_state()

# ==========================================
# AUTHENTICATION
# ==========================================
def authenticate():
    print("Starting Fyers Authentication...")
    session = fyersModel.SessionModel(
        client_id=config.APP_ID,
        secret_key=config.SECRET_KEY,
        redirect_uri=config.REDIRECT_URI,
        response_type='code',
        grant_type='authorization_code'
    )
    
    # Step 1: Generate Auth Code URL
    response = session.generate_authcode()
    print("\n" + "="*50)
    print("Please login using this URL if your browser doesn't open automatically:")
    print(response)
    print("="*50 + "\n")
    
    # Try to open the browser automatically
    webbrowser.open(response)
    
    # Step 2: Get Auth Code from User
    print("After logging in, you will be redirected to your REDIRECT_URI (e.g., https://127.0.0.1:5000/?action=login&status=success&auth_code=XXXXXX)")
    auth_code = input("Please copy the 'auth_code' from the URL and paste it here: ")
    
    # Step 3: Generate Access Token
    session.set_token(auth_code)
    try:
        response = session.generate_token()
        access_token = response['access_token']
        print("\n✅ Authentication Successful!")
        return access_token
    except Exception as e:
        print(f"\n❌ Authentication Failed: {e}")
        exit(1)

# ==========================================
# WEBSOCKET LOGIC
# ==========================================
def onmessage(message):
    """
    Handles live ticks from Fyers WebSocket
    message format usually: [{'symbol': 'NSE:NIFTY50-INDEX', 'ltp': 19500.5, ...}]
    """
    global state
    
    # If message is a list, process each tick
    if isinstance(message, list):
        for tick in message:
            process_tick(tick)
    elif isinstance(message, dict) and 'ltp' in message:
        process_tick(message)
        
def process_tick(tick, simulated_time=None):
    global state
    
    # Ensure it's the correct symbol and has LTP
    if 'symbol' in tick and tick['symbol'] != config.SYMBOL:
        return
    
    if 'ltp' not in tick:
        return
        
    ltp = tick['ltp']
    state['live_price'] = ltp
    
    # Get current time or use simulated time
    if simulated_time:
        current_time = simulated_time
    else:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
    
    # 1. OBSERVATION PHASE (09:15:00 to 09:29:59)
    if "09:15:00" <= current_time <= "09:29:59":
        state['status'] = "OBSERVATION"
        
        if state['session_high'] == -1 or ltp > state['session_high']:
            state['session_high'] = ltp
            
        if ltp < state['session_low']:
            state['session_low'] = ltp
            
    # 2. ACTION PHASE (09:30:00 to 15:14:59)
    elif "09:30:00" <= current_time < "15:15:00":
        # Check if we need to take a trade
        if state['trade'] is None:
            state['status'] = "ACTION"
            
            # CE BREAKOUT
            if ltp > state['session_high'] and state['session_high'] != -1:
                strike = round(ltp / 50) * 50
                state['trade'] = {
                    "type": "CE BUY",
                    "entry_time": current_time,
                    "entry_price": ltp,
                    "atm_strike": strike,
                    "pnl": 0.0,
                    "exit_time": None,
                    "exit_price": None
                }
                state['status'] = "IN_POSITION"
                print(f"[{current_time}] 🟢 BREAKOUT! CE BUY Triggered at {ltp} (Strike: {strike})")
                
            # PE BREAKOUT
            elif ltp < state['session_low'] and state['session_low'] != 999999:
                strike = round(ltp / 50) * 50
                state['trade'] = {
                    "type": "PE BUY",
                    "entry_time": current_time,
                    "entry_price": ltp,
                    "atm_strike": strike,
                    "pnl": 0.0,
                    "exit_time": None,
                    "exit_price": None
                }
                state['status'] = "IN_POSITION"
                print(f"[{current_time}] 🔴 BREAKDOWN! PE BUY Triggered at {ltp} (Strike: {strike})")
        
        # We are IN POSITION, update PnL
        else:
            if state['trade']['exit_time'] is None:
                # Calculate simple points-based PnL based on Nifty Spot movement
                if state['trade']['type'] == "CE BUY":
                    state['trade']['pnl'] = ltp - state['trade']['entry_price']
                else:  # PE BUY
                    state['trade']['pnl'] = state['trade']['entry_price'] - ltp
    
    # 3. SQUARE OFF PHASE (15:15:00 onwards)
    elif current_time >= "15:15:00":
        if state['trade'] is not None and state['trade']['exit_time'] is None:
            # Auto Square-Off Active Trade
            state['trade']['exit_time'] = current_time
            state['trade']['exit_price'] = ltp
            state['status'] = "SQUARED_OFF"
            
            # Final PnL Calculation
            if state['trade']['type'] == "CE BUY":
                state['trade']['pnl'] = ltp - state['trade']['entry_price']
            else:
                state['trade']['pnl'] = state['trade']['entry_price'] - ltp
                
            print(f"[{current_time}] ⏹️ Auto Square-Off triggered at {ltp}. Final PnL: {state['trade']['pnl']:.2f}")
            
        elif state['status'] != "SQUARED_OFF":
            state['status'] = "MARKET_CLOSED"

    # Save state so Dashboard can read it
    save_state(state)

def onerror(message):
    print("WebSocket Error:", message)

def onclose(message):
    print("WebSocket Closed:", message)

def onopen():
    print("WebSocket Connected! Subscribing to", config.SYMBOL)
    global fyers_ws
    data_type = "SymbolUpdate"
    symbols = [config.SYMBOL]
    fyers_ws.subscribe(symbols=symbols, data_type=data_type)

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("Initializing Nifty ORB Bot...")
    
    # 1. Authenticate
    raw_token = authenticate()
    
    # Format required by FyersDataSocket is APP_ID:access_token
    formatted_access_token = f"{config.APP_ID}:{raw_token}"
    
    # 2. Reset daily state if starting fresh
    print("Resetting daily state file...")
    state = {
        "status": "WAITING",
        "live_price": 0.0,
        "session_high": -1,
        "session_low": 999999,
        "trade": None
    }
    save_state(state)
    
    # 3. Connect to WebSocket
    fyers_ws = data_ws.FyersDataSocket(
        access_token=formatted_access_token,
        log_path="", 
        litemode=True,
        write_to_file=False,
        reconnect=True,
        on_connect=onopen,
        on_close=onclose,
        on_error=onerror,
        on_message=onmessage
    )
    
    print("Starting WebSocket Client...")
    fyers_ws.connect()
