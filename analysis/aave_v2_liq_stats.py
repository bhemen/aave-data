import pandas as pd
from web3 import Web3
import sys
sys.path.append("../scripts/")
from utils import get_cached_abi
from web3.providers.rpc import HTTPProvider
from tqdm import tqdm
import numpy as np

#Connect to an Ethereum Node
api_url = "https://mainnet.infura.io/v3/43480ee1e64147de963916215adaa3a8"
provider = HTTPProvider(api_url)
web3 = Web3(provider)

#Get Aave V2 protocol data provider contract
aave_protocol_data_provider_address = Web3.toChecksumAddress("0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d")
aave_protocol_data_provider_abi = get_cached_abi( aave_protocol_data_provider_address )
aave_protocol_data_provider_contract = web3.eth.contract( address=aave_protocol_data_provider_address, abi=aave_protocol_data_provider_abi )

#Get Aave V2 lending pool contract
aave_lending_pool_address = Web3.toChecksumAddress("0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9")
aave_lending_pool_abi = get_cached_abi(aave_lending_pool_address)
aave_lending_pool_contract = web3.eth.contract( address=aave_lending_pool_address, abi=aave_lending_pool_abi)

# Reading liquidation event data from lending pool logs
lendingpool_df = pd.read_csv("../data/lending_pool_logs.csv")
lendingpool_df = lendingpool_df[( lendingpool_df['event'] == 'LiquidationCall' ) ]
lendingpool_df.reset_index(drop=True, inplace=True)

#Reading necessary filess
df = pd.read_csv("../data/aave_collateralization.csv" )
meta_df = pd.read_csv("../data/aave_collateralization_meta.csv" )
eth_df = pd.read_csv("../data/usd_prices/WETH_usd.csv")

# Setting up a dictionary to map each token's address to its decimal places
decimals = { r['address']: r['decimals'] for i, r in meta_df.iterrows() }
decimals['UST'] = 6
decimals['LUSD'] = 18
decimals['stETH'] = 18
decimals['ENS'] = 18
decimals['CVX'] = 18
decimals['1INCH'] = 18

"""
Get the closest ETH price to a given timestamp.

Parameters:
    timestamp (int): The timestamp for which to find the closest ETH price.

Returns:
    float: The closest ETH price to the given timestamp.
"""
def get_ETH_prices(timestamp):
    differences = abs(eth_df['timestamp'] - timestamp)
    min_diff_index = differences.idxmin()
    closest_value = eth_df.loc[min_diff_index, 'USD_price']
    return closest_value

# Variables to store the total liquidation loss in ETH and USD
liquidation_loss_eth = 0
liquidation_loss = 0

# Create an empty list to store data rows
rows=[]

# Looping through each liquidation event
for i in tqdm(range(len(lendingpool_df))):

    block_num = lendingpool_df.blockNumber.iloc[i]
    user = lendingpool_df.user.iloc[i]
    timestamp = lendingpool_df.timestamp.iloc[i]

    #Calling getUserAccountData function from LendingPool Contract => https://docs.aave.com/developers/v/2.0/the-core-protocol/lendingpool#getuseraccountdata
    try:
        user_account_data = aave_lending_pool_contract.functions.getUserAccountData(user).call(block_identifier=int(block_num))
        debt = (user_account_data[1])/(10**18)
        collateral = (user_account_data[0])/(10**18)

        # Checking if collateral is less than debt (undercollateralized)
        if collateral < debt:

            # Checking if the collateral value is approximately zero
            if np.isclose(collateral,0):
                row = {
                    'block': block_num,
                    'timestamp': timestamp,
                    'borrower': lendingpool_df.user.iloc[i],
                    'liquidator': lendingpool_df.liquidator.iloc[i],
                    'debtLeft (in ETH)': debt,
                    'debtLeft (in USD)': (debt)*get_ETH_prices(int(timestamp)),
                    'debtAsset': lendingpool_df.debtAsset.iloc[i],
                    'collateral_Asset': lendingpool_df.collateralAsset.iloc[i],
                }
                rows.append(row)

                # Accumulating the total liquidation loss
                liquidation_loss_eth += debt
                liquidation_loss += (debt)*get_ETH_prices(int(timestamp))

            # print(f"{user} has a collateral of {collateral} ETH and a debt of {debt} ETH")

    except Exception as e:
        with open( "../data/aave_liquidation_errors.csv", "a" ) as f:
            f.write( f"Error calling getUserAccountData at {block_num} for user {user}" )
        continue

print(f"Aave has lost {liquidation_loss_eth} ETH in liquidations equivalent to {liquidation_loss} USD")

# Convert the rows list to a Pandas DataFrame and save to CSV
df = pd.DataFrame(rows)
df.to_csv("../data/aave_liquidation_loss_v2.csv",index=False)