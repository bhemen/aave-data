import pandas as pd
from web3 import Web3
from scripts.get_contract_logs import getContractEvents

df = pd.read_csv("data/aave_v3_atokens.csv")

symbols = df['symbol']
atokens_addresses = df['aTokenAddress']

#Manually added deploy blocks for all atoken addresses
#['0x4d5F47FA6A74757f35C14fD3a6Ef8E3C9BC514E8', '0x0B925eD163218f6662a35e0f0371Ac234f9E9371', '0x5Ee5bf7ae06D1Be5997A1A72006FE6C607eC6DE8', '0x98C23E9d8f34FEFb1B7BD6a91B7FF122F4e16F5c', '0x018008bfb33d285247A21d44E50697654f754e63', '0x5E8C8A7243651DB1384C0dDfDbE39761E8e7E51a', '0xA700b4eB416Be35b2911fd5Dee80678ff64fF6C9', '0x977b6fc5dE62598B08C85AC8Cf2b745874E8b78c', '0x23878914EFE38d27C4D67Ab83ed1b93A74D4086a', '0xCc9EE9483f662091a1de4795249E24aC0aC2630f', '0x3Fe6a295459FAe07DF8A0ceCC36F37160FE86AA9', '0x7B95Ec873268a6BFC6427e7a28e396Db9D0ebc65', '0x8A458A9dc9048e005d22849F470891b840296619', '0xC7B4c17861357B8ABB91F25581E7263E08DCB59c', '0x2516E7B3F76294e03C42AA4c5b5b4DCE9C436fB8', '0xF6D2224916DDFbbab6e6bd0D1B7034f4Ae0CaB18', '0x9A44fd41566876A39655f74971a3A6eA0a17a454', '0x545bD6c032eFdde65A377A6719DEF2796C8E0f2e', '0x71Aef7b30728b9BB371578f36c5A1f1502a5723e', '0xd4e245848d6E1220DBE62e155d89fa327E43CB06', '0x00907f9921424583e7ffBfEdf84F92B7B2Be4977']
deploy_blocks = [16496792, 16496795, 16496800, 16496802, 16496806, 16496808, 16496810, 16575788, 16620256, 16620261, 16669829, 16784190, 17019320, 17019320, 17019320, 17019320, 17075380, 17539726, 17539726, 17641336, 17699249]

for symbol, address, block in zip(symbols, atokens_addresses, deploy_blocks):
    print(f"Grabbing token {symbol}" )
    contract_address = Web3.to_checksum_address(address)
    start_block = block
    outfile = f"data/aave_v3_{symbol}_atoken_transfers.csv"
    scanned_events = 'all'
    getContractEvents(contract_address,scanned_events,outfile,start_block,end_block=None)


