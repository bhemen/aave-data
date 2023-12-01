# AAVE

## V2

Aave v2 provides a [Protocol Data Provider Contract](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider) which provides many useful aggregate statistics.

* [get_atokens.py](get_atokens.py) calls the function [getAllReservesTokens()](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens) to get a list of all the reserve assets and their corresponding aTokens
* [get_collateralization_meta.py](get_collateralization_meta.py) calls the function [getReserveConfigurationData](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getreserveconfigurationdata) for each reserve asset provided by [getAllReservesTokens()](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens)
* [get_collateralization.py](get_collateralization.py) calls the function [getReserveData](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getreservedata) for each reserve asset provided by [getAllReservesTokens()](https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getallreservestokens)

## V3




