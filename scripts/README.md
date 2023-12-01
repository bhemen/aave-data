# AAVE

These scripts are designed to scrape Aave data from an Ethereum archive node.  There are two ways we scrape data: 

1. We get historical balances by querying the Aave Protocol data provider contracts at historical block heights
2. We get event data, by parsing the events emitted by different Aave contracts, using our tool [get_contract_logs.py](get_contract_logs.py), which grabs all the events emitted by a target contract
  * [get_atoken_transfers_v2.py](get_atoken_transfers_v2.py) gets all the transfer events from all the Aave aTokens

## V2

Aave v2 provides a [Protocol Data Provider Contract](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider) which provides many useful aggregate statistics.

* [get_atokens.py](get_atokens.py) calls the function [getAllReservesTokens()](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens) to get a list of all the reserve assets and their corresponding aTokens
* [get_collateralization_meta.py](get_collateralization_meta.py) calls the function [getReserveConfigurationData](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getreserveconfigurationdata) for each reserve asset provided by [getAllReservesTokens()](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens)
* [get_collateralization.py](get_collateralization.py) calls the function [getReserveData](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getreservedata) for each reserve asset provided by [getAllReservesTokens()](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens)

## V3




