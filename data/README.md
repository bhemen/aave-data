# Schema

## Aave v2 pool-level data

The file [aave_collateralization_v2.csv](https://upenn.box.com/shared/static/rjgq5fjkmh1blem46c4edibjsfk056jx.csv) about the historical pool balances, e.g. the collateral held by the Aave contracts and the total outstanding loans in all tokens.  This data set has the *net* balance of the Aave contracts, as well as the *net* borrows -- it does not have user-level data.  For user level data, we have parsed and extracted all the logs from the Aave lending pool see [User-level data](##Aave-v2-user-level-data).


has the output of repeated calls to the Aave Protocol Data Provider Contract (the calls were made every 100 blocks).

* `availableLiquidity` - The amount of liquidity available for each asset in the lending pool. For example: If available liquidity of WETH at any moment is `x`. This means there are `x/10^Decimal(WETH)` number of WETH tokens in the lending pool at the time.
* `totalStableDebt` - The total amount of debt borrowed at the stable rate. Equivalently, it is the amount of stable debt tokens in circulation.
* `totalVariableDebt` - The total amount of debt borrowed at the variable rate. Equivalently, it is the amount of variable debt tokens in circulation.
* `totalDebt` - The total amount of debt borrowed. It is the sum of `totalStableDebt` and `totalVariableDebt`.
* `utilizationRate` - Utilization Rate is the total debt divided by the total liquidity. This shows how much a particular asset in the pool is being utilized. Utilization rate helps in adjusting borrow interest rates. If the asset in the pool is being less utilized (i.e. a lower utilization rate) then lower borrow rates are applied and vice versa. The goal is to strike an Optimal utilization rate that is set by Aave governance for each asset.
* `liquidityRate` - The interest rates given to depositors for depositing assets into the pool.
* `variableBorrowRate` - The interest rate for borrowing at a variable rate. This changes in real time based on supply and demand.
* `stableBorrowRate` - The interest rate for borrowing at a stable rate. This is slightly higher than the variable rate, since it is fixed. It only rebalances when 2 conditions are met:
  * Utilization rate > 95%
  * Current Supply Rate <= Max. Variable Rate*40%
* `averageStableBorrowRate` - The current average stable borrow rate.
* `liquidityIndex` - The Interest accumulated by the reserve during the time interval since the last updated timestamp.
* `variableBorrowIndex` - The borrow Interest accumulated by the reserve during the time interval since the last updated timestamp.
* `lastUpdateTimestamp` - The timestamp of the reserve's last update.

## Aave v2 Reserve Configuration Data
The file aave_collateralization_meta_v2.csv contains collateralization parameters for various assets.

Here is a description of the columns inside this file:
* `ltv` - The maximum borrowing power of a specific collateral. If a collateral has a Loan to Value of 75%, for every 1 ETH worth of collateral the user will be able to borrow 0.75 ETH worth of principal currency. Specified per collateral.
* `liquidationThreshold` - The threshold of a borrow position that will be considered undercollateralized and subject to liquidation. If a collateral has a liquidation threshold of 80%, it means that the loan will be liquidated when the debt value is worth 80% of the collateral value. Specified per collateral.
* `liquidationBonus` - The bonus received by liquidators to incentivise the purchase of specific collateral that has a health factor below 1. Specified per collateral.
* `reserveFactor` - Keeps aside a percentage of protocol’s interests as reserve for the ecosystem.
* `usageAsCollateralEnabled` - Tells us whether the particular asset can be used as collateral or not.
* `borrowingEnabled` - Tells us whether the particular asset can be borrowed or not
* `stableBorrowEnabled` - Tells us whether stable borrowing is enabled for the asset or not
* `isActive` - Tells us whether the reserve is active or not
* `isFrozen` - Tells us whether the reserve is frozen / disabled


## Aave v2 Borrow Rate Attributes

The file `borrow_rate_attributes_v2.csv` contains the different borrow rate settings defined by the aave governance.

* `excessUtilizationRate` - This constant represents the excess utilization rate above the optimal. It's always equal to 1-optimalUtilizationRate. Added as a constant here for gas optimizations.
* `optimalUtilizationRate` - This constant represents the utilization rate at which the pool aims to obtain most competitive borrow rates
* `addressesProvider` - Address of the address provider contract
* `baseVariableBorrowRate` - Base variable borrow rate when Utilization rate = 0
* `getMaxVariableBorrowRate` - baseVariableBorrowRate + variableRateSlope1 + variableRateSlope2
* `stableRateSlope1` - Slope of the stable interest curve when utilization rate > 0 and <= optimalUtilizationRate
* `stableRateSlope2` - Slope of the stable interest curve when utilization rate > optimalUtilizationRate
* `variableRateSlope1` - Slope of the variable interest curve when utilization rate > 0 and <= optimalUtilizationRate
* `variableRateSlope2` - Slope of the variable interest curve when utilization rate > optimalUtilizationRate

## Aave v2 Liquidation Loss

The file [aave_liquidation_loss_v2.csv](https://upenn.box.com/s/j21staqnqq15rrhkby7qojlyvg34i171) contains information about users who have experienced a significant reduction in their collateral value, approaching or reaching zero, while still maintaining a nonzero amount of debt. This dataset specifically highlights instances where Aave incurred financial losses during the liquidation process. This file was derived using the script `aave_v2_liq_stats.py`.

* `borrower` - Address of the borrower
* `liquidator` - Address of the last liquidator 
* `debtLeft (in ETH)` - Amount of debt left in ETH
* `debtLeft (in USD)` - Amount of debt left in USD
* `debtAsset` - The debt asset that the borrower holds
* `collateral_Asset` - Last liquidated collateral asset

## Aave v2 User Interests

The [aave_v2_user_interests](https://upenn.box.com/s/sj6y194ab14yopx2k5npfh7rxvftuf3u) folder contains CSV files for all assets where each row corresponds to a user and the interest they gained from depositing a specific asset. 

* `user` - User address
* `actual_interest` - Total interest gained throughout the deposited duration
* `amount_deposited` - Total amount of that asset deposited
* `amount_withdrawn` - Total amount of that asset withdrawn
* `deposit_count` - Number of deposits made
* `withdraw_count` - Number of withdrawals made
* `interestAccrualPeriod` - Number of blocks the asset remained deposited and thus gained interest
* `initialInterestBlockProduct` - This column represents the cumulative product of the initial interest amount at the beginning of a specified number of blocks and the duration (in blocks) for which the asset remained deposited without any intervening events. It essentially quantifies the initial interest, factoring in the time period over which the asset was continuously invested in the system.
* `normalizedInterest` - Sum of `actual_interest` / Sum of `initialInterestBlockProduct`. This normalized metric accounts for both the duration (in number of blocks deposited) and the initial interest rate at the start of the block period, offering a comparative analysis of actual interest earned against initial expectations.


## Aave v2 user-level data

### Deposits
The file [aavev2_Deposit.csv](https://upenn.box.com/s/1y1v6qaeuf2wxc26h3lpy2sc41r9z7ws) has all the deposits events emitted by the [Aave v2 Lending Pool contract](https://docs.aave.com/developers/v/2.0/the-core-protocol/lendingpool/ilendingpool)

This data set includes all the fields in the event itself:
* `reserve` - The address of the token being deposited
* `user` - The address of the user who initiated the deposit
* `onBehalfOf` - The address who the deposit is "for"
* `amount` - The amount of the deposit
* `referral` - A [referral](https://docs.aave.com/developers/v/1.0/integrating-aave/referral-program) code

In addition, the data set has
* `event` - The name of the event (in this case "Deposit")
* `logIndex` - The index of this specific event within this transaction
* `transactionHash` - The transaction hash of the transaction that triggered this event
* `address` - The address of the contract that generated this event (in this case, the address of the Aave v2 lending pool)
* `blockHash` - The block hash of the block where this event was generated
* `blockNumber` - The block number of the block where this event was generated
* `date` - The date of the transaction (taken from the timestamp in the block)

### Borrows
The file [aavev2_Borrow.csv](https://upenn.box.com/s/j5zrbra5t41z69ob8pt22jjo686tdhbg) contains all the borrow events emitted by the [Aave v2 Lending Pool contract](https://docs.aave.com/developers/v/2.0/the-core-protocol/lendingpool/ilendingpool)

This dataset includes all fields from the borrow event itself:
* `reserve` - The address of the token being borrowed
* `user` - The address of the user who initiated the borrow
* `onBehalfOf` - The address for whom the borrow is initiated
* `referral` - A [referral code](https://docs.aave.com/developers/v/1.0/integrating-aave/referral-program)
* `amount` - The amount of the token borrowed
* `borrowRateMode` - The mode of the borrow rate (e.g., stable, variable)
* `borrowRate` - The rate at which the user is borrowing

In addition, the dataset includes transaction and block information:
* `event` - The name of the event (in this case "Borrow")
* `logIndex` - The index of this specific event within its transaction
* `transactionIndex` - The index position of the transaction within the block
* `transactionHash` - The hash of the transaction that triggered this event
* `address` - The address of the contract that generated this event (the Aave v2 lending pool)
* `blockHash` - The hash of the block where this event was recorded
* `blockNumber` - The number of the block where this event was recorded

Additional metadata includes:
* `date` - The date of the transaction (derived from the block's timestamp)
* `tokenName` - The name of the token that was borrowed
* `decimal` - The number of decimals the token uses

### Flash Loans
The file [aavev2_FlashLoan.csv](https://upenn.box.com/s/lvhcoo7gauv5zw4g2s1f1is493zkz70v) captures all flash loan events emitted by the Aave v2 Lending Pool contract.

Each event in the data set includes the following fields:
* `event` - The type of event, "FlashLoan" in this case.
* `logIndex` - The index of this event within the transaction log.
* `transactionIndex` - The position of the transaction within the block.
* `transactionHash` - The unique identifier of the transaction associated with this event.
* `address` - The contract address that emitted the event, the Aave v2 Lending Pool.
* `blockHash` - The identifier of the block that recorded this event.
* `blockNumber` - The number of the block in which this event was recorded.
* `target` - The address of the recipient of the flash loan.
* `initiator` - The address that initiated the flash loan.
* `asset` - The token address of the asset taken in the flash loan.
* `amount` - The quantity of the asset borrowed.
* `premium` - The additional fee paid for the flash loan.
* `referralCode` - An optional referral code associated with the transaction.
* `date` - The date and time when the event was recorded, based on the block's timestamp.


### Liquidation Calls
The file [aavev2_LiquidationCall.csv](https://upenn.box.com/s/senrd2zv9as26kieo25wx0a7c3j638k5) contains records of all liquidation call events emitted by the Aave v2 Lending Pool contract.

This dataset encompasses the following attributes for each liquidation event:
* `event` - The name of the event, which is "LiquidationCall" for these entries.
* `logIndex` - The index of the log entry for the event within the transaction.
* `transactionIndex` - The sequence number of the transaction within the block.
* `transactionHash` - The unique transaction identifier for the event.
* `address` - The Aave v2 Lending Pool contract address that logged the event.
* `blockHash` - The hash of the block in which the event occurred.
* `blockNumber` - The number of the block containing the event.
* `collateralAsset` - The address of the collateral asset involved in the liquidation.
* `debtAsset` - The address of the debt asset for which the liquidation is occurring.
* `user` - The address of the user whose position is being liquidated.
* `debtToCover` - The amount of debt that the liquidation is covering.
* `liquidatedCollateralAmount` - The amount of collateral that is being liquidated.
* `liquidator` - The address of the user who is performing the liquidation.
* `receiveAToken` - Indicates whether the liquidator receives aTokens.
* `date` - The timestamp of when the liquidation event was logged.

### Rebalance Stable Borrow Rate
The file [aavev2_RebalanceStableBorrowRate.csv](https://upenn.box.com/s/xdyykz37sxnw8ok1tp8kck0j5qw69b4i) details all the rebalance stable borrow rate events emitted by the Aave v2 Lending Pool contract.

Each entry in the dataset represents a rebalance event and includes these fields:
* `event` - The type of event, "RebalanceStableBorrowRate" in this case.
* `logIndex` - The index of this event in the transaction log.
* `transactionIndex` - The index of the transaction within the block.
* `transactionHash` - The unique hash identifier of the transaction associated with this event.
* `address` - The contract address of the Aave v2 Lending Pool that emitted the event.
* `blockHash` - The hash of the block that includes this event.
* `blockNumber` - The number of the block in which this event was recorded.
* `reserve` - The address of the reserve token for which the borrow rate is being rebalanced.
* `user` - The address of the user for whom the borrow rate is being rebalanced.
* `date` - The timestamp of when the event was logged.
* `tokenName` - The name of the reserve token.
* `decimal` - The number of decimals of the reserve token.

### Repays
The file [aavev2_Repay.csv](https://upenn.box.com/s/022fsqsx79tcf65q8vv8dbge3d3hmfjf) logs all the repay events emitted by the Aave v2 Lending Pool contract.

This dataset includes the following details for each repay event:
* `event` - Identifies the type of event, "Repay" in this instance.
* `logIndex` - The log entry index of the event within the transaction.
* `transactionIndex` - The index of the transaction within the block.
* `transactionHash` - The unique identifier of the transaction for this event.
* `address` - The address of the Aave v2 Lending Pool contract that generated the event.
* `blockHash` - The hash of the block containing this event.
* `blockNumber` - The number of the block where this event is recorded.
* `reserve` - The address of the reserve token that is being repaid.
* `user` - The address of the user on whose behalf the repayment is made.
* `repayer` - The address of the user who performed the repay action.
* `amount` - The amount of the token that has been repaid.
* `date` - The date and time of the event, according to the block's timestamp.
* `tokenName` - The name of the reserve token that is repaid.
* `decimal` - The number of decimal places used by the reserve token.


### Reserve Data Updated
The file [aavev2_ReserveDataUpdated.csv](https://upenn.box.com/s/rl67cryy8yian2rkfpy4v0ddep32qbrf) contains all the ReserveDataUpdated events emitted by the Aave v2 Lending Pool contract.

This dataset captures detailed information on each event with the following fields:
* `event` - The name of the event, "ReserveDataUpdated" in this case.
* `logIndex` - The index of this event within the transaction log.
* `transactionIndex` - The position of the transaction within its block.
* `transactionHash` - The unique hash of the transaction that included this event.
* `address` - The address of the Aave v2 Lending Pool contract where the event occurred.
* `blockHash` - The hash of the block in which this event was recorded.
* `blockNumber` - The sequential number of the block containing this event.
* `reserve` - The address of the reserve currency to which the updated data pertains.
* `liquidityRate` - The updated liquidity rate for the reserve.
* `stableBorrowRate` - The updated stable borrow rate for the reserve.
* `variableBorrowRate` - The updated variable borrow rate for the reserve.
* `liquidityIndex` - The updated liquidity index for the reserve.
* `variableBorrowIndex` - The updated variable borrow index for the reserve.
* `date` - The timestamp when the event was logged.
* `tokenName` - The name of the reserve token.
* `decimal` - The number of decimals for the reserve token.

### Reserve Used As Collateral Disabled
The file [aavev2_ReserveUsedAsCollateralDisabled.csv](https://upenn.box.com/s/ounc43bc8ty2k6xzdwv27q2bhjmzi1nm) captures all events where a reserve asset is disabled as collateral in the Aave v2 Lending Pool.

This dataset records each event with the following fields:
* `event` - The type of event, "ReserveUsedAsCollateralDisabled" in this case.
* `logIndex` - The index of this event within the transaction log.
* `transactionIndex` - The index of the transaction within the block.
* `transactionHash` - The unique hash identifier of the transaction associated with this event.
* `address` - The contract address of the Aave v2 Lending Pool that emitted the event.
* `blockHash` - The hash of the block that includes this event.
* `blockNumber` - The block number where this event was recorded.
* `reserve` - The address of the reserve token being disabled as collateral.
* `user` - The address of the user for whom the collateral is being disabled.
* `date` - The timestamp when the event was logged, based on the block's timestamp.
* `tokenName` - The name of the reserve token.
* `decimal` - The number of decimals of the reserve token.

### Reserve Used As Collateral Enabled
The file [aavev2_ReserveUsedAsCollateralEnabled.csv](https://upenn.box.com/s/mqfwxb1nzlqp6kfibb1hoc20tyvnulbz) contains all the events where a reserve asset is enabled as collateral in the Aave v2 Lending Pool.

The dataset includes these fields for each event:
* `event` - The name of the event, "ReserveUsedAsCollateralEnabled" in this instance.
* `logIndex` - The index of this event within the transaction log.
* `transactionIndex` - The index of the transaction within the block.
* `transactionHash` - The unique hash of the transaction that triggered this event.
* `address` - The contract address of the Aave v2 Lending Pool that recorded the event.
* `blockHash` - The hash of the block that includes this event.
* `blockNumber` - The block number where this event was logged.
* `reserve` - The address of the reserve token that is being enabled as collateral.
* `user` - The address of the user who is enabling the reserve as collateral.
* `date` - The timestamp of when the event was logged, as per the block's timestamp.
* `tokenName` - The name of the reserve token.
* `decimal` - The number of decimal places for the reserve token.

### Swap Rate
The file [aavev2_Swap.csv](https://upenn.box.com/s/v0zx3dvpjfcmoybv0n8lytglfi7jcc0c) includes all swap rate events emitted by the Aave v2 Lending Pool contract.

This dataset provides a record of each swap rate event with the following data:
* `event` - The type of event, "Swap" in this case.
* `logIndex` - The index of this event within the transaction log.
* `transactionIndex` - The transaction's index within its block.
* `transactionHash` - The unique hash of the transaction that included this event.
* `address` - The address of the Aave v2 Lending Pool contract that logged the event.
* `blockHash` - The hash of the block that recorded the event.
* `blockNumber` - The number of the block in which the event occurred.
* `reserve` - The address of the reserve token involved in the swap.
* `user` - The address of the user performing the swap.
* `rateMode` - The rate mode that the user is switching to (1 for stable, 2 for variable).
* `date` - The timestamp when the event was logged.
* `tokenName` - The name of the reserve token.
* `decimal` - The number of decimal places used by the reserve token.

### Withdrawals
The file [aavev2_Withdraw.csv](https://upenn.box.com/s/cw7k1xbm9ydwtcqgt5hdfwjqjq938eq6) documents all withdrawal events from the Aave v2 Lending Pool.

The dataset contains the following fields for each withdrawal event:
* `event` - The event's identifier, "Withdraw" in this case.
* `logIndex` - The index of this event in the log of its transaction.
* `transactionIndex` - The order of the transaction within the block.
* `transactionHash` - The unique hash of the transaction where this event occurred.
* `address` - The address of the Aave v2 Lending Pool contract that captured the event.
* `blockHash` - The hash of the block containing this event.
* `blockNumber` - The sequential number of the block with this event.
* `reserve` - The address of the reserve token being withdrawn.
* `user` - The address of the user making the withdrawal.
* `to` - The address where the withdrawn funds are sent.
* `amount` - The amount of tokens withdrawn.
* `date` - The timestamp of the block in which the event was logged.
* `tokenName` - The name of the reserve token.
* `decimal` - The number of decimal places for the reserve token.










