export DJANGO_SETTINGS_MODULE=afe.settings
export CONF_IP=${1-127.0.0.1}
redis-server  --bind ${1-127.0.0.1} --daemonize yes 
CENTRIFUGE_INSECURE=1 centrifuge --logging=debug --debug --port=8080 --address=${1-127.0.0.1} &
python -u run-worker.py &
python -u run-worker.py &
python manage.py rqscheduler --interval 1 &
python manage.py runserver ${1-127.0.0.1}:8000
