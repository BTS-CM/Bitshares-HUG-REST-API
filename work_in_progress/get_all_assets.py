@hug.get(examples='api_key=API_KEY')
def get_all_assets(api_key: hug.types.text, hug_timer=5):
	"""Retrieve a list of all assets registered on the BTS DEX, return as JSON."""
	if (check_api_token(api_key) == True): # Check the api key
	# API KEY VALID
		for
		try:
		  target_asset = Asset(asset_name)
		except:
		  return {'valid_asset': False,
				  'valid_key': True,
				  'took': float(hug_timer)}

		try:
		  bitasset_data = target_asset['bitasset_data_id']
		except:
		  bitasset_data = None

		if bitasset_data is not None:
	 		return {'id': target_asset['id'],
					'symbol': target_asset['symbol'],
					'precision': target_asset['precision'],
					'issuer': target_asset['issuer'],
					'options': target_asset['options'],
					'dynamic_asset_data_id': target_asset['dynamic_asset_data_id'],
					'bitasset_data_id': target_asset['bitasset_data_id'],
					'permissions': target_asset['permissions'],
					'flags': target_asset['flags'],
					'description': target_asset['description'],
					'valid_asset': True,
					'valid_key': True,
					'took': float(hug_timer)}
		else:
			return {'id': target_asset['id'],
					'symbol': target_asset['symbol'],
					'precision': target_asset['precision'],
					'issuer': target_asset['issuer'],
					'options': target_asset['options'],
					'dynamic_asset_data_id': target_asset['dynamic_asset_data_id'],
					'permissions': target_asset['permissions'],
					'flags': target_asset['flags'],
					'description': target_asset['description'],
					'valid_asset': True,
					'valid_key': True,
					'took': float(hug_timer)}
	else:
	# API KEY INVALID!
		return {'valid_key': False,
				'took': float(hug_timer)}
