#!/bin/bash

# Set RAM disk size in MB
SIZE_MB=128

# Define the mount point
data_dir="$(pwd)/data"

# Ensure the directory exists
mkdir -p "$data_dir"

# Unmount the RAM disk if it is already mounted
sudo umount "$data_dir" 2>/dev/null

# Mount the RAM disk using tmpfs
sudo mount -t tmpfs -o size=${SIZE_MB}M tmpfs "$data_dir"

echo "RAM disk of ${SIZE_MB}MB mounted at $data_dir"
echo "You can test the RAM disk speed by running: sudo dd if=/dev/zero of=$data_dir/test bs=4k count=10000 && rm $data_dir/test"
