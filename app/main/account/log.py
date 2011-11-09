from app.main.models import *
from app.main.tools import *
from app.main.form import *
from django.utils.datastructures import MultiValueDictKeyError
import traceback



@requireRoles()
def log(self,rc):
    lfkey = "account:logform"
    userChoices = [ n for n in getDistinct(Log,'user_name') if n != None]
    view_qr = getDistinct(View,'view_class__name','name')
    viewChoices = ["%s:%s"%(n[0],n[1]) for n in view_qr]

    sortChoices(userChoices,viewChoices)        
    rc.ctx['datepickers'] = ['#id_start_date','#id_stop_date']
    rc.ctx['logform'] = rc.session.get(lfkey,
                           getChoiceForm(LogForm(),
                           user=userChoices,
                           view=viewChoices))


    if rc.form_named()=='LogForm':
        logform = getChoiceForm(LogForm(rc.request.POST),
                           user=userChoices,
                           view=viewChoices)
        if not logform.is_valid():
            rc.ctx['operror'] = rc.logger.log('Invalid form LogForm')
            rc.ctx['logform'] = logform
            return self.render(rc)

        rc.session[lfkey] = logform
        rc.ctx["logform"]=logform
        rc.logger.log("Fetching log records")

        q = Q()

        user_name = logform.cleaned_data["user"]
        if user_name and user_name != "---":
            q &= Q(user_name=user_name)
        
        view = logform.cleaned_data["view"]
        if view and view != "---":
            q &= Q(view_class=view.split(":")[0])
            q &= Q(view_name=view.split(":")[1])

        start_date = logform.cleaned_data["start_date"]
        if start_date:
            q &= Q(evtime__gte=start_date)
        stop_date = logform.cleaned_data["stop_date"]
        if stop_date:
            q &= Q(evtime__lte=stop_date)

        msg_like = logform.cleaned_data["msg_like"]
        if msg_like and msg_like != "":
            q &=Q(msg__contains=msg_like)

        only_exc = logform.cleaned_data["only_show_exceptions"]
        if only_exc:
            q &=Q(exception__isnull=False)

        rs = Log.objects.filter(q)
        cols = ['id','evtime', 'req_id', 'pid', 'thread_id', 
                'thread_name', 'view_class', 'view_name', 
                'user_name', 'msg']
        logentries = getLogEntries(rc,rs,cols)
    return self.render(rc)

@requireRoles()
def logException(self,rc):
    try:
        id = int(rc.request.GET["id"])
    except KeyError:
        msg = "request should be of type /account/logexception?id=%%i"
        rc.ctx["operror"] = rc.logger.log(msg)
        return self.render(rc)
    try:
        ex = ExceptionLog.objects.get(id=id).trace_back
        html = django.utils.html.escape(ex)
        html = html.replace("\r","").replace("\n","<br/>")
        html = html.replace(" ","&nbsp;")
        rc.ctx["ex"] = html
        self.render(rc)
    except ExceptionLog.DoesNotExist:
        msg = "ExceptionLog with id=%i not found in database"%id
        rc.ctx["operror"] = rc.logger.log(msg)
        return self.render(rc)      
    return self.render(rc)

def getLogEntries(rc,rs,cols):
    rc.logger.log("Populateing Log table")
    ctx = {}
    ctx["th"] = []
    ctx["tr"] = []
    for col in cols:
        ctx["th"].append(col)

    for row in rs:
        tr = []
        for col in cols:
            td = {}
            if col == "evtime":
                td["class"] = "td_tiny"
                td["val"] = dt2sqldt(getattr(row,col))
                tr.append(td)
                continue
            if col == "msg" and row.exception:
                td["class"] = "td_red"
                rid = row.exception.id
                url = onClickLink("/account/logexception?id=%i"%rid)
                td["self_link"] = url
                ex = row.exception.trace_back
                td["hover"] = onHoverMessage(ex)
            td["val"] = getattr(row,col)
            tr.append(td)
        ctx["tr"].append(tr)
    rc.ctx["logentries"] = ctx
