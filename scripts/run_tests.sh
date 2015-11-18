#!/bin/bash
python manage.py test --parallel --settings=app.settings.test $@
