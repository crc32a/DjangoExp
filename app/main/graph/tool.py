import graphhtml
import math

def div(id):
    return graphhtml.div%id

def scalLog(x,*args):
    if x == 0.0:
        return x
    if len(args)<1:
        return math.log(abs(x))
    return math.log(abs(x))/math.log(args[0])

def baseChart(rc,id,*args,**kw):
    width = kw.get("width",450)
    height = kw.get("height",300)
    title = kw.get("title",None)
    is3d = kw.get("is3d",False)
    data = kw.get("data")
    rc.ctx["include_google_graphs"] = True
    return (width,height,title,data,is3d)

def annotatedtimeChart(rc,id,*args,**kw):
    scriptStr = ""
    (width,height,title,data,is3d) = baseChart(rc,id,*args,**kw)
    cols = kw["data"][0]
    scriptStr += "data.addColumn('date','Date');\n"
    useLog = kw.get("useLog",False)
    for i in xrange(0,len(cols)):
        scriptStr += "data.addColumn('number','%s');\n"%cols[i]
        scriptStr += "data.addColumn('string','title%i');\n"%i
        scriptStr += "data.addColumn('string','text%i');\n"%i
    rows = kw["data"][1:]
    scriptStr += "data.addRows(%i);\n"%len(rows)
    for i in xrange(0,len(rows)):
        (dt,ent) = rows[i]
        scriptStr += "data.setValue(%i,0,%s);\n"%(i,dt2jsdate(dt))
        for j in xrange(0,len(cols)):
            if useLog:
                val = scalLog(ent[cols[j]])
            else:
                val = ent[cols[j]]
                
            args = (i, 3*j+1, val)
            scriptStr += "data.setValue(%i,%i,%s);\n"%args
    scriptStr += "var chart = new "
    scriptStr += "google.visualization.AnnotatedTimeLine("
    scriptStr += "document.getElementById('%s'));\n"%id
    scriptStr += "    chart.draw(data, {displayAnnotations: true});\n"
    rc.ctx["extra_headers"].append(graphhtml.annotadtime_chart%scriptStr)
    return graphhtml.annotatedtime_div%(id,width,height)

def dt2jsdate(dt):
    attrList = ["year","month","day","hour","minute","second"]
    scriptStr = "new Date("
    for attr in attrList:
        val = getattr(dt,attr)
        scriptStr += "%s,"%val
    scriptStr += "0)"
    return scriptStr


def pieChart(rc,id,*args,**kw):
    scriptStr = ""
    (width,height,title,data,is3d) = baseChart(rc,id,*args,**kw)
    colors = kw.get("colors",None)
    sliceStyle = kw.get("sliceStyle",(None,None,None))
    
    scriptStr += "data.addColumn('string','%s');\n"%data[0][0]
    scriptStr += "data.addColumn('number','%s');\n"%data[0][1]
    nrows = len(data)-1
    scriptStr += "data.addRows(%i);\n"%nrows
    i = 0
    for (col,val) in data[1:]:
        scriptStr += "data.setValue(%i,0,'%s');\n"%(i,col)
        scriptStr += "data.setValue(%i,1,%s);\n"%(i,val)
        i += 1
    scriptStr += "var chart = new google.visualization.PieChart("
    scriptStr += "document.getElementById('%s'));\n"%id
    scriptStr += "chart.draw(data, {width: %i, height: %i, "%(width,height)
    if colors != None:
        scriptStr += "colors: ["
        for c in colors[:-1]:
            scriptStr += "'%s',"%c
        for c in colors[-1:]:
            scriptStr += "'%s'"%c
        scriptStr += "],"
    if is3d:
        scriptStr += "is3D: true,"
    scriptStr += fontStyle("pieSliceTextStyle",*sliceStyle)
    scriptStr += "title: '%s'});\n"%title
    rc.ctx["extra_headers"].append(graphhtml.base_chart%scriptStr)
    return div(id)

def lineChart(rc,id,*args,**kw):
    scriptStr = ""
    (width,height,title,data,is3d) = baseChart(rc,id,*args,**kw)
    useLog = kw.get("useLog",False)
    cols = data[0][:]
    scriptStr += "data.addColumn('string','%s');\n"%cols[0]
    for i in xrange(1,len(cols)):
        scriptStr += "data.addColumn('number','%s');\n"%data[0][i]
    nrows = len(data)-1
    ncols = len(cols)
    scriptStr += "data.addRows(%i)\n"%nrows

    for i in xrange(1,len(data)):
        scriptStr += "data.setValue(%i,0,'%s');\n"%(i-1,data[i][0])
        for j in xrange(1,len(cols)):
            if useLog:
                value = scalLog(data[i][j],useLog)
            else:	
                value = data[i][j]
            scriptStr += "data.setValue(%i,%i,%s);\n"%(i-1,j,value)
    scriptStr += "var chart = new google.visualization.LineChart("
    scriptStr += "document.getElementById('%s'));\n"%id
    scriptStr += "chart.draw(data, {width: %i, height: %i, "%(width,height)
    if is3d:
        scriptStr += "is3d: true,"
    scriptStr += "title: '%s'});\n"%title
    rc.ctx["extra_headers"].append(graphhtml.base_chart%scriptStr)
    return div(id)

def columnChart(rc,id,*args,**kw):
    scriptStr = ""
    (width,height,title,data,is3d) = baseChart(rc,id,*args,**kw)
    useLog = kw.get("useLog",False)
    cols = data[0][:]
    haxis_title = kw.get("haxis_title",data[0][0])
    scriptStr += "data.addColumn('string','%s');\n"%cols[0]
    for i in xrange(1,len(cols)):
        scriptStr += "data.addColumn('number','%s');\n"%data[0][i]
    nrows = len(data)-1
    ncols = len(cols)
    scriptStr += "data.addRows(%i)\n"%nrows

    for i in xrange(1,len(data)):
        scriptStr += "data.setValue(%i,0,'%s');\n"%(i-1,data[i][0])
        for j in xrange(1,len(cols)):
            if useLog:
                value = scalLog(data[i][j],useLog)
            else:	
                value = data[i][j]
            scriptStr += "data.setValue(%i,%i,%s);\n"%(i-1,j,value)
    scriptStr += "var chart = new google.visualization.ColumnChart("
    scriptStr += "document.getElementById('%s'));\n"%id
    scriptStr += "chart.draw(data, {width: %i, height: %i, "%(width,height)
    if is3d:
        scriptStr += "is3d: true,"
    scriptStr += "title: '%s',"%title
    scriptStr += "hAxis: {title:'%s'}});\n"%haxis_title
    rc.ctx["extra_headers"].append(graphhtml.base_chart%scriptStr)
    return div(id)

def fontStyle(attrName,*args):
    out = ""
    attrs = []
    cols = [("color","string"),("fontName","string"),("fontSize","int")]
    for i in xrange(0,len(cols)):
        if args[i] == None:
            continue
        (col,colType) = cols[i]
        if colType == "string":
            attrs.append("\"%s\":\"%s\""%(col,args[i]))
        elif colType == "int":
            attrs.append("\"%s\":%i"%(col,args[i]))
    if len(attrs)<=0:
        return out
    out = "%s: {"%attrName
    for attr in attrs[:-1]:
        out += "%s,"%attr
    for attr in attrs[-1:]:
        out += "%s"%attr
    out += "},\n"
    return out
