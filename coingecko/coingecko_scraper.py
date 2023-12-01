from pycoingecko import CoinGeckoAPI
from requests import HTTPError
import arrow
import time
import progressbar
import pandas as pd
import sys

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


df = pd.read_csv("../data/aave_collateralization_meta.csv" )
cg_df = pd.DataFrame( allcgcoins )

bad_ids = ['decentraland-wormhole','force-bridge-usdc','limited-usd','unicorn-token','uniswap-wormhole','usd-coin-avalanche-bridged-usdc-e','raicoin','stabilize-usd','genesis-mana','lusd','paxos-standard']

aave_symbols = list( df.symbol.unique() )
aave_symbols = list(map( lambda x: x.lower(), aave_symbols ))

ids = cg_df[cg_df.symbol.isin(aave_symbols) & ~cg_df.id.isin(bad_ids)]
ids = pd.concat( [ids, cg_df[cg_df.id == 'filecoin']] )

#print( list( set(aave_symbols).difference(ids.symbol) ) )
assert ids.shape[0] == len(aave_symbols), f'Error AAVE has {len(aave_symbols)} tokens.  Coingecko has {ids.shape[0]}'

ids_to_scrape = list(ids.id)

if len( set(ids_to_scrape).difference(allids) ) > 0:
	print( f"Error invalid id" )
	print( set(ids_to_scrape).difference(allids) )
	ids_to_scrape = list( set(ids_to_scrape).intersect(allids) )

start_date = arrow.get(2021,1,1)
end_date = arrow.utcnow()

error_filename = "errors.csv"
error_file = open(error_filename, "w")
files = {}

for c in ids_to_scrape:
	filename = ids[ids.id == c].symbol.iloc[0]
	filename = filename.upper()
	if filename == "FIL":
		filename = "reNFIL"
	if filename == 'SUSD':
		filename = 'sUSD'
	if filename == 'XSUSHI':
		filename = 'xSUSHI'
	if filename == 'STETH':
		filename = 'stETH'
	filename += "_usd.csv"
	filename = "../data/usd_prices/" + filename
	files[c] = open(filename, "w")

num_days = (end_date-start_date).days
date_range = arrow.Arrow.span_range('day',start_date,end_date)

print( f"Grabbing price data for {ids_to_scrape}" )
print( f"{start_date.format('YYYY-MM-DD')} - {end_date.format('YYYY-MM-DD')} ({num_days} days)" )

day_num = 0
with progressbar.ProgressBar(max_value=num_days) as bar:
    for day_start, day_end in date_range:
        bar.update(day_num)
        #print( f"Grabbing data for {day_start.format('YYYY-MM-DD')}" )
        for c in ids_to_scrape:
            try:                
                prices = wait_for_limit(cg, c, day_start.timestamp(), day_end.timestamp() )
                if prices["prices"]:
                    for price in prices["prices"]:
                        files[c].write(f"{price[0]},{price[1]}\n")
            except Exception as e:
                # simply log the coin and timestamp, not hard to regrab this data
                error_file.write(f"{c},{day_start.timestamp()},{e}\n")
        day_num += 1
