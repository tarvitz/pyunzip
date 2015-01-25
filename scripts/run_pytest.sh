#!/bin/bash
PYTEST=`which py.test-2.7`
DJANGO_MODULE_SETTINGS='app.settings.test'
ALLURE_DIR=db/allure
PYTEST_CONFIG=tests/pytest/base.ini
ALLURE=`which allure`
ALLURE_VERSION="1.4.4"
ALLURE_DIR="db/allure"
ALLURE_OUTPUT_DIR="db/reports"

if [ -z $PYTEST ]; then
    echo "py.test not found"
    exit 0
fi
$PYTEST --ds=$DJANGO_MODULE_SETTINGS --alluredir=$ALLURE_DIR -c $PYTEST_CONFIG $@

if [ ! $? -eq 0 ]; then
    echo "generating reports"
    $ALLURE generate $ALLURE_DIR -o $ALLURE_OUTPUT_DIR -v $ALLURE_VERSION
fi
