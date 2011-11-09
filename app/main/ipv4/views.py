from app.main.views import BaseView

methods = [
       ('^ipv4/dec2bin/?$','Decimal to Binary','/ipv4/dec2bin',
        'ipv4/dec2bin.html','app.main.ipv4.binary','dec2bin'),

       ('^ipv4/bin2dec/?$','Binary to Decimal','/ipv4/bin2dec',
        'ipv4/bin2dec.html','app.main.ipv4.binary','bin2dec'),

    ]

class IPv4View(BaseView):
    def __init__(self,*args,**kw):
        BaseView.__init__(self,*args,**kw)
        self.methods = methods
        self.init_methods()
        self.init_barlinks()
