import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import sys
sys.path.append("../scripts/")

df = pd.read_csv( "../data/aave_collateralization_v2.csv" )

meta_df = pd.read_csv("../data/aave_collateralization_meta_v2.csv" )

decimals = { r['symbol']: r['decimals'] for i, r in meta_df.iterrows() }

#Adding a date column in df
if 'dt' not in df:
    df['dt'] = df['timestamp'].apply( lambda x: datetime.fromtimestamp(x) )

#Adding a date column in meta_df
if 'dt' not in meta_df:
    meta_df['dt'] = meta_df['timestamp'].apply( lambda x: datetime.fromtimestamp(x) )

# Check if 'totalDebt' column exists, if not, create it
if 'totalDebt' not in df.columns:
    df.insert(7, 'totalDebt', df['totalStableDebt'].astype(float) + df['totalVariableDebt'].astype(float))
    df.to_csv("../data/aave_collateralization_v2.csv")

# Check if 'utilizationRate' column exists, if not, create it
if 'utilizationRate' not in df.columns:
    util_rate = df['totalDebt'].astype(float)/(df['availableLiquidity'].astype(float) + df['totalDebt'].astype(float))
    df.insert(8, 'utilizationRate', util_rate)
    df.to_csv("../data/aave_collateralization_v2.csv")

#Can include whichever tokens you want in the plots by uncommenting
symbols = [
    'USDC',
    'USDT',
    'WETH',
    # '1INCH',
    # 'AAVE',
    # 'BAL',
    # 'BAT',
    # 'BUSD',
    # 'CRV',
    # 'CVX',
    'DAI',
    # 'DPI',
    # 'ENJ',
    # 'ENS',
    # 'FEI',
    # 'FRAX',
    # 'GUSD',
    # 'KNC',
    # 'LINK',
    # 'MANA',
    # 'MKR',
    # 'RAI',
    # 'REN',
    # 'renFIL',
    # 'SNX',
    # 'stETH',
    # 'sUSD',
    # 'TUSD',
    # 'UNI',
    # 'USDP',
    # 'UST',
    'WBTC',
    # 'xSUSHI',
    # 'YFI',
    # 'ZRX'
]

#Can plot whichever attributes you want in aave_collateralization_v2.csv by uncommenting
target_cols = {
    # "availableLiquidity": "Total Value Locked (in USD)",
    # "totalVariableDebt": "Total Variable Debt (in USD)",
    # "totalStableDebt": "Total Stable Debt (in USD)",
    # "totalDebt": "Total Value Borrowed (in USD)",
    # "variableBorrowRate": "Variable Borrow Rate (in %)",
    # "stableBorrowRate": "Stable Borrow Rate (in %)",
    "liquidityRate": "Liquidity Rate (in %)",
    "utilizationRate": "Utilization Rate (in %)"
}

#Can plot whichever attributes you want in aave_collateralization_meta_v2.csv by uncommenting
target_cols_meta = {
    "ltv": "LTV (in %)",
    "liquidationThreshold": "Liquidation Threshold (in %)",
    "reserveFactor": "Reserve Factor (in %)",
    "liquidationBonus": "Liquidation Bonus (in %)",
    #"isFrozen": "Asset Frozen",
    #"isActive": "Asset Active"
    #"usageAsCollateralEnabled": "Collateral Enabled",
    #"borrowingEnabled": "Borrowing Enabled",
    #"stableBorrowEnabled": Stable Borrow Enabled",
}

#Make a pivot table to get usd price for a particular symbol at a particular timetamp
usd_ndf = pd.pivot( df, index=['dt'], columns=['symbol'], values=['USD_price'] )
usd_ndf.columns = [tup[-1] for tup in usd_ndf.columns.to_flat_index()]
usd_ndf.reset_index(inplace=True )
usd_ndf = usd_ndf.astype( { c:float for c in symbols} )

#Function to calculate correlation between WETH prices and borrowing/lending of WETH
def weth_correl():

    for attr,label in [("availableLiquidity","WETH Lending"), ("totalDebt","WETH Borrowing")]:

        _,ax = plt.subplots()
        
        # Plotting WETH prices with dates on the x-axis and prices on the y-axis
        ax.plot(usd_ndf.dt,usd_ndf['WETH'],color="red",label="WETH Price")
        ax.legend(loc="upper left")
        ax.set_ylabel("WETH Prices (in USD)")

        # Creating a pivot table for the specified attribute (either lending or borrowing)
        ndf = pd.pivot( df, index=['dt'], columns=['symbol'], values=[attr] )
        ndf.columns = [tup[-1] for tup in ndf.columns.to_flat_index()]
        ndf.reset_index(inplace=True )
        ndf = ndf.astype( { c:float for c in symbols} )

        # Calculate the correlation between WETH price and the lending/borrowing attribute
        correlation = usd_ndf["WETH"].corr(ndf["WETH"]/(10**decimals["WETH"])*usd_ndf["WETH"])

        # Creating a second y-axis to plot the lending/borrowing attribute
        ax2=ax.twinx()
        ax2.plot(usd_ndf.dt, ndf["WETH"]/(10**decimals["WETH"])*usd_ndf["WETH"],color="blue",label=label)
        ax2.set_ylabel(f"{label} (in USD)")
        ax2.legend()

        # Setting the title of the plot based on the correlation value
        plt.suptitle(f"Assessing Correlation between {label} and WETH Prices")
        if attr == "availableLiquidity":
            plt.title(f"High Positive Correlation: {round(correlation,2)}", fontsize= 10)
        else:
            plt.title(f"Low Negative Correlation: {round(correlation,2)}", fontsize = 10)

        # Formatting the x-axis to show dates in a readable format
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.gcf().autofmt_xdate()
        plt.show()

#For plotting aave_collateralization.csv
def collateralization_plots():

    # Loop over each metric in target_cols to create separate plots
    for target_col, title in target_cols.items():

        # Pivot the DataFrame to restructure data for plotting
        ndf = pd.pivot( df, index=['dt'], columns=['symbol'], values=[target_col] )
        ndf.columns = [tup[-1] for tup in ndf.columns.to_flat_index()]
        ndf.reset_index(inplace=True )
        ndf = ndf.astype( { c:float for c in symbols} )    

        # Generate plots for target columns which are uncommented
        if target_col in ["availableLiquidity", "totalVariableDebt", "totalStableDebt", "totalDebt"]:
            target_col_values = [(ndf[symbol]/(10**decimals[symbol]))*usd_ndf[symbol] for symbol in symbols]
            #Plotting a stacked area chart
            plt.stackplot( ndf.dt, target_col_values, labels=symbols )

        elif target_col in ["stableBorrowRate", "variableBorrowRate", "liquidityRate"]:
            # Plot rates as a line chart for each symbol
            for symbol in symbols:
                #All rates queried on chain or subgraph, are expressed in RAY units i.e. 10^27. So dividing by 10**25 to get values in percent 
                plt.plot( ndf.dt, ndf[symbol]//(10**25), label = symbol)

        elif target_col=="utilizationRate":
            for symbol in symbols:
                plt.plot( ndf.dt, ndf[symbol]*100, label = symbol)

        # Formatting the x-axis to display dates and setting labels and titles
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.gcf().autofmt_xdate()
        plt.legend()
        plt.ylabel(title)
        plt.title(title)

        #Plotting the crypto crash date
        plt.axvline(datetime(2022,5,7), color = 'r')

        #Plotting FTX collapse
        plt.axvline(datetime(2022,11,11), color = 'b')

        #plotting ethereum merge
        plt.axvline(datetime(2022,9,15), color = 'g')

        #Annotating the significant historical events, separately for each plot
        #Note: Still need to do this for the remaining plots
        if target_col == "availableLiquidity":
            plt.annotate("Terra Collapse", xy=(datetime(2022,5,7), 0.8*10**10), xytext=(datetime(2021,12,15), 1.1*10**10),arrowprops=dict(arrowstyle="->"))
            plt.annotate("Ethereum Merge", xy=(datetime(2022,9,15), 0.4*10**10), xytext=(datetime(2022,10,15), 0.6*10**10),arrowprops=dict(arrowstyle="->"))
            plt.annotate("FTX Collapse", xy=(datetime(2022,11,11), 0.8*10**10), xytext=(datetime(2022,10,15), 1.1*10**10),arrowprops=dict(arrowstyle="->"))

        elif target_col == "totalDebt":
            plt.annotate("Terra Collapse", xy=(datetime(2022,5,7), 6*10**9), xytext=(datetime(2021,12,15), 8*10**9),arrowprops=dict(arrowstyle="->"))
            plt.annotate("Ethereum Merge", xy=(datetime(2022,9,15), 3*10**9), xytext=(datetime(2022,10,15), 5*10**9),arrowprops=dict(arrowstyle="->"))
            plt.annotate("FTX Collapse", xy=(datetime(2022,11,11), 6*10**9), xytext=(datetime(2022,10,15), 8*10**9),arrowprops=dict(arrowstyle="->"))

        elif target_col == "utilizationRate":
            plt.annotate("Terra Collapse", xy=(datetime(2022,5,7), 85), xytext=(datetime(2021,12,15), 100),arrowprops=dict(arrowstyle="->"))
            plt.annotate("Ethereum Merge", xy=(datetime(2022,9,15), 90), xytext=(datetime(2022,6,1), 100),arrowprops=dict(arrowstyle="->"))
            plt.annotate("FTX Collapse", xy=(datetime(2022,11,11), 95), xytext=(datetime(2023,1,1), 100),arrowprops=dict(arrowstyle="->"))

        plt.show()

#For plotting aave_collateralization_meta.csv
def collateralization_meta_plots():

    for target_col, title in target_cols_meta.items():

        # Pivot the meta DataFrame to restructure data for plotting
        meta_ndf = pd.pivot( meta_df, index=['dt'], columns=['symbol'], values=[target_col] )
        meta_ndf.columns = [tup[-1] for tup in meta_ndf.columns.to_flat_index()]
        meta_ndf.reset_index(inplace=True )
        meta_ndf = meta_ndf.astype( { c:float for c in symbols} )

        # Plotting different metrics for each symbol
        for symbol in symbols:

            if target_col in ["ltv", "liquidationThreshold", "reserveFactor"]:

                if not (meta_ndf[symbol] == 0).all():

                    plt.plot( meta_ndf.dt, meta_ndf[symbol]//100, label=symbol )
                    # plt.plot( meta_ndf.dt, meta_ndf[symbol].mean()//100 )
                    # meta_ndf[symbol] = meta_ndf[symbol].mean()
                    # plt.errorbar(x=meta_ndf.dt, y=meta_ndf[symbol]//100, yerr=meta_ndf[symbol].std()//100, label=f"{symbol} Average")

            #Special handling for Liquidation bonus since it is interpreted slightly differently
            #A liquidation bonus value of 10500 is interpreted as 5% bonus
            #So, to calculate this we first divide by 100 and then subtract 100.
            elif target_col == 'liquidationBonus':
                #Note for this to work we must discard the cases where liquidation bonus is 0
                if not (meta_ndf[symbol] == 0).all():
                    plt.plot( meta_ndf.dt, (meta_ndf[symbol]//100) - 100, label=symbol )

            elif target_col in ["isFrozen", "isActive", "usageAsCollateralEnabled", "borrowingEnabled", "stableBorrowEnabled"]:
                plt.plot( meta_ndf.dt, meta_ndf[symbol], label = symbol)

        # Formatting the x-axis to display dates and setting labels and titles
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.gcf().autofmt_xdate()
        plt.legend()
        plt.ylabel(title)
        plt.title(title)

        #Plotting the crypto crash date
        plt.axvline(datetime(2022,5,7), color = 'r')

        #Plotting FTX collapse
        plt.axvline(datetime(2022,11,11), color = 'b')

        #plotting ethereum merge
        plt.axvline(datetime(2022,9,15), color = 'g')

        plt.show()

def plot_user_stats():

    #Defining and iterating over the user attributes that we want to plot
    attributes = [('amount_deposited', "Amount Deposited"), ("actual_interest","Total Interest Earned")]
    for attribute, title in attributes:

        # Initialize a dictionary to hold the aggregated data for each user.
        attributes_dict = {}
        for symbol in decimals.keys():
            #Right now don't have interests for these 2. Remove this once we have them
            if symbol not in ['LUSD', '1INCH']:
                df_temp = pd.read_csv(f"../data/aave_user_interests/{symbol}_user_interests.csv")
                for i in range(len(df_temp)):
                    user = df_temp.at[i,"user"]
                    if user not in attributes_dict.keys():
                        attributes_dict[user] = 0
                    attributes_dict[user] += float(df_temp.at[i,attribute])
                break

        #Finding the user with the max value of a particular attribute
        top_users = [(val,key) for key,val in attributes_dict.items()]
        top_users.sort(reverse=True)

        #Printing top 50 entries from a list of tuples of the form (attribute values, user)
        # print(tops_users[0:50])
        attribute_values = list(attributes_dict.values())

        def add_to_bucket(number, buckets):
            for lower, upper in buckets:
                if lower <= number < upper:
                    return (lower, upper)
            return None

        def addlabels(x,y):
            for i in range(len(x)):
                plt.text(i, y[i], y[i], ha = 'center')

        # Define the bucket ranges. Each bucket is a range representing an order of magnitude.
        buckets = []
        lower_bound = 1
        upper_bound = 10

        # Generate buckets covering ranges from 1 to 10 billion.
        while upper_bound < 10000000000:
            buckets.append((lower_bound, upper_bound))
            lower_bound = upper_bound
            upper_bound *= 10

        # Add the final bucket for the highest range.
        buckets.append((lower_bound, 10000000000))

        # Initialize a dictionary to count the number of values in each bucket.
        bucket_dict = {bucket: [] for bucket in buckets}

        # Categorize each attribute value into a bucket and count them.
        for attribute_value in attribute_values:
            bucket = add_to_bucket(attribute_value, buckets)
            if bucket:
                bucket_dict[bucket].append(attribute_value)

        for bucket, numbers_in_bucket in bucket_dict.items():
            print(f"Numbers in bucket {bucket}: {len(numbers_in_bucket)}")

        # For each bucket, update the dictionary to hold the count of values in that bucket.
        for i,j in bucket_dict.items():
            bucket_dict[i] = len(j)
        
        # Define the width of the bars for the bar chart.
        bar_width = 0.35
        plt.plot()
        plt.title(title)

        # Set x-axis labels as the bucket ranges in a readable format (e.g., "1$ - 10$").
        x = ["1\$ - 10\$","10\$ - 100\$","100\$ - 1K\$","1K\$ - 10K\$","10K\$ - 100K\$","100K\$ - 1M\$","1M\$ - 10M\$", "10M\$ - 100M\$", "100M\$ - 1B\$", "1B\$ - 10B\$"]

        # Set y-axis values as the counts of users in each bucket.
        y = list(bucket_dict.values())
        addlabels(x,y)
        # create the bar plot
        plt.bar(x, y, width=bar_width)
        plt.xticks(rotation=30, ha='right')
        # display the plot
        plt.show()



#Uncomment it to plot_user_stats() to get plots showing how many users deposited how much and interest gained 
# plot_user_stats()

#Uncomment it to run weth_correl() function to get plots showing correlation between WETH prices and WETH lending and borrowing
# weth_correl()

#Uncomment it to run collateralization_plots() function
collateralization_plots()

#Uncomment it to run collateralization_meta_plots() function
# collateralization_meta_plots()