from app.main.models import *
from django.db.models import Q
import datetime
import copy

class CacheManager(object):
    def __init__(self,view_class,*args,**kw):
        self.view_class = view_class

    def evtime(self,key):
        q = self.getKeyQuery(key)
        try:
            pe = PickleCache.objects.get(q)
        except PickleCache.DoesNotExist:
            return None
        return pe.evtime

    def get(self,key,*args,**kw):
        q = self.getKeyQuery(key)
        try:
            pe = PickleCache.objects.get(q)
        except PickleCache.DoesNotExist:
            if len(args) >= 1:
                return args[0]
            raise KeyError("%s not found in cache"%key)
        return pe.getValue()

    def put(self,key,val,*args,**kw):
        q = self.getKeyQuery(key)
        try:
            pe = PickleCache.objects.get(q)
        except PickleCache.DoesNotExist:
            pe = PickleCache()
            pe.view_class = ViewClass.objects.get(name=self.view_class)
            pe.cache_key = key
        pe.setValue(val)
        pe.save()
        
    def iteritems(self):
        q = Q(view_class__name=self.view_class)
        qs = PickleCache.objects.filter(q)
        for r in qs:
            yield (r.cache_key,r.getValue())

    def items(self):
        return list(self.iteritems())

    def has_key(self,key):
        q = self.getKeyQuery(key)
        try:
            pe = PickleCache.objects.get(q)
            return True
        except PickleCache.DoesNotExist:
            return False

    def remove(self,key):
        q = self.getKeyQuery(key)
        PickleCache.objects.filter(q).delete()

    def keys(self):
        q = Q(view_class__name=self.view_class)
        qs = PickleCache.objects.values('cache_key').filter(q)
        return [r['cache_key'] for r in qs]

    def getKeyQuery(self,key):
        return Q(view_class__name=self.view_class)&Q(cache_key=key)

