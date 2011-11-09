from app.main.views import BaseView
from app.main.form import *

methods = [
    ('^account/login/?$','Login','/account/login','account/login.html',
     'app.main.account.methods','login'),

    ('^account/edituser/?$','Edit/Add User','/account/edituser',
     'account/edituser.html','app.main.account.methods','edituser'),

    ('^account/changepasswd/?$','Change My Passwd','/account/changepasswd',
     'account/changepasswd.html','app.main.account.methods',
     'changepasswd'),  

    ('^/?$',None,None,None,'app.main.account.methods','redirectLogin'),

    ('^account/userinfo/?$','User Info','/account/userinfo',
     'account/userinfo.html','app.main.account.methods','userInfo'),

    ('^account/log/?$','View Logs','/account/log',
     'account/log.html','app.main.account.log','log'),

    ('^account/logexception/?.*',None,None,
     'account/logexception.html','app.main.account.log','logException'),


    (None,"Admin","/admin/",None,None,None)

    ]

class AccountView(BaseView):
    def __init__(self,*args,**kw):
        BaseView.__init__(self,*args,**kw)
        self.methods = methods
        self.init_methods()
        self.init_barlinks()


        
