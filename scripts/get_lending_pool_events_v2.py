"""
This script retrieves and records all events from the Aave lending pool contract within a specified block range.

The script uses the `getContractEvents` function from the get_contract_logs.py file to fetch the events. It then saves these events to a CSV file for further analysis or processing.
"""

from get_contract_logs import getContractEvents

lending_pool = "0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9"
deploy_block = 11362579
outfile = "data/lending_pool_logs.csv"
target_events = 'all'

"""
Parameters:
- lending_pool (str): The Ethereum address of the Aave lending pool contract.
- deploy_block (int): The block number from which to start retrieving events. This is typically the block in which the contract was deployed.
- outfile (str): The path to the CSV file where the retrieved events will be saved.
- target_events (str): Specifies the type of events to retrieve. If set to 'all', all events from the contract will be fetched.
"""
getContractEvents( lending_pool, target_events, outfile, deploy_block,end_block=None )
