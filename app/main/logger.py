from app.main.models import *
import threading
import os

class BaseLogger(object):
    def __init__(self,view_class,*args,**kw):
        self.view_class = view_class

    def logEntry(self,*args,**kw):
        t = threading.current_thread()
        entry = Log()
        entry.pid = os.getpid()
        entry.thread_name = t.getName()
        entry.thread_id = t.ident
        entry.view_class = self.view_class
        if kw.has_key("exception"):
            ex = ExceptionLog()
            ex.trace_back = kw["exception"]
            ex.save()
            entry.exception = ex
        return entry

    def log(self,format,*args,**kw):
        msg = format%args
        entry = self.logEntry(**kw)
        entry.msg = msg
        entry.save()
        return msg

class ViewLogger(BaseLogger):
    def __init__(self,rc,*args,**kw):
        self.rc = rc
        super(ViewLogger,self).__init__(rc.view_class)
	
    def logEntry(self,*args,**kw):
        entry = super(ViewLogger,self).logEntry(*args,**kw)
        entry.req_id = self.rc.req_id
        entry.user_name = self.rc.user.uid if self.rc.user != None else None
        entry.view_name = self.rc.view_name
        return entry
        

