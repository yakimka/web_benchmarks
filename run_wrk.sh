#!/usr/bin/env sh

if [ -z "$1" ]; then
  echo "Error: Missing name."
  echo "Usage: $0 <name>"
  exit 1
fi

name="$1"
host="${2:-http://127.0.0.1:8000}"
duration="${3:-600}"
threads="${4:-4}"

if [ -z "$5" ]; then
  echo "Error: Missing connections count."
  exit 1
fi
connections="$5"

echo "Warming up for 10 seconds"
wrk -t 4 -c 40 -d 10 $host/plaintext > /dev/null 2>&1

echo "Running load testing for $name"
mkdir -p ./results
echo "Starting tests for $name $(date +"%Y-%m-%dT%H:%M:%S")" > ./results/$name.txt

echo "Plaintext endpoint"
echo "Start plaintext $(date +"%Y-%m-%dT%H:%M:%S")" >> ./results/$name.txt
wrk -t $threads -c $connections -d $duration --latency $host/plaintext >> ./results/$name.txt
echo "End test $(date +"%Y-%m-%dT%H:%M:%S")" >> ./results/$name.txt

echo "JSON endpoint"
echo "Start json $(date +"%Y-%m-%dT%H:%M:%S")" >> ./results/$name.txt
wrk -t $threads -c $connections -d $duration --latency $host/json >> ./results/$name.txt
echo "End test $(date +"%Y-%m-%dT%H:%M:%S")" >> ./results/$name.txt

echo "End $name $(date +"%Y-%m-%dT%H:%M:%S")" >> ./results/$name.txt
echo "Results saved to ./results/$name.txt"
