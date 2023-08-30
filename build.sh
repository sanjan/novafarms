#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py runscript init_inventory -v3 # --script-args inventory.csv
python manage.py migrate
