from charset_normalizer import api
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
from pycoingecko import CoinGeckoAPI
from requests import HTTPError
import arrow
import time
import os

def usd_scraper():
    api_id = {
        'USDT': 'tether',
        'WBTC': 'wrapped-bitcoin',
        'WETH': 'weth',
        'YFI': 'yearn-finance',
        'ZRX': '0x',
        'UNI': 'uniswap',
        'AAVE': 'aave',
        'BAT': 'basic-attention-token',
        'BUSD': 'binance-usd',
        'DAI': 'dai',
        'ENJ': 'enjincoin',
        'KNC': 'kyber-network-crystal',
        'LINK': 'chainlink',
        'MANA': 'decentraland',
        'MKR': 'maker',
        'REN': 'republic-protocol',
        'SNX': 'havven',
        'sUSD': 'nusd',
        'TUSD': 'true-usd',
        'USDC': 'usd-coin',
        'CRV': 'curve-dao-token',
        'GUSD': 'gemini-dollar',
        'BAL': 'balancer',
        'xSUSHI': 'xsushi',
        'renFIL': 'renfil',
        'RAI': 'rai',
        'AMPL': 'ampleforth',
        'USDP': 'paxos-standard',
        'DPI': 'defipulse-index',
        'FRAX': 'frax',
        'FEI': 'fei-usd',
        'stETH': 'staked-ether',
        'ENS': 'ethereum-name-service',
        'UST': 'terrausd-wormhole',
        'CVX': 'convex-finance',
        '1INCH': '1inch'
    }
    cg = CoinGeckoAPI()

    allcgcoins = cg.get_coins_list()
    allids = [x['id'] for x in allcgcoins]

    def wait_for_limit(cg, c, current_time, next_day):
        # try 5 times max
        for _ in range(5):
            try:
                prices = cg.get_coin_market_chart_range_by_id(c, "usd", current_time, next_day)
                return prices
            except HTTPError as e:
                # sleep 5 seconds if we get rate limited
                if e.response.status_code == 429:
                    time.sleep(5)
        raise Exception("retried too many times after rate limited")

    ids_to_scrape = []
    for i in api_id.values():
        ids_to_scrape.append(i)

    if len( set(ids_to_scrape).difference(allids) ) > 0:
        print( f"Error invalid id" )
        print( set(ids_to_scrape).difference(allids) )
        ids_to_scrape = list( set(ids_to_scrape).intersection(allids) )

    start_time = arrow.get(2022,12,1).timestamp()
    end_time = arrow.get(2022,8,25).timestamp()

    if not os.path.exists("../data/usd_prices/"):
        os.makedirs("../data/usd_prices/")
    error_filename = "errors.csv"
    error_file = open(f"../data/usd_prices/{error_filename}", "w")
    files = {}

    for c in ids_to_scrape:
        for key,value in api_id.items():
            if value == c:
                filename = key.replace("-", "_")
                filename = filename + "_usd.csv"
                files[c] = open(f"../data/usd_prices/{filename}", "a")

    current_time = start_time
    total_queries = 0
    query_limit_per_min = 50
    
    while current_time < end_time:
        print(f"grabbing data for time {current_time}")
        next_day = arrow.get(current_time).shift(days=1).timestamp()
        for symbol,c in api_id.items():
            try:                
                prices = wait_for_limit(cg, c, current_time, next_day)
                total_queries += 1
                if prices["prices"]:
                    for price in prices["prices"]:
                        files[c].write(f"{symbol},{price[0]},{price[1]}\n")
            except Exception as e:
                # simply log the coin and timestamp, not hard to regrab this data
                error_file.write(f"{c},{current_time},{e}\n")
        current_time = next_day

def get_usd():
    df = pd.read_csv("../data/aave_collateralization.csv")

    symbols = list(df.symbol.unique())

    new_df = pd.DataFrame()

    for symbol in symbols:
        temp_df = pd.read_csv(f"./{symbol}_usd.csv")
        temp_df.astype(dtype={'timestamp':int}, copy=False)
        temp_df.sort_values(by=['timestamp'], inplace=True)
        temp_df['timestamp'] = temp_df['timestamp']//1000
        new_df = new_df.append(temp_df, ignore_index=True)

    df.sort_values(by=['timestamp'],inplace=True)
    new_df.sort_values(by=['timestamp'],inplace=True)

    df = pd.merge_asof(df, new_df,on = 'timestamp',by = 'symbol')

    df.to_csv("../data/aave_collateralization.csv")

#Run this to scrape US dollar prices for all tokens deposited into AAVE, from coingecko
#usd_scraper()

#Run this to merge US dollar prices for tokens with aave_collateralization.csv
#get_usd()

