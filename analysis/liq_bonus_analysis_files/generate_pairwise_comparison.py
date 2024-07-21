import pandas as pd

# Load the dataset
liquidations_df = pd.read_csv("../../data/liquidation_calls_details.csv")

#Getting decimals for each token
atokens_df = pd.read_csv("../../data/aave_atokens_v2.csv")
decimals = { r['symbol']: r['decimals'] for _, r in atokens_df.iterrows() }
tokens = { r['address']: r['symbol'] for _, r in atokens_df.iterrows() }

liquidations_df = pd.read_csv("../../data/liquidation_calls_details.csv")
liquidations_df['liquidatedCollateralAmount'] = pd.to_numeric(liquidations_df['liquidatedCollateralAmount'], errors='coerce')

# Define a function to get the symbol for each collateral asset
def get_symbol(asset_address):
    return tokens.get(asset_address, '')

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

for address, symbol in tokens.items():
    temp_df = pd.read_csv(f"../../data/usd_prices/{symbol}_usd.csv")
    temp_df.astype(dtype={'timestamp':int}, copy=False)
    temp_df.sort_values(by=['timestamp'], inplace=True)
    temp_df['timestamp'] = temp_df['timestamp']//1000
    temp_df.rename(columns={'timestamp': 'block_timestamp_unix', 'symbol': 'collateral_symbol'}, inplace=True)
    new_df = pd.concat( [new_df,temp_df] )

liquidations_df.sort_values(by=['block_timestamp_unix'],inplace=True)
new_df.sort_values(by=['block_timestamp_unix'],inplace=True)

liquidations_df = pd.merge_asof(liquidations_df, new_df,on = 'block_timestamp_unix',by = 'collateral_symbol', direction = 'nearest')

liquidations_df['scaled_liquidatedCollateralAmountUSD'] = liquidations_df.apply(
    lambda x: x['scaled_liquidatedCollateralAmount'] * (x['USD_price']), axis=1
)

# Handle missing values and ensure all values are strings
liquidations_df['collateral_assets'] = liquidations_df['collateral_assets'].fillna('').astype(str)
liquidations_df['collateral_assets_addresses'] = liquidations_df['collateral_assets_addresses'].fillna('').astype(str)
liquidations_df['collateral_amounts'] = liquidations_df['collateral_amounts'].fillna('0').astype(str)
liquidations_df['liquidation_bonuses'] = liquidations_df['liquidation_bonuses'].fillna('').astype(str)

# Split columns into lists
liquidations_df['collateral_assets'] = liquidations_df['collateral_assets'].apply(lambda x: x.split(';') if x != '' else [])
liquidations_df['collateral_assets_addresses'] = liquidations_df['collateral_assets_addresses'].apply(lambda x: x.split(';') if x != '' else [])
liquidations_df['collateral_amounts'] = liquidations_df['collateral_amounts'].apply(lambda x: [int(amount) for amount in x.split(';') if amount != ''] if x != '0' else [])
liquidations_df['liquidation_bonuses_list'] = liquidations_df['liquidation_bonuses'].apply(lambda x: [float(bonus) for bonus in x.split(';') if bonus] if x else [])

def create_pairwise_comparisons(df):
    # Container for all pairwise comparison records
    all_pairwise_data = []

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        chosen_asset = row['collateralAsset']
        available_assets = row['collateral_assets_addresses']
        bonuses = row['liquidation_bonuses_list']
        amounts = row['collateral_amounts']
        liquidated_amount = row['liquidatedCollateralAmount']

        # Map addresses to symbols for readability
        asset_symbols = [tokens.get(addr, '') for addr in available_assets]

        # Generate pairwise comparisons
        for i, asset in enumerate(available_assets):
            if asset == chosen_asset:
                for j, comparison_asset in enumerate(available_assets):
                    if i != j:  # Avoid comparing the asset with itself
                        pairwise_data = {
                            'chosen_asset': asset_symbols[i],
                            'comparison_asset': asset_symbols[j],
                            'chosen_bonus': bonuses[i] if i < len(bonuses) else 0,
                            'comparison_bonus': bonuses[j] if j < len(bonuses) else 0,
                            'chosen_liquidated_amount': liquidated_amount/10**(decimals[tokens[asset]]),
                            'chosen_available_amount': amounts[i]/10**(decimals[tokens[asset]]) if i < len(amounts) else 0,
                            'comparison_available_amount': amounts[j]/10**(decimals[tokens[comparison_asset]]) if j < len(amounts) else 0,
                        }
                        all_pairwise_data.append(pairwise_data)

    return pd.DataFrame(all_pairwise_data)

# Apply the function to generate the pairwise comparison DataFrame
pairwise_df = create_pairwise_comparisons(liquidations_df)

pairwise_df.to_csv("pairwise.csv",index=False)