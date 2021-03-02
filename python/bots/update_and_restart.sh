#!/bin/bash -e

echo "pulling latest code"
git pull
echo "restarting KFP bot..."
bash start_kfp.sh
