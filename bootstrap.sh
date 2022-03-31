#!/bin/bash -ex
# The -e option would make our script exit with an error if any command
# fails while the -x option makes verbosely it output what it does

# Install Pipenv, the -n option makes sudo fail instead of asking for a
# password if we dont have sufficient privileges to run it
sudo -n dnf install -y pipenv

cd /vagrant
# Install dependencies with Pipenv
pipenv sync --dev

# run database migrations
pipenv run python manage.py migrate

# run our app on localhost port
setsid pipenv run python manage.py runserver 0.0.0.0:8000 > runserver.log 2>&1 &
