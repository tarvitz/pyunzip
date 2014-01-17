#!/bin/bash
python manage.py runprofileserver --use-cprofile --prof-path=/tmp/prof/ 0.0.0.0:40000
