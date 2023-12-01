"""
Utilities for getting contract ABIs from Etherscan and caching them locally
"""

import requests
import json
import time
#from web3 import Web3
import os

ABI_ENDPOINT = 'https://api.etherscan.io/api?module=contract&action=getabi&address='

if not os.path.exists('abis'):
	os.makedirs('abis')

_cache_file = "abis/cached_abis.json"

def get_rarible_721():
	base_url = "https://raw.githubusercontent.com/rarible/protocol-contracts/master/deploy/build/contracts/"
	contracts = ['ERC721RaribleMinimal.json',
				'ERC721BaseMinimal.json',
				'ERC721LazyMinimal.json',
				'ERC721URI.json',
				'RoyaltiesV2.json',
				'RoyaltiesV2Upgradeable.json' ]

	abi = {}
	for c in contracts:
		try:
			c_abi= json.loads(requests.get(f"{base_url}{c}").text)['abi']
		except Exception as e:
			print( f"Failed to get {c}" )
			continue
		abi.update( { x['name']: x for x in c_abi } ) #Deduplicate on name field
	abi = list( abi.values() )
	
	return abi	

def get_sound_artist(addr):
	'''
	sound.xyz uses a proxy pattern to allow each artist to have their own contract
	'''
	try:
		import pandas as pd
		datafile = "data/sound_artists.csv"
		df = pd.read_csv("datafile")
		artists = set( df['artistAddress'] )
	except Exception as e:
		return addr

	if addr in artists: #Should also probably compare against checksumaddress
		return "0xe2364090b151c09c596e1b58cb4a412906ff2127" #Address of sound.xyz artist template
	else:
		return addr

def fetch_abi(contract_address,retry=0):
	"""
	get abi for contract address from etherscan
	"""

	if contract_address == "rarible_erc721":
		print( f"Getting Rarible ERC721 Contract Info" )
		abi = get_rarible_721()
		return abi
	
	if contract_address == "sound_artist":
		print( f"Getting artist from sound.xyz" )
		return fetch_abi("0xe2364090b151c09c596e1b58cb4a412906ff2127")
	
	if contract_address == "0x78E3aDc0E811e4f93BD9F1f9389b923c9A3355c2": #Sound.xyz
		return fetch_abi("0xD537Fa993cC018d87324d0ab703Ef6F18B1C9071")

	if contract_address == "0x9757F2d2b135150BBeb65308D4a91804107cd8D6": #Rarible exchange
		abi_url = "https://raw.githubusercontent.com/rarible/protocol-contracts/master/deploy/build/contracts/ExchangeV2.json"
		try:
			abi = json.loads(requests.get(abi_url).text)['abi']
		except Exception as e:
			print( "Failed to get Rarible Exchange abi" )
			return None 
		return abi

	if contract_address == "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9": #Aave LendingPool
		return fetch_abi( "0xc6845a5c768bf8d7681249f8927877efda425baf" )

	if contract_address == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": #USDC
		usdc_abi = "https://gist.githubusercontent.com/Ankarrr/570cc90f26ef7fb6a2a387612db80ceb/raw/e4e6dd3fc2d572f8999b06adc557b3edbbadf930/usdc-abi.json"
		try:
			abi = json.loads(requests.get(usdc_abi).text)
		except Exception as e:
			print( "Failed to get USDC abi" )
			return None 
		return abi

	aTokens = ['0x3Ed3B47Dd13EC9a98b44e6204A523E766B225811', '0x9ff58f4fFB29fA2266Ab25e75e2A8b3503311656', '0x030bA81f1c18d280636F32af80b9AAd02Cf0854e', '0x5165d24277cD063F5ac44Efd447B27025e888f37', '0xDf7FF54aAcAcbFf42dfe29DD6144A69b629f8C9e', '0xB9D7CB55f463405CDfBe4E90a6D2Df01C2B92BF1', '0xFFC97d72E13E01096502Cb8Eb52dEe56f74DAD7B', '0x05Ec93c0365baAeAbF7AefFb0972ea7ECdD39CF1', '0xA361718326c15715591c299427c62086F69923D9', '0x028171bCA77440897B824Ca71D1c56caC55b68A3', '0xaC6Df26a590F08dcC95D5a4705ae8abbc88509Ef', '0x39C6b3e42d6A679d7D776778Fe880BC9487C2EDA', '0xa06bC25B5805d5F8d82847D191Cb4Af5A3e873E0', '0xa685a61171bb30d4072B338c80Cb7b2c865c873E', '0xc713e5E149D5D0715DcD1c156a020976e7E56B88', '0xCC12AbE4ff81c9378D670De1b57F8e0Dd228D77a', '0x35f6B052C598d933D69A4EEC4D04c73A191fE6c2', '0x6C5024Cd4F8A59110119C56f8933403A539555EB', '0x101cc05f4A51C0319f570d5E146a8C625198e636', '0xBcca60bB61934080951369a648Fb03DF4F96263C', '0x8dAE6Cb04688C62d939ed9B68d32Bc62e49970b1', '0xD37EE7e4f452C6638c96536e68090De8cBcdb583', '0x272F97b7a56a387aE942350bBC7Df5700f8a4576', '0xF256CC7847E919FAc9B808cC216cAc87CCF2f47a', '0x514cd6756CCBe28772d4Cb81bC3156BA9d1744aa', '0xc9BC48c72154ef3e5425641a3c747242112a46AF', '0x1E6bb68Acec8fefBD87D192bE09bb274170a0548', '0x2e8F4bdbE3d47d7d7DE490437AeA9915D930F1A3', '0x6F634c6135D2EBD550000ac92F494F9CB8183dAe', '0xd4937682df3C8aEF4FE912A96A74121C0829E664', '0x683923dB55Fead99A79Fa01A27EeC3cB19679cC3', '0x1982b2F5814301d4e9a8b0201555376e62F82428', '0x9a14e23A58edf4EFDcB360f68cd1b95ce2081a2F', '0xc2e2152647F4C26028482Efaf64b2Aa28779EFC4', '0x952749E07d7157bb9644A894dFAF3Bad5eF6D918']
	if contract_address in aTokens: #aave a-tokens are interest-bearing ERC-20 tokens
		atoken_abi = "https://raw.githubusercontent.com/aave/aave-protocol/master/abi/AToken.json"
		try:
			abi = json.loads(requests.get(atoken_abi).text)
		except Exception as e:
			print( "Failed to get aToken abi" )
			return None 
		return abi
	
	#ctoken proxy contracts
	if contract_address in ['0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643','0xf650C3d88D12dB855b8bf7D11Be6C55A4e07dCC9','0x35A18000230DA775CAc24873d00Ff85BccdeD550','0x70e36f6BF80a52b3B46b3aF8e106CC0ed743E8e4', '0xccF4429DB6322D5C611ee964527D42E5d685DD6a', '0x12392F67bdf24faE0AF363c24aC620a2f67DAd86', '0xFAce851a4921ce59e912d19329929CE6da6EB0c7', '0x95b4eF2869eBD94BEb4eEE400a99824BF5DC325b', '0x4B0181102A0112A2ef11AbEE5563bb4a3176c9d7', '0xe65cdB6479BaC1e22340E4E755fAE7E509EcD06c', '0x80a2AE356fc9ef4305676f7a3E2Ed04e12C33946', '0x041171993284df560249B57358F931D9eB7b925D', '0x7713DD9Ca933848F6819F38B8352D9A15EA73F67']:
		return fetch_abi("0x3363bae2fc44da742df13cd3ee94b6bb868ea376")
	
	#REP
	if contract_address == '0x1985365e9f78359a9B6AD760e32412f4a445E862':
		return fetch_abi('0x6c114b96b7a0e679c2594e3884f11526797e43d1')

	#USDC
	if contract_address == '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48':
		return fetch_abi('0xa2327a938febf5fec13bacfb16ae10ecbc4cbdcf')

	#AAVE
	if contract_address == '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9':
		return fetch_abi('0x96f68837877fd0414b55050c9e794aecdbcfca59')

	#USDP
	if contract_address == '0x8E870D67F660D95d5be530380D0eC0bd388289E1':
		return fetch_abi('0xb54d4e8bb827f99af764b37249990fa9d6840e20')

	#TUSD
	if contract_address == '0x0000000000085d4780B73119b644AE5ecd22b376':
		return fetch_abi('0xb650eb28d35691dd1bd481325d40e65273844f9b')
	
	#Compound Comptroller
	if contract_address == '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B':
		return fetch_abi('0xbafe01ff935c7305907c33bf824352ee5979b526')
	
	#BUSD
	if contract_address == '0x4Fabb145d64652a948d72533023f6E7A623C7C53':
		return fetch_abi('0x2a3f1a37c04f82aa274f5353834b2d002db91015')

	#renFIL
	if contract_address == '0xD5147bc8e386d91Cc5DBE72099DAC6C9b99276F5':
		return fetch_abi('0xa074139a4975318e7c011783031504d1c177f8ca')
	
	#AMPL
	if contract_address == '0xD46bA6D942050d489DBd938a2C909A5d5039A161':
		return fetch_abi('0xd0e3f82ab04b983c05263cf3bf52481fbaa435b1')
	
	#stETH
	if contract_address == '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84':
		return fetch_abi('0x17144556fd3424edc8fc8a4c940b2d04936d17eb')

	#UST
	if contract_address == '0xa693B19d2931d498c5B318dF961919BB4aee87a5':
		return fetch_abi('0x3ee18b2214aff97000d974cf647e7c347e8fa585')


	#contract_address = get_sound_artist(contract_address) #Check if the contract address is a known artist contract from sound.xyz, if so point it to the artist template, otherwise leave it unchanged.


	max_retries = 5
	try:
		response = requests.get( f"{ABI_ENDPOINT}{contract_address}", timeout = 20 )	
	except requests.exceptions.ReadTimeout as e:
		if retry < max_retries:
			print( f"Timeout, trying again" )
			return fetch_abi(contract_address,retry+1)
		else:
			print( f"Retried {retry} times" )
			print( f"Failed to get abi for address {contract_address}" )
			return None
	except Exception as e:
		print( f"Failed to get {contract_address} from {ABI_ENDPOINT}" )
		print( e )
		return None

	try:
		response_json = response.json()
		abi_json = json.loads(response_json['result'])
	except Exception as e:
		print( f"Failed to load json" )
		print( f"Contract address = {contract_address}" )
		print( e )
		if retry < max_retries:
			print( f"JSON error, trying again" )
			return fetch_abi(contract_address,retry+1)
		else:
			print( f"Retried {retry} times" )
			print( f"Failed to get abi" )
			return None
	#print( type( abi_json ) ) #list
	#print( type( abi_json[0] ) ) #dict
	return abi_json

def set_abi(contract_address,abi):
	try:
		with open(_cache_file) as f:
			_cache = json.load(f)
	except Exception as e:
		_cache = dict()
	
	if contract_address not in _cache.keys():
		_cache[contract_address] = abi	
		with open(_cache_file, 'w') as outfile:
			json.dump(_cache, outfile,indent=2)
	else:
		print( f"abi already exists" )
		


def get_cached_abi(contract_address,abikw=""):
	"""Per process over-the-network ABI file retriever"""

	try:
		with open(_cache_file) as f:
			_cache = json.load(f)
	except Exception as e:
		_cache = dict()
	
	if abikw:
		search_for = abikw
	else:
		search_for = contract_address
	
	abi = _cache.get(search_for)

	if not abi:
		print( f"No cached version of {search_for}" )
		print( _cache.keys() )
		print( _cache_file )
		abi = fetch_abi(search_for)
		if abi is not None:
			_cache[search_for] = abi
			with open(_cache_file, 'w') as outfile:
				json.dump(_cache, outfile,indent=2)
		
	return abi

def create_contract(web3,address):
	abi = get_cached_abi(address)
	#print( abi )
	contract = web3.eth.contract(address, abi=abi)
	return contract

#if __name__ == '__main__':
#	print( get_rarible_721() )
