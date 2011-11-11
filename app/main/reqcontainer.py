from django.template import Context
from app.main.logger import ViewLogger
from app.main.models import *
from app.main.tools import *
import app.crypttools
import app.settings
import copy
import sys
import os

metaMap = [ ("CONTENT_LENGTH",intOrZero),
            ("CONTENT_TYPE",maxStr(8192)),
            ("HTTP_ACCEPT_ENCODING",maxStr(8192)),
            ("HTTP_ACCEPT_LANGUAGE",maxStr(8192)),
            ("HTTP_HOST",maxStr(128)),
            ("HTTP_REFERER",maxStr(256)),
            ("HTTP_USER_AGENT",maxStr(256)),
            ("QUERY_STRING",maxStr(8192)),
            ("REMOTE_ADDR",maxStr(64)),
            ("REMOTE_HOST",maxStr(128)),
            ("REMOTE_USER",maxStr(64)),
            ("REQUEST_METHOD",maxStr(8)),
            ("SERVER_NAME",maxStr(128)),
            ("SERVER_PORT",intOrZero)
]

class ReqContainer(object):
    def __init__(self,caller_object,request,*args,**kw):
        self.rcount = RequestCounter()
        self.fetchRequestMeta(self.rcount,request)
        self.rcount.save()
        self.req_id = self.rcount.id
        self.args = copy.deepcopy(args) #For debugging purposes
        self.kw   = copy.deepcopy(kw)     #Also for debuggin purposes        
        self.selflink = kw.pop("self_link")
        self.template_file = kw.pop("template_file","default.html")
        self.view_name  = kw.pop("view_name") #Required keyword
        self.view_object = caller_object
        self.view_class = caller_object.__class__.__name__
        self.view_method = getattr(self.view_object,self.view_name)
        self.cm = kw.pop("cache_manager")
        self.crypto_key = app.settings.CRYPTO_KEY
        self.aes = app.crypttools.Aes_wrapper(self.crypto_key)
        self.request = request
        self.session = request.session
        self.raw = request.raw_post_data
        self.ctx = {}
        self.ctx["static_path"] = app.settings.STATIC_PATH
        self.ctx["links"] = caller_object.links
        self.ctx["debug"] = {}
        self.ctx["title"] = kw.pop("title",None)
        self.ctx["extra_headers"] = []
        self.configUser()
        self.logger = ViewLogger(self)
        self.logger.log("Entering %s.%s",self.view_class,self.view_name)

    def configUser(self):
        self.user = None
        self.roles = set()
        self.ctx["roles"] = []
        self.ctx["uid"] = self.uid = None
        try:
            uid = self.session["uid"]
            user = User.objects.get(uid=uid)
        except (User.DoesNotExist, KeyError):
            return
        self.ctx["uid"] = self.uid = uid
        self.user = user
        self.ctx["roles"] = []
        allRoles = Role.objects.all()
        userRoles = Role.objects.filter(user__uid=uid)
        allRolesSet = set([r.name for r in allRoles])
        userRoleSet = set([r.name for r in userRoles])
        self.roles = set()
        for role in allRoles:
            if role.name in userRoleSet:
                color="td_green"
                self.roles.add(role.name)
            else:
                color="td_gray"
            val = {}
            val["color"] = color
            val["name"] = role.name
            val["desc"] = role.desc
            self.ctx["roles"].append(val)
        return

    def killsession(self):
        session = self.request.session
        for key in session.keys():
            del session[key]
        session.modified = True
        return

    def form_named(self):
        if self.request.method == "POST" and "form_name" in self.request.POST:
            form_name = self.request.POST["form_name"]
        elif self.request.method == "GET" and "form_name" in self.request.GET:
            form_name = self.request.GET["form_name"]
        else:
            form_name = None
        return form_name

    def fetchRequestMeta(self,rcount,request):
        for (name,cookfunc) in metaMap:
            val = request.META.get(name,None)
            cooked_val = cookfunc(val)
            setattr(rcount,name,cooked_val)
