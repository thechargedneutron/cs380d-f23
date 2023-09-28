#!/bin/bash

sudo docker image rm $(sudo docker image ls --format '{{.Repository}} {{.ID}}' | grep 'thechargedneutron' | awk '{print $2}')

cd dockerfiles

sudo docker build . -f base.dockerfile -t thechargedneutron/kvs:base --network=host
sudo docker push thechargedneutron/kvs:base

sudo docker build . -f client.dockerfile -t thechargedneutron/kvs:client --network=host
sudo docker push thechargedneutron/kvs:client

sudo docker build . -f frontend.dockerfile -t thechargedneutron/kvs:frontend --network=host
sudo docker push thechargedneutron/kvs:frontend

sudo docker build . -f server.dockerfile -t thechargedneutron/kvs:server --network=host
sudo docker push thechargedneutron/kvs:server

cd ..
