from django.db import models
from app.crypttools import sha256,aes_b64encrypt, aes_b64decrypt
from app.crypttools import AesWrapperException
from app.settings import CRYPTO_KEY
from app.main.util import p64d,p64e
import datetime

class Role(models.Model):
    name = models.CharField(max_length=32,null=False,unique=True)
    desc = models.TextField(max_length=8196,null=True,blank=True)
    def __unicode__(self):
        return unicode("%s"%(self.name))

class ViewClass(models.Model):
    name = models.CharField(max_length=64,editable=False,
                null=False,blank=False,unique=True)
    desc = models.TextField(max_length=8196,null=True,blank=True)

    def __unicode__(self):
        return unicode("%s"%(self.name))

class View(models.Model):
    name = models.CharField(max_length=64,null=False,editable=False)
    view_class = models.ForeignKey(ViewClass,null=False,editable=False)
    desc = models.TextField(max_length=8196,null=True,blank=True)
    roles = models.ManyToManyField(Role,blank=True)
    class Meta:
        unique_together = [("view_class","name")]

    def __unicode__(self):
        return unicode("%s:%s"%(self.view_class,self.name))

class PickleCache(models.Model):
    view_class = models.ForeignKey(ViewClass,null=False)
    cache_key = models.CharField(max_length=128,null=False)
    cache_val = models.TextField(max_length=1024*1024*64,null=False)
    evtime =  models.DateTimeField(null=False)

    def setValue(self,obj):
        self.cache_val = p64e(obj)

    def getValue(self):
        return p64d(self.cache_val)

    def save(self):
        self.evtime = datetime.datetime.now()
        super(PickleCache,self).save()

    class Meta:
        unique_together = [("view_class","cache_key")]

class User(models.Model):
    uid = models.CharField(max_length=32,null=False,unique=True)
    desc = models.TextField(max_length=8196,null=True,blank=True)
    passwd = models.CharField(max_length=128,null=False,unique=False)
    enabled = models.BooleanField(null=False,default=False)
    roles = models.ManyToManyField(Role,blank=True)
    def __unicode__(self):
        return unicode("%s"%self.uid)

    def authenticate(self,passwd):
        if passwd == None:
            return false
        hash = sha256(passwd.encode("utf-8"))
        if hash == self.passwd.decode("utf-8"):
            return True
        else:
            return False

    def setPasswd(self,passwd):
        hash = sha256(passwd.encode("utf-8"))
        self.passwd = hash
        super(User,self).save()

class ExceptionLog(models.Model):
    trace_back = models.TextField(max_length=8192,null=False)

class Log(models.Model):
    req_id       = models.IntegerField(null=True)
    evtime       = models.DateTimeField(null=False)
    pid          = models.IntegerField(null=False)
    thread_id    = models.BigIntegerField(null=False)
    thread_name  = models.CharField(max_length=128,null=False)
    view_class   = models.CharField(max_length=32,null=True)
    view_name    = models.CharField(max_length=32,null=True)
    user_name    = models.CharField(max_length=32,null=True)
    exception    = models.ForeignKey(ExceptionLog,null=True)
    msg          = models.CharField(max_length=512,null=True)
    
    def save(self):
        self.evtime = datetime.datetime.now()
        super(Log,self).save()

class RequestMeta(models.Model):
    CONTENT_LENGTH = models.IntegerField(null=True)
    CONTENT_TYPE = models.TextField(max_length=8192,null=True)
    HTTP_ACCEPT_ENCODING = models.TextField(max_length=8192,null=True)
    HTTP_ACCEPT_LANGUAGE = models.TextField(max_length=8192,null=True)    
    HTTP_HOST = models.CharField(max_length=128,null=True)
    HTTP_REFERER = models.CharField(max_length=256,null=True)
    HTTP_USER_AGENT = models.CharField(max_length=256,null=True)
    QUERY_STRING = models.TextField(max_length=8192,null=True)
    REMOTE_ADDR = models.CharField(max_length=64,null=True)
    REMOTE_HOST = models.CharField(max_length=128,null=True)
    REMOTE_USER = models.CharField(max_length=64,null=True)
    REQUEST_METHOD = models.CharField(max_length=8,null=True)
    SERVER_NAME = models.CharField(max_length=128,null=True)
    SERVER_PORT = models.IntegerField(null=True)

class RequestCounter(models.Model):
    evtime      = models.DateTimeField(null=False)
    request_meta = models.ForeignKey(RequestMeta,null=False)
    render_time = models.FloatField(null=True)

    def save(self):
        self.evtime = datetime.datetime.now()
        super(RequestCounter,self).save()
