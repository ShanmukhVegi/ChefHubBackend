web: gunicorn ChefHubRestApi.wsgi

release: python3 manage.py makemigrations --noinput
release: python3 manage.py collectstatic 
release: python3 manage.py migrate --noinput