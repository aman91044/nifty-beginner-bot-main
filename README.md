# Nifty 50 ORB Trading Bot

A fully automated, beginner-friendly Opening Range Breakout (ORB) bot for the Indian Stock Market (Nifty 50), built with Python and the Fyers API v3. 

This bot was designed as a "plug-and-play" paper-trading simulator to demonstrate how easily you can automate the famous 15-minute ORB strategy without needing complex coding knowledge.

## Features
- **Zero-Latency Live Data**: Connects directly to the Fyers WebSocket for instant price ticks.
- **Automated ORB Calculation**: Tracks every tick from 09:15 to 09:30 to perfectly mark the session High and Low.
- **Instant Breakout Execution**: Automatically logs a virtual trade the exact millisecond the Nifty index breaks the High (Call) or Low (Put).
- **Live PnL Tracking**: Simulates Profit and Loss in real-time based on Nifty 50 index points.
- **Auto Square-Off**: Automatically closes any open position at 15:15 to prevent holding overnight.
- **Modern Dashboard**: Includes a sleek, dark-themed Streamlit dashboard that reads the live bot data and displays it beautifully in your browser.

## How to Set It Up

### 1. Install Dependencies
Make sure you have Python installed, then install the required libraries:
```bash
pip install fyers-apiv3 streamlit pandas
```

### 2. Get Your Fyers API Keys (100% Free)
1. Go to [myapi.fyers.in](https://myapi.fyers.in/) and log in with your Fyers account.
2. Click **Create App** and fill in your details. 
3. **Important**: Set the **Redirect URI** to exactly `https://127.0.0.1:5000/`
4. Copy the **App ID** and **Secret Key** generated for your app.

### 3. Configure the Bot
Open the `config.py` file and paste your `APP_ID` and `SECRET_KEY` into the placeholder variables.

## How to Run It

You need two terminal windows to run both the bot (the brain) and the dashboard (the viewer).

**Terminal 1: Start the Dashboard**
```bash
streamlit run dashboard.py
```
This will automatically open the beautiful dashboard in your browser.

**Terminal 2: Start the Trading Bot (Run this at 09:00 AM)**
```bash
python strategy.py
```
*Note: The script will give you a login link. Open it in your browser, log in to Fyers, and copy the `auth_code` from the URL to paste back into the terminal. After that, the bot takes over completely!*

## Custom Bot Development
This is a simplified, beginner-friendly version of the bot meant for paper-trading and strategy validation.

If you are a trader with a profitable strategy and you want to build a fully automated, institutional-grade bot that routes real money orders to your broker and manages advanced stop-losses—you don't need to learn Python.

**[Book a 1:1 Call with me here to automate your strategy!]** *https://topmate.io/ritishfx*

---
*Disclaimer: This code is for educational purposes only. The creator is not responsible for any financial losses incurred if you modify this code to trade real capital.*
