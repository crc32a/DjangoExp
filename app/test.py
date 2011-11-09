import sys, os, json, random, copy,base64
from crypttools import *
dir_name = os.path.dirname(os.path.abspath("__file__"))
base_dir = os.path.abspath(os.path.join(dir_name,".."))
uni = json.loads(open("uni.json","r").read())
sys.path.insert(0,base_dir)
from django.core.management import setup_environ
from app import settings
setup_environ(settings)
from settings import CRYPTO_KEY
from django.db.models import Q,Count, Avg, Max, Min
from django.db import connection, reset_queries
import app.main.cachemanager
from app.main.models import *
from app.main.tools import *
from app.main.util import *

