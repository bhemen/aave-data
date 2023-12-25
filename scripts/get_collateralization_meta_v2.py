"""
	This script calls the Aave V2 Lending pool data provider contract to get information about each of the reserve assets at specific block heights

	This script generates the file data/aave_collateralization_meta_v2.csv
"""

# Import necessary libraries
import pandas as pd
from web3 import Web3
from web3.providers.rpc import HTTPProvider
from utils import get_cached_abi
import progressbar

# Connect to Ethereum node
api_url = ""
provider = HTTPProvider(api_url)
web3 = Web3(provider)

#Get Aave V2 protocol data provider contract
aave_protocol_data_provider_address = Web3.to_checksum_address("0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d")
aave_protocol_data_provider_abi = get_cached_abi( aave_protocol_data_provider_address )
aave_protocol_data_provider_contract = web3.eth.contract( address=aave_protocol_data_provider_address, abi=aave_protocol_data_provider_abi )

# Calling getAllReservesTokens function from Protocol Data Provider Contract => https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens
reserve_tokens = aave_protocol_data_provider_contract.functions.getAllReservesTokens().call()
#reserve_tokens looks like:
#[('USDT', '0xdAC17F958D2ee523a2206206994597C13D831ec7'), ('WBTC', '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'), ('WETH', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'), ('YFI', '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e'), ('ZRX', '0xE41d2489571d322189246DaFA5ebDe1F4699F498'), ('UNI', '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'), ('AAVE', '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9'), ('BAT', '0x0D8775F648430679A709E98d2b0Cb6250d2887EF'), ('BUSD', '0x4Fabb145d64652a948d72533023f6E7A623C7C53'), ('DAI', '0x6B175474E89094C44Da98b954EedeAC495271d0F'), ('ENJ', '0xF629cBd94d3791C9250152BD8dfBDF380E2a3B9c'), ('KNC', '0xdd974D5C2e2928deA5F71b9825b8b646686BD200'), ('LINK', '0x514910771AF9Ca656af840dff83E8264EcF986CA'), ('MANA', '0x0F5D2fB29fb7d3CFeE444a200298f468908cC942'), ('MKR', '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2'), ('REN', '0x408e41876cCCDC0F92210600ef50372656052a38'), ('SNX', '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F'), ('sUSD', '0x57Ab1ec28D129707052df4dF418D58a2D46d5f51'), ('TUSD', '0x0000000000085d4780B73119b644AE5ecd22b376'), ('USDC', '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'), ('CRV', '0xD533a949740bb3306d119CC777fa900bA034cd52'), ('GUSD', '0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd'), ('BAL', '0xba100000625a3754423978a60c9317c58a424e3D'), ('xSUSHI', '0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272'), ('renFIL', '0xD5147bc8e386d91Cc5DBE72099DAC6C9b99276F5'), ('RAI', '0x03ab458634910AaD20eF5f1C8ee96F1D6ac54919'), ('AMPL', '0xD46bA6D942050d489DBd938a2C909A5d5039A161'), ('USDP', '0x8E870D67F660D95d5be530380D0eC0bd388289E1'), ('DPI', '0x1494CA1F11D487c2bBe4543E90080AeBa4BA3C2b'), ('FRAX', '0x853d955aCEf822Db058eb8505911ED77F175b99e'), ('FEI', '0x956F47F50A910163D8BF957Cf5846D573E7f87CA'), ('stETH', '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84'), ('ENS', '0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72'), ('UST', '0xa693B19d2931d498c5B318dF961919BB4aee87a5'), ('CVX', '0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B'), ('1INCH', '0x111111111117dC0aa78b770fA6A738034120C302'), ('LUSD', '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0')]

#Define output and error file paths
outfile = "../data/aave_collateralization_meta.csv"
errorfile = "../data/aave_collateralization_meta_errors.csv"

#Define starting and ending block heights
latest_block = web3.eth.block_number
start_block = 11362589

# Looking at every 100th block starting from the current block down to the start block
blocks = list(range(latest_block, start_block-1, -100))

# Create an empty list to store data rows
rows = []

with progressbar.ProgressBar(max_value=len(blocks)) as bar:

    for i,block_num in enumerate(blocks):

        block = web3.eth.get_block(block_num)

        for symbol,address in reserve_tokens:

            #Calling getReserveData function from Protocol Data Provider Contract => https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getreserveconfigurationdata
            try:
                token_info = aave_protocol_data_provider_contract.functions.getReserveConfigurationData(address).call(block_identifier=block_num)
            except Exception as e:
                with open( errorfile, "a" ) as f:
                    f.write( f"Error calling getReserveConfigurationData at {block_num}\n" )
                continue

            # Compile the data into a row and append to the rows list
            row = { 'block': block_num,
                    'timestamp': block.timestamp,
                    'symbol': symbol,
                    'address': address,
                    'decimals': token_info[0],
                    'ltv': token_info[1],
                    'liquidationThreshold': token_info[2], 
                    'liquidationBonus': token_info[3],
                    'reserveFactor': token_info[4], 
                    'usageAsCollateralEnabled': token_info[5],
                    'borrowingEnabled': token_info[6], 
                    'stableBorrowEnabled': token_info[7],
                    'isActive': token_info[8], 
                    'isFrozen': token_info[9] }
            rows.append(row)
            bar.update(i)

# Convert the rows list to a Pandas DataFrame and save to CSV
df = pd.DataFrame(rows)
df.to_csv(outfile,index=False)


