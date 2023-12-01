# Import necessary libraries
import pandas as pd
from web3 import Web3

#Connect to an Ethereum node
url="" #This should really only be run against a local node
w3 = Web3(Web3.HTTPProvider(url))

"""
Get the sender of a transaction given its hash.

:param txhash: The hash of the transaction.
:type txhash: str
:return: The sender of the transaction.
:rtype: str or None
"""
def getSender(txhash):
	try:
		tx = w3.eth.get_transaction(txhash)
		sender = tx['from']
	except Exception as e:
		sender = None
	return sender

def getTimestamp(blockhash):
	try:
		tx = w3.eth.get_block(blockhash)
		ts = tx['timestamp']
	except Exception as e:
		ts = None
	return ts

"""
Adds a new column to a CSV file based on the values of an existing column and then overwrites the initial file.

Parameters:
- datafile (str): The path to the CSV file.
- fn (function): The function to apply to the values of the source column to generate the values for the new column.
- src_col (str): The name of the existing column.
- dest_col (str): The desired name for the new column.
"""
def addCol(datafile,fn,src_col,dest_col):
	df = pd.read_csv(datafile)

	if src_col not in df.columns:
		return

	while dest_col in df.columns:
		dest_col += 'a'
		
	df[dest_col] = df[src_col].apply(fn)
	
	df.to_csv(datafile,index=False)

if __name__ == '__main__':
    addCol('data/lending_pool_logs.csv',getTimestamp,'blockHash','timestamp')
