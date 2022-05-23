#!/usr/bin/env bash

#FLASK_APP=web FLASK_ENV=development flask run --host=0.0.0.0
gunicorn -w 40 -b 0.0.0.0:5000 web:app
