#Import Necessary Libraries
import pandas as pd
from web3 import Web3
from get_contract_logs import getContractEvents

df = pd.read_csv("data/aave_atokens_v2.csv")

symbols = df['symbol']
atoken_addresses = df['aTokenAddress']

for symbol,address in zip(symbols, atoken_addresses):
    print(f"Grabbing token {symbol}" )
    contract_address = Web3.to_checksum_address(address)
    start_block = 9000000
    outfile = f"data/{symbol}_atoken_transfers.csv"
    scanned_events = 'all'
    getContractEvents(contract_address,scanned_events,outfile,start_block,end_block=None)


