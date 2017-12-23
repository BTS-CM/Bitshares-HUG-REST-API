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

Documentation: http://docs.pybitshares.com/en/latest/

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
