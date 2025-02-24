#!/bin/bash

INTERVAL=3

while true
do
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S")

  docker compose stats --no-stream --format \
  "{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}" \
  | while read line; do
      echo "$TIMESTAMP,$line" | tee -a docker_stats.log
    done

  sleep $INTERVAL
done
