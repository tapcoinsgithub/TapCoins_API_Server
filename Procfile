release: python manage.py makemigrations
release: python manage.py migrate
web: uwsgi --http :8000 --wsgi-file application.py --master --processes 4 --threads 2
web: gunicorn --bind :8000 --workers 3 --threads 2 project.wsgi:application