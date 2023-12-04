# Import necessary libraries
from web3 import Web3
import pandas as pd
from utils import get_cached_abi
from web3.providers.rpc import HTTPProvider
import os
from tqdm import tqdm

# Connect to Ethereum node
api_url = "http://localhost:8545"
provider = HTTPProvider(api_url)
web3 = Web3(provider)

#Get Aave v2 protocol data provider contract
aave_protocol_data_provider_address = Web3.toChecksumAddress("0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d")
aave_protocol_data_provider_abi = get_cached_abi( aave_protocol_data_provider_address )
aave_protocol_data_provider_contract = web3.eth.contract( address=aave_protocol_data_provider_address, abi=aave_protocol_data_provider_abi )

# Calling getAllReservesTokens function from Protocol Data Provider Contract => https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens
reserve_tokens = aave_protocol_data_provider_contract.functions.getAllReservesTokens().call()
#reserve_tokens looks like:
#[('USDT', '0xdAC17F958D2ee523a2206206994597C13D831ec7'), ('WBTC', '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'), ('WETH', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'), ('YFI', '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e'), ('ZRX', '0xE41d2489571d322189246DaFA5ebDe1F4699F498'), ('UNI', '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'), ('AAVE', '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9'), ('BAT', '0x0D8775F648430679A709E98d2b0Cb6250d2887EF'), ('BUSD', '0x4Fabb145d64652a948d72533023f6E7A623C7C53'), ('DAI', '0x6B175474E89094C44Da98b954EedeAC495271d0F'), ('ENJ', '0xF629cBd94d3791C9250152BD8dfBDF380E2a3B9c'), ('KNC', '0xdd974D5C2e2928deA5F71b9825b8b646686BD200'), ('LINK', '0x514910771AF9Ca656af840dff83E8264EcF986CA'), ('MANA', '0x0F5D2fB29fb7d3CFeE444a200298f468908cC942'), ('MKR', '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2'), ('REN', '0x408e41876cCCDC0F92210600ef50372656052a38'), ('SNX', '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F'), ('sUSD', '0x57Ab1ec28D129707052df4dF418D58a2D46d5f51'), ('TUSD', '0x0000000000085d4780B73119b644AE5ecd22b376'), ('USDC', '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'), ('CRV', '0xD533a949740bb3306d119CC777fa900bA034cd52'), ('GUSD', '0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd'), ('BAL', '0xba100000625a3754423978a60c9317c58a424e3D'), ('xSUSHI', '0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272'), ('renFIL', '0xD5147bc8e386d91Cc5DBE72099DAC6C9b99276F5'), ('RAI', '0x03ab458634910AaD20eF5f1C8ee96F1D6ac54919'), ('AMPL', '0xD46bA6D942050d489DBd938a2C909A5d5039A161'), ('USDP', '0x8E870D67F660D95d5be530380D0eC0bd388289E1'), ('DPI', '0x1494CA1F11D487c2bBe4543E90080AeBa4BA3C2b'), ('FRAX', '0x853d955aCEf822Db058eb8505911ED77F175b99e'), ('FEI', '0x956F47F50A910163D8BF957Cf5846D573E7f87CA'), ('stETH', '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84'), ('ENS', '0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72'), ('UST', '0xa693B19d2931d498c5B318dF961919BB4aee87a5'), ('CVX', '0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B'), ('1INCH', '0x111111111117dC0aa78b770fA6A738034120C302'), ('LUSD', '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0')]

#Mapping token addresses to symbols
tokens={}
# reserve_tokens = reserve_tokens[0:-1]
for symbol,address in reserve_tokens:
    tokens[address] = symbol

#Getting decimals for each token
atokens_df = pd.read_csv("../data/aave_atokens_v2.csv")
decimals = { r['symbol']: r['decimals'] for _, r in atokens_df.iterrows() }

#filtering the deposit events to get the list of users
df = pd.read_csv('../data/lending_pool_logs_v2.csv', low_memory=False)
deposits_df = df[df['event'] == 'Deposit']

def get_aave_user_addresses(deposits_df, reserve_tokens):
    """
    Retrieves a sorted list of unique user addresses from Aave lending pool deposit events and token transfer logs.

    Parameters:
        deposits_df (DataFrame): The dataframe containing the lending pool logs with 'Deposit' events already filtered.
        reserve_tokens (list): A list of tuples containing the symbols and addresses of reserve tokens.

    Returns:
        list: A sorted list of unique user addresses.
    """
    # Initialize the set of user addresses with 'onBehalfOf' and 'user' columns from the filtered dataframe
    aave_user_addresses = set(deposits_df['onBehalfOf']).union(deposits_df['user'])

    # Column types for reading token transfer csvs
    coltypes = {
        'address': str, 'blockHash': str, 'blockNumber': int, 'transactionHash': str,
        'data': str, 'from': str, 'to': str, 'value': float, 'event': str,
        'msg.sender': str, 'owner': str, 'spender': str
    }

    # Process each token's transfer data
    for symbol, _ in reserve_tokens:
        df_temp = pd.read_csv(f"../data/atoken_transfers/{symbol}_atoken_transfers.csv", dtype=coltypes)
        # Update the address set by adding unique addresses from each specified column
        aave_user_addresses.update(df_temp['owner'], df_temp['spender'], df_temp['from'], df_temp['to'])

    # Filter the address set to remove non-string entries and null values
    aave_user_addresses = [a for a in aave_user_addresses if isinstance(a, str) and pd.notna(a)]

    # Remove the zero address and return a sorted list of user addresses
    aave_user_addresses.remove('0x0000000000000000000000000000000000000000')
    return sorted(aave_user_addresses)

ctr=0
for symbol,address in reserve_tokens:
    if ctr == 0:
        transfers_df = pd.read_csv(f"../data/atoken_transfers/{symbol}_atoken_transfers.csv")
        transfers_df['reserve'] = address
        transfers_df = transfers_df[transfers_df['event'] == 'Transfer']
    else:
        temp_df = pd.read_csv(f"../data/atoken_transfers/{symbol}_atoken_transfers.csv")
        temp_df['reserve'] = address
        transfers_df = pd.concat( [transfers_df,temp_df] )
        transfers_df = transfers_df[transfers_df['event'] == 'Transfer']
    ctr += 1

#Dropping and adding columns from the 2 dataframes, to make the column names the same, so we can merge them into one dataframe for Deposit, Withdraw and Transfer events
transfers_df.drop(['value', 'msg.sender', 'owner', 'spender', 'USD_price', 'value (in USD)'], axis=1, inplace = True)
transfers_df = transfers_df.reindex(columns = transfers_df.columns.tolist() + ['user', 'onBehalfOf', 'amount'])
df.drop(['liquidityRate','stableBorrowRate','variableBorrowRate','liquidityIndex','variableBorrowIndex','msg.sender','referral','to','borrowRateMode','borrowRate','repayer','rateMode','target','initiator','asset','premium','referralCode','collateralAsset','debtAsset','debtToCover','liquidatedCollateralAmount','liquidator','receiveAToken'], axis=1, inplace = True)
df = df.reindex(columns = df.columns.tolist() + ['from', 'to'])
new_df = pd.concat( [df,transfers_df] )

# Drop rows with NaN in 'reserve'
new_df = new_df.dropna(subset=['reserve'], axis=0)

# Map 'reserve' to 'symbol' using a vectorized approach
new_df['symbol'] = (new_df['reserve'].map(tokens)).astype('string')

#Filtering and sorting the new dataframe formed
new_df = new_df[(new_df['event'] == 'Deposit') | (new_df['event'] == 'Withdraw') | (new_df['event'] == 'Transfer')]
new_df.sort_values(by=['timestamp'],inplace=True)

#Creating a dataframe for token prices in USD 
usd_df = pd.DataFrame()
for symbol,address in reserve_tokens:
    temp_df = pd.read_csv(f"../data/usd_prices/{symbol}_usd.csv")
    temp_df.astype(dtype={'timestamp':int}, copy=False)
    temp_df.sort_values(by=['timestamp'], inplace=True)

    #Dividing by 1000 to convert timestamp from milliseconds to seconds
    temp_df['timestamp'] = temp_df['timestamp']//1000
    usd_df = pd.concat( [usd_df,temp_df] )

#Filtering and sorting the USD dataframe
usd_df.sort_values(by=['timestamp'], inplace=True)
usd_df['symbol'] = usd_df['symbol'].astype('string')

#Merging and saving
new_df = pd.merge_asof(new_df, usd_df, on = 'timestamp', by = 'symbol', direction = 'nearest')

#Creating a dataframe for interest gained
interest_gained = {}
for symbol, address in reserve_tokens:
    interest_gained[symbol] = {}

aave_user_addresses = get_aave_user_addresses(deposits_df, reserve_tokens)

for user in tqdm(aave_user_addresses):
    
    #Filtering the aave users
    df_1 = new_df[(new_df['user'] == user) | (new_df['onBehalfOf'] == user) | (new_df['from'] == user) | (new_df['to'] == user)]
    df_1.sort_values(by=['timestamp'], inplace=True)

    for i in range(len(df_1)):

        actual_interest = 0
        initialInterestBlockProduct = 0
        normalized_interest = 0
        deposit_count = 0
        withdraw_count = 0
        amount_deposited = 0
        amount_withdrawn = 0
        reserve = df_1.reserve.iloc[i]
        event = df_1.event.iloc[i]      
        
        #Calculating the number of times user deposited and withdrew and the respective amounts in USD
        if event == 'Deposit':
            deposit_count += 1
            amount_deposited += (( df_1.amount.iloc[i] )/( 10**decimals[tokens[reserve]] ))*df_1.USD_price.iloc[i]
        elif event == 'Withdraw':
            withdraw_count += 1
            amount_withdrawn += (( df_1.amount.iloc[i] )/( 10**decimals[tokens[reserve]] ))*df_1.USD_price.iloc[i]

        #Since we are taking the i and i+1th rows, we stop when i is the last row.
        if i != len(df_1)-1:
            current_block_num = int(df_1.blockNumber.iloc[i])

            #current_User_Reserve_Data[0] is the current atoken balance
            try:
                current_User_Reserve_Data = aave_protocol_data_provider_contract.functions.getUserReserveData(reserve,user).call(block_identifier=current_block_num)
                # print(f"Token: {tokens[reserve]}")
                # print(f"Event: {df_1.event.iloc[i]}")
                # print(f"Current atoken balance: {current_User_Reserve_Data[0]}\n")

            except Exception as e:
                with open( "../data/aave_user_reserve_data_errors.csv", "a" ) as f:
                    f.write( f"Error calling getUserReserveData at {current_block_num} for asset {tokens[reserve]}\n" )
                continue

            next_block_num = int(df_1.blockNumber.iloc[i+1])

            #We call it at next_block_num - 1 so as to get the atoken balance just before the event at next_block_num
            try:
                next_User_Reserve_Data = aave_protocol_data_provider_contract.functions.getUserReserveData(reserve,user).call(block_identifier=next_block_num-1)
                # print(f"Token: {tokens[reserve]}")
                # print(f"Event: {df_1.event.iloc[i+1]}")
                # print(f"Next atoken balance: {next_User_Reserve_Data[0]}\n")

            except Exception as e:
                with open( "../data/aave_user_reserve_data_errors.csv", "a" ) as f:
                    f.write( f"Error calling getUserReserveData at {next_block_num} for asset {tokens[reserve]}\n" )
                continue
            
            #Since we are calling on (next_block - 1) so current and next blocks need to be atleast 2 blocks apart
            if abs(current_block_num - next_block_num) > 1:
                actual_interest += ((next_User_Reserve_Data[0]-current_User_Reserve_Data[0])/(10**decimals[tokens[reserve]]))*df_1.USD_price.iloc[i]
                initialInterestBlockProduct += (next_block_num-current_block_num)*(current_User_Reserve_Data[0]/10**decimals[tokens[reserve]])*df_1.USD_price.iloc[i]
                interestAccrualPeriod = next_block_num - current_block_num
        
        #Storing user interest information in a dictionary called interest_gained
        #Here first keys are tokens. Then in each subdictionary, users (who deposited, withdrew or transferred that token) are keys and then in the following subdictionary the below attributes are keys
        if user not in interest_gained[tokens[reserve]].keys():
            interest_gained[tokens[reserve]][user] = {
                'normalized_interest': normalized_interest,
                'actual_interest': actual_interest,
                'interestAccrualPeriod': interestAccrualPeriod,
                'initialInterestBlockProduct': initialInterestBlockProduct,
                'amount_deposited': amount_deposited,
                'amount_withdrawn': amount_withdrawn,
                'deposit_count': deposit_count,
                'withdraw_count': withdraw_count
            }
        else:
            interest_gained[tokens[reserve]][user]['normalized_interest'] = normalized_interest
            interest_gained[tokens[reserve]][user]['actual_interest'] += actual_interest
            interest_gained[tokens[reserve]][user]['interestAccrualPeriod'] += interestAccrualPeriod
            interest_gained[tokens[reserve]][user]['initialInterestBlockProduct'] += initialInterestBlockProduct
            interest_gained[tokens[reserve]][user]['amount_deposited'] += amount_deposited
            interest_gained[tokens[reserve]][user]['amount_withdrawn'] += amount_withdrawn
            interest_gained[tokens[reserve]][user]['deposit_count'] += deposit_count
            interest_gained[tokens[reserve]][user]['withdraw_count'] += withdraw_count

    #normalized interest = (sum of actual_interests) / (sum of initialInterestBlockProduct)
    for symbol in interest_gained.keys():
        if user in interest_gained[symbol].keys():
            if interest_gained[symbol][user]['initialInterestBlockProduct'] != 0:
                interest_gained[symbol][user]['normalized_interest'] = interest_gained[symbol][user]['actual_interest']/interest_gained[symbol][user]['initialInterestBlockProduct']
    
#Making the final dataframes from the dictionary
if not os.path.exists("../data/aave_v2_user_interests/"):
    os.makedirs("../data/aave_v2_user_interests/")

for symbol, address in reserve_tokens:
    if len(interest_gained[symbol].keys())>0:
        temp_user = list(interest_gained[symbol].keys())[0]
        final_df = pd.DataFrame(columns=['user'] + [ attribute for attribute in sorted(interest_gained[symbol][temp_user].keys())])
        for user in interest_gained[symbol].keys():
            final_df.loc[len(final_df)] = [user] + [interest_gained[symbol][user][attribute] for attribute in sorted(interest_gained[symbol][user].keys())]

        final_df.to_csv(f"../data/aave_v2_user_interests/{symbol}_user_interests.csv", index = False)