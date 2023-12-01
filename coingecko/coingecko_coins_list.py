from pycoingecko import CoinGeckoAPI
import pandas as pd

cg = CoinGeckoAPI()

allcgcoins = cg.get_coins_list()

rows = []
for c in allcgcoins:
	rows.append( { 'id': c['id'], 'symbol': c['symbol'], 'name': c['name'] } )

df = pd.DataFrame( rows )

df.to_csv( "coin_list.csv", index=False )
