#!/bin/bash
if ! [ -a .build-test ] ; then
	echo "Creating Virtual Environment"
	virtualenv .build-test -p python3
fi
source .build-test/bin/activate
pip3 -q install -r test-requirements.txt
PYTHONPATH=. pytest --cov=ons_ras_common --cov-report term-missing 
