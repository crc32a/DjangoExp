import sys
import os

user_dir = "/var/www/django-app/platform-django-app"
proj     = "app.settings"
sys.path.append(user_dir)

from pkg_resources import require
os.environ["BASE_PATH"]=user_dir
os.environ["DJANGO_SETTINGS_MODULE"]=proj
import django.core.handlers.wsgi
sys.path.insert(0,user_dir)
application = django.core.handlers.wsgi.WSGIHandler()



