#Django specific tools
import django.db
from app.main.models import *
from app.main.util import *
from django.db.models import Q,Count
from django.db import transaction
from app.main.graph.tool import pieChart
from app.main.form import *
import django.utils.html
import re

lt_re = re.compile("^(.*)_lt$")
gt_re = re.compile("^(.*)_gt$")
lte_re = re.compile("^(.*)_lte$")
gte_re = re.compile("^(.*)_gte$")
ne_re = re.compile("^(.*)_ne$")

op_re = re.compile("^(.*)_lt$|^(.*)_gt$|^(.*)_lte$|^(.*)_gte$|^(.*)_ne$")

def requireRoles():
    def decorator(func):
        def wrapper(self,rc):
            if not isUserLoggedIn(rc):
                msg = "User must be logged in to see this view"
                rc.ctx["operror"] = rc.logger.log(msg)
                rc.template_file = 'notallowed.html'
                return rc.view_object.render(rc)
            if not userMeetsRoles(rc):
                msg = "User not allowed to see this view"
                rc.ctx["operror"] = rc.logger.log(msg)
                rc.template_file = 'notallowed.html'
                return rc.view_object.render(rc)
            else:
                return func(self,rc)
        return wrapper
    return decorator

def isUserLoggedIn(rc):
    if rc.user != None:
        return True
    return False

def fetchViewRoles(rc):
    vr = set()
    if rc.view_class != None and rc.view_name != None:
        q = Q(view_class__name=rc.view_class)&Q(name=rc.view_name)
        try:
            r = View.objects.get(q)
        except View.DoesNotExist:
            return vr
        for a in r.roles.all():
            vr.add(a.name)
        return set(vr)
    return vr

def userMeetsRoles(rc):
    format= "loggedin = %s\nvr=%sroles=%s\n"
    args = (isUserLoggedIn(rc),fetchViewRoles(rc),rc.roles)
    vr = fetchViewRoles(rc)
    if not isUserLoggedIn(rc):
        return False #Assume a logged in user is a minimum requirement
    if len(vr)<1:   #This method doesn't have any roles so assume user
        return True #is allowed
    if len(vr&rc.roles)>0:
        return True
    return False

def pieCount(rc,div_id,title,cols,modelClass,**kw):
    p = {}
    p.update(kw)
    p["title"] = title
    labels = kw.pop("labels",("x","y",))
    p["data"] = [(labels[0],labels[1])]

    q = modelClass.objects.values(*cols)
    q = q.annotate(count=Count('id'))
    q = q.order_by('count')
    for counts in q:
        name = ""
        val = counts.pop("count")
        for col in cols[:-1]:
            name += "%s:"%counts[col]
        for col in cols[-1:]:
            name += "%s"%counts[col]
        p["data"].append((name,val))
    return pieChart(rc,div_id,**p)

def listModelVals(model_class,col_name,*args,**kw):
    qs = model_class.objects.filter(**kw)
    choices = [getDotAttr(r,col_name.replace("__",".")) for r in qs]
    choices.sort()
    choices.insert(0,"---")
    return choices
    
def getChoiceForm(formobj,*args,**kw):
    for (k,v) in kw.items():
        choices = [(c,c) for c in v]
        formobj.fields[k].choices = choices
    return formobj

def onHoverMessage(msg):
    html = msg.replace("'","\\'")
    html = django.utils.html.escape(msg)
    html = html.replace("\n","<br/>").replace("\r","")
    format  = "onMouseover=\"ddrivetip('%s','yellow', 300)\"; "
    format += "onMouseout=\"hideddrivetip()\""
    out = format%html
    return out

def onClickLink(url):
   if url == "":
      return ""
   return "onClick=\"location.href='%s'\" style=\"cursor: pointer\""%url

def getDistinct(modelClass,*fields,**kw):
    values = modelClass.objects.values(*fields).distinct()
    out = tupleDictList(values,*fields,**kw)
    if len(fields)==1:
        singleElements = [o[0] for o in out]
        return singleElements
    return out

def getCount(modelClass,*fields,**kw):
    dlist = modelClass.objects.values(*fields).annotate(_counterField=Count('id'))
    args = list(fields)
    args.append("_counterField")
    out = tupleDictList(dlist,*tuple(args),**kw)
    return out

def sortChoices(*args,**kw):
    for choice in args:
        choice.sort()
        choice.insert(0,"---")


def getModelDict(modelClass,uniqueKeyCol):
    out = {}
    for row in modelClass.objects.all():
        out[getattr(row,uniqueKeyCol)] = row
    return out
    
def dbgQ():
    q = django.db.connection.queries
    return [q["sql"] for q in q]

def dbgResetQ():
   django.db.reset_queries()

def dbgPrintQ():
   for q in dbgQ():
       print q
       print ''

def changedroppasswd(rc,modelClass,idField,setterMethod):
    choices = listModelVals(modelClass,idField)
    changedroppasswdform = getChoiceForm(ChangeDropPasswdForm(),name=choices)
    if rc.form_named()=="ChangeDropPasswdForm":
        changedroppasswdform = getChoiceForm(ChangeDropPasswdForm(rc.request.POST),
                                          name=choices)
        rc.ctx["changedroppasswdform"] = changedroppasswdform
        if not changedroppasswdform.is_valid():
           rc.ctx["operror"] = rc.logger.log("Invalid ChangeDropPasswdForm")
           return
        name = changedroppasswdform.cleaned_data["name"]
        p1 = changedroppasswdform.cleaned_data["new_password"]
        try:
            obj = modelClass.objects.get(**{idField:name})
        except modelClass.DoesNotExist:
            msg = "%s does not exist. Can not modify password"%name
            rc.ctx["operror"] = rc.logger.log(msg)
            return
        getattr(obj,setterMethod)(p1)
        obj.save()
        msg = "Passwd for %s %s modified"%(modelClass.__name__,name)
        rc.ctx["opsuccess"] = rc.logger.log(msg)
    rc.ctx["changedroppasswdform"] = changedroppasswdform
    return

def listDictFilter(listIn,*args,**kw):
    out = []
    for ent in listIn:
        addent = True
        for (k,v) in kw.iteritems():
            if op_re.match(k):
                m = lt_re.match(k)
                if m and ent[m.group(1)] >= v:
                    addent = False
                    break
                m = gt_re.match(k)
                if m and ent[m.group(1)] <= v:
                    addent = False
                    break
                m = lte_re.match(k)
                if m and ent[m.group(1)] > v:
                    addent = False
                    break
                m = gte_re.match(k)
                if m and ent[m.group(1)] < v:
                    addent = False
                    break
                m = ne_re.match(k)
                if m and ent[m.group(1)] == v:
                    addent = False
                    break
            else:
                if ent[k] != v:
                    addent = False
                    break
        if addent:
            out.append(ent)
    return out

def dt(*args,**kw):
    tzinfo = kw.pop("tzinfo",pytz.UTC)
    return datetime.datetime(*args).replace(tzinfo=tzinfo)

def keygetter(key):
    def wrapper(item):
        return item[key]
    return wrapper

def maxStr(n):
    def wrapper(strIn):
        if strIn == None:
            return None
        return strIn[:n]
    return wrapper

def intOrZero(strIn):
    try:
        val = int(strIn)
    except:
        val = 0
    return val

@transaction.commit_manually
def flush_tx():
    transaction.commit()
