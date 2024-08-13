import pandas as pd
import numpy as np
import scipy.optimize as opt
from sklearn.utils import resample
from tqdm import tqdm

# Load the CSV file
atokens_df = pd.read_csv("../data/aave_atokens_v2.csv")
decimals = {r['symbol']: r['decimals'] for _, r in atokens_df.iterrows()}
symbol_to_address = {r['symbol']: r['address'] for _, r in atokens_df.iterrows()}
address_to_symbol = {r['address']: r['symbol'] for _, r in atokens_df.iterrows()}

df = pd.read_csv('../data/liquidation_calls_details.csv')

# Create a new column 'collateralAssetSymbol' by mapping the addresses
df['collateralAssetSymbol'] = df['collateralAsset'].map(address_to_symbol)

# Handle missing values and ensure all values are strings
df['collateral_assets'] = df['collateral_assets'].fillna('').astype(str)
df['collateral_assets_addresses'] = df['collateral_assets_addresses'].fillna('').astype(str)
df['collateral_amounts'] = df['collateral_amounts'].fillna('0').astype(str)

# Split columns into lists
df['collateral_assets'] = df['collateral_assets'].apply(lambda x: x.split(';') if x != '' else [])
df['collateral_assets_addresses'] = df['collateral_assets_addresses'].apply(lambda x: x.split(';') if x != '' else [])
df['collateral_amounts'] = df['collateral_amounts'].apply(lambda x: [int(amount) for amount in x.split(';') if amount != ''] if x != '0' else [])

# Define the negative log-likelihood function
def negative_log_likelihood(theta, data, M):
    likelihood = 0
    for _, row in data.iterrows():
        collaterals = row['collateral_assets']
        top_choice = row['collateralAssetSymbol']
        denom_sum = np.sum(np.exp(theta[collaterals]))
        if denom_sum == 0:
            continue  # Avoid divide by zero
        likelihood += np.log(np.exp(theta[top_choice]) / denom_sum)
    return -likelihood

# Compute the MLE
def compute_mle(initial_theta, data, M):
    print("Starting MLE computation...")
    result = opt.minimize(
        negative_log_likelihood,
        initial_theta,
        args=(data, M),
        method='BFGS'
    )
    print("MLE computation finished.")
    return result.x

# Initialize theta with zeros
collateral_types = atokens_df['symbol'].unique()
initial_theta = np.zeros(len(collateral_types))
theta_index = {symbol: idx for idx, symbol in enumerate(collateral_types)}

# Map collateral symbols to indices
df['collateral_assets'] = df['collateral_assets'].apply(lambda lst: [theta_index[symbol] for symbol in lst])
df['collateralAssetSymbol'] = df['collateralAssetSymbol'].apply(lambda symbol: theta_index[symbol])

# Compute MLE
mle_theta = compute_mle(initial_theta, df, len(collateral_types))

# Construct confidence intervals using Gaussian multiplier bootstrap
def gaussian_multiplier_bootstrap(data, theta, num_bootstrap=100, alpha=0.05):
    n = len(theta)
    bootstrapped_thetas = np.zeros((num_bootstrap, n))
    
    print(f"Starting bootstrap sampling with num_bootstrap = {num_bootstrap}...")
    for i in tqdm(range(num_bootstrap)):
        sampled_data = resample(data)
        bootstrapped_theta = compute_mle(theta, sampled_data, n)
        bootstrapped_thetas[i] = bootstrapped_theta
    print("Bootstrap sampling finished.")
    
    lower_bounds = np.percentile(bootstrapped_thetas, 100 * (alpha / 2), axis=0)
    upper_bounds = np.percentile(bootstrapped_thetas, 100 * (1 - alpha / 2), axis=0)
    
    return lower_bounds, upper_bounds

# Get confidence intervals
lower_bounds, upper_bounds = gaussian_multiplier_bootstrap(df, mle_theta)

# Rank the collaterals based on estimated preference scores
collateral_rankings = sorted(
    [(symbol, mle_theta[idx], lower_bounds[idx], upper_bounds[idx]) for symbol, idx in theta_index.items()],
    key=lambda x: -x[1]  # Sort in descending order of preference scores
)

# Display the rankings
for rank, (symbol, score, lower, upper) in enumerate(collateral_rankings, 1):
    print(f"Rank {rank}: {symbol} - Score: {score:.4f}, 95% CI: ({lower:.4f}, {upper:.4f})")