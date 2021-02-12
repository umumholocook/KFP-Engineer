#!/bin/bash -e
if [[ "$OSTYPE" == "darwin"* ]]; then
    # check if python 3 exist
    if [[ "$(python3 -V)" =~ "Python 3" ]]; then
        echo "Running Shiritori on OSX with python 3"
        python3 shiritori.py
        exit 0
    fi
fi
# else, run the default python
python shiritori.py