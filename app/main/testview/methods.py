from app.main.graph.tool import pieChart, lineChart
from app.main.tools import *
from app.main.models import *
from operator import itemgetter
import time
import math
import copy

def hello(self,rc):
    rc.logger.log("Saying hello")
    return self.render(rc)

def byebye(self,rc):
    rc.logger.log("Saying goodbye")
    return self.render(rc)

def yhwh(self,rc):
    rc.logger.log("YHWH called")
    rc.ctx["yhwh"] = self.yhwhText()
    return self.render(rc)

def showCtx(self,rc):
    rc.logger.log("Showing CTX")
    rc.ctx["ctx"] = copy.deepcopy(rc.ctx)
    return self.render(rc)

def linechart(self,rc):
    kw = {}
    kw["title"] = "Test Chart"
    kw["width"] = 1024
    kw["height"] = 640
    kw["useLog"] = 10.0
    kw["data"]=[('x','x','1/x','x*x','sin(x)','cos(x)')]
    for x in frange(-math.pi,math.pi,400):
        x2 = x*x
        dx = 0 if x==0.0 else 1/x
        sx = math.sin(x)
        cx = math.cos(x)
        label = "%f"%x
        kw["data"].append( (label,x,dx,x2,sx,cx) )
    rc.ctx["line_chart"] = lineChart(rc,'line_chart',**kw)
    return self.render(rc)

def piechart(self,rc):
    user_count = {}
    for (user_name,req_id) in getDistinct(Log,'user_name','req_id'):
        if user_name == None:
            continue
        if not user_count.has_key(user_name):
            user_count[user_name] = 0
        user_count[user_name] += 1
    kw = {}
    kw['data'] = [('user','number of requests')]
    kw['title']='Log entries by user'
    for(k,v) in sorted(user_count.items(),key=itemgetter(1),reverse=True):
        kw['data'].append((k,v))
    rc.ctx['by_user'] = pieChart(rc,'by_user',**kw)


    view_count = {}

    for (vc,vn,ri) in getDistinct(Log,'view_class','view_name','req_id'):
        if vc == None or vn == None or ri == None:
            continue
        key = "%s:%s"%(vc,vn)
        if not view_count.has_key(key):
            view_count[key] = 0
        view_count[key] += 1

    kw = {}
    kw["data"] = [('view_name','request count')]
    kw['title']  = 'Log entries by view_name'
    for (k,v) in sorted(view_count.items(),key=itemgetter(1),reverse=True):
        kw['data'].append((k,v))
    rc.ctx['by_view'] = pieChart(rc,'by_view',**kw)

    return self.render(rc)

def showHide(self,rc):
    return self.render(rc)

def yhwhText(self):
    msg  = u"\u05D9\u05D4\u05D5\u05D4 "
    msg += u"\u05D4\u05D5\u05D0 "
    msg += u"\u05D9\u05D4\u05D5\u05D4"
    return msg

