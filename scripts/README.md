# AAVE

These scripts are designed to scrape Aave data from an Ethereum archive node.  There are two ways we scrape data: 

1. We get historical balances by querying the Aave Protocol data provider contracts at historical block heights.  This includes
    * [get_collateralization_v2.py](get_collateralization_v2.py)
    * [get_collateralization_v3.py](get_collateralization_v3.py)
    * [get_collateralization_meta_v2.py](get_collateralization_meta_v2.py)
    * [get_collateralization_meta_v3.py](get_collateralization_meta_v3.py)
    * [get_get_borrow_rate_attributes_v2.py](get_borrow_rate_attributes_v2.py)
    * [get_get_borrow_rate_attributes_v3.py](get_borrow_rate_attributes_v3.py)
2. We get event data, by parsing the events emitted by different Aave contracts, using our tool [get_contract_logs.py](get_contract_logs.py), which grabs all the events emitted by a target contract
    * [get_atoken_transfers_v2.py](get_atoken_transfers_v2.py) gets all the transfer events from all the Aave aTokens
    * [get_atoken_transfers_v3.py](get_atoken_transfers_v3.py) gets all the transfer events from all the Aave aTokens
    * [get_lending_pool_events_v2.py](get_lending_pool_events_v2.py) gets all the transfer events from all the Aave aTokens
    * [get_lending_pool_events_v3.py](get_lending_pool_events_v3.py) gets all the transfer events from all the Aave aTokens

## V2

Aave v2 provides a [Protocol Data Provider Contract](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider) which provides many useful aggregate statistics.

* [get_atokens_v2.py](get_atokens_v2.py) calls the function [getAllReservesTokens()](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens) to get a list of all the reserve assets and their corresponding aTokens.  It writes the resulting list to [aave_atokens_v2.csv](../data/aave_atokens_v2.csv).
* [get_collateralization_meta_v2.py](get_collateralization_meta_v2.py) calls the function [getReserveConfigurationData](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getreserveconfigurationdata) for each reserve asset provided by [getAllReservesTokens()](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens)
* [get_collateralization_v2.py](get_collateralization_v2.py) calls the function [getReserveData](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getreservedata) for each reserve asset provided by [getAllReservesTokens()](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens)

## V3

Aave v3 provides a [Protocol Data Provider Contract]([https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider](https://docs.aave.com/developers/core-contracts/aaveprotocoldataprovider)https://docs.aave.com/developers/core-contracts/aaveprotocoldataprovider) which provides many useful aggregate statistics.

* [get_atokens_v3.py](get_atokens_v3.py) calls the function [getAllReservesTokens()](https://docs.aave.com/developers/core-contracts/aaveprotocoldataprovider#getallreservestokens) to get a list of all the reserve assets and their corresponding aTokens.  It writes the resulting list to [aave_atokens_v3.csv](../data/aave_atokens_v3.csv).
* [get_collateralization_meta_v3.py](get_collateralization_meta_v3.py) calls the function [getReserveConfigurationData](https://docs.aave.com/developers/core-contracts/aaveprotocoldataprovider#getreserveconfigurationdata) for each reserve asset provided by [getAllReservesTokens()](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens)
* [get_collateralization_v3.py](get_collateralization_v3.py) calls the function [getReserveData](https://docs.aave.com/developers/core-contracts/aaveprotocoldataprovider#getreservedata) for each reserve asset provided by [getAllReservesTokens()](https://docs.aave.com/developers/core-contracts/aaveprotocoldataprovider#getallreservestokens)
