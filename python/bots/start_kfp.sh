#!/bin/bash -e
if [[ "$OSTYPE" == "darwin"* ]]; then
    # check if python 3 exist
    if [[ "$(python3 -V)" =~ "Python 3" ]]; then
        echo "Running KFP bot on OSX with python 3"
        python3 main.py
        exit 0
    fi
fi
pkill -9 Python
# else, run the default python
python main.py
