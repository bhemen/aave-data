# Import necessary libraries
import pandas as pd

collateralization_file = "../data/aave_collateralization_v2.csv"

df = pd.read_csv( collateralization_file, dtype={'symbol':str, 'address': str, 'timestamp':int, 'availableLiquidity': float, 'totalStableDebt': float, 'totalVariableDebt': float, 'liquidityRate': float, 'variableBorrowRate': float, 'stableBorrowRate': float, 'averageStableBorrowRate': float, 'liquidityIndex': float, 'variableBorrowIndex': float } )

#Getting decimals for each token
meta_df = pd.read_csv("../data/aave_collateralization_meta_v2.csv")
decimals = { r['symbol']: r['decimals'] for i, r in meta_df.iterrows() }

df['decimals'] = df.symbol.apply( lambda x: decimals[x] )

#Creating a dataframe for token prices in USD 
usd_df = pd.DataFrame()
for symbol in decimals.keys():
    try:
        temp_df = pd.read_csv(f"../data/usd_prices/{symbol}_usd.csv", dtype={'timestamp': int, 'symbol':str, 'USD_price': float} )
#        temp_df.astype(dtype={'timestamp':int, 'symbol': str }, copy=False)
        temp_df.sort_values(by=['timestamp'], inplace=True)
        temp_df['timestamp'] = temp_df['timestamp']//1000
        usd_df = pd.concat( [usd_df,temp_df] )
    except Exception as e:
        print( f"Couldn't get prices for {symbol}" )

#Filtering and sorting the USD dataframe
usd_df.sort_values(by=['timestamp'], inplace=True)
df.sort_values(by=['timestamp'], inplace=True)

if 'USD_price' in df.columns:
	df.drop(columns=['USD_price'],inplace=True)

#Merging and saving
new_df = pd.merge_asof(df, usd_df, on = 'timestamp', by = 'symbol', direction='nearest')
new_df['date'] = pd.to_datetime(df['timestamp'], unit='s')

token_cols = ['availableLiquidity','totalStableDebt','totalVariableDebt']
for c in token_cols:
	new_df[f"{c}_USD"] = new_df[c]*new_df['USD_price']/(10**new_df['decimals'])

new_df.to_csv("../data/aave_collateralization_usd_v2.csv")



