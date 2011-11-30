from app.main.views import BaseView

methods = [ 
             ('^bible/reader/?(.*)','Bible Reader','/bible/reader',
             'bible/reader.html','app.main.bible.methods','reader'),
          ]

class BibleView(BaseView):
    def __init__(self,*args,**kw):
        BaseView.__init__(self,*args,**kw)
        self.methods = methods
        self.init_methods()
        self.init_barlinks()

