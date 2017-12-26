# Required for rest of hug scripts
import bitshares
from bitshares import BitShares
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
from bitshares.instance import set_shared_bitshares_instance # Used to reduce bitshares instance load
import hug

# Configure Full/API node for querying network info
# Only enable ONE of the following API nodes!
bitshares_full_node = BitShares(
	#"wss://singapore.bitshares.apasia.tech/ws", # Singapore. Telegram: @murda_ra
	#"wss://japan.bitshares.apasia.tech/ws", # Tokyo, Japan. Telegram: @murda_ra
	#"wss://seattle.bitshares.apasia.tech/ws", # Seattle, WA, USA. Telegram: @murda_ra
	#"wss://us-ny.bitshares.apasia.tech/ws", # New York, NY, USA. Telegram: @murda_ra
	#"wss://bitshares.apasia.tech/ws", # Bangkok, Thailand. Telegram: @murda_ra
	#"wss://slovenia.bitshares.apasia.tech/ws", # Slovenia. Telegram: @murda_ra
	#"wss://openledger.hk/ws", # Hone Kong. Telegram: @ronnyb
	#"wss://dex.rnglab.org", # Netherlands. Telegram: @naueh
	"wss://bitshares.openledger.info/ws", # Berlin, Germany. Telegram: @xeroc
	#"wss://bitshares.crypto.fans/ws", # https://crypto.fans/ Telegram: @startail
	#"wss://eu.openledger.info/ws", # Nuremberg, Germany. Telegram: @xeroc
    nobroadcast=False
)
set_shared_bitshares_instance(bitshares_full_node)
# End of node configuration

def check_api_token(api_key):
	"""Check if the user's API key is valid."""
	if (api_key == '123abc'):
		return True
	else:
		return False

@hug.get(examples='api_key=API_KEY')
def get_all_account_balances(api_key: hug.types.text, hug_timer=60):
	"""Retrieve all Bitshares account names & balances.
       WARNING: This may take hours to complete! """
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		chain = Blockchain()
		chain_get_all_accounts = chain.get_all_accounts()

		list_of_accounts = []

		for account in chain_get_all_accounts:
			target_account_balances = Account(account).balances
			if (len(target_account_balances) > 0):
				balance_json_list = []
				for balance in target_account_balances:
				  current_balance_target = Amount(balance)
				  balance_json_list.append({current_balance_target.symbol: current_balance_target.amount})

				list_of_accounts.append({'account_name': account, 'balances': balance_json_list})
			else:
				list_of_accounts.append({'account_name': account, 'balances': []})

		return {'accounts': list_of_accounts,
				'num_accounts': len(list_of_accounts),
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}
