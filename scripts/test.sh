#!/bin/bash
if ! [ -a .build-test ] ; then
	echo "Creating Virtual Environment"
	virtualenv .build-test -p python3
fi
source .build-test/bin/activate
pip3 -q install -r test-requirements.txt
ONS_ENV=test PYTHONPATH="`pwd`:$PYTHONPATH" py.test --cov-report term-missing --cov-config=.coveragerc --cov=ons_ras_common/
