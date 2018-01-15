# Required for rest of hug scripts
from bitshares import BitShares
from bitshares.account import Account
from bitshares.amount import Amount
from bitshares.asset import Asset
from bitshares.blockchain import Blockchain
from bitshares.block import Block
from bitshares.dex import Dex
from bitshares.price import Price
from bitshares.market import Market
from bitshares.witness import Witness # Retrieving 1
from bitshares.witness import Witnesses # Listing many
from bitshares.proposal import Proposal # Retrieving 1
from bitshares.proposal import Proposals # Listing many
from bitshares.instance import shared_bitshares_instance # Used to reduce bitshares instance load
from bitshares.instance import set_shared_bitshares_instance # Used to reduce bitshares instance load
import bitshares
import hug
import requests
import pendulum
import math

"""
Configure Full/API node for querying network info
Only enable ONE of the following API nodes!
"""
full_node_url = 'wss://node.testnet.bitshares.eu'
bitshares_full_node = BitShares(full_node_url, nobroadcast=False)
set_shared_bitshares_instance(bitshares_full_node)
# End of node configuration

def check_api_token(api_key):
	"""Check if the user's API key is valid."""
	if (api_key == '123abc'):
		return True
	else:
		return False

def request_json(input_data):
	"""Request JSON data from full node, given request data input.
	   More info: http://docs.python-requests.org/en/master/"""
	request_url = full_node_url.replace("wss://", "https://") # Your selected full node must have HTTPS configured properly!
	requested_data = requests.get(request_url, data=input_data)
	return requested_data

"""
request = request_json('')

if request.status_code is not 200:
	# We want to catch any failed GET requests!
	return {'request_status_code_error': True,
		  'valid_key': True,
		  'took': float(hug_timer)}

valid_request_json = request.json()
"""

def extract_object(input_object):
	"""Chunk of code to extract the inner JSON from objects.
	   Required to reduce unneccessary lines in HUG script & improve maintainability."""
	temp_dict = {}
	for item in input_object:
		temp_dict[str(item)] = input_object[item]
	return temp_dict

@hug.get(examples='object_id=1.2.0&api_key=API_KEY')
def get_bts_oject(object_id: hug.types.text, api_key: hug.types.text, hug_timer=15):
	"""Enable retrieving and displaying any TEST object in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		try:
			retrieved_object = bitshares_full_node.rpc.get_objects([object_id])[0]
		except:
			return {'valid_object_id': False,
					'valid_key': True,
					'took': float(hug_timer)}
		if retrieved_object is not None:
			return {'retrieved_object': retrieved_object,
					'valid_object_id': True,
					'valid_key': True,
					'took': float(hug_timer)}
		else:
			return {'valid_object_id': False,
					'valid_key': True,
					'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='committee_id=1.5.10&api_key=API_KEY')
def get_committee_member(committee_id: hug.types.text, api_key: hug.types.text, hug_timer=15):
	"""Retrieve information about a single committee member (inc full account details)!"""
	if (check_api_token(api_key) == True): # Check the api key
		try:
			target_committee_member = bitshares_full_node.rpc.get_objects([committee_id])[0]
		except:
			return {'valid_committee_id': False,
					'valid_key': True,
					'took': float(hug_timer)}

		target_account = Account(target_committee_member['committee_member_account'], full=True) # Full info!
		target_account_data = extract_object(target_account)

		active_committee_members = Blockchain().config()['active_committee_members']

		if committee_id in active_committee_members:
			target_account_data['status'] = True
		else:
			target_account_data['status'] = False

		target_committee_member['committee_member_details'] = target_account_data

		return {'get_committee_member': target_committee_member,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='api_key=API_KEY')
def get_committee_members(api_key: hug.types.text, hug_timer=15):
	"""Get a list of all committee members!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		num_committee_members_request = request_json('{"jsonrpc": "2.0", "method": "get_committee_count", "params": [], "id": 1}')

		if num_committee_members_request.status_code is not 200:
			# We want to catch any failed GET requests!
			return {'request_status_code_error': True,
				  'valid_key': True,
				  'took': float(hug_timer)}

		active_committee_members = Blockchain().config()['active_committee_members']

		num_committee_members = num_committee_members_request.json()['result']

		committee_member_list = []
		for member in range(num_committee_members):
			committee_id = "1.5." + str(member)
			current_committee_member = bitshares_full_node.rpc.get_objects([committee_id])[0]

			if committee_id in active_committee_members:
				current_committee_member['status'] = True
			else:
				current_committee_member['status'] = False

			committee_member_list.append(current_committee_member)

		return {'committee_members': committee_member_list,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='worker_id=1.14.50&api_key=API_KEY')
def get_worker(worker_id: hug.types.text, api_key: hug.types.text, hug_timer=15):
	"""Retrieve a specific worker proposal & the details of the worker's account."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		try:
			target_worker = bitshares_full_node.rpc.get_objects([worker_id])[0]
		except:
			return {'valid_worker': False,
					'valid_key': True,
					'took': float(hug_timer)}

		target_account = Account(target_worker['worker_account'], full=True)

		target_account_data = extract_object(target_account)

		target_worker['worker_account_details'] = target_account_data

		return {'worker': target_worker,
				'valid_worker': True,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='api_key=API_KEY')
def get_worker_proposals(api_key: hug.types.text, hug_timer=15):
	"""Get a list of all worker proposals!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		num_workers_request = request_json('{"jsonrpc": "2.0", "method": "get_worker_count", "params": [], "id": 1}')

		if num_workers_request.status_code is not 200:
			# We want to catch any failed GET requests!
			return {'request_status_code_error': True,
				  'valid_key': True,
				  'took': float(hug_timer)}

		num_workers = num_workers_request.json()['result']

		worker_list = []
		for worker in range(num_workers):
			worker_id = "1.14." + str(worker)
			current_worker = bitshares_full_node.rpc.get_objects([worker_id])[0]

			target_account = Account(current_worker['worker_account'])
			target_account_data = extract_object(target_account)

			current_worker['worker_account_details'] = target_account_data

			worker_list.append(current_worker)

		return {'workers': worker_list,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='asset_name=USD&api_key=API_KEY')
def get_asset(asset_name: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Get info regarding a single input asset."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		try:
		  target_asset = Asset(asset_name, full=True)
		except:
		  return {'valid_asset': False,
				  'valid_key': True,
				  'took': float(hug_timer)}

		try:
		  bitasset_data = target_asset['bitasset_data_id']
		except:
		  bitasset_data = None

		extracted_object = extract_object(target_asset)

		return {'asset_data': extracted_object,
				'valid_asset': True,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='api_key=API_KEY')
def chain_info(api_key: hug.types.text, hug_timer=5):
	"""Bitshares current chain information!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		chain = Blockchain()
		chain_info = chain.info()

		extracted_object = extract_object(chain_info)

		return {'chain_info': extracted_object,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='api_key=API_KEY')
def get_chain_properties(api_key: hug.types.text, hug_timer=5):
	"""Bitshares current chain properties!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		chain = Blockchain()
		chain_properties = chain.get_chain_properties()

		return {'chain_properties': chain_properties,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='api_key=API_KEY')
def get_config(api_key: hug.types.text, hug_timer=5):
	"""Bitshares current chain config!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		chain = Blockchain()
		chain_config = chain.config()

		return {'chain_config': chain_config,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='api_key=API_KEY')
def get_info(api_key: hug.types.text, hug_timer=5):
	"""Bitshares current chain info!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		chain = Blockchain()
		chain_info = chain.info()

		return {'chain_info': chain_info,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='api_key=API_KEY')
def get_network(api_key: hug.types.text, hug_timer=5):
	"""Bitshares current chain network!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		chain = Blockchain()
		chain_get_network = chain.get_network()

		return {'get_network': chain_get_network,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='block_number=50&api_key=API_KEY')
def get_block_details(block_number: hug.types.number, api_key: hug.types.text, hug_timer=5):
	"""Retrieve a specific block's details (date & time) & output in JSON!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		try:
			target_block = Block(block_number)
		except:
			return {'valid_block_number': False,
					'valid_key': True,
					'took': float(hug_timer)}

		chain = Blockchain()
		block_date = chain.block_time(block_number)

		return {'previous': target_block['previous'],
				'timestamp': target_block['timestamp'],
				'witness': target_block['witness'],
				'transaction_merkle_root': target_block['transaction_merkle_root'],
				'extensions': target_block['extensions'],
				'witness_signature': target_block['witness_signature'],
				'transactions': target_block['transactions'],
				'id': target_block['id'],
				'date': block_date,
				'block_number': block_number,
				'valid_block_number': True,
				'valid_key': True,
				'took': float(hug_timer)}

	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='api_key=API_KEY')
def get_latest_block(api_key: hug.types.text, hug_timer=5):
	"""Retrieve the latest block's details (date & time) & output in JSON!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		chain = Blockchain()
		current_block_number = chain.get_current_block_num()
		block_date = chain.block_time(current_block_number)

		target_block = Block(current_block_number)

		return {'previous': target_block['previous'],
				'timestamp': target_block['timestamp'],
				'witness': target_block['witness'],
				'transaction_merkle_root': target_block['transaction_merkle_root'],
				'extensions': target_block['extensions'],
				'witness_signature': target_block['witness_signature'],
				'transactions': target_block['transactions'],
				'id': target_block['id'],
				'block_date': block_date,
				'block_number': current_block_number,
				'valid_block_number': True,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

##################

@hug.get(examples='api_key=API_KEY')
def get_all_accounts(api_key: hug.types.text, hug_timer=5):
	"""Retrieve all Bitshares account names. Takes a while!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		chain = Blockchain()
		chain_get_all_accounts = chain.get_all_accounts()

		list_of_accounts = []

		for account in chain_get_all_accounts:
			list_of_accounts.append(account)

		return {'accounts': list_of_accounts,
				'num_accounts': len(list_of_accounts),
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='account_name=blahblahblah&api_key=API_KEY')
def account_info(account_name: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Retrieve information about an individual Bitshares account!"""
	try:
	  target_account = Account(account_name)
	except:
	  return {'valid_account': False,
			  'account': account_name,
			  'valid_key': True,
			  'took': float(hug_timer)}

	extracted_object = extract_object(target_account)

	return {'account_info': extracted_object,
			'valid_key': True,
			'took': float(hug_timer)}

@hug.get(examples='account_name=blahblahblah&api_key=API_KEY')
def full_account_info(account_name: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Retrieve verbose information about an individual Bitshares account!"""
	try:
	  target_account = Account(account_name, full=True)
	except:
	  return {'valid_account': False,
			  'account': account_name,
			  'valid_key': True,
			  'took': float(hug_timer)}

	extracted_object = extract_object(target_account)

	return {'full_account_info': extracted_object,
			'valid_key': True,
			'took': float(hug_timer)}

@hug.get(examples='account_name=blahblahblah&api_key=API_KEY')
def account_balances(account_name: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Bitshares account balances! Simply supply an account name & provide the API key!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		try:
		  target_account = Account(account_name, full=True)
		except:
		  print("Account doesn't exist.")
		  return {'valid_account': False,
				  'account': account_name,
				  'valid_key': True,
				  'took': float(hug_timer)}

		target_account_balances = target_account.balances
		if (len(target_account_balances) > 0):

			balance_json_list = {}
			for balance in target_account_balances:
			  current_balance_target = Amount(balance)
			  balance_json_list[current_balance_target.symbol] = current_balance_target.amount

			return {'balances': balance_json_list,
					'account_has_balances': True,
					'account': account_name,
					'valid_account': True,
					'valid_key': True,
					'took': float(hug_timer)}
		else:
			return {'account_has_balances': False,
					'account': account_name,
					'valid_account': True,
					'valid_key': True,
					'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='account_name=blahblahblah&api_key=API_KEY')
def account_open_orders(account_name: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Bitshares account open orders! Simply supply an account name & provide the API key!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		try:
		  target_account = Account(account_name)
		except:
		  print("Account doesn't exist.")
		  return {'valid_account': False,
				  'account': account_name,
				  'valid_key': True,
				  'took': float(hug_timer)}

		target_account_oo = target_account.openorders
		if (len(target_account_oo) > 0):
			open_order_list = []
			for open_order in target_account_oo:
				oo_str = str(open_order)
				first_split_oo = oo_str.split(" @ ")[0]
				second_split_oo = first_split_oo.split(" ")
				buy_amount = second_split_oo[0].replace(",", "")
				buy_asset = "Buy: " + second_split_oo[1]
				sell_amount = second_split_oo[2].replace(",", "")
				sell_asset = "Sell: " + second_split_oo[3]
				rate_amount = float(sell_amount) / float(buy_amount)
				rate_asset = second_split_oo[3] + "/" + second_split_oo[1]
				open_order_list.append({sell_asset: sell_amount, buy_asset: buy_amount, rate_asset: rate_amount})

			return {'open_orders': open_order_list,
					'account_has_open_orders': True,
					'account': account_name,
					'valid_account': True,
					'took': float(hug_timer)}
		else:
			return {'account_has_open_orders': False,
					'account': account_name,
					'valid_account': True,
					'valid_key': True,
					'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='account_name=blahblahblah&api_key=API_KEY')
def account_callpositions(account_name: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Bitshares account call positions! Simply supply an account name & provide the API key!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		try:
		  target_account = Account(account_name)
		except:
		  print("Account doesn't exist.")
		  return {'valid_account': False,
				  'account': account_name,
				  'valid_key': True,
				  'took': float(hug_timer)}

		target_account_callpos = target_account.callpositions
		if (len(target_account_callpos) > 0):
			return {'call_positions': target_account_callpos,
					'account_has_call_positions': True,
					'account': account_name,
					'valid_account': True,
					'valid_key': True,
					'took': float(hug_timer)}
		else:
			return {'account_has_call_positions': False,
					'account': account_name,
					'valid_account': True,
					'valid_key': True,
					'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='account_name=blahblahblah&api_key=API_KEY')
def account_history(account_name: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Given a valid account name, output the user's history in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		try:
		  target_account = Account(account_name)
		except:
		  # Accoun is not valid!
		  return {'valid_account': False,
				  'account': account_name,
				  'valid_key': True,
				  'took': float(hug_timer)}

		target_account_history = target_account.history(first=0, last=100, limit=100)

		tx_container = []
		for transaction in target_account_history:
		  tx_container.append(transaction)

		if (len(tx_container) > 0):
			return {'tx_history': tx_container,
					'account_has_tx_history': True,
					'account': account_name,
					'valid_account': True,
					'valid_key': True,
					'took': float(hug_timer)}
		else:
			return {'account_has_tx_history': False,
					'account': account_name,
					'valid_account': True,
					'valid_key': True,
					'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='account_name=blahblahblah&api_key=API_KEY')
def account_is_ltm(account_name: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Given a valid account name, check if they're LTM & output confirmation as JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		try:
		  target_account = Account(account_name)
		except:
		  # Accoun is not valid!
		  return {'valid_account': False,
				  'account': account_name,
				  'valid_key': True,
				  'took': float(hug_timer)}

		target_account_ltm = target_account.is_ltm

		return {'account_is_ltm': target_account_ltm,
				'account': account_name,
				'valid_account': True,
				'valid_key': True,
				'took': float(hug_timer)}

	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='market_pair=USD:TEST&api_key=API_KEY')
def market_ticker(market_pair: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Given a valid market pair, retrieve ticker data & output as JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		try:
		  target_market = Market(market_pair)
		except:
		  # Market is not valid
		  return {'valid_market': False,
				  'valid_key': True,
				  'took': float(hug_timer)}

		target_market_ticker_data = target_market.ticker()

		return {'market_ticker': target_market_ticker_data,
				'market': market_pair,
				'valid_market': True,
				'valid_key': True,
				'took': float(hug_timer)}

	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='market_pair=USD:TEST&api_key=API_KEY')
def market_orderbook(market_pair: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Given a valid market pair (e.g. USD:TEST) and your desired orderbook size limit, output the market pair's orderbook (buy/sell order) information in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		try:
		  target_market = Market(market_pair)
		except:
		  # Market is not valid
		  return {'valid_market': False,
				  'valid_key': True,
				  'took': float(hug_timer)}

		target_market_orderbook_data = target_market.orderbook(limit=50)

		return {'market_orderbook': target_market_orderbook_data,
				'market': market_pair,
				'valid_market': True,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='market_pair=USD:TEST&api_key=API_KEY')
def market_24hr_vol(market_pair: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Given a valid market_pair (e.g. USD:TEST), output their 24hr market volume in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		try:
		  target_market = Market(market_pair)
		except:
		  # Market is not valid
		  return {'valid_market': False,
				  'valid_key': True,
				  'took': float(hug_timer)}

		return {'market_volume_24hr': target_market.volume24h(),
				'market': market_pair,
				'valid_market': True,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}
# &start_time=2017-07-01T00:00:00Z&stop_time=2017-07-10T00:00:00Z
# start_time: hug.types.text, stop_time: hug.types.text,
@hug.get(examples='market_pair=USD:TEST&api_key=API_KEY')
def market_trade_history(market_pair: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Given a valid market_pair (e.g. USD:TEST) & a TX limit, output the market's trade history in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		try:
		  target_market = Market(market_pair)
		except:
		  # Market is not valid
		  return {'valid_market': False,
				  'valid_key': True,
				  'took': float(hug_timer)}

		temp_market_history = list(target_market.trades(limit=100))

		#print(temp_market_history)
		# (2017-12-24 15:37:21) 55.8699 USD 106.84792 TEST @ 1.912441583 TEST/USD
		market_history_json_list = []
		for market_trade in temp_market_history:
			str_market_trade = str(market_trade).split(" @ ") # ["(2017-12-24 15:37:21) 55.8699 USD 106.84792 TEST", "1.912441583 TEST/USD"]
			trade_rate = str_market_trade[1] # "1.912441583 TEST/USD"
			trade_time = (str_market_trade[0].split(") ")[0]).replace("(", "")
			trade_details = str_market_trade[0].split(") ")[1]
			split_trade = trade_details.split(" ")
			market_history_json_list.append({"datetime": trade_time.replace(" ", "T"), "bought": split_trade[0] + " " + split_trade[1], "sold": split_trade[2] + " " + split_trade[3], "rate ": trade_rate})

		return {'market_trade_history': market_history_json_list,
				'market': market_pair,
				'valid_market': True,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='witness_name=blockchained&api_key=API_KEY')
def find_witness(witness_name: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Given a valid witness name, output witness data in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		try:
		  target_witness = Witness(witness_name)
		except:
		  # Market is not valid
		  return {'valid_witness': False,
				  'valid_key': True,
				  'took': float(hug_timer)}

		target_account = Account(target_witness['witness_account'], full=True)
		witness_account_data = extract_object(target_account)
		witness_role_data = extract_object(target_witness)

		active_witnesses = Blockchain().config()['active_witnesses']

		if witness_role_data['id'] in active_witnesses:
			witness_status = True
		else:
			witness_status = False

		return {'witness_role_data': witness_role_data,
				'witness_account_data': witness_account_data,
				'active_witness': witness_status,
				'valid_witness': True,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='api_key=API_KEY')
def list_of_witnesses(api_key: hug.types.text, hug_timer=5):
	"""Output the list of active witnesses in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		list_of_witnesses = Witnesses()

		witness_data = []
		for witness in list_of_witnesses:
			target_account = Account(witness['witness_account'])
			witness_account_data = extract_object(target_account)
			witness_role_data = extract_object(witness)

			active_witnesses = Blockchain().config()['active_witnesses']

			if witness_role_data['id'] in active_witnesses:
				witness_status = True
			else:
				witness_status = False

			witness_data.append({'witness_role_data': witness_role_data,
								 'witness_account_data': witness_account_data,
								 'witness_status': witness_status})

		return {'witnesses': witness_data,
				'witness_count': len(list_of_witnesses),
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='api_key=API_KEY')
def list_fees(api_key: hug.types.text, hug_timer=5):
	"""Output the current Bitshares network fees in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		network_fees = Dex().returnFees()

		extracted_fees = extract_object(network_fees)

		return {'network_fees': extracted_fees,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}
