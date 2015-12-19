#!/bin/bash
./manage.py makemessages -l ru --ignore=ve/* --ignore=ve3/* \
    --ignore=db/* --ignore=media/* --ignore=uploads/*\
    --ignore=*/tests/* --ignore=*test_*.py -v 3
