web: gunicorn ChefHubRestApi.wsgi

release: python manage.py makemigrations --noinput
release: python manage.py collectstatic 
release: python manage.py migrate --noinput