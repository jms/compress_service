#!/bin/bash

cd $HOME/compress_service
git pull 
sudo pip install -r requirements.txt

sudo cp -v  $HOME/compress_service/zipit.conf /etc/supervisor/conf.d/
sudo cp -v  $HOME/compress_service/rqworker.conf /etc/supervisor/conf.d/

sudo cp -v  $HOME/compress_service/zipit-nginx.conf /etc/nginx/conf.d/

sudo service nginx reload 
sudo service supervisor restart 


