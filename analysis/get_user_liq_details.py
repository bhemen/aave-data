import pandas as pd
from web3 import Web3
from web3.providers.rpc import HTTPProvider
import progressbar
import sys
import os
from tqdm import tqdm
sys.path.append("../scripts/")
from utils import get_cached_abi, get_proxy_address

#Connect to an ethereum node
api_url = ''
provider = HTTPProvider(api_url)
web3 = Web3(provider)

#Get Aave V2 protocol data provider contract
aave_protocol_data_provider_address = Web3.to_checksum_address("0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d")
aave_protocol_data_provider_abi = get_cached_abi( aave_protocol_data_provider_address )
aave_protocol_data_provider_contract = web3.eth.contract( address=aave_protocol_data_provider_address, abi=aave_protocol_data_provider_abi )

#Get Aave V2 lending pool contract
aave_lending_pool_address = Web3.to_checksum_address("0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9")
aave_lending_pool_abi = get_proxy_address(web3, aave_lending_pool_address) #The lending pool contract is a proxy, we want the ABI of the lending pool, not of the proxy
aave_lending_pool_contract = web3.eth.contract( address=aave_lending_pool_address, abi = aave_lending_pool_abi)

# Calling getAllReservesTokens function from Protocol Data Provider Contract => https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens
reserve_tokens = aave_protocol_data_provider_contract.functions.getAllReservesTokens().call()
#reserve_tokens looks like:
#[('USDT', '0xdAC17F958D2ee523a2206206994597C13D831ec7'), ('WBTC', '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'), ('WETH', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'), ('YFI', '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e'), ('ZRX', '0xE41d2489571d322189246DaFA5ebDe1F4699F498'), ('UNI', '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'), ('AAVE', '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9'), ('BAT', '0x0D8775F648430679A709E98d2b0Cb6250d2887EF'), ('BUSD', '0x4Fabb145d64652a948d72533023f6E7A623C7C53'), ('DAI', '0x6B175474E89094C44Da98b954EedeAC495271d0F'), ('ENJ', '0xF629cBd94d3791C9250152BD8dfBDF380E2a3B9c'), ('KNC', '0xdd974D5C2e2928deA5F71b9825b8b646686BD200'), ('LINK', '0x514910771AF9Ca656af840dff83E8264EcF986CA'), ('MANA', '0x0F5D2fB29fb7d3CFeE444a200298f468908cC942'), ('MKR', '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2'), ('REN', '0x408e41876cCCDC0F92210600ef50372656052a38'), ('SNX', '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F'), ('sUSD', '0x57Ab1ec28D129707052df4dF418D58a2D46d5f51'), ('TUSD', '0x0000000000085d4780B73119b644AE5ecd22b376'), ('USDC', '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'), ('CRV', '0xD533a949740bb3306d119CC777fa900bA034cd52'), ('GUSD', '0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd'), ('BAL', '0xba100000625a3754423978a60c9317c58a424e3D'), ('xSUSHI', '0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272'), ('renFIL', '0xD5147bc8e386d91Cc5DBE72099DAC6C9b99276F5'), ('RAI', '0x03ab458634910AaD20eF5f1C8ee96F1D6ac54919'), ('AMPL', '0xD46bA6D942050d489DBd938a2C909A5d5039A161'), ('USDP', '0x8E870D67F660D95d5be530380D0eC0bd388289E1'), ('DPI', '0x1494CA1F11D487c2bBe4543E90080AeBa4BA3C2b'), ('FRAX', '0x853d955aCEf822Db058eb8505911ED77F175b99e'), ('FEI', '0x956F47F50A910163D8BF957Cf5846D573E7f87CA'), ('stETH', '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84'), ('ENS', '0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72'), ('UST', '0xa693B19d2931d498c5B318dF961919BB4aee87a5'), ('CVX', '0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B'), ('1INCH', '0x111111111117dC0aa78b770fA6A738034120C302'), ('LUSD', '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0')]

#Getting the top 10 users who had the highest debt left after their collateral was liquidated completely
df = pd.read_csv("../data/aave_liquidation_loss_v2.csv")
df.sort_values(by = 'debtLeft (in USD)', ascending=False, inplace = True)
df.reset_index(drop = True, inplace=True)
user_df = df[:10]

#Getting decimals for each token
atokens_df = pd.read_csv("../data/aave_atokens_v2.csv")
decimals = { r['symbol']: r['decimals'] for _, r in atokens_df.iterrows() }

lending_pool_df = pd.read_csv("../data/lending_pool_logs_v2.csv", low_memory=False)

for i in range(len(user_df)):
	
	user = Web3.to_checksum_address(user_df.borrower.iloc[i])

	start_block = lending_pool_df[(lending_pool_df['onBehalfOf'] == user) & (lending_pool_df['event'] == 'Borrow')].sort_values(by='blockNumber').reset_index(drop=True).blockNumber.iloc[0]
	end_block = user_df.block.iloc[i]
	blocks = [ctr for ctr in range(start_block, end_block, 5000)] + [end_block]

	rows = []
	with progressbar.ProgressBar(max_value=len(blocks)) as bar:
		for x,block_num in enumerate(blocks):
			block = web3.eth.get_block(int(block_num))

			try:
				user_account_data = aave_lending_pool_contract.functions.getUserAccountData(user).call(block_identifier=int(block_num))

			except Exception as e:
				with open( "../data/aave_user_liq_analysis_errors.csv", "a" ) as f:
					f.write( f"Error calling getUserAccountData at {block_num} for user {user}" )
				continue

			try:
				bitmask = aave_lending_pool_contract.functions.getUserConfiguration(user).call(block_identifier = int(block_num) - 10)[0]
		
			except Exception as e:
				with open( "../data/aave_user_liq_analysis_errors.csv", "a" ) as f:
					f.write( f"Error calling getUserConfiguration at {block_num} for user {user}" )
				continue
			
			#Getting the collateral and debt assets of the user at a given block
			bitmask = bin(bitmask)[2:]
			debt_bits = [bitmask[i] for i in range(len(bitmask) - 1, -1, -2)]
			collateral_bits = [bitmask[i] for i in range(len(bitmask) - 2, -1, -2)]
			collateral_assets = [reserve_tokens[i] for i, bit in enumerate(collateral_bits) if bit == '1']
			debt_assets = [reserve_tokens[i] for i, bit in enumerate(debt_bits) if bit == '1']

			row = { 'block': block_num,
					'timestamp': block.timestamp,
					'user': user,
					'totalCollateral': user_account_data[0],
					'totalDebt': user_account_data[1],
					'healthFactor': round((user_account_data[5])/(10**18),2) }

			#Getting collateral and debt values for the involved assets 
			for symbol,address in reserve_tokens:

				row['symbol'] = symbol
				row['tokenAddress'] = address
				if (symbol,address) in collateral_assets:
					try:
						row[f'{symbol}_collateral'] = aave_protocol_data_provider_contract.functions.getUserReserveData(Web3.to_checksum_address(address), user).call(block_identifier=int(block_num)-10)[0]
					except Exception as e:
						with open( "../data/aave_user_liq_analysis_errors.csv", "a" ) as f:
							f.write( f"Error calling getUserReserveData at {block_num} for user {user}" )
						row[f'{symbol}_collateral'] = 0
				else:
					row[f'{symbol}_collateral'] = 0
				
				if (symbol,address) in debt_assets:
					try:
						user_reserve_data = aave_protocol_data_provider_contract.functions.getUserReserveData(Web3.to_checksum_address(address), user).call(block_identifier=int(block_num)-10)
						row[f'{symbol}_debt'] = user_reserve_data[1] + user_reserve_data[2]
					except Exception as e:
						with open( "../data/aave_user_liq_analysis_errors.csv", "a" ) as f:
							f.write( f"Error calling getUserReserveData at {block_num} for user {user}" )
						row[f'{symbol}_debt'] = 0
				else:
					row[f'{symbol}_debt'] = 0

			rows.append(row)
			bar.update(x)

	new_df = pd.DataFrame(rows)

	#Dropping unnecessary and empty columns
	new_df.drop(['symbol'], axis=1, inplace=True)
	for col in new_df.columns:
		if (new_df[col] == 0).all():
			new_df.drop([col], axis=1, inplace = True)

	print("Adding USD prices")
	#Adding WETH_USD_price column manually because we need it later to convert totalCollateral and totalDebt which are in WETH to USD
	eth_df = pd.read_csv(f"../data/usd_prices/WETH_usd.csv")
	eth_df.rename(columns={'USD_price': f"WETH_USD_price"}, inplace= True)
	eth_df.drop(['symbol'], axis=1, inplace=True)
	eth_df.sort_values(by="timestamp", inplace=True)
	eth_df['timestamp'] = eth_df['timestamp']//1000
	new_df = pd.merge_asof(new_df, eth_df, on = 'timestamp', direction='nearest')

	#Adding USD Prices to the dataframe
	for col in tqdm(new_df.columns):
		for symbol,address in reserve_tokens:
			if f"{symbol}_USD_price" not in new_df.columns:
				if col == f"{symbol}_collateral" or col == f"{symbol}_debt":
					usd_df = pd.read_csv(f"../data/usd_prices/{symbol}_usd.csv")
					usd_df.rename(columns={'USD_price': f"{symbol}_USD_price"}, inplace= True)
					usd_df.drop(['symbol'], axis=1, inplace=True)
					usd_df.sort_values(by="timestamp", inplace=True)
					usd_df['timestamp'] = usd_df['timestamp']//1000
					new_df = pd.merge_asof(new_df, usd_df, on = 'timestamp', direction='nearest')
	
	#Converting dtype of relevant columns to float
	for col in new_df.columns:
		if '_collateral' in col or '_debt' in col:
			new_df[col] = new_df[col].astype(float)

	new_df['totalCollateral'] = new_df['totalCollateral'].astype(float)
	new_df['totalDebt'] = new_df['totalDebt'].astype(float)

	#Adding columns with USD values
	for symbol,address in reserve_tokens:
		if f"{symbol}_collateral" in new_df.columns:
			new_df[f"{symbol}_collateral (in USD)"] = (new_df[f"{symbol}_collateral"]/10**(decimals[symbol])) * new_df[f"{symbol}_USD_price"]
		if f"{symbol}_debt" in new_df.columns:
			new_df[f"{symbol}_debt (in USD)"] = (new_df[f"{symbol}_debt"]/10**(decimals[symbol])) * new_df[f"{symbol}_USD_price"]

	new_df['totalCollateral (in USD)'] = (new_df['totalCollateral']/(10**18))* new_df['WETH_USD_price']
	new_df['totalDebt (in USD)'] = (new_df['totalDebt']/(10**18))* new_df['WETH_USD_price']

	#Creating a new directory and saving
	if not os.path.exists("../data/aave_user_details_v2/"):
		os.makedirs("../data/aave_user_details_v2/")
	new_df.to_csv(f"../data/aave_user_details_v2/{user}_details_v2.csv",index=False)