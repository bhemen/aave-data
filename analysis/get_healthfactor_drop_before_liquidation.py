# Required imports
import pandas as pd
from web3 import Web3
import sys
from tqdm import tqdm
import numpy as np
sys.path.append("../scripts/")
from utils import get_proxy_address, get_cached_abi
from web3.providers.rpc import HTTPProvider
import csv
import os

# Connect to an Ethereum Node
api_url = "http://localhost:8545"  # your node url here
provider = HTTPProvider(api_url)
web3 = Web3(provider)

# Get Aave V2 lending pool contract
aave_lending_pool_address = Web3.to_checksum_address("0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9")
#aave_lending_pool_abi = get_proxy_address(web3, aave_lending_pool_address)  # The lending pool contract is a proxy, we want the ABI of the lending pool, not of the proxy
aave_lending_pool_abi = get_cached_abi(aave_lending_pool_address)  # The lending pool contract is a proxy, we want the ABI of the lending pool, not of the proxy
aave_lending_pool_contract = web3.eth.contract(address=aave_lending_pool_address, abi=aave_lending_pool_abi)

# Load the liquidations DataFrame
#liquidations_df = pd.read_csv("../data/aave_v2_LiquidationCall.csv")
liquidations_df = pd.read_csv("../data/aave_v2_LiquidationCall_with_total_collateral_debt_final.csv")
liquidations_df.sort_values(by='block_timestamp_unix', inplace=True)
liquidations_df.reset_index(drop=True, inplace=True)

borrow_df = pd.read_csv("../data/aave_v2_Borrow.csv")
borrow_df.sort_values(by='block_timestamp_unix', inplace=True)
borrow_df.reset_index(drop=True, inplace=True)

# Add new columns for health factor block and blocks until liquidation if not already present
new_cols = ['block_number_when_healthfactor_above_one','blocks_for_liquidation']
added_cols = list(set(new_cols).difference(liquidations_df.columns))

if len(added_cols) > 0:
	for c in added_cols:
		liquidations_df[c] = -1
	liquidations_df = liquidations_df.astype( { c: int for c in added_cols } )

# Path to output and error files
output_file = "../data/liquidations_health_factor_details.csv"
partial_output_file = "../data/liquidations_health_factor_details_partial.csv"
errors_file = "../data/liquidations_health_factor_errors_updated.csv"

# Function to get user account data
def get_health_factor(user, block_number):
	try:
		user_data = aave_lending_pool_contract.functions.getUserAccountData(user).call(block_identifier=block_number)
		health_factor = user_data[-1]  # Last element in response is health factor
		return health_factor
	except Exception as e:
		with open(errors_file, "a") as f:
			f.write(f"Error calling getUserAccountData for user {user} at block {block_number}\n")
		return np.nan

def get_first_borrow_block_number(user):
	# Filter the DataFrame for the given user
	user_df = borrow_df[borrow_df['onBehalfOf'] == user]
	
	# Check if user_df is not empty
	if not user_df.empty:
		# Get the first blockNumber from the sorted DataFrame
		first_block_number = user_df['blockNumber'].iloc[0]
		return first_block_number
	else:
		return None  # Return None if the user doesn't exist in the DataFrame

# Setup partial results file
headers = list(liquidations_df.columns) + added_cols
if not os.path.exists(partial_output_file):
	with open(partial_output_file, 'w', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=headers)
		writer.writeheader()
	completed_rows = set()
else:
	partial_df = pd.read_csv( partial_output_file )
	completed_rows = set( partial_df.transactionHash.unique() )

unfinished_df = liquidations_df[ ~liquidations_df.transactionHash.isin(completed_rows) ]
assert len( unfinished_df ) + len(completed_rows) == len(liquidations_df), 'Uncompleted + Completed != Total' 

# Iterate over each row in the dataframe
for i in tqdm(range(len(liquidations_df))):
	if liquidations_df.transactionHash.iloc[i] in completed_rows:
		continue

	user = liquidations_df.user.iloc[i]
	block_number = int(liquidations_df.blockNumber.iloc[i])
	first_borrow_block = get_first_borrow_block_number(user)
	
	current_block = block_number
	
	# Go back block by block until health factor > 1
	for current_block in range( block_number, first_borrow_block, -1 ):
		health_factor = get_health_factor(user, current_block)
		
		# If health factor is valid and >= 1, we stop
		if health_factor and health_factor >= 10**18:
			break
		 
	# Update DataFrame with the results
	liquidations_df.at[i, 'block_number_when_healthfactor_above_one'] = int(current_block)
	liquidations_df.at[i, 'blocks_for_liquidation'] = int(block_number) - int(current_block)
	row_dict = liquidations_df.iloc[i].to_dict()
	with open(partial_output_file, 'a', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=row_dict.keys())
		writer.writerow(row_dict)

liquidations_df.to_csv(output_file, index=False)
