#!/bin/bash

INTERVAL=2

while true
do
  TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%S")

  docker compose stats --no-stream --format \
  "{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}" \
  | while read line; do
      echo "$TIMESTAMP,$line"
    done >> docker_stats.log

  sleep $INTERVAL
done
