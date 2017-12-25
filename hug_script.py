# Required for rest of hug scripts
import bitshares
from bitshares.account import Account
from bitshares.amount import Amount
from bitshares.asset import Asset
from bitshares.blockchain import Blockchain
from bitshares.market import Market
from bitshares.witness import Witness # Retrieving 1
from bitshares.witness import Witnesses # Listing many
from bitshares.proposal import Proposal # Retrieving 1
from bitshares.proposal import Proposals # Listing many
from bitshares.instance import shared_bitshares_instance # Used to reduce bitshares instance load
import hug

# uptick set node <host>  # THIS CHANGES THE WSS NODE!

def check_api_token(api_key):
	"""Check if the user's API key is valid."""
	if (api_key == '123abc'):
		return True
	else:
		return False

@hug.get(examples='api_key=API_KEY')
def chain_info(api_key: hug.types.text, hug_timer=5):
	"""Bitshares current chain information!"""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		chain = Blockchain()
		chain_info = chain.info()

		return {'id': chain_info['id'],
				'head_block_number': chain_info['head_block_number'],
				'head_block_id': chain_info['head_block_id'],
				'time': chain_info['time'],
				'current_witness': chain_info['current_witness'],
				'next_maintenance_time': chain_info['next_maintenance_time'],
				'last_budget_time': chain_info['last_budget_time'],
				'witness_budget': chain_info['witness_budget'],
				'accounts_registered_this_interval': chain_info['accounts_registered_this_interval'],
				'recently_missed_count': chain_info['recently_missed_count'],
				'current_aslot': chain_info['current_aslot'],
				'recent_slots_filled': chain_info['recent_slots_filled'],
				'dynamic_flags': chain_info['dynamic_flags'],
				'last_irreversible_block_num': chain_info['last_irreversible_block_num'],
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
def account_balances(account_name: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Bitshares account balances! Simply supply an account name & provide the API key!"""
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

		target_account_balances = target_account.balances
		if (len(target_account_balances) > 0):
			balance_json_list = []
			for balance in target_account_balances:
			  current_balance_target = Amount(balance)
			  balance_json_list.append({current_balance_target.symbol: current_balance_target.amount})

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

@hug.get(examples='account_name=blahblahblah&tx_limit=100&api_key=API_KEY')
def account_history(account_name: hug.types.text, tx_limit: hug.types.number, api_key: hug.types.text, hug_timer=5):
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

		target_account_history = target_account.history(first=0, limit=tx_limit)

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

@hug.get(examples='market_pair=USD:BTS&api_key=API_KEY')
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

@hug.get(examples='market_pair=USD:BTS&orderbook_limit=25&api_key=API_KEY')
def market_orderbook(market_pair: hug.types.text, orderbook_limit: hug.types.number, api_key: hug.types.text, hug_timer=5):
	"""Given a valid market pair (e.g. USD:BTS) and your desired orderbook size limit, output the market pair's orderbook (buy/sell order) information in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		if (orderbook_limit > 0):
			try:
			  target_market = Market(market_pair)
			except:
			  # Market is not valid
			  return {'valid_market': False,
			  		  'valid_key': True,
					  'took': float(hug_timer)}

			target_market_orderbook_data = target_market.orderbook(limit=orderbook_limit)

			return {'market_orderbook': target_market_orderbook_data,
					'market': market_pair,
					'valid_market': True,
					'valid_key': True,
					'took': float(hug_timer)}
		else:
			return {'invalid_orderbook_limit': True,
					'valid_key': True,
				  	'took': float(hug_timer)}

	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='market_pair=USD:BTS&api_key=API_KEY')
def market_24hr_vol(market_pair: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Given a valid market_pair (e.g. USD:BTS), output their 24hr market volume in JSON."""
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

@hug.get(examples='market_pair=USD:BTS&tx_limit=10&api_key=API_KEY')
def market_trade_history(market_pair: hug.types.text, tx_limit: hug.types.number, api_key: hug.types.text, hug_timer=5):
	"""Given a valid market_pair (e.g. USD:BTS) & a TX limit, output the market's trade history in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		if (tx_limit > 0):
			try:
			  target_market = Market(market_pair)
			except:
			  # Market is not valid
			  return {'valid_market': False,
			  		  'valid_tx_limit': True,
			  		  'valid_key': True,
					  'took': float(hug_timer)}

			temp_market_history = list(target_market.trades(limit=tx_limit))

			#print(temp_market_history)
			# (2017-12-24 15:37:21) 55.8699 USD 106.84792 BTS @ 1.912441583 BTS/USD
			market_history_json_list = []
			for market_trade in temp_market_history:
				str_market_trade = str(market_trade).split(" @ ")
				trade_rate = str_market_trade[1]
				trade_time = (str_market_trade[0].split(") ")[0]).replace("(", "")
				trade_details = str_market_trade[0].split(") ")[1]
				split_trade = trade_details.split(" ")
				market_history_json_list.append({"date": trade_time.split(" ")[0], "time": trade_time.split(" ")[1], "bought": split_trade[0] + " " + split_trade[1], "sold": split_trade[2] + " " + split_trade[3], "rate ": trade_rate})

			return {'market_trade_history': market_history_json_list,
					'market': market_pair,
					'valid_market': True,
					'valid_tx_limit': True,
					'valid_key': True,
					'took': float(hug_timer)}
		else:
			return {'valid_tx_limit': False,
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

		return {'id': target_witness['id'],
				'witness_account': target_witness['witness_account'],
				'last_aslot': target_witness['last_aslot'],
				'signing_key': target_witness['signing_key'],
				'pay_vb': target_witness['pay_vb'],
				'vote_id': target_witness['vote_id'],
				'total_votes': target_witness['total_votes'],
				'url': target_witness['url'],
				'total_missed': target_witness['total_missed'],
				'last_confirmed_block_num': target_witness['last_confirmed_block_num'],
				'witness_name': witness_name,
				'valid_witness': True,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='witness_name=blockchained&api_key=API_KEY')
def list_of_witnesses(witness_name: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Given a valid witness name, output witness data in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID

		list_of_witnesses = Witnesses()

		witness_data = []
		for witness in list_of_accounts:
			witness_data.append({'id': witness_data['id'],
							     'witness_account': witness_data['witness_account'],
								 'last_aslot': witness_data['last_aslot'],
								 'signing_key': witness_data['signing_key'],
								 'pay_vb': witness_data['pay_vb'],
								 'vote_id': witness_data['vote_id'],
								 'total_votes': witness_data['total_votes'],
								 'url': witness_data['url'],
								 'total_missed': witness_data['total_missed'],
								 'last_confirmed_block_num': witness_data['last_confirmed_block_num']
								})

		return {'witnesses': witness_data,
				'witness_count': len(list_of_witnesses),
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}
