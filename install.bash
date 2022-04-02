#!/bin/bash

# a directory of project
  chdir="/srv/flask-uwsgi/"
  project_dir='generic-drawing-server/'
  pgmode="production" #debug, production

  #удаление всех папок и файлов
  if [ -h /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
    echo "delete /etc/nginx/sites-enabled/default"
  fi
  if [ -f /etc/nginx/sites-available/default ]; then
    sudo rm /etc/nginx/sites-available/default
    echo "delete /etc/nginx/sites-available/default"
  fi
  if [ -f /etc/nginx/sites-available/flask-uwsgi.conf ]; then
    sudo rm /etc/nginx/sites-available/flask-uwsgi.conf
    echo "delete /etc/nginx/sites-available/flask-uwsgi.conf"
  fi
  if [ -h /etc/nginx/sites-enabled/flask-uwsgi.conf ]; then
    sudo rm /etc/nginx/sites-enabled/flask-uwsgi.conf
    echo "delete /etc/nginx/sites-enabled/flask-uwsgi.conf"
  fi
  if [ -f /etc/uwsgi/apps-available/readme ]; then
    sudo rm /etc/uwsgi/apps-available/readme
    echo "echo /etc/uwsgi/apps-available/readme"
  fi
  if [ -f /etc/uwsgi/apps-available/flask-uwsgi.ini ]; then
    sudo rm /etc/uwsgi/apps-available/flask-uwsgi.ini
    echo "delete /etc/uwsgi/apps-available/flask-uwsgi.ini"
  fi
  if [ -h /etc/uwsgi/apps-enabled/flask-uwsgi.ini ]; then
    sudo rm /etc/uwsgi/apps-enabled/flask-uwsgi.ini
    echo "delete /etc/uwsgi/apps-enabled/flask-uwsgi.ini"
  fi
  if [ -f /etc/systemd/system/flask-uwsgi.service ]; then
    sudo rm /etc/systemd/system/flask-uwsgi.service
    echo "delete  /etc/systemd/system/flask-uwsgi.service"
  fi
  if [ -d "$chdir" ]; then
    sudo rm -rf "$chdir"
    echo "delete $chdir"
  fi

# creating a directory for a project
  mkdir -p "$chdir"
  cd "$chdir"
  mkdir "$project_dir"
  cd "$project_dir"
# клонирование только ветки dev
  git init
  git remote add origin https://github.com/Vl4d1k/generic-drawing-server.git
  git pull origin main

  cd "$chdir$project_dir"
  apt-get -y install python3 virtualenv
  virtualenv -p python3 venv
  source venv/bin/activate
  pip install Flask argparse sshtunnel requests


# configuring nginx
  cd "$chdir"
  apt-get -y install nginx
  cp "$chdir$project_dir""/install_config/flask-uwsgi.conf" /etc/nginx/sites-available/
  sudo ln -s /etc/nginx/sites-available/flask-uwsgi.conf /etc/nginx/sites-enabled/
  systemctl reload nginx


# configuring uwsgi
  apt-get -y install uwsgi uwsgi-plugin-python3
  cp "$chdir$project_dir""/install_config/flask-uwsgi.ini" /etc/uwsgi/apps-available/
  sudo ln -s /etc/uwsgi/apps-available/flask-uwsgi.ini /etc/uwsgi/apps-enabled/
  systemctl restart uwsgi
  service uwsgi restart
  systemctl enable uwsgi
  cp "$chdir$project_dir""/install_config/flask-uwsgi.service" /etc/systemd/system/
  systemctl daemon-reload
  systemctl start flask-uwsgi
  systemctl enable flask-uwsgi