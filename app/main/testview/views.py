from app.main.views import BaseView

methods = [ 
       ('^test/hello/?$','Hello','/test/hello','test/hello.html',
            'app.main.testview.methods','hello'),
       ('^test/goodbye/?$','GoodBye','/test/goodbye','test/goodbye.html',
            'app.main.testview.methods','byebye'),
       ('^test/yhwh/?$',"YHWH","/test/yhwh",'test/yhwh.html',
            'app.main.testview.methods','yhwh'),
       ('^test/showctx/?$','Show Ctx','/test/showctx','test/showctx.html',
            'app.main.testview.methods','showCtx'),
       (None,None,None,None,
            'app.main.testview.methods','yhwhText'),

       ('^test/piechart/?$','Pie Chart','/test/piechart','test/piechart.html',
            'app.main.testview.methods','piechart'),

       ('^test/linechart/?$','Line Chart','/test/linechart',
        'test/linechart.html','app.main.testview.methods','linechart'),

       ('^test/show_hide/?$','Show Hide Text','/test/show_hide',
         'test/show_hide.html','app.main.testview.methods','showHide'),
       ]

class TestView(BaseView):
    def __init__(self,*args,**kw):
        BaseView.__init__(self,*args,**kw)
        self.methods = methods
        self.init_methods()
        self.init_barlinks()
