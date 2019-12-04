#!/bin/sh
pkill -f gunicorn
python manage.py db init
python manage.py db migrate
python manage.py db upgrade

/home/ubuntu/.local/bin/gunicorn --bind 0.0.0.0:30303 -k gevent wsgi:app &
