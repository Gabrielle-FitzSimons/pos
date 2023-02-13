#!/bin/bash

sudo apt-get update
# sudo apt-get install -y build-essential

# curl https://pyenv.run | bash
# pyenv install pyenv install 3.9.13
sudo apt-get install -y python3.10-venv

sudo apt-get install -y authbind

sudo touch /etc/authbind/byport/80
sudo chmod 500 /etc/authbind/byport/80
sudo chown ubuntu /etc/authbind/byport/80

authbind gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80