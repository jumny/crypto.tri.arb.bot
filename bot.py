import ccxt.pro as ccxt  # Use ccxt.pro for WebSocket support import json import asyncio import logging

Load API credentials from config.json

try: with open('config.json', 'r') as config_file: config = json.load(config_file) api_key = config['api_key'] api_secret = config['api_secret'] trade_balance_ratio = config.get('trade_balance_ratio', 1.0)  # Default to 100% balance usage except Exception as e: print(f"Error loading API credentials: {e}") exit()

Initialize logging

logging.basicConfig(filename='trade_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

Initialize Crypto.com exchange with WebSockets

exchange = ccxt.crypto_com({ 'apiKey': api_key, 'secret': api_secret, 'rateLimit': 10, 'enableRateLimit': True, })

priority_symbols = ['SHIB/BTC', 'BTC/USD', 'SHIB/USD']  # Prioritized pairs

async def find_triangular_arbitrage(): try: await exchange.load_markets() symbols = list(exchange.markets.keys())

while True:
        ticker_data = await asyncio.gather(*[exchange.watch_ticker(symbol) for symbol in priority_symbols])
        
        shib_btc = ticker_data[0]['bid']
        btc_usd = ticker_data[1]['bid']
        shib_usd = ticker_data[2]['ask']
        
        arbitrage_profit = (shib_btc * btc_usd / shib_usd - 1) * 100
        
        if arbitrage_profit > 1:  # 1% profit threshold
            print(f"Arbitrage Opportunity Found! Profit: {arbitrage_profit:.2f}% (Priority Pair)")
            logging.info(f"Arbitrage Opportunity (Priority Pair): {arbitrage_profit:.2f}%")
            await execute_trade(shib_btc, btc_usd, shib_usd)
        else:
            print("No priority arbitrage opportunity at the moment. Checking other pairs...")
            
            other_ticker_data = await asyncio.gather(*[exchange.watch_ticker(symbol) for symbol in symbols if symbol not in priority_symbols])
            for i in range(0, len(other_ticker_data) - 2, 3):
                base1 = other_ticker_data[i]['bid']
                base2 = other_ticker_data[i+1]['bid']
                base3 = other_ticker_data[i+2]['ask']
                
                potential_profit = (base1 * base2 / base3 - 1) * 100
                
                if potential_profit > 1:
                    print(f"Arbitrage Opportunity Found! Profit: {potential_profit:.2f}% (Other Pair)")
                    logging.info(f"Arbitrage Opportunity (Other Pair): {potential_profit:.2f}%")
                    await execute_trade(base1, base2, base3)
except Exception as e:
    print(f"Error fetching data: {e}")
    logging.error(f"Error fetching data: {e}")

async def execute_trade(base1, base2, base3): try: balance = await exchange.fetch_balance() available_usd = balance['total']['USD'] * trade_balance_ratio  # Adjust balance usage

if available_usd > 10:  # Minimum trade amount
        order1 = await exchange.create_market_order('SHIB/USD', 'buy', available_usd / base3)
        order2 = await exchange.create_market_order('SHIB/BTC', 'sell', order1['amount'])
        order3 = await exchange.create_market_order('BTC/USD', 'sell', order2['amount'] * base2)
        print("Trade executed successfully!")
        logging.info("Trade executed: SHIB/USD -> SHIB/BTC -> BTC/USD")
    else:
        print("Insufficient balance to trade.")
        logging.warning("Insufficient balance to trade.")
except Exception as e:
    print(f"Error executing trade: {e}")
    logging.error(f"Error executing trade: {e}")

async def main(): await find_triangular_arbitrage()

if name == "main": asyncio.run(main())


