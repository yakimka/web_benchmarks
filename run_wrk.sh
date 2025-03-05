#!/usr/bin/env sh

if [ -z "$1" ]; then
  echo "Error: Missing host."
  echo "Usage: $0 <host> <name> [duration] [threads] [connections]"
  exit 1
fi

if [ -z "$2" ]; then
  echo "Error: Missing name."
  echo "Usage: $0 <host> <name> [duration] [threads] [connections]"
  exit 1
fi

host="$1"
name="$2"
duration="${3:-600}"
threads="${4:-8}"
connections="${5:-64}"

export NAME=$name
mkdir -p ./results


echo "Running load testing for $name"

echo "Plaintext endpoint"
echo "Warming up for 10 seconds"
wrk -t 4 -c 40 -d 10 $host/plaintext > /dev/null 2>&1
echo "Running $(date)"
wrk -t $threads -c $connections -d $duration -s wrk/write_stats.lua $host/plaintext

echo "API endpoint"
echo "Warming up for 10 seconds"
wrk -t 4 -c 40 -d 10 $host/api > /dev/null 2>&1
echo "Running $(date)"
wrk -t $threads -c $connections -d $duration -s wrk/write_stats.lua -H "X-Header: somevaluefromheader" "$host/api?query=somequerystringfromclient"

echo "DB endpoint"
echo "Warming up for 10 seconds"
wrk -t 4 -c 40 -d 10 $host/db > /dev/null 2>&1
echo "Running $(date)"
wrk -t $threads -c $connections -d $duration -s wrk/write_stats.lua $host/db

echo "All done!"
