from web3 import Web3
import progressbar
import pandas as pd
from utils import get_cached_abi
from get_contract_logs import getContractEvents

lending_pool = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
deploy_block = 16291127
outfile = "data/aave_v3_lending_pool_logs.csv"
target_events = 'all'

getContractEvents( lending_pool, target_events, outfile, deploy_block,end_block=None )
