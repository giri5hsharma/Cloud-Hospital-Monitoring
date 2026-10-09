#!/bin/sh
export PYTHONPATH="/home/site/wwwroot/.deps:${PYTHONPATH}"
cd /home/site/wwwroot
exec python -m gunicorn --bind=0.0.0.0:8000 --timeout 90 app:app
