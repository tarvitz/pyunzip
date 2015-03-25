#!/bin/bash

coverage run --source=apps -m py.test --alluredir=db/allure
coverage report --fail-under=90
allure generate db/allure -o db/reports -v 1.4.11
