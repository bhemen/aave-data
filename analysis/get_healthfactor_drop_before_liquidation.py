# Required imports
import pandas as pd
from web3 import Web3
import sys
from tqdm import tqdm
import numpy as np
import time
import os
sys.path.append("../scripts/")
from utils import get_proxy_address, get_cached_abi
from web3.providers.rpc import HTTPProvider

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

# Add new columns for health factor block and blocks until liquidation if not already present
if 'health_factor_above_one_block' not in liquidations_df.columns:
    liquidations_df['health_factor_above_one_block'] = np.nan
if 'blocks_for_liquidation' not in liquidations_df.columns:
    liquidations_df['blocks_for_liquidation'] = np.nan

# Path to checkpoint and error files
checkpoint_file = "../data/liquidations_health_factor_final.csv"
errors_file = "../data/liquidations_health_factor_errors.csv"

# Check if the checkpoint file already exists, and load progress if it does
if os.path.exists(checkpoint_file):
    processed_df = pd.read_csv(checkpoint_file)
    start_idx = len(processed_df)  # Start from where we left off
    header_needed = False  # Don't need header if resuming
else:
    start_idx = 0  # Start from the beginning
    header_needed = True  # First time saving, so include headers

# Function to get user account data
def get_health_factor(user, block_number):
    try:
        user_data = aave_lending_pool_contract.functions.getUserAccountData(user).call(block_identifier=block_number)
        health_factor = user_data[-1]  # Last element in response is health factor
        return health_factor
    except Exception as e:
        with open(errors_file, "a") as f:
            f.write(f"Error calling getUserAccountData for user {user} at block {block_number}: {e}\n")
        return np.nan

# Iterate over each row in the dataframe, starting from the last processed index
for idx, row in tqdm(liquidations_df.iloc[start_idx:].iterrows(), total=liquidations_df.shape[0] - start_idx, initial=start_idx):
    user = row['user']
    block_number = int(row['blockNumber'])
    
    health_factor_after_one_block = None
    current_block = block_number
    blocks_for_liquidation = 0
    
    # Go back block by block until health factor > 1
    while True:
        # Go back one block
        current_block -= 1
        blocks_for_liquidation += 1
        health_factor = get_health_factor(user, current_block)
        
        # If health factor is valid and > 1, we stop
        if health_factor and health_factor >= 1:
            health_factor_after_one_block = current_block
            break
         
    # Update DataFrame with the results
    liquidations_df.at[idx, 'health_factor_above_one_block'] = int(health_factor_after_one_block)
    liquidations_df.at[idx, 'blocks_for_liquidation'] = int(blocks_for_liquidation)
    
    # Save the dataframe every 200 rows to the same CSV
    if (idx + 1) % 200 == 0:
        # Save in append mode, with header if first save
        if header_needed:
            liquidations_df.iloc[start_idx:idx+1].to_csv(checkpoint_file, mode='w', header=True, index=False)
            header_needed = False  # Header is written once
        else:
            liquidations_df.iloc[start_idx:idx+1].to_csv(checkpoint_file, mode='a', header=False, index=False)
        print(f"Checkpoint saved at row {idx + 1}")

# Final save
if header_needed:  # If we haven't saved before, include the header
    liquidations_df.iloc[start_idx:].to_csv(checkpoint_file, mode='w', header=True, index=False)
else:
    liquidations_df.iloc[start_idx:].to_csv(checkpoint_file, mode='a', header=False, index=False)
print("Final DataFrame saved.")
