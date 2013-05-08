#!/bin/bash
source ve/bin/activate
./manage.py compilemessages -l ru
deactivate
