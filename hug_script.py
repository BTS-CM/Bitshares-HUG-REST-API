# Required for rest of hug scripts
import bitshares
from bitshares.blockchain import Blockchain
import hug

def check_api_token(api_key):
	"""
	Check if the user's API key is valid.
	"""
	if (api_key == '123abc'):
		return True
	else:
		return False

@hug.get(examples='api_key=API_KEY')
def chain_info(api_key: hug.types.text, hug_timer=5):
	"""
	Bitshares current chain information!
	URL: http://HOST:PORT/function?variable=example_var_data&api_key=API_KEY
	"""
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
