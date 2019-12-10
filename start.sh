PATH=/$DJANGO_PROJECT:$PATH
python $DJANGO_PROJECT/manage.py makemigrations $APP_NAME
python $DJANGO_PROJECT/manage.py migrate
python $DJANGO_PROJECT/manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('fing', 'admin@example.com', 'fing')"
#bash
python $DJANGO_PROJECT/manage.py runserver $DJANGO_HOST:$APP_PORT