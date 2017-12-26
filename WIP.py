@hug.get(examples='market_pair=USD:BTS&tx_limit=10&time_from=2017-12-24&time_to=2017-12-24&api_key=API_KEY')
def specific_market_trade_history(market_pair: hug.types.text, tx_limit: hug.types.number, time_from: hug.types.text, time_to: hug.types.text, api_key: hug.types.text, hug_timer=5):
	"""Given a valid market_pair (e.g. USD:BTS), a trade history limit and a specific time range, output the market's trade history in JSON."""
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

			temp_market_history = list(target_market.trades(limit=tx_limit, start=time_from, stop=time_to))

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

			return {'specific_market_trade_history': market_history_json_list,
					'market': market_pair,
					'time_from': time_from,
					'time_to': time_to,
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
