# Import necessary libraries
import pandas as pd
from web3 import Web3
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

reserve_tokens = aave_protocol_data_provider_contract.functions.getAllReservesTokens().call()

outfile = "data/aave_v3_borrow_rate_attributes.csv"
errorfile = "data/aave_v3_borrow_rate_attributes_errors.csv"

latest_block = web3.eth.block_number

#Lending Pool Deploy Block
start_block = 16291127

#[latest_block, .... , start_block]
blocks = list(range(latest_block, start_block-1, -1))

rows = []
with progressbar.ProgressBar(max_value=len(blocks)) as bar:
	for i,block_num in enumerate(blocks):
		block = web3.eth.get_block(block_num)
		for symbol,address in reserve_tokens:
			try:
				interest_rate_strategy_address = Web3.to_checksum_address(aave_pool_contract.functions.getReserveData(address).call(block_identifier=block_num)[-4])
				interest_rate_strategy_abi = get_cached_abi(interest_rate_strategy_address)
				interest_rate_strategy_contract = web3.eth.contract( address=interest_rate_strategy_address, abi=interest_rate_strategy_abi )
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getReserveData at {block_num} for asset {symbol}\n" )
				continue

			try:
				maxExcessStableToTotalDebtRatio = interest_rate_strategy_contract.functions.MAX_EXCESS_STABLE_TO_TOTAL_DEBT_RATIO().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling MAX_EXCESS_STABLE_TO_TOTAL_DEBT_RATIO at {block_num} for asset {symbol}\n" )
				continue

			try:
				maxExcessUsageRatio = interest_rate_strategy_contract.functions.MAX_EXCESS_USAGE_RATIO().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling MAX_EXCESS_USAGE_RATIO at {block_num} for asset {symbol}\n" )
				continue
			
			try:
				optimalStableToTotalDebtRatio = interest_rate_strategy_contract.functions.OPTIMAL_STABLE_TO_TOTAL_DEBT_RATIO().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling OPTIMAL_STABLE_TO_TOTAL_DEBT_RATIO at {block_num} for asset {symbol}\n" )
				continue

			try:
				optimalUsageRatio = interest_rate_strategy_contract.functions.OPTIMAL_USAGE_RATIO().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling OPTIMAL_USAGE_RATIO at {block_num} for asset {symbol}\n" )
				continue

			try:
				addressesProvider = interest_rate_strategy_contract.functions.ADDRESSES_PROVIDER().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling ADDRESSES_PROVIDER at {block_num} for asset {symbol}\n" )
				continue

			try:
				baseStableBorrowRate = interest_rate_strategy_contract.functions.getBaseStableBorrowRate().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getBaseStableBorrowRate at {block_num} for asset {symbol}\n" )
				continue

			try:
				baseVariableBorrowRate = interest_rate_strategy_contract.functions.getBaseVariableBorrowRate().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getBaseVariableBorrowRate at {block_num} for asset {symbol}\n" )
				continue

			try:
				maxVariableBorrowRate = interest_rate_strategy_contract.functions.getMaxVariableBorrowRate().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getMaxVariableBorrowRate at {block_num} for asset {symbol}\n" )
				continue
			
			try:
				stableRateExcessOffset = interest_rate_strategy_contract.functions.getStableRateExcessOffset().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getStableRateExcessOffset at {block_num} for asset {symbol}\n" )
				continue

			try:
				stableRateSlope1 = interest_rate_strategy_contract.functions.getStableRateSlope1().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getStableRateSlope1 at {block_num} for asset {symbol}\n" )
				continue
			try:
				stableRateSlope2 = interest_rate_strategy_contract.functions.getStableRateSlope2().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getStableRateSlope2 at {block_num} for asset {symbol}\n" )
				continue
			try:
				variableRateSlope1 = interest_rate_strategy_contract.functions.getVariableRateSlope1().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getVariableRateSlope1 at {block_num} for asset {symbol}\n" )
				continue
			try:
				variableRateSlope2 = interest_rate_strategy_contract.functions.getVariableRateSlope2().call(block_identifier=block_num)
			except Exception as e:
				with open( errorfile, "a" ) as f:
					f.write( f"Error calling getVariableRateSlope2 at {block_num} for asset {symbol}\n" )
				continue

			row = { 'block': block_num,
					'timestamp': block.timestamp,
					'symbol': symbol,
					'address': address,
					'maxExcessStableToTotalDebtRatio': maxExcessStableToTotalDebtRatio,
					'excessUtilizationRatio': maxExcessUsageRatio,
					'optimalStableToTotalDebtRatio': optimalStableToTotalDebtRatio,
					'optimalUtilizationRatio': optimalUsageRatio, 
					'addressesProvider': addressesProvider,
					'baseStableBorrowRate': baseStableBorrowRate,
					'baseVariableBorrowRate': baseVariableBorrowRate, 
					'maxVariableBorrowRate': maxVariableBorrowRate,
					'stableRateExcessOffset': stableRateExcessOffset,
					'stableRateSlope1': stableRateSlope1, 
					'stableRateSlope2': stableRateSlope2,
					'variableRateSlope1': variableRateSlope1, 
					'variableRateSlope2': variableRateSlope2 }
			rows.append(row)
			bar.update(i)

df = pd.DataFrame(rows)
df.to_csv(outfile,index=False)