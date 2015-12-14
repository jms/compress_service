#!/bin/bash

cd $HOME/compress_service
git pull 
sudo pip install -r requirements.txt

sudo cp -v  $HOME/compress_service/deploy/supervisor.d/zipit.conf /etc/supervisor/conf.d/
sudo cp -v  $HOME/compress_service/deploy/supervisor.d/rqworker.conf /etc/supervisor/conf.d/
sudo cp -v  $HOME/compress_service/deploy/nginx/zipit-nginx.conf /etc/nginx/sites-available/

sudo service nginx stop
sudo service supervisor restart 


