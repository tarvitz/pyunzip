#!/bin/bash
lessc static/less/bootstrap-light.less > static/css/bootstrap-light.css
lessc static/less/bootstrap-dark.less > static/css/bootstrap-dark.css
python ./manage.py collectstatic --noinput
