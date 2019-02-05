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
import statistics
import uuid
import os

from bs4 import BeautifulSoup
import re
import json

full_node_list = [
	"wss://eu.nodes.bitshares.works", #location: "Central Europe - BitShares Infrastructure Program"
	"wss://us.nodes.bitshares.works", #location: "U.S. West Coast - BitShares Infrastructure Program"
	"wss://sg.nodes.bitshares.works", #location: "Singapore - BitShares Infrastructure Program"
	"wss://bitshares.crypto.fans/ws", #location: "Munich, Germany"
	"wss://bit.btsabc.org/ws", #location: "Hong Kong"
	"wss://api.bts.blckchnd.com", #location: "Falkenstein, Germany"
	"wss://openledger.hk/ws", #location: "Hong Kong"
	"wss://bitshares-api.wancloud.io/ws", #location:  "China"
	"wss://dex.rnglab.org", #location: "Netherlands"
	"wss://dexnode.net/ws", #location: "Dallas, USA"
	"wss://kc-us-dex.xeldal.com/ws", #location: "Kansas City, USA"
	"wss://la.dexnode.net/ws" #location: "Los Angeles, USA"
]

full_node_list_http = [
	"https://bitshares.crypto.fans/ws", #location: "Munich, Germany"
	"https://bit.btsabc.org/ws", #location: "Hong Kong"
	"https://api.bts.blckchnd.com", #location: "Falkenstein, Germany"
	"https://openledger.hk/ws", #location: "Hong Kong"
	"https://bitshares-api.wancloud.io/ws", #location:  "China"
	"https://dex.rnglab.org", #location: "Netherlands"
	"https://dexnode.net/ws", #location: "Dallas, USA"
	"https://kc-us-dex.xeldal.com/ws", #location: "Kansas City, USA"
	"https://la.dexnode.net/ws", #location: "Los Angeles, USA"
]

bitshares_api_node = BitShares(full_node_list, nobroadcast=True) # True prevents TX being broadcast through the HUG REST API
set_shared_bitshares_instance(bitshares_api_node)
# End of node configuration

def google_analytics(request, function_name):
	"""
	#Tracking usage via Google Analytics (using the measurement protocol).
	#Why? Because the only insight into the use of HUG currently is the access & error logs (insufficient).
	"""
	google_analytics_code = 'ANALYTICS_CODE'
	user_agent = str(request.user_agent)
	user_source = str(request.referer)
	user_request = str(request.uri)

	headers = {'User-Agent': user_agent}
	#function_dp = 'https://btsapi.grcnode.co.uk/' + function_name

	payload = { 'v': 1,
				'an': 'HUG',
				'tid': google_analytics_code,
				'cid': str(uuid.uuid4()),
				't': 'pageview',
				'ec': 'HUG',
				'ds': 'HUG',
				'el': 'HUG',
				'ea': 'Action',
				'dr': user_source,
				'de': 'JSON',
				'ua': user_agent,
				'dt': function_name,
				'dl': user_request,
				'ev': 0}

	try:
		r = requests.post('https://www.google-analytics.com/collect', params=payload, headers=headers)
	#	r = requests.post('www.google-analytics.com/collect', data=payload) # Either data or params
	except:
		print("COULD NOT POST TO GOOGLE ANALYTICS!")

def check_api_token(api_key):
	"""Check if the user's API key is valid. Change the API key if you want it to be private!"""
	if (api_key == '123abc'):
		return True
	else:
		return False

def request_json(input_data):
	"""Request JSON data from full node, given request data input.
	   More info: http://docs.python-requests.org/en/master/"""
	requested_data = None # Prevent no state if all servers fail!

	for full_node_url in full_node_list_http:
		try:
			requested_data = requests.get(full_node_url, data=input_data)
		except requests.exceptions.ConnectionError:
			continue

		if requested_data.status_code is not 200:
			# Fail! Move onto the next URL!
			continue
		else:
			# Stop iterating through the list of servers!
			break

	return requested_data

def extract_object(input_object):
	"""Chunk of code to extract the inner JSON from objects.
	   Required to reduce unneccessary lines in HUG script & improve maintainability."""
	temp_dict = {}
	for item in input_object:
		temp_dict[str(item)] = input_object[item]
	return temp_dict

def get_hertz_feed(reference_timestamp, current_timestamp, period_days, phase_days, reference_asset_value, amplitude):
	"""
	Given the reference timestamp, the current timestamp, the period (in days), the phase (in days), the reference asset value (ie 1.00) and the amplitude (> 0 && < 1), output the current hertz value.
	You can use this for an alternative HERTZ asset!
	"""
	hz_reference_timestamp = pendulum.parse(reference_timestamp).timestamp() # Retrieving the Bitshares2.0 genesis block timestamp
	hz_period = pendulum.SECONDS_PER_DAY * period_days
	hz_phase = pendulum.SECONDS_PER_DAY * phase_days
	hz_waveform = math.sin(((((current_timestamp - (hz_reference_timestamp + hz_phase))/hz_period) % 1) * hz_period) * ((2*math.pi)/hz_period)) # Only change for an alternative HERTZ ABA.
	hz_value = reference_asset_value + ((amplitude * reference_asset_value) * hz_waveform)
	return hz_value

@hug.get('/home', output=hug.output_format.html)
def root(request, hug_timer=60):
	"""
	Hertz price feed HTML page
	"""
	try:
		google_analytics(request, 'hertz price feed page')
	except:
		return "<html><body><h4>Internal HUG Server error!</h4></body></html>"

	hertz_json = get_hertz_value('123abc', request)
	html_start = "<html><head><title>Hertz Price feed page!</title><meta name='viewport' content='width=device-width, initial-scale=1'><link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/pure/1.0.0/tables-min.css' integrity='sha256-V3z3FoW8AUbK98fJsgyLL7scF5dNrNStj6Rp8tPsJs0=' crossorigin='anonymous' /></head><body>"
	table_start = "<h1>Hertz price feeds</h1><h2><a href='https://sites.google.com/view/hertz-aba/'>Hertz technical documentation</a></h2><h3>White Paper: <a href='https://steemit.com/bitshares/@cm-steem/hertz-is-now-live-on-the-bts-dex'>Steemit Post with PDF mirrors</a></h3><table class='pure-table pure-table-bordered'><thead><tr><th>Name</th><th>Timestamp</th><th>Settlement Price</th><th>CER</th><th>MCR</th><th>MSSR</th><th>URL</th></tr></thead><tbody>"
	table_rows = ""

	witness = hertz_json['witness_feeds']
	# Unofficial reference row
	unofficial_reference = hertz_json['unofficial_reference']

	settlement_price_list = []
	cer_list = []

	for key, value in witness.items():
		settlement_price = value['settlement_price']['api_calculated_rate']

		if (settlement_price > 0):
			settlement_price_list.append(settlement_price)

			try:
				witness_url = value['witness_url']
			except:
				witness_url = None

			core_exchange_rate = value['core_exchange_rate']['api_calculated_rate']
			cer_list.append(core_exchange_rate)

			maintenance_collateral_ratio = value['maintenance_collateral_ratio']
			maximum_short_squeeze_ratio = value['maximum_short_squeeze_ratio']
			witness_name = value['witness_name']
			parsed_timestamp = pendulum.parse(value['publish_timestamp'])
			current_timestamp = pendulum.now()
			time_difference = current_timestamp.diff(parsed_timestamp).in_minutes()

			if (time_difference > 0):
				time_difference_text = str(time_difference) + " Mins ago"
			else:
				time_difference_text = "< 1 Min ago"

			usd_settlement_price = settlement_price * unofficial_reference['bts_price_in_usd']

			if witness_url is None:
				table_rows += "<tr><td><a href='http://open-explorer.io/#/accounts/" + str(witness_name) + "'>" + str(witness_name) + "</a></td><td>" + time_difference_text + "</td><td>" + "{0:.2f}".format(settlement_price) + " BTS ($" + "{0:.2f}".format(usd_settlement_price) + ")</td><td>" + "{0:.2f}".format(core_exchange_rate) + "</td><td>" + str(maintenance_collateral_ratio/10) + "%</td><td>" + str(maximum_short_squeeze_ratio/10) + "%</td><td>N/A</td></tr>"
			else:
				table_rows += "<tr><td><a href='http://open-explorer.io/#/accounts/" + str(witness_name) + "'>" + str(witness_name) + "</a></td><td>" + time_difference_text + "</td><td>" + "{0:.2f}".format(settlement_price) + " BTS ($" + "{0:.2f}".format(usd_settlement_price) + ")</td><td>" + "{0:.2f}".format(core_exchange_rate) + "</td><td>" + str(maintenance_collateral_ratio/10) + "%</td><td>" + str(maximum_short_squeeze_ratio/10) + "%</td><td><a href='" + str(witness_url) + "'>Link</a></td></tr>"
		else:
			continue

	table_rows += "<tr><td>Unofficial reference</td><td>Now</td><td>" + "{0:.2f}".format(unofficial_reference['hertz_price_in_bts']) + "</td><td>" + "{0:.2f}".format(unofficial_reference['core_exchange_rate']) + "</td><td>200.0%</td><td>110.0%</td><td><a href='https://btsapi.grcnode.co.uk'>Link</a></td></tr>"
	table_end = "</tbody></table></br>"

	active_feeds = hertz_json['current_feeds']
	if (active_feeds['settlement_price']['api_calculated_rate'] > 0):
		hertz_status = "Active"
	else:
		hertz_status = "Not Active"

	#active_details = "<h2>Price feed summary</h2><ul><li>Status: " + hertz_status + "</li><li>Settlement rate: " + "{0:.2f}".format(int(active_feeds['settlement_price']['api_calculated_rate'])/10) + "</li><li>CER: " + "{0:.2f}".format(int(active_feeds['core_exchange_rate']['api_calculated_rate'])/10) + "</li><li>MCR: " + "{0:.2f}".format(int(active_feeds['maintenance_collateral_ratio'])/10) + "</li><li>MSSR: " + "{0:.2f}".format((int(active_feeds['maximum_short_squeeze_ratio'])/10)) + "</li></ul>"

	settlement_price_median = statistics.median(settlement_price_list)

	cer_median = statistics.median(cer_list)

	extra_details = "<h2>Extra reference info</h2><ul><li>Median settle price: " + "{0:.2f}".format(settlement_price_median) + "</li><li>Median CER: " + "{0:.2f}".format(cer_median) + "</li><li>BTS price in USD: " + "{0:.2f}".format(unofficial_reference['bts_price_in_usd']) + "</li><li>USD price in BTS: " + "{0:.2f}".format(unofficial_reference['usd_price_in_bts']) + "</li><li> Hertz price in USD: " + "{0:.2f}".format(unofficial_reference['hertz_price_in_usd']) + "</li><li><a href='https://btsapi.grcnode.co.uk/get_hertz_value?api_key=123abc'>Hertz JSON price feed data</a></li></ul>"
	html_end = "</body></html>"

	output_html = html_start + table_start + table_rows + table_end + extra_details + html_end

	return output_html

@hug.get(examples='api_key=API_KEY')
def get_hertz_value(api_key: hug.types.text, request, hug_timer=15):
	"""Retrieve reference Hertz feed price value in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		google_analytics(request, 'get_hertz_value')

		# Getting the value of USD in BTS
		market = Market("USD:BTS") # Set reference market to USD:BTS
		price = market.ticker()["quoteSettlement_price"] # Get Settlement price of USD
		price.invert() # Switching from quantity of BTS per USD to USD price of one BTS.

		hertz_reference_timestamp = "2015-10-13T14:12:24+00:00" # Bitshares 2.0 genesis block timestamp
		hertz_current_timestamp = pendulum.now().timestamp() # Current timestamp for reference within the hertz script
		hertz_amplitude = 0.14 # 14% fluctuating the price feed $+-0.14 (1% per day)
		hertz_period_days = 28 # Aka wavelength, time for one full SIN wave cycle.
		hertz_phase_days = 0.908056 # Time offset from genesis till the first wednesday, to set wednesday as the primary Hz day.
		hertz_reference_asset_value = 1.00 # $1.00 USD, not much point changing as the ratio will be the same.

		hertz_value = get_hertz_feed(hertz_reference_timestamp, hertz_current_timestamp, hertz_period_days, hertz_phase_days, hertz_reference_asset_value, hertz_amplitude)
		hertz = Price(hertz_value, "USD/HERTZ") # Limit the hertz_usd decimal places & convert from float.

		# Calculate HERTZ price in BTS (THIS IS WHAT YOU PUBLISH!)
		hertz_bts = price.as_base("BTS") * hertz.as_quote("HERTZ")

		unofficial_data = {'hertz_price_in_usd': hertz['price'],
						   'hertz_price_in_bts': hertz_bts['price'],
						   'core_exchange_rate': hertz_bts['price']*0.80,
						   'usd_price_in_bts': 1/price['price'],
						   'bts_price_in_usd': price['price']}
		########

		try:
		  target_asset = Asset("HERTZ", full=True)
		except:
		  return {'valid_asset': False,
				  'valid_key': True,
				  'took': float(hug_timer)}

		try:
		  bitasset_data = target_asset['bitasset_data_id']
		except:
		  bitasset_data = None

		extracted_object = extract_object(target_asset)

		bitasset_data = extracted_object['bitasset_data']
		current_feeds = bitasset_data['current_feed']
		current_feed_settlement_price = current_feeds['settlement_price']
		current_feed_cer = current_feeds['core_exchange_rate']

		if (int(current_feed_settlement_price['base']['amount']) > 0 and int(current_feed_settlement_price['quote']['amount']) > 0):
			current_feed_settlement_price['api_calculated_rate'] = int(current_feed_settlement_price['quote']['amount'])/int(current_feed_settlement_price['base']['amount'])
		else:
			current_feed_settlement_price['api_calculated_rate'] = 0

		if (int(current_feed_cer['base']['amount']) > 0 and int(current_feed_cer['quote']['amount']) > 0):
			current_feed_cer['api_calculated_rate'] = int(current_feed_cer['quote']['amount'])/int(current_feed_cer['base']['amount'])
		else:
			current_feed_cer['api_calculated_rate'] = 0

		witness_feeds = bitasset_data['feeds']
		witness_feed_data = {}
		witness_iterator = 0

		for witness_feed in witness_feeds:
			# Extract that data!
			witness_id = witness_feed[0]
			witness_iterator += 1

			try:
			  target_account = Account(str(witness_id))
			except:
			  print("Witness account doesn't work?!")

			extracted_object = extract_object(target_account)

			witness_name = extracted_object['name']
			publish_timestamp = witness_feed[1][0]
			feed_data = witness_feed[1][1]
			settlement_price = feed_data['settlement_price']

			if (int(settlement_price['quote']['amount']) > 0):
				maintenance_collateral_ratio = feed_data['maintenance_collateral_ratio']
				maximum_short_squeeze_ratio = feed_data['maximum_short_squeeze_ratio']
				core_exchange_rate = feed_data['core_exchange_rate']

				settlement_price_before = int(settlement_price['quote']['amount'])/int(settlement_price['base']['amount'])
				core_exchange_rate_before = int(core_exchange_rate['quote']['amount'])/(int(core_exchange_rate['base']['amount']))

				settlement_price['api_calculated_rate'] = settlement_price_before / 10
				core_exchange_rate['api_calculated_rate'] = core_exchange_rate_before / 10

				try:
					target_witness = Witness(witness_name)
				except:
					target_witness = None

				if (target_witness is not None):
					witness_role_data = extract_object(target_witness)
					witness_identity = witness_role_data['id']
					witness_url = witness_role_data['url']
					witness_feed_data[str(witness_iterator)] = {'witness_account_id': witness_id,
											  'witness_name': witness_name,
											  'witness_id': witness_identity,
											  'witness_url': witness_url,
											  'publish_timestamp': publish_timestamp,
											  'settlement_price': settlement_price,
											  'maintenance_collateral_ratio': maintenance_collateral_ratio,
											  'maximum_short_squeeze_ratio': maximum_short_squeeze_ratio,
											  'core_exchange_rate': core_exchange_rate}
				else:
					witness_feed_data[str(witness_iterator)] = {'witness_account_id': witness_id,
											  'witness_name': witness_name,
											  'witness_id': "N/A",
											  'witness_url': "#",
											  'publish_timestamp': publish_timestamp,
											  'settlement_price': settlement_price,
											  'maintenance_collateral_ratio': maintenance_collateral_ratio,
											  'maximum_short_squeeze_ratio': maximum_short_squeeze_ratio,
											  'core_exchange_rate': core_exchange_rate}
			else:
				continue

		return {'unofficial_reference': unofficial_data,
				'witness_feeds': witness_feed_data,
				'current_feeds': current_feeds,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='object_id=1.2.0&api_key=API_KEY')
def get_bts_object(object_id: hug.types.text, api_key: hug.types.text, request, hug_timer=15):
	"""Enable retrieving and displaying any BTS object in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		google_analytics(request, 'get_bts_object')
		try:
			retrieved_object = bitshares_api_node.rpc.get_objects([object_id])[0]
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
def get_committee_member(committee_id: hug.types.text, api_key: hug.types.text, request, hug_timer=15):
	"""Retrieve information about a single committee member (inc full account details)!"""
	if (check_api_token(api_key) == True): # Check the api key
		google_analytics(request, 'get_committee_member')
		if ("1.5." not in committee_id):
			return {'valid_committee_id': False,
					'valid_key': True,
					'took': float(hug_timer)}

		try:
			target_committee_member = bitshares_api_node.rpc.get_objects([committee_id])[0]
		except:
			return {'valid_committee_id': False,
					'valid_key': True,
					'took': float(hug_timer)}

		if target_committee_member is None:
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
				'valid_committee_id': True,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='api_key=API_KEY')
def get_committee_members(api_key: hug.types.text, request, hug_timer=15):
	"""Get a list of all committee members!"""
	if (check_api_token(api_key) == True): # Check the api key
		google_analytics(request, 'get_committee_members')
		# API KEY VALID
		num_committee_members_request = request_json('{"jsonrpc": "2.0", "method": "get_committee_count", "params": [], "id": 1}')

		if num_committee_members_request.status_code is not 200:
			# We want to catch any failed GET requests!
			return {'request_status_code_error': True,
				  'valid_key': True,
				  'took': float(hug_timer)}
		else:
			# Request was successful
			active_committee_members = Blockchain().config()['active_committee_members']

			num_committee_members = num_committee_members_request.json()['result']

			committee_member_list = []
			for member in range(num_committee_members):
				committee_id = "1.5." + str(member)
				current_committee_member = bitshares_api_node.rpc.get_objects([committee_id])[0]

				if committee_id in active_committee_members:
					current_committee_member['status'] = True
					# The following needs to be cached, it takes far too long to query even just 11 account names..
					#target_account = Account(current_committee_member['committee_member_account'])
					#target_account_data = extract_object(target_account)
					#current_committee_member['name'] = target_account_data['name']
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
def get_worker(worker_id: hug.types.text, api_key: hug.types.text, request, hug_timer=15):
	"""Retrieve a specific worker proposal & the details of the worker's account."""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'get_worker')
		if '1.14' not in worker_id:
			return {'valid_worker': False,
					'valid_key': True,
					'took': float(hug_timer)}

		try:
			target_worker = bitshares_api_node.rpc.get_objects([worker_id])[0]
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
def get_worker_proposals(api_key: hug.types.text, request, hug_timer=15):
	"""Get a list of all worker proposals!"""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'get_worker_proposals')

		num_workers_request = request_json('{"jsonrpc": "2.0", "method": "get_worker_count", "params": [], "id": 1}')

		if num_workers_request.status_code is not 200:
			# We want to catch any failed GET requests!
			return {'request_status_code_error': True,
				  'valid_key': True,
				  'took': float(hug_timer)}
		else:
			# Request is valid!
			num_workers = num_workers_request.json()['result']

			worker_list = []
			for worker in range(num_workers):
				worker_id = "1.14." + str(worker)
				current_worker = bitshares_api_node.rpc.get_objects([worker_id])[0]

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
def get_asset(asset_name: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Get info regarding a single input asset."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		google_analytics(request, 'get_asset')
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
def chain_info(api_key: hug.types.text, request, hug_timer=5):
	"""Bitshares current chain information!"""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'chain_info')
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
def get_chain_properties(api_key: hug.types.text, request, hug_timer=5):
	"""Bitshares current chain properties!"""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'get_chain_properties')
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
def get_config(api_key: hug.types.text, request, hug_timer=5):
	"""Bitshares current chain config!"""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'get_config')
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
def get_info(api_key: hug.types.text, request, hug_timer=5):
	"""Bitshares current chain info!"""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'get_info')
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
def get_network(api_key: hug.types.text, request, hug_timer=5):
	"""Bitshares current chain network!"""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'get_network')
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
def get_block_details(block_number: hug.types.number, api_key: hug.types.text, request, hug_timer=5):
	"""Retrieve a specific block's details (date & time) & output in JSON!"""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'get_block_details')

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
def get_latest_block(api_key: hug.types.text, request, hug_timer=5):
	"""Retrieve the latest block's details (date & time) & output in JSON!"""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'get_latest_block')

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

@hug.get(examples='account_name=blahblahblah&api_key=API_KEY')
def account_info(account_name: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Retrieve information about an individual Bitshares account!"""
	google_analytics(request, 'account_info')

	try:
	  target_account = Account(account_name)
	except:
	  return {'account': account_name,
			  'valid_account': False,
			  'valid_key': True,
			  'took': float(hug_timer)}

	extracted_object = extract_object(target_account)

	return {'account_info': extracted_object,
			'valid_account': True,
			'valid_key': True,
			'took': float(hug_timer)}

@hug.get(examples='account_name=blahblahblah&api_key=API_KEY')
def full_account_info(account_name: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
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
def account_balances(account_name: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Bitshares account balances! Simply supply an account name & provide the API key!"""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'account_balances')

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
def account_open_orders(account_name: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Bitshares account open orders! Simply supply an account name & provide the API key!"""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'account_open_orders')

		try:
		  target_account = Account(account_name)
		except:
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
					'valid_key': True,
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
def account_callpositions(account_name: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Bitshares account call positions! Simply supply an account name & provide the API key!"""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'account_callpositions')

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
		return {'valid_account': False,
				'valid_key': False,
				'took': float(hug_timer)}

@hug.get(examples='account_name=blahblahblah&api_key=API_KEY')
def account_history(account_name: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Given a valid account name, output the user's history in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'account_history')

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
def account_is_ltm(account_name: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Given a valid account name, check if they're LTM & output confirmation as JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'account_is_ltm')

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
def market_ticker(market_pair: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Given a valid market pair, retrieve ticker data & output as JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'market_ticker')

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

@hug.get(examples='market_pair=USD:BTS&api_key=API_KEY')
def market_orderbook(market_pair: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Given a valid market pair (e.g. USD:BTS) and your desired orderbook size limit, output the market pair's orderbook (buy/sell order) information in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'market_orderbook')

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

@hug.get(examples='market_pair=USD:BTS&api_key=API_KEY')
def market_24hr_vol(market_pair: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Given a valid market_pair (e.g. USD:BTS), output their 24hr market volume in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'market_24hr_vol')

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
@hug.get(examples='market_pair=USD:BTS&api_key=API_KEY')
def market_trade_history(market_pair: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Given a valid market_pair (e.g. USD:BTS) & a TX limit, output the market's trade history in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'market_trade_history')

		try:
		  target_market = Market(market_pair)
		except:
		  # Market is not valid
		  return {'valid_market': False,
				  'valid_key': True,
				  'took': float(hug_timer)}

		temp_market_history = list(target_market.trades(limit=100))

		#print(temp_market_history)
		# (2017-12-24 15:37:21) 55.8699 USD 106.84792 BTS @ 1.912441583 BTS/USD
		market_history_json_list = []
		for market_trade in temp_market_history:
			str_market_trade = str(market_trade).split(" @ ") # ["(2017-12-24 15:37:21) 55.8699 USD 106.84792 BTS", "1.912441583 BTS/USD"]
			trade_rate = str_market_trade[1] # "1.912441583 BTS/USD"
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
def find_witness(witness_name: hug.types.text, api_key: hug.types.text, request, hug_timer=5):
	"""Given a valid witness name, output witness data in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'find_witness')

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
def list_of_witnesses(api_key: hug.types.text, request, hug_timer=5):
	"""Output the list of active witnesses in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'list_of_witnesses')

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
def list_fees(api_key: hug.types.text, request, hug_timer=5):
	"""Output the current Bitshares network fees in JSON."""
	if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
		google_analytics(request, 'list_fees')

		network_fees = Dex().returnFees()
		extracted_fees = extract_object(network_fees)

		return {'network_fees': extracted_fees,
				'valid_key': True,
				'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}

###################################

def create_wordy_phrase(input_csi_str):
		"""
		Summarise input comma separated integer
		"""
		input_int_str = (str(input_csi_str)).replace(',', '')
		input_len = len(input_int_str)
		if (input_len > 3 and input_len < 7):
				temp = round((int(input_int_str)/1000), 1)
				return str(temp) + "K"
		elif (input_len >= 7 and input_len < 10):
				temp = round((int(input_int_str)/1000000), 2)
				return str(temp) + "M"
		elif (input_len >= 10 and input_len < 14):
				temp = round((int(input_int_str)/1000000000), 3)
				return str(temp) + "B"
		else:
				return input_csi_str

def scrape_blocktivity():
		"""
		A function to scrape blocktivity.
		Outputs to JSON.
		"""
		scraped_page = requests.get("https://blocktivity.info")
		if scraped_page.status_code == 200:
				soup = BeautifulSoup(scraped_page.text, 'html.parser')
				crypto_rows = soup.findAll('tr', attrs={'class': 'font_size_row'})

				blocktivity_summary = []
				for row in crypto_rows:
						crypto_columns = row.findAll('td')
						ranking = re.sub('<[^>]+?>', '', str(crypto_columns[0]))
						#logo = (str(crypto_columns[1]).split('cell">'))[1].split('</td')[0]
						name = re.sub('<[^>]+?>', '', str(crypto_columns[2])).split(' ⓘ')
						activity = re.sub('<[^>]+?>', '', str(crypto_columns[3])).strip('Op ').strip('Tx')
						rounded_activity = create_wordy_phrase(activity)
						average_7d = re.sub('<[^>]+?>', '', str(crypto_columns[4])).strip('Op ').strip('Tx')
						rounded_average_7d = create_wordy_phrase(average_7d)
						record = re.sub('<[^>]+?>', '', str(crypto_columns[5])).strip('Op ').strip('Tx')
						rounded_record = create_wordy_phrase(record)
						market_cap = re.sub('<[^>]+?>', '', str(crypto_columns[6]))
						AVI = re.sub('<[^>]+?>', '', str(crypto_columns[7]))
						CUI = re.sub('<[^>]+?>', '', str(crypto_columns[8])).strip('ⓘ')

						blocktivity_summary.append({'rank': ranking, 'ticker': name[0], 'name': name[1], 'activity': activity, 'rounded_activity': rounded_activity, 'average_7d':average_7d, 'rounded_average_7d':rounded_average_7d, 'record': record, 'rounded_record': rounded_record, 'market_cap': market_cap, 'AVI': AVI, 'CUI':CUI})

				now = pendulum.now() # Getting the time
				current_timestamp = int(round(now.timestamp())) # Converting to timestamp

				write_json_to_disk('blocktivity.json', {'timestamp': current_timestamp, 'blocktivity_summary': blocktivity_summary}) # Storing to disk

				return {'timestamp': current_timestamp, 'blocktivity_summary': blocktivity_summary}
		else:
				return None

def return_json_file_contents(filename):
		"""
		Simple function for returning the contents of the input JSON file
		"""
		try:
				with open(filename) as json_data:
						return json.load(json_data)
		except IOError:
				print("File not found: "+filename)
				return None

def write_json_to_disk(filename, json_data):
		"""
		When called, write the json_data to a json file.
		"""
		with open(filename, 'w') as outfile:
				json.dump(json_data, outfile)

@hug.get(examples='api_key=API_KEY')
def current_blocktivity(api_key: hug.types.text, hug_timer=5):
		"""Output the current Blocktivity stats."""
		if (check_api_token(api_key) == True): # Check the api key
		# API KEY VALID
				need_to_download = True
				MAX_STATS_LIFETIME = 60

				if os.path.isfile("./blocktivity.json"):
						existing_json = return_json_file_contents("./blocktivity.json")
						now = pendulum.now() # Getting the time
						current_timestamp = int(round(now.timestamp())) # Converting to timestamp

						if (current_timestamp - int(existing_json['timestamp']) < MAX_STATS_LIFETIME):
								"""Data is still valid - let's return it instead of fetching it!"""
								print("Blocktivity JSON within lifetime - using cached copy!")
								blocktivity_storage = existing_json
						else:
								"""No existing file"""
								print("Blocktivity JSON too old - downloading fresh copy!")
								blocktivity_storage = scrape_blocktivity()
				else:
						"""File doesn't exist"""
						blocktivity_storage = scrape_blocktivity()

				if blocktivity_storage != None:
						return {'result': blocktivity_storage,
										'valid_key': True,
										'took': float(hug_timer)}
				else:
						return {'valid_key': True,
										'success': False,
										'error_message': 'blocktivity storage returned None!',
										'took': float(hug_timer)}
		else:
		# API KEY INVALID!
				return {'valid_key': False,
								'took': float(hug_timer)}
