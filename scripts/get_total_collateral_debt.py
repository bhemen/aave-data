import pandas as pd
from web3 import Web3
import sys
from tqdm import tqdm
import numpy as np
sys.path.append("../scripts/")
from utils import get_proxy_address
from web3.providers.rpc import HTTPProvider


# Connect to an Ethereum Node
api_url = ""  # your node url here
provider = HTTPProvider(api_url)
web3 = Web3(provider)

# Get Aave V2 lending pool contract
aave_lending_pool_address = Web3.to_checksum_address("0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9")
aave_lending_pool_abi = get_proxy_address(web3, aave_lending_pool_address)  # The lending pool contract is a proxy, we want the ABI of the lending pool, not of the proxy
aave_lending_pool_contract = web3.eth.contract(address=aave_lending_pool_address, abi=aave_lending_pool_abi)

# Load the liquidations DataFrame
liquidations_df = pd.read_csv("../data/aave_v2_LiquidationCall.csv")
liquidations_df.sort_values(by='block_timestamp_unix', inplace=True)
liquidations_df.reset_index(drop=True, inplace=True)

error_file = '../data/get_total_collateral_debt_errors.csv'

# Function to fetch data for a specific user and block number
def fetch_user_data(user, block_num):
    try:
        # Fetch user data just before the liquidation event
        user_account_data = aave_lending_pool_contract.functions.getUserAccountData(user).call(block_identifier=int(block_num - 1))
        user_account_data_one_day_before = aave_lending_pool_contract.functions.getUserAccountData(user).call(block_identifier=int(block_num - 7000))

        # Extract debt and collateral information
        debt = user_account_data[1] / (10**18)
        collateral = user_account_data[0] / (10**18)
        debt_one_day_before = user_account_data_one_day_before[1] / (10**18)
        collateral_one_day_before = user_account_data_one_day_before[0] / (10**18)
        
        return debt, collateral, debt_one_day_before, collateral_one_day_before
    
    except Exception as e:
        with open( error_file, "a" ) as f:
            f.write( f"Error calling getUserAccountData for user {user} at block {block_num}\n" )
        return np.nan, np.nan, np.nan, np.nan

# Apply the function to each row in the DataFrame
def process_row(row):
    user = row['user']
    block_num = row['blockNumber']
    debt, collateral, debt_one_day_before, collateral_one_day_before = fetch_user_data(user, block_num)
    
    row['total_debt'] = debt
    row['total_collateral'] = collateral
    row['total_debt_one_day_before'] = debt_one_day_before
    row['total_collateral_one_day_before'] = collateral_one_day_before
    
    return row


def get_total_collateral_debt():
    
    # Apply the processing function to each row of the DataFrame with a progress bar
    tqdm.pandas()  # Initialize tqdm with pandas
    liquidations_df = liquidations_df.progress_apply(process_row, axis=1)

    # Save the updated DataFrame
    liquidations_df.to_csv('../data/aave_v2_LiquidationCall_with_total_collateral_debt.csv', index=False)

def calculate_collateral_debt_change():
    # Load the updated DataFrame
    liq_updated_df = pd.read_csv("../data/aave_v2_LiquidationCall_with_total_collateral_debt_updated.csv")
    
    # Remove rows where `total_collateral_one_day_before` or `total_debt_one_day_before` are exactly 0.0
    liq_updated_df = liq_updated_df[(liq_updated_df['total_collateral_one_day_before'] != 0.0) & 
                                    (liq_updated_df['total_debt_one_day_before'] != 0.0)]
    
    # Calculate the collateral to debt ratios
    liq_updated_df['collateral_debt_ratio'] = liq_updated_df['total_collateral'] / liq_updated_df['total_debt']
    liq_updated_df['collateral_debt_ratio_one_day_before'] = liq_updated_df['total_collateral_one_day_before'] / liq_updated_df['total_debt_one_day_before']

    # Calculate the debt to collateral ratios
    liq_updated_df['debt_collateral_ratio'] = liq_updated_df['total_debt'] / liq_updated_df['total_collateral']
    liq_updated_df['debt_collateral_ratio_one_day_before'] = liq_updated_df['total_debt_one_day_before'] / liq_updated_df['total_collateral_one_day_before']

    # Calculate the percentage change in collateral and debt over one day
    liq_updated_df['collateral_value_change_one_day (in %)'] = (
        (liq_updated_df['total_collateral'] - liq_updated_df['total_collateral_one_day_before']) / liq_updated_df['total_collateral_one_day_before']
    ) * 100

    liq_updated_df['debt_value_change_one_day (in %)'] = (
        (liq_updated_df['total_debt'] - liq_updated_df['total_debt_one_day_before']) / liq_updated_df['total_debt_one_day_before']
    ) * 100

    # Save the updated DataFrame
    liq_updated_df.to_csv('../data/aave_v2_LiquidationCall_with_total_collateral_debt_final.csv', index=False)

    print("Finished processing and saved the final DataFrame.")

## Uncomment this to run the get_total_collateral_debt function which will fetch collateral and debt values 1 day before the liquidation event
get_total_collateral_debt()

## Uncomment this to run the calculate_collateral_debt_change function which will calculate new features from the data fetched by the above function
# calculate_collateral_debt_change()