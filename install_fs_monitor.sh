sudo apt-get install python-setuptools python-dev build-essential
sudo easy_install pip
sudo pip install watchdog
touch fs_monitor.log
sudo apt-get install supervisor
sudo cp fs_monitor_supervisor.conf /etc/supervisor/conf.d/
sudo supervisorctl update
sudo supervisorctl start redroid-fs-monitor