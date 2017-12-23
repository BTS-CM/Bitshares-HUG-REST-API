# Bitshares HUG API

![BTS HUG API Banner](https://i.imgur.com/secsyPh.png "BTS HUG API Banner")

## TODO

    Improve the NGINX & Gunicorn configurations.

## License

The contents of this entire repo should be considered MIT licenced.

## How to contribute

It's difficult to debug development issues whilst running behind Gunicorn & NGINX, you're best running the HUG REST API directly with HUG during development "hug -f bts_api.py". Note that running HUG directly in this manner should only be performed during development, it is not suitable for exposing directly to the public as a production ready API.

If you want to donate: [Customminer](http://cryptofresh.com/u/customminer)

### About : Python-Bitshares

https://github.com/xeroc/python-bitshares/tree/develop

Created by xeroc, it's a thorough Bitshares python library which will be extensively used throughout this API. We won't be using it for any serious wallet control, purely the read-only blockchain/account/asset monitoring functionality.

Web Docs: http://docs.pybitshares.com/en/latest/

PDF Docs: https://media.readthedocs.org/pdf/python-bitshares/latest/python-bitshares.pdf

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

    sudo apt-get install libffi-dev libssl-dev python3-pip python3-dev build-essential git nginx python3-setuptools virtualenv

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

## Available functions

### chain_info

A high level overview of the Bitshares chain information.

Use: website/chain_info?&api_key=API_KEY

#### Example JSON output

```
{
 "id": "2.1.0",
 "head_block_number": 22901637,
 "head_block_id": "015d73858661412b31201155f6f77c772d044a95",
 "time": "2017-12-23T14:04:03",
 "current_witness": "1.6.16",
 "next_maintenance_time": "2017-12-23T15:00:00",
 "last_budget_time": "2017-12-23T14:00:00",
 "witness_budget": 112200000,
 "accounts_registered_this_interval": 10,
 "recently_missed_count": 0,
 "current_aslot": 23041161,
 "recent_slots_filled": "340282366920938463463374607431768211455",
 "dynamic_flags": 0,
 "last_irreversible_block_num": 22901622,
 "valid_key": true,
 "took": 0.12855
}
```

### account_balances

Given a valid account name, output the user's balances in JSON.

Use: website/account_balances?account=example_usera&api_key=API_KEY

#### Example JSON output

Note: 'balances' has been concatenated to save space in this example.

```
{
  "balances": [{"BTS": 780.3515},
              {"ROSE": 999.0},
              {"FASTCASS": 8.0},
              {"DELETIP": 12760.0}],
 "account_has_balances": true,
 "valid_account": true,
 "valid_key": true,
 "took": 0.50434
}
```

### account_open_orders

Given a valid account name, output the user's open orders in JSON.

Use: website/account_open_orders?account=example_usera&api_key=API_KEY

#### Example JSON output

```
{
  "open_orders": [{"Sell: USD": "558.8355", "Buy: OPEN.PPY": "553.30247", "USD/OPEN.PPY": 1.0100000095788477},
                 {"Sell: BEYONDBIT": "500", "Buy: WHALESHARE": "12500", "BEYONDBIT/WHALESHARE": 0.04}],
  "account_has_open_orders": true,
  "valid_account": true,
  "valid_key": true,
  "took": 0.24319
}
```

### account_callpositions

Given a valid account name, output the user's call positions in JSON.

Use: website/account_callpositions?account=example_usera&api_key=API_KEY

#### [Example JSON output](https://github.com/BTS-CM/Bitshares-HUG-REST-API/blob/master/example_json/account_callposition.json)

### account_history

Given a valid account name, output the user's history in JSON.

Use: website/account_history?account=example_user&tx_limit=10&api_key=API_KEY

#### [Example JSON output](https://github.com/BTS-CM/Bitshares-HUG-REST-API/blob/master/example_json/account_history.json)
