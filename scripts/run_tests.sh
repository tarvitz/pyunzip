#!/bin/bash
python manage.py test --settings=app.settings.test $@
