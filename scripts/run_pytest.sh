#!/bin/bash
ALLURE=`which allure.sh`
COV=`which coverage`
PYTHONPATH=$PWD $COV run --source=apps -m py.test --alluredir=../db/reports/allure
if [ ! -z $ALLURE ]; then
    if [ ! $? -eq 0 ]; then
        echo "building allure reports"
        $ALLURE generate generate db/reports/allure/ -o db/reports/reports -v 1.4.11
    fi
fi
