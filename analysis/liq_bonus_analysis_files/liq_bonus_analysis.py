import pandas as pd

# Load the data from both files
def load_data(meta_filepath, config_filepath):
    meta_data = pd.read_csv(meta_filepath)
    config_data = pd.read_csv(config_filepath)
    return meta_data, config_data

# Function to get the liquidation bonus at a specific block number for a specific asset
def get_liquidation_bonus_at_block(meta_data, config_data, block_number, asset_symbol):
    # Filter meta_data for the initial setup block
    initial_data = meta_data[meta_data['block'] == 11362887]
    
    # Get initial liquidation bonus for the specified asset
    asset_data = initial_data[initial_data['symbol'] == asset_symbol]
    if asset_data.empty:
        return "No initial data available for this asset."
    initial_bonus = asset_data['liquidationBonus'].iloc[0]
    
    # Filter config data for changes up to the specified block number for this asset
    relevant_config = config_data[(config_data['blockNumber'] <= block_number) & (config_data['asset'] == asset_data['address'].iloc[0])]
    if not relevant_config.empty:
        # Sort data as specified and get the last entry
        relevant_config_sorted = relevant_config.sort_values(by=['blockNumber', 'logIndex'])
        last_entry = relevant_config_sorted.iloc[-1]
        updated_bonus = last_entry['liquidationBonus']
        return updated_bonus
    else:
        return initial_bonus

atokens_df = pd.read_csv("../../data/aave_atokens_v2.csv")
decimals = { r['symbol']: r['decimals'] for _, r in atokens_df.iterrows() }
symbol_to_address = { r['symbol']: r['address'] for _, r in atokens_df.iterrows() }
address_to_symbol = { r['address']: r['symbol'] for _, r in atokens_df.iterrows() }
meta_filepath = '../../data/aave_collateralization_meta_v2.csv'
config_filepath = '../../data/lending_pool_config_CollateralConfigurationChanged.csv'
meta_data, config_data = load_data(meta_filepath, config_filepath)

initial_bonuses = {}

def get_initial_liquidation_bonus(meta_data):
    initial_data = meta_data[meta_data['block'] == 11362887]
    for index, row in initial_data.iterrows():
        initial_bonuses[row['symbol']] = [(1606775755, 11362887, row['liquidationBonus'])]  # timestamp, block, bonus
    return initial_bonuses

def append_changes_to_bonuses(config_data):

    for symbol, address in symbol_to_address.items():
        filtered_data = config_data[config_data['asset'] == address]

        if len(filtered_data)!=0:
            filtered_data.sort_values(by=['blockNumber', 'logIndex'], inplace = True)
            for i in range(len(filtered_data)):
                previous_liq_bonus = initial_bonuses[symbol][-1][2]
                current_liq_bonus = filtered_data.liquidationBonus.iloc[i]
                block = filtered_data.blockNumber.iloc[i]
                timestamp = filtered_data.block_timestamp_unix.iloc[i]
                if current_liq_bonus != previous_liq_bonus:
                    initial_bonuses[symbol].append((timestamp, block, current_liq_bonus))

    return initial_bonuses


# Get initial bonuses for each asset
initial_bonuses = get_initial_liquidation_bonus(meta_data)

# Append changes to the bonuses dictionary
bonuses_with_changes = append_changes_to_bonuses(config_data)


liquidations_df = pd.read_csv("../../data/liquidation_calls_details.csv")
liquidations_df['liquidatedCollateralAmount'] = pd.to_numeric(liquidations_df['liquidatedCollateralAmount'], errors='coerce')

# Define a function to get the symbol for each collateral asset
def get_symbol(asset_address):
    return address_to_symbol[asset_address]

# Define a function to get the decimal places for each collateral asset
def get_decimal(symbol):
    return decimals.get(symbol, 18)  # Default to 18 if not found

# Map collateral asset addresses to symbols
liquidations_df['collateral_symbol'] = liquidations_df['collateralAsset'].map(get_symbol)
liquidations_df['collateral_symbol'] = liquidations_df['collateral_symbol'].astype(str)

# Apply the scaling
liquidations_df['scaled_liquidatedCollateralAmount'] = liquidations_df.apply(
    lambda x: x['liquidatedCollateralAmount'] / (10 ** get_decimal(x['collateral_symbol'])), axis=1
)

new_df = pd.DataFrame()

for symbol, address in symbol_to_address.items():
    temp_df = pd.read_csv(f"../../data/usd_prices/{symbol}_usd.csv")
    temp_df.astype(dtype={'timestamp': int}, copy=False)
    temp_df.sort_values(by=['timestamp'], inplace=True)
    temp_df['timestamp'] = temp_df['timestamp'] // 1000
    temp_df.rename(columns={'timestamp': 'block_timestamp_unix', 'symbol': 'collateral_symbol'}, inplace=True)
    new_df = pd.concat([new_df, temp_df])

liquidations_df.sort_values(by=['block_timestamp_unix'], inplace=True)
new_df.sort_values(by=['block_timestamp_unix'], inplace=True)

liquidations_df = pd.merge_asof(liquidations_df, new_df, on='block_timestamp_unix', by='collateral_symbol', direction='nearest')

liquidations_df['scaled_liquidatedCollateralAmountUSD'] = liquidations_df.apply(
    lambda x: x['scaled_liquidatedCollateralAmount'] * (x['USD_price']), axis=1
)

# Handle missing values and ensure all values are strings
liquidations_df['collateral_assets'] = liquidations_df['collateral_assets'].fillna('').astype(str)
liquidations_df['collateral_assets_addresses'] = liquidations_df['collateral_assets_addresses'].fillna('').astype(str)
liquidations_df['collateral_amounts'] = liquidations_df['collateral_amounts'].fillna('0').astype(str)

# Split columns into lists
liquidations_df['collateral_assets'] = liquidations_df['collateral_assets'].apply(lambda x: x.split(';') if x != '' else [])
liquidations_df['collateral_assets_addresses'] = liquidations_df['collateral_assets_addresses'].apply(lambda x: x.split(';') if x != '' else [])
liquidations_df['collateral_amounts'] = liquidations_df['collateral_amounts'].apply(lambda x: [int(amount) for amount in x.split(';') if amount != ''] if x != '0' else [])

for symbol, bonus_tuple in bonuses_with_changes.items():
    print("____________________________________________________________________________")
    print(f"{symbol}: {bonus_tuple}")
    
    tuple_length = len(bonus_tuple)
    for i in range(tuple_length):
        print("********************************************************")
        temp_liq_df = liquidations_df
        if len(bonus_tuple) > 1:
            if i == 0:
                temp_liq_df = temp_liq_df[temp_liq_df['block_timestamp_unix'] < bonus_tuple[i+1][0]]
            elif i == tuple_length - 1:
                temp_liq_df = temp_liq_df[temp_liq_df['block_timestamp_unix'] >= bonus_tuple[i][0]]
            else:
                temp_liq_df = temp_liq_df[(temp_liq_df['block_timestamp_unix'] < bonus_tuple[i+1][0]) & (temp_liq_df['block_timestamp_unix'] >= bonus_tuple[i][0])]
        else:
            temp_liq_df = temp_liq_df[temp_liq_df['block_timestamp_unix'] >= bonus_tuple[i][0]]
        asset_not_chosen_count = 0
        total_asset_available = 0

        for index, row in temp_liq_df.iterrows():
            # Check if the asset list is indeed a list and the symbol is part of it
            if isinstance(row['collateral_assets'], list) and symbol in row['collateral_assets']:
                total_asset_available += 1  # Increment the counter for availability
                if row['collateral_symbol'] != symbol:
                    asset_not_chosen_count += 1  # Increment the counter if symbol was not chosen

        if total_asset_available > 0:
            asset_not_chosen_percentage = (asset_not_chosen_count / total_asset_available) * 100
        else:
            asset_not_chosen_percentage = 0  # Avoid division by zero

        print(f"Liquidation Bonus: {bonus_tuple[i][2]}")
        print(f"Count of times {symbol} was available but not chosen: {asset_not_chosen_count}")
        print(f"Total times {symbol} was available: {total_asset_available}")
        print(f"Percentage of times {symbol} was available but not chosen: {round(asset_not_chosen_percentage, 2)}%")
        print(f"Percentage of times {symbol} was available and was chosen: {round(100 - asset_not_chosen_percentage, 2)}%")