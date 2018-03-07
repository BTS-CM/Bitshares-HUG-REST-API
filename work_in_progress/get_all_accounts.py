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
