#!/bin/bash

sudo docker image rm $(sudo docker image ls --format '{{.Repository}} {{.ID}}' | grep 'thechargedneutron' | awk '{print $2}')

sudo docker build . -f dockerfiles/base.dockerfile -t thechargedneutron/kvs:base --network=host
sudo docker push thechargedneutron/kvs:base

sudo docker build . -f dockerfiles/client.dockerfile -t thechargedneutron/kvs:client --network=host
sudo docker push thechargedneutron/kvs:client

sudo docker build . -f dockerfiles/frontend.dockerfile -t thechargedneutron/kvs:frontend --network=host
sudo docker push thechargedneutron/kvs:frontend

sudo docker build . -f dockerfiles/server.dockerfile -t thechargedneutron/kvs:server --network=host
sudo docker push thechargedneutron/kvs:server
