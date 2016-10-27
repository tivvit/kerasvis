#!/usr/bin/env bash

NAME=$USER"0kerasvis"
docker-compose -p $NAME up -d
docker-compose -p $NAME ps
