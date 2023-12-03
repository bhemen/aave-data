# Import necessary libraries
import pandas as pd
from web3 import Web3
from web3.providers.rpc import HTTPProvider
from utils import get_cached_abi, get_proxy_address
import progressbar
import json
import sys

# Connect to Ethereum node
api_url = ""
provider = HTTPProvider(api_url)
web3 = Web3(provider)

#Get Aave V2 protocol data provider contract
aave_protocol_data_provider_address = Web3.toChecksumAddress("0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d")
aave_protocol_data_provider_abi = get_cached_abi( aave_protocol_data_provider_address )
aave_protocol_data_provider_contract = web3.eth.contract( address=aave_protocol_data_provider_address, abi=aave_protocol_data_provider_abi )

#Get Aave V2 lending pool contract
aave_lending_pool_address = Web3.to_checksum_address("0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9")
aave_lending_pool_abi = get_proxy_address(web3, aave_lending_pool_address) #The lending pool contract is a proxy, we want the ABI of the lending pool, not of the proxy
#aave_lending_pool_abi = get_cached_abi(lending_pool_proxy_address)
aave_lending_pool_contract = web3.eth.contract( address=aave_lending_pool_address, abi=aave_lending_pool_abi)

# Calling getAllReservesTokens function from Protocol Data Provider Contract => https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens
reserve_tokens = aave_protocol_data_provider_contract.functions.getAllReservesTokens().call()
#reserve_tokens looks like:
#[('USDT', '0xdAC17F958D2ee523a2206206994597C13D831ec7'), ('WBTC', '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'), ('WETH', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'), ('YFI', '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e'), ('ZRX', '0xE41d2489571d322189246DaFA5ebDe1F4699F498'), ('UNI', '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'), ('AAVE', '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9'), ('BAT', '0x0D8775F648430679A709E98d2b0Cb6250d2887EF'), ('BUSD', '0x4Fabb145d64652a948d72533023f6E7A623C7C53'), ('DAI', '0x6B175474E89094C44Da98b954EedeAC495271d0F'), ('ENJ', '0xF629cBd94d3791C9250152BD8dfBDF380E2a3B9c'), ('KNC', '0xdd974D5C2e2928deA5F71b9825b8b646686BD200'), ('LINK', '0x514910771AF9Ca656af840dff83E8264EcF986CA'), ('MANA', '0x0F5D2fB29fb7d3CFeE444a200298f468908cC942'), ('MKR', '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2'), ('REN', '0x408e41876cCCDC0F92210600ef50372656052a38'), ('SNX', '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F'), ('sUSD', '0x57Ab1ec28D129707052df4dF418D58a2D46d5f51'), ('TUSD', '0x0000000000085d4780B73119b644AE5ecd22b376'), ('USDC', '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'), ('CRV', '0xD533a949740bb3306d119CC777fa900bA034cd52'), ('GUSD', '0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd'), ('BAL', '0xba100000625a3754423978a60c9317c58a424e3D'), ('xSUSHI', '0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272'), ('renFIL', '0xD5147bc8e386d91Cc5DBE72099DAC6C9b99276F5'), ('RAI', '0x03ab458634910AaD20eF5f1C8ee96F1D6ac54919'), ('AMPL', '0xD46bA6D942050d489DBd938a2C909A5d5039A161'), ('USDP', '0x8E870D67F660D95d5be530380D0eC0bd388289E1'), ('DPI', '0x1494CA1F11D487c2bBe4543E90080AeBa4BA3C2b'), ('FRAX', '0x853d955aCEf822Db058eb8505911ED77F175b99e'), ('FEI', '0x956F47F50A910163D8BF957Cf5846D573E7f87CA'), ('stETH', '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84'), ('ENS', '0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72'), ('UST', '0xa693B19d2931d498c5B318dF961919BB4aee87a5'), ('CVX', '0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B'), ('1INCH', '0x111111111117dC0aa78b770fA6A738034120C302'), ('LUSD', '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0')]

#Define output and error file paths
outfile = "../data/borrow_rate_attributes_v2.csv"
errorfile = "../data/aave_borrow_rate_attributes_errors_v2.csv"

with open( "abis/aave_v2_interest_rate_strategy.abi", "r" ) as f:
	interest_rate_strategy_abi = json.load(f)

#Define starting and ending block heights
latest_block = web3.eth.block_number
start_block = 11275902

# Looking at every 100th block starting from the current block down to the start block
blocks = list(range(latest_block, start_block-1, -100))

# Create an empty list to store data rows
rows = []

with progressbar.ProgressBar(max_value=len(blocks)) as bar:

	for i,block_num in enumerate(blocks):

		#Getting block info for a block_num to get its timestamp
		block = web3.eth.get_block(block_num)

		for symbol,address in reserve_tokens:

			#Getting Interest Rate Strategy Contract using the getReserveData function of the Lending Pool Contract
			try:
				interest_rate_strategy_address = Web3.toChecksumAddress(aave_lending_pool_contract.functions.getReserveData(address).call(block_identifier=block_num)[-2])
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getReserveData at {block_num} for asset {symbol} on contract {aave_lending_pool_address}\n" )
				continue
			try:
				#interest_rate_strategy_abi = get_cached_abi(interest_rate_strategy_address) #This works, but it takes too long, since querying Etherscan is slow
				interest_rate_strategy_contract = web3.eth.contract( address=interest_rate_strategy_address, abi=interest_rate_strategy_abi )
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error creating interest_rate_strategy_contract {interest_rate_strategy_address}" )
				continue

			if interest_rate_strategy_abi is not None:
				#Calling EXCESS_UTILIZATION_RATE function from interest_rate_strategy_contract
				try:
					excessUtilizationRate = interest_rate_strategy_contract.functions.EXCESS_UTILIZATION_RATE().call(block_identifier=block_num)
				except Exception as e:
					with open( errorfile, "a" ) as f:
						f.write( f"Error calling EXCESS_UTILIZATION_RATE at {block_num} for asset {symbol} on contract {interest_rate_strategy_address}\n" )
					continue

				#Calling OPTIMAL_UTILIZATION_RATE function from interest_rate_strategy_contract
				try:
					optimalUtilizationRate = interest_rate_strategy_contract.functions.OPTIMAL_UTILIZATION_RATE().call(block_identifier=block_num)
				except Exception as e:
					with open( errorfile, "a" ) as f:
						f.write( f"Error calling OPTIMAL_UTILIZATION_RATE at {block_num} for asset {symbol} on contract {interest_rate_strategy_address}\n" )
					continue

				#Calling addressesProvider function from interest_rate_strategy_contract
				try:
					addressesProvider = interest_rate_strategy_contract.functions.addressesProvider().call(block_identifier=block_num)
				except Exception as e:
					with open( errorfile, "a" ) as f:
						f.write( f"Error calling addressesProvider at {block_num} for asset {symbol} on contract {interest_rate_strategy_address}\n" )
					continue

				#Calling baseVariableBorrowRate function from interest_rate_strategy_contract
				try:
					baseVariableBorrowRate = interest_rate_strategy_contract.functions.baseVariableBorrowRate().call(block_identifier=block_num)
				except Exception as e:
					with open( errorfile, "a" ) as f:
						f.write( f"Error calling baseVariableBorrowRate at {block_num} for asset {symbol} on contract {interest_rate_strategy_address}\n" )
					continue

				#Calling getMaxVariableBorrowRate function from interest_rate_strategy_contract
				try:
					maxVariableBorrowRate = interest_rate_strategy_contract.functions.getMaxVariableBorrowRate().call(block_identifier=block_num)
				except Exception as e:
					with open( errorfile, "a" ) as f:
						f.write( f"Error calling getMaxVariableBorrowRate at {block_num} for asset {symbol}\n" )
					continue

				#Calling stableRateSlope1 function from interest_rate_strategy_contract
				try:
					stableRateSlope1 = interest_rate_strategy_contract.functions.stableRateSlope1().call(block_identifier=block_num)
				except Exception as e:
					with open( errorfile, "a" ) as f:
						f.write( f"Error calling stableRateSlope1 at {block_num} for asset {symbol}\n" )
					continue

				#Calling stableRateSlope2 function from interest_rate_strategy_contract
				try:
					stableRateSlope2 = interest_rate_strategy_contract.functions.stableRateSlope2().call(block_identifier=block_num)
				except Exception as e:
					with open( errorfile, "a" ) as f:
						f.write( f"Error calling stableRateSlope2 at {block_num} for asset {symbol}\n" )
					continue
				
				#Calling variableRateSlope1 function from interest_rate_strategy_contract
				try:
					variableRateSlope1 = interest_rate_strategy_contract.functions.variableRateSlope1().call(block_identifier=block_num)
				except Exception as e:
					with open( errorfile, "a" ) as f:
						f.write( f"Error calling variableRateSlope1 at {block_num} for asset {symbol}\n" )
					continue

				#Calling variableRateSlope2 function from interest_rate_strategy_contract
				try:
					variableRateSlope2 = interest_rate_strategy_contract.functions.variableRateSlope2().call(block_identifier=block_num)
				except Exception as e:
					with open( errorfile, "a" ) as f:
						f.write( f"Error calling variableRateSlope2 at {block_num} for asset {symbol}\n" )
					continue

				# Compile the data into a row and append to the rows list
				row = { 'block': block_num,
						'timestamp': block.timestamp,
						'symbol': symbol,
						'address': address,
						'interestRateStrategyAddress': interest_rate_strategy_address,
						'excessUtilizationRate': excessUtilizationRate,
						'optimalUtilizationRate': optimalUtilizationRate, 
						'addressesProvider': addressesProvider,
						'baseVariableBorrowRate': baseVariableBorrowRate, 
						'maxVariableBorrowRate': maxVariableBorrowRate,
						'stableRateSlope1': stableRateSlope1, 
						'stableRateSlope2': stableRateSlope2,
						'variableRateSlope1': variableRateSlope1, 
						'variableRateSlope2': variableRateSlope2 }
				rows.append(row)
				bar.update(i)
			else:
				with open( errorfile, "a" ) as f:
					f.write( f"Interest Rate Strategy Abi not found for asset {symbol} at block number {block_num}" )
				continue

# Convert the rows list to a Pandas DataFrame and save to CSV
df = pd.DataFrame(rows)
df.to_csv(outfile,index=False)
