cd foodgram/
python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py csv_data_load
python manage.py collectstatic --no-input
cp -r /app/foodgram/collected_static/. /backend_static/static/
gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
