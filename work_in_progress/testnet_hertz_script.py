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

@hug.get(examples='api_key=API_KEY')
def get_hertz_value(api_key: hug.types.text, hug_timer=15):
	"""Retrieve reference Hertz feed price value in JSON."""
	if (check_api_token(api_key) == True): # Check the api key

		hertz_reference_timestamp = "2015-10-13T14:12:24+00:00" # Bitshares 2.0 genesis block timestamp
		hertz_current_timestamp = pendulum.now().timestamp() # Current timestamp for reference within the hertz script
		hertz_amplitude = 0.14 # 14% fluctuating the price feed $+-0.14 (1% per day)
		hertz_period_days = 28 # Aka wavelength, time for one full SIN wave cycle.
		hertz_phase_days = 0.908056 # Time offset from genesis till the first wednesday, to set wednesday as the primary Hz day.
		hertz_reference_asset_value = 1.00 # $1.00 USD, not much point changing as the ratio will be the same.

		hertz_value = get_hertz_feed(hertz_reference_timestamp, hertz_current_timestamp, hertz_period_days, hertz_phase_days, hertz_reference_asset_value, hertz_amplitude)

		#market = Market("USD:TEST") # Set reference market to USD:TEST
		#price = market.ticker()["quoteSettlement_price"] # Get Settlement price of USD
		#price.invert() # Switching from quantity of TEST per USD to USD price of one TEST.
		#hertz = Price(hertz_value, "USD/HERTZ") # Limit the hertz_usd decimal places & convert from float.
		#hertz_bts = hertz / price # Calculate HERTZ price in TEST

		market = Market("USD:TEST") # Set reference market to USD:TEST
		price = market.ticker()["quoteSettlement_price"] # Get Settlement price of USD
		hertz = Price(hertz_value, "USD/HERTZ") # Limit the hertz_usd decimal places & convert from float.
		hertz_bts = hertz / price # Calculate HERTZ price in TEST (THIS IS WHAT YOU PUBLISH!)

		unofficial_data = {'hertz_price_in_usd': hertz['price'],
						   'hertz_price_in_bts': hertz_bts['price'],
						   'bts_price_in_usd': price.invert()['price']}
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

		witness_feeds = bitasset_data['feeds']
		witness_feed_data = {}
		witness_iterator = 0

		for witness_feed in witness_feeds:
			# Extract that data!
			witness_id = witness_feed[0]

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

				target_witness = Witness(witness_name)
				witness_role_data = extract_object(target_witness)
				witness_identity = witness_role_data['id']
				witness_url = witness_role_data['url']

				settlement_price['api_calculated_rate'] = (int(settlement_price['quote']['amount'])/settlement_price['base']['amount'])/10
				core_exchange_rate['api_calculated_rate'] = (int(core_exchange_rate['quote']['amount'])/core_exchange_rate['base']['amount'])/10

				witness_feed_data[str(witness_iterator)] = ({'witness_account_id': witness_id,
										  'witness_name': witness_name,
										  'witness_id': witness_identity,
										  'witness_url': witness_url,
										  'publish_timestamp': publish_timestamp,
										  'settlement_price': settlement_price,
										  'maintenance_collateral_ratio': maintenance_collateral_ratio,
										  'maximum_short_squeeze_ratio': maximum_short_squeeze_ratio,
										  'core_exchange_rate': core_exchange_rate})
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
