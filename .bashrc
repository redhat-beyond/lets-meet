# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]
then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
if [ -d ~/.bashrc.d ]; then
        for rc in ~/.bashrc.d/*; do
                if [ -f "$rc" ]; then
                        . "$rc"
                fi
        done
fi

# addeing aliases
alias manage="pipenv run python manage.py"
alias shell="manage shell"
alias run="manage runserver 0.0.0.0:8000"
alias makemigrations="manage makemigrations"
alias migrate="manage migrate"
alias migration="makemigrations | migrate"
alias run_tests="pipenv run pytest -v"
alias run_flake8="pipenv run flake8 --max-line-length 120"
alias reset_db="rm db.sqlite3 | rm -r static/files | rm -r static/profiles | migrate"

alias find_program="netstat -plten | grep python"
alias stop_program="sudo kill -9 "

unset rc
