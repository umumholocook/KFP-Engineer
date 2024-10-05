#!/bin/bash -e

if [[ "$OSTYPE" == "darwin"* ]]; then
    # check if python 3 exist
    if [[ "$(python3 -V)" =~ "Python 3" ]]; then
        echo "Running KFP bot on OSX with python 3"
        pkill -9 Python
        python3 main.py
        exit 0
    fi
elif [[ "$OSTYPE" == "linux-gnu" ]]; then
    echo "Running KFP bot on Linux with python"
    killall -9 python
    python main.py
    exit 0
fi
pkill -9 Python
# else, run the default python
python main.py
