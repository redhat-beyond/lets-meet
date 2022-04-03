# alias creation for easier use
  head -n -1 .bashrc > .temp ; mv .temp .bashrc
  echo '# addeing aliases ' >> .bashrc
  echo 'alias manage="pipenv run python manage.py"' >>  .bashrc
  echo 'alias run="pipenv run python manage.py runserver 0.0.0.0:8000"' >>  .bashrc
  echo 'alias makemigrations="pipenv run python manage.py makemigrations"' >>  .bashrc
  echo 'alias migrate="pipenv run python manage.py migrate"' >>  .bashrc
  echo 'alias migration="pipenv run python manage.py makemigrations | pipenv run python manage.py migrate"' >>  .bashrc
  echo 'alias run_tests="pipenv run pytest"' >> .bashrc
  echo 'alias run_flake8="pipenv run flake8 --max-line-length 120"' >>  .bashrc
  echo 'unset rc' >>  .bashrc
