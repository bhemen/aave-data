import pandas as pd
from web3 import Web3
import json
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from utils import get_cached_abi

api_url = "http://localhost:8545" # your api here
provider = HTTPProvider(api_url)
web3 = Web3(provider)

#AaveProtocolDataProvider Contract
aave_protocol_data_provider = Web3.to_checksum_address("0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3")
aave_protocol_data_provider_abi = get_cached_abi( aave_protocol_data_provider )
aave_protocol_data_provider_contract = web3.eth.contract( address=aave_protocol_data_provider, abi=aave_protocol_data_provider_abi )

reserve_tokens = aave_protocol_data_provider_contract.functions.getAllReservesTokens().call()

rows = []
for symbol,address in reserve_tokens:
    token_info = aave_protocol_data_provider_contract.functions.getReserveTokensAddresses(address).call()
    row = { 'symbol': symbol,
            'address': address,
            'aTokenAddress': token_info[0],
            'stableDebtTokenAddress': token_info[1],
            'variableDebtTokenAddress': token_info[2] }
    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv("../data/aave_atokens_v3.csv",index=False)


