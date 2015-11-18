#!/bin/bash
ALLURE=`which allure`
COV=`which coverage`
PYTHONPATH=$PWD $COV run --source=apps -m py.test --alluredir=db/reports/allure $@
STATUS=$?
if [ ! -z $ALLURE ]; then
    echo "allure found"
    if [ ! $STATUS -eq 0 ]; then
        echo "building allure reports"
        $ALLURE generate -o db/reports/reports generate db/reports/allure
    fi
fi
