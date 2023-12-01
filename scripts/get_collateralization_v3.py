import pandas as pd
from web3 import Web3
import json
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from utils import get_cached_abi
import progressbar

api_url = "" # your api here
provider = HTTPProvider(api_url)
web3 = Web3(provider)

#AaveProtocolDataProvider Contract
aave_protocol_data_provider = Web3.to_checksum_address("0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3")
aave_protocol_data_provider_abi = get_cached_abi( aave_protocol_data_provider )
aave_protocol_data_provider_contract = web3.eth.contract( address=aave_protocol_data_provider, abi=aave_protocol_data_provider_abi )

aave_pool_address = Web3.to_checksum_address("0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2")
aave_pool_abi = get_cached_abi( aave_pool_address )
aave_pool_contract = web3.eth.contract( address=aave_pool_address, abi=aave_pool_abi )

#https://docs.aave.com/developers/core-contracts/aaveprotocoldataprovider#getallreservestokens
reserve_tokens = aave_protocol_data_provider_contract.functions.getAllReservesTokens().call()
# [('WETH', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'), ('wstETH', '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0'), ('WBTC', '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'), ('USDC', '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'), ('DAI', '0x6B175474E89094C44Da98b954EedeAC495271d0F'), ('LINK', '0x514910771AF9Ca656af840dff83E8264EcF986CA'), ('AAVE', '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9'), ('cbETH', '0xBe9895146f7AF43049ca1c1AE358B0541Ea49704'), ('USDT', '0xdAC17F958D2ee523a2206206994597C13D831ec7'), ('rETH', '0xae78736Cd615f374D3085123A210448E74Fc6393'), ('LUSD', '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0'), ('CRV', '0xD533a949740bb3306d119CC777fa900bA034cd52'), ('MKR', '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2'), ('SNX', '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F'), ('BAL', '0xba100000625a3754423978a60c9317c58a424e3D'), ('UNI', '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'), ('LDO', '0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32'), ('ENS', '0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72'), ('1INCH', '0x111111111117dC0aa78b770fA6A738034120C302'), ('FRAX', '0x853d955aCEf822Db058eb8505911ED77F175b99e'), ('GHO', '0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f')]

outfile = "data/aave_v3_collateralization.csv"
errorfile = "data/aave_v3_collateralization_errors.csv"

latest_block = web3.eth.block_number

start_block = 16291078

# #[latest_block, .... , start_block]
blocks = list(range(latest_block, start_block-1, -1))

rows = []
with progressbar.ProgressBar(max_value=len(blocks)) as bar:
	for i,block_num in enumerate(blocks):
		block = web3.eth.get_block(block_num)
		for symbol,address in reserve_tokens:
			try:
				token_info = aave_protocol_data_provider_contract.functions.getReserveData(address).call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getReserveData at {block_num} for asset {symbol}\n" )
				continue

			try:
				reserveNormalizedIncome = aave_pool_contract.functions.getReserveNormalizedIncome(address).call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getReserveNormalizedIncome at {block_num} for asset {symbol}\n" )
				continue
		
			try:
				reserveNormalizedVariableDebt = aave_pool_contract.functions.getReserveNormalizedVariableDebt(address).call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getReserveNormalizedVariableDebt at {block_num} for asset {symbol}\n" )
				continue
			
			row = { 'block': block_num,
					'timestamp': block.timestamp,
					'symbol': symbol,
					'address': address,
					'unbacked': token_info[0],
					'accruedToTreasuryScaled': token_info[1],
					'totalAToken': token_info[2],
					'totalStableDebt': token_info[3], 
					'totalVariableDebt': token_info[4],
					'liquidityRate': token_info[5], 
					'variableBorrowRate': token_info[6],
					'stableBorrowRate': token_info[7], 
					'averageStableBorrowRate': token_info[8],
					'liquidityIndex': token_info[9], 
					'variableBorrowIndex': token_info[10],
					'lastUpdateTimestamp': token_info[11],
					'reserveNormalizedIncome': reserveNormalizedIncome,
					'reserveNormalizedVariableDebt': reserveNormalizedVariableDebt
					}
			rows.append(row)
			bar.update(i)

df = pd.DataFrame(rows)

df.to_csv(outfile,index=False)