# Bitshares HUG API

![BTS HUG API Banner](https://i.imgur.com/secsyPh.png "BTS HUG API Banner")

# Updates

* Added new functions: get_bts_object, get_committee_member, get_committee_members, get_worker_proposals, get_worker.
* Changed formatting of readme & added more example json snippets.
*

## About

The intention of this Bitshares HUG REST API repo is to provide the Bitshares network an open-source high performance interface to the Bitshares network through simple GET requests.

By following the readme, you can easily recreate the API in your own control. Do remember to change the API key and the Bitshares FULL/API node you're connecting to. If you're creating a service which will produce a large amount of traffic, alert the node operator or consider running your own Bitshares node.

This HUG REST API makes heavy use of the [python-bitshares](https://github.com/xeroc/python-bitshares)

## TODO

    Improve the NGINX & Gunicorn configurations
    Implement additional HUG functions using websockets to access data inaccessible via python-bitshares.
    Work on date range input for iterable objects like market_history, trade_history and asset_holder data. (See: [Issue #30](https://github.com/xeroc/python-bitshares/issues/30)).
    Investigate functions for dumping large amounts of data (years of data).

## License

The contents of this entire repo should be considered MIT licenced.

## How to contribute

It's difficult to debug development issues whilst running behind Gunicorn & NGINX, you're best running the HUG REST API directly with HUG during development "hug -f bts_api.py". Note that running HUG directly in this manner should only be performed during development, it is not suitable for exposing directly to the public as a production ready API.

### About : Python-Bitshares

https://github.com/xeroc/python-bitshares/tree/develop

Created by xeroc, it's a thorough Bitshares python library which will be extensively used throughout this API. We won't be using it for any serious wallet control, purely the read-only blockchain/account/asset monitoring functionality.

Web Docs: http://docs.pybitshares.com/en/latest/

PDF Docs: https://media.readthedocs.org/pdf/python-bitshares/latest/python-bitshares.pdf

### About: HUG

> ##### Embrace the APIs of the future
> Drastically simplify API development over multiple interfaces. With hug, design and develop your API once, then expose it however your clients need to consume it. Be it locally, over HTTP, or through the command line - hug is the fastest and most modern way to create APIs on Python3.
> ##### Unparalleled performance
> hug has been built from the ground up with performance in mind. It is built to consume resources only when necessary and is then compiled with Cython to achieve amazing performance. As a result, hug consistently benchmarks as one of the fastest Python frameworks and without question takes the crown as the fastest high-level framework for Python 3.
>
> Source: [Official website](http://www.hug.rest/).

### About: Extensibility

If your HUG functions takes a long time to compute, then you must account for NGINX & Gunicorn worker timeouts (both the systemctl service file & the 'default' NGINX sites-available file). If you fail to account for this, the user will experience unhandled timeouts.

Since HUG utilizes Python, any Python library can be used to process/manipulate Bitshares data.

Ideally, rather than over-scraping data we should cache it or limit scraping functions to large batches (1000 instead of 500k etc).

---

## Install guide

This is an install guide for Ubuntu 17.10, it uses Python3+, HUG, Gunicorn & NGINX. If you change the OS or server components then the following guide will be less applicable, if you succeed please do provide a separate readme for alternative implementation solutions.

### Setup dependencies & Python environment

NOTE: We use the develop branch of python-bitshares because it uses the pycryptodome package (required since pycrypto is depreciated).

We create the 'btsapi' user, however you could rename this to whatever you want, just remember to change the NGINX & Gunicorn configuration files.

#### Setup a dedicated user

    adduser btsapi
    <ENTER NEW PASSWORD>
    <CONFIRM NEW PASSWORD>
    usermod -aG sudo btsapi
    sudo usermod -a -G www-data btsapi
    su - btsapi

#### Install required applications

    sudo apt-get install libffi-dev libssl-dev python3-pip python3-dev build-essential git nginx python3-setuptools virtualenv libcurl4-openssl-dev

#### Create Python virtual environment

    mkdir HUG
    virtualenv -p python3 HUG
    echo "source ./HUG/bin/activate" > access_env.sh
    chmod +x access_env.sh
    source access_env.sh

#### Install Python packages

    pip3 install --upgrade pip
    pip3 install --upgrade setuptools
    pip3 install --upgrade wheel
    pip3 install requests
    pip3 install lomond
    pip3 install hug
    pip3 install gunicorn
    git clone https://github.com/xeroc/python-bitshares.git -b develop
    pip3 install -e python-bitshares/

### Configure NGINX

NGINX serves as a reverse web proxy to Gunicorn & uses an UNIX socket instead of an IP address for referencing Gunicorn.

    Copy the nginx.conf file to /etc/nginx/
    Reset nginx (sudo service nginx restart)

    sudo mv default /etc/nginx/sites-available/default

### Implement SSL Cert

You aught to implement a free LetsEncrypt SSL certificate, this requires a domain name (they don't sign IP addresses) and it needs to be renewed every few months by running certbot again.

https://certbot.eff.org/

    sudo add-apt-repository ppa:certbot/certbot
    sudo apt-get update
    sudo apt-get install python-certbot-nginx
    sudo certbot --nginx -d api.domain.tld

### Configure Gunicorn

Official website: http://gunicorn.org/

Documentation: http://docs.gunicorn.org/en/stable/

Gunicorn is used to provide scalable worker process management and task buffering for the HUG REST API. Gunicorn's documentation states that each CPU can provide roughly 2-3+ Gunicorn workers, however it may be able to achieve a higher quantity (worth testing).

    cp gunicorn.service /etc/systemd/system/gunicorn.service
    sudo systemctl start gunicorn
    sudo systemctl enable gunicorn

### MISC

If you make changes to the service or the hug script:

    sudo systemctl daemon-reload
    sudo systemctl restart gunicorn

If you want to monitor Gunicorn:

    tail -f gunicorn_access_log
    tail -f gunicorn_error_log
    sudo systemctl status gunicorn

---

# Available HUG REST API functionality

This section will detail the functionality which will be available to the public through GET requests.

The functions are currently all read-only functions, enabling the public to request data from the network without the risk of exposing critical wallet controls.

## Asset functions

More info: [python-bitshares docs](https://python-bitshares.readthedocs.io/en/latest/asset.html)

### get_asset

Retrieve basic information about an individual asset & return in JSON!

##### Parameters

* asset_name `string`
* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_asset?asset_name=USD&api_key=123abc`

#### [Run Command](https://btsapi.grcnode.co.uk/get_asset?asset_name=USD&api_key=123abc)

#### [Example JSON output](./example_json/get_asset.json)

## MISC functions

### get_bts_oject

Request any Bitshares object's high level overview. Does not provide in depth details (ie asset/account/witness/.. details).

[List of possible objects](http://docs.bitshares.org/development/blockchain/objects.html)

##### Parameters

* object_id `2.0.0` (`string`)
* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_bts_oject?object_id=2.0.0&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/get_bts_oject?object_id=2.13.1&api_key=123abc)

## Blockchain functions

More info: [python-bitshares docs](http://docs.pybitshares.com/en/latest/blockchain.html)

### chain_info

A high level overview of the Bitshares chain information.

##### Parameters

* api_key `string`

##### Usage
`https://subdomain.domain.tld/chain_info?&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/chain_info?&api_key=123abc)

#### [Example JSON output](./example_json/chain_info.json)

###  get_chain_properties

Get chain properties, return in JSON.

##### Parameters

* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_chain_properties?api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/get_chain_properties?api_key=123abc)

#### Example JSON output

```
{
  "chain_properties": {
    "id": "2.11.0",
    "chain_id": "4018d7844c78f6a6c41c6a552b898022310fc5dec06da467ee7905a8dad512c8",
    "immutable_parameters": {
      "min_committee_member_count": 11,
      "min_witness_count": 11,
      "num_special_accounts": 100,
      "num_special_assets": 100
    }
  },
  "valid_key": true,
  "took": 0.01954
}
```

###  get_network

Return BTS network information in JSON.

##### Parameters

* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_network?api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/get_network?api_key=123abc)

#### Example JSON output

```
{
  "get_network": {
    "chain_id": "4018d7844c78f6a6c41c6a552b898022310fc5dec06da467ee7905a8dad512c8",
    "core_symbol": "BTS",
    "prefix": "BTS"
  },
  "valid_key": true,
  "took": 0.12271
}
```

### get_info

This call returns the dynamic global properties in JSON.

##### Parameters

* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_info?api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/get_info?api_key=123abc)

#### [Example JSON output](./example_json/get_info.json)

### get_config

Returns object 2.0.0 in JSON.

##### Parameters

* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_config?api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/get_config?api_key=123abc)

#### [Example JSON output](./example_json/get_config.json)

### get_block_details

Retrieve the specified block's date/time details, return in JSON.

##### Parameters

* block_number `number`
* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_block_details?block_number=10&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/get_block_details?block_number=10&api_key=123abc)

#### Example JSON output

```
{
  "previous": "0000003157e4849fe0d04e1f60462764d2a1f3d1",
  "timestamp": "2015-10-13T14:15:00",
  "witness": "1.6.5",
  "transaction_merkle_root": "0000000000000000000000000000000000000000",
  "extensions": [],
  "witness_signature": "1f0441febc1a8ce32287749ba5ec2797be8202eab82e6275340c508e16238cd7af21aba15a1c09bbeca03751fd4abb10580e1fea69a4f4dde17b9b54b4beeb654b",
  "transactions": [],
  "id": "50",
  "date": "2015-10-13T14:15:00",
  "block_number": 50,
  "valid_block_number": true,
  "valid_key": true,
  "took": 0.04568
}
```

### get_latest_block

Retrieve the details of the latest block, return in JSON.

##### Parameters

* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_latest_block?api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/get_latest_block?api_key=123abc)

#### [Example JSON output](./example_json/get_latest_block.json)

### get_all_accounts

Retrieve all Bitshares account names. Takes a while!

##### Parameters

* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_all_accounts?api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/get_all_accounts?api_key=123abc)

#### Example JSON output

```
{
  'accounts': [{acc1, acc2, ...}],
  'num_accounts': 500000,
  'valid_key': True,
  'took': 20.5
}
```

## Account information functions

More info: [python-bitshares docs](http://docs.pybitshares.com/en/latest/account.html)

### account_balances

Given a valid account name, output the user's balances in JSON.

##### Parameters

* account `string`
* api_key `string`

##### Usage
`https://subdomain.domain.tld/account_balances?account=example_usera&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/account_balances?account_name=xeroc&api_key=123abc)

#### [Example JSON output](./example_json/account_balances.json)

### account_open_orders

Given a valid account name, output the user's open orders in JSON.

##### Parameters

* account_name `string`
* api_key `string`

##### Usage
`https://subdomain.domain.tld/account_open_orders?account_name=example_usera&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/account_open_orders?account_name=abit&api_key=123abc)

#### [Example JSON output](./example_json/account_open_orders.json)

### account_callpositions

Given a valid account name, output the user's call positions in JSON.

Note: Highly verbose! Example contains 26k lines of JSON!

##### Parameters

* account `string`
* api_key `string`

##### Usage
`https://subdomain.domain.tld/account_callpositions?account=example_usera&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/account_callpositions?account_name=abit&api_key=123abc)

#### [Example JSON output](./example_json/account_callposition.json)

### account_history

Given a valid account name and transaction history limit (int), output the user's transaction history in JSON.

##### Parameters

* account_name `string`
* api_key `string`

##### Usage
`https://subdomain.domain.tld/account_history?account_name=example_user&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/account_history?account_name=xeroc&api_key=123abc)

#### [Example JSON output](./example_json/account_history.json)

### account_is_ltm

Given a valid account name, check if the user has LTM.

##### Parameters

* account_name `string`
* api_key `string`

##### Usage
`https://subdomain.domain.tld/account_is_ltm?account_name=example_user&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/account_is_ltm?account_name=xeroc&api_key=123abc)

#### Example JSON output

```
{
  "account_is_ltm": true,
  "account": "xeroc",
  "valid_account": true,
  "valid_key": true,
  "took": 0.14034
}
```

## DEX functions

More info: [python-bitshares docs](http://docs.pybitshares.com/en/latest/dex.html)

### list_fees

Retrieve the currently implemented fees in JSON format.

##### Parameters

* api_key `string`

##### Usage
`https://subdomain.domain.tld/list_fees?api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/list_fees?api_key=123abc)

#### [Example JSON output](./example_json/list_fees.json)

## Market information functions

More info: [python-bitshares docs](http://docs.pybitshares.com/en/latest/market.html)

### market_ticker

Given a valid market pair (e.g. USD:BTS), output the market pair's ticker information in JSON.

##### Parameters

* market_pair `base:quote` (`string`)
* api_key `string`

##### Usage
`https://subdomain.domain.tld/market_ticker?market_pair=USD:BTS&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/market_ticker?market_pair=USD:BTS&api_key=123abc)


#### [Example JSON output](./example_json/market_ticker.json)

### market_orderbook

Given a valid market pair (e.g. USD:BTS) and your desired orderbook size limit, output the market pair's orderbook (buy/sell order) information in JSON.

##### Parameters

* market_pair `base:quote` (`string`)
* orderbook_limit `number`
* api_key `string`

##### Usage
`https://subdomain.domain.tld/market_orderbook?market_pair=USD:BTS&orderbook_limit=25&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/market_orderbook?market_pair=USD:BTS&orderbook_limit=25&api_key=123abc)

#### [Example JSON output](./example_json/market_orderbook.json)

### market_24hr_vol

Given a valid market_pair (e.g. USD:BTS), output their 24hr market volume in JSON.

##### Parameters

* market_pair `base:quote` (`string`)
* api_key `string`

##### Usage
`https://subdomain.domain.tld/market_24hr_vol?market_pair=USD:BTS&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/market_24hr_vol?market_pair=USD:BTS&api_key=123abc)

#### [Example JSON output](./example_json/market_24hr_vol.json)

### market_trade_history

Given a valid market_pair (e.g. USD:BTS) & a TX limit, output the market's trade history in JSON.

##### Parameters

* market_pair `base:quote` (`string`)
* api_key `string`

##### Usage
`https://subdomain.domain.tld/market_trade_history?market_pair=USD:BTS&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/market_trade_history?market_pair=USD:BTS&api_key=123abc)

#### [Example JSON output](./example_json/market_trade_history.json)

## Witness functions

More info: [python-bitshares docs](http://docs.pybitshares.com/en/latest/witness.html)

### find_witness

Find details about a specific witness.

##### Parameters

* witness_name `string`
* api_key `string`

##### Usage
`https://subdomain.domain.tld/find_witness?witness_name=sc-ol&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/find_witness?witness_name=sc-ol&api_key=123abc)

#### [Example JSON output](./example_json/find_witness.json)

### list_of_witnesses

Retrieve a list of available witnesses.

##### Parameters

* api_key `string`

##### Usage
`https://subdomain.domain.tld/list_of_witnesses?api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/list_of_witnesses?api_key=123abc)

#### [Example JSON output](./example_json/list_of_witnesses.json)

## Committee functions

To implement this, we need to use the '[Requests](http://docs.python-requests.org/en/master/)' python library to access functionality currently not present in the python-bitshares library (AFAIK).

### get_committee_member

Retrieve a single committee member's full account (and role) information.

##### Parameters

* committee_id `1.5.0` (`string`)
* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_committee_member?committee_id=1.5.10&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/get_committee_member?committee_id=1.5.10&api_key=123abc)

#### [Example JSON output](./example_json/get_committee_member.json)

### get_committee_members

Get a list of all committee members, and their Bitshares account details.

#### [Run Command](https://btsapi.grcnode.co.uk/get_committee_members?api_key=123abc)

##### Usage
`https://subdomain.domain.tld/get_committee_members?api_key=API_KEY`

#### [Example JSON output](./example_json/get_committee_members.json)

## Worker functions

Similar to the committee function, we need to use the '[Requests](http://docs.python-requests.org/en/master/)' python library to access functionality currently not present in the python-bitshares library (AFAIK).

### get_worker

Retrieve an individual worker proposal & its associated proposer account details.

##### Parameters:

* worker_id `1.14.x` (`string`)
* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_worker?worker_id=1.14.x&api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/get_worker?worker_id=1.14.50&api_key=123abc)

#### [Example JSON output](./example_json/get_worker.json)

### get_worker_proposals

Retrieve a list of all worker proposals (including past/inactive) and the worker account details.

##### Parameters:

* api_key `string`

##### Usage
`https://subdomain.domain.tld/get_worker_proposals?api_key=API_KEY`

#### [Run Command](https://btsapi.grcnode.co.uk/get_worker_proposals?api_key=123abc)

#### [Example JSON output](./example_json/get_worker_proposals.json)
