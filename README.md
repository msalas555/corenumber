# Kraken Trading Bot

## Overview
This Python script is an automated trading bot for the Kraken cryptocurrency exchange, specifically designed to trade Bitcoin (BTC) against USDC with automated buy and sell strategies.

## Features
- **Automated Trading**: Executes buy and sell orders based on predefined price triggers
- **Balance Tracking**: Monitors current USDC and BTC balances
- **Logging**: Maintains daily log files of trading activities
- **Dynamic Core Number Management**: Adjusts trading core number based on portfolio performance

## Prerequisites
- Python 3.x
- `requests` library
- Kraken API Key and Secret
- Environment variables for API authentication

## Configuration
### Required Environment Variables
- `API`: Kraken API Key
- `SEC`: Kraken API Secret

### Trading Parameters
- **Core Number**: Base investment amount
- **Trigger Percentage**: 3% (configurable)
- **Wait Time**: 10 minutes between checks

## Key Functions
- `get_balance()`: Retrieves current USDC and BTC balances
- `price()`: Fetches current market prices
- `buy()`: Execute market buy order
- `sell()`: Execute market sell order
- `compound()`: Adjusts core investment number

## Trading Logic
1. Checks current market prices every 10 minutes
2. Sells BTC if portfolio value exceeds core number by trigger percentage
3. Buys BTC if portfolio value falls below core number by trigger percentage
4. Logs all trading activities in daily log files

## Security Notes
- Uses HMAC-SHA512 for API request signatures
- Implements basic error handling for connection issues

## Disclaimer
**Use at your own risk. Cryptocurrency trading involves significant financial risk.**
