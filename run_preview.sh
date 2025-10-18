#!/bin/bash
cd /home/ubuntu/SawaednaCostApp
export FLASK_APP=index.py
export FLASK_ENV=development
python3.11 -m flask run --host=0.0.0.0 --port=5000
