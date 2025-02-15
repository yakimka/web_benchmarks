#!/usr/bin/env sh

if [ -z "$1" ]; then
  echo "Error: Missing name."
  echo "Usage: $0 <name> [host] [duration] [threads] [connections]"
  exit 1
fi

name="$1"
host="${2:-http://127.0.0.1:8000}"
duration="${3:-600}"
threads="${4:-8}"
connections="${5:-180}"

export NAME=$name
mkdir -p ./results


echo "Running load testing for $name"

echo "Plaintext endpoint"
echo "Warming up for 10 seconds"
wrk -t 4 -c 40 -d 10 $host/plaintext > /dev/null 2>&1
echo "Running for $duration seconds"
wrk -t $threads -c $connections -d $duration -s wrk/write_stats.lua $host/plaintext

echo "API endpoint"
echo "Warming up for 10 seconds"
wrk -t 4 -c 40 -d 10 $host/api > /dev/null 2>&1
echo "Running for $duration seconds"
wrk -t $threads -c $connections -d $duration -s wrk/write_stats.lua $host/api

echo "All done!"
