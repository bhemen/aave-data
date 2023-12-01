# Scraping price data

[Coingecko](https://www.coingecko.com) provides a nice API for scraping price data for different tokens.

Read the [API documentation here](https://www.coingecko.com/en/api/documentation).

The API is simple to use, and you can do most of what you want without registering for an account.  If you need to make more than [50 calls /min, you 
need to use a paid plan](https://www.coingecko.com/en/api/pricing).

The [coingecko_scraper](coingecko_scraper.py) script will let you scrape the price history for a set of tokens in a given time range.

The complete list of coins indexed by coingecko can be obtained by running [coingecko_coin_list](coingecko_coin_list.py), which stores the list of coins in [coin_list.csv](coin_list.csv).
