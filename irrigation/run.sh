#!/bin/sh -xe
cd /daten/src/git/moat/irrigation/
export DJANGO_SETTINGS_MODULE="settings"
export PYTHONPATH=$(pwd)/..:$(pwd)
(
python manage.py runserver 0.0.0.0:58000 &
python manage2.py runschedule Schleiermacher+Hardenberg &
) > /tmp/rainman.log 2>&1
