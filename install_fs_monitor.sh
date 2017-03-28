python-setuptools python-dev build-essential
sudo pip install watchdog
sudo easy_install pip
touch fs_monitor.log
sudo apt-get install supervisor
sudo cp fs_monitor_supervisor.conf /etc/supervisor/conf.d/
sudo supervisorctl update
sudo supervisorctl start redroid-fs-monitor