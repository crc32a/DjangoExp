from app.classutil import DynamicLoader
from django.template import Context
from app.main.reqcontainer import ReqContainer
from app.main.cachemanager import CacheManager
from app.main.logger import BaseLogger
from app.main.util import Timer
from django.shortcuts import render_to_response
import traceback
import app.settings
import time
import copy

class BaseView(object):
    def __init__(self,sidename,sidehref):
        class_name = self.__class__.__name__
        self.localLink = {"name":sidename,"href":sidehref}
        self.dl = DynamicLoader()
        self.links = {"side":[],"bar":[]}
        self.bl = BaseLogger(class_name)
        self.bl.log("Spinning up instance of %s",class_name)
        self.cm = CacheManager(class_name)
        self.bl.log("Loading cache from database for %s",class_name)

    def gview(self,request,*args,**kw):
        post = request.POST
        get = request.GET
        kw["cache_manager"] = self.cm
        rc = ReqContainer(self,request,*args,**kw)
        try:
            resp = rc.view_method(rc)
        except:
            tb = traceback.format_exc()
            rc.logger.log("Exception caught",exception=tb)
            raise
        return resp

    def render(self,rc):
        ctx = Context(rc.ctx)
        t = Timer()
        t.start()
        resp = render_to_response(rc.template_file,ctx)
        t.stop()
        rc.rcount.render_time = t.read()
        rc.rcount.save()
        return resp

    def getSideLink(self):
        return self.localLink

    def setSideLinks(self,sideLinks):
        self.links["side"] = sideLinks

    def init_methods(self):
        for m in self.methods:
            mod_path = m[4]
            view_method = m[5]
            if mod_path != None and view_method != None:
                self.dl.addMethod(self,mod_path,view_method)

    def init_barlinks(self):
        for m in self.methods:
            name = m[1]
            href = m[2]
            if name != None and href != None:
                link = {"name":name, "href":href}
                self.links["bar"].append(link)

    # methods is defined in the child view class 
    # see app/main/testviews/views.py for an example
    def getUrlRoutes(self):
        urls = []
        for m in self.methods:
            pattern = m[0]
            barname = m[1]
            self_link = m[2]
            template_file = m[3]
            view_name = m[5]
            method_func = self.gview
            if pattern == None:
                continue #This must not be a URL method
            kw = {}
            kw["self_link"] = self_link
            kw["view_name"]=view_name
            if template_file != None:
                kw["template_file"] = template_file
            if barname != None:
                kw["title"] = barname
            urls.append( (pattern,method_func,kw) )
        return urls

