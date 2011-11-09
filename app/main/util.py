#Non django specific tools

import datetime
import cPickle
import urllib
import base64
import string
import copy
import json
import zlib
import time
import sys
import os

COMPRESS = True

class Timer(object):
    def __init__(self):
        self.begin   = time.time()
        self.end   = time.time()
        self.stored  = 0.0
        self.stopped = True

    def start(self):
        if not self.stopped:
            return
        self.begin = time.time()
        self.stopped = False

    def stop(self):
        if self.stopped:
            return
        self.end = time.time()
        self.stored += self.end - self.begin
        self.stopped = True

    def read(self):
        if self.stopped:
             return self.stored
        now = time.time()
        total_time = now - self.begin + self.stored
        return total_time

    def reset(self):
        self.begin = time.time()
        self.end   = time.time()
        self.stored = 0.0

class DateRangeDict(object):
    def __init__(self,start,stop,npoints,*args,**kw):
        self.start = start
        self.stop = stop
        self.npoints = npoints
        self.records = {}
        self.res = kw.get("res",4)
        self.M = 1000000

    def snap(self,dtIn):
        dt = copy.deepcopy(dtIn)
        m = dt.microsecond
        M = self.M
        r = self.res
        ms = ((m*r)/M)*(M/r)
        dt = dt.replace(microsecond=ms)
        return dt

    def getKey(self,dt):
        dx = self.td2frac((self.stop - self.start)/self.npoints)
        vx = self.td2frac((dt - self.start))
        frac = (vx/dx)*dx
        td = self.frac2td(frac)
        key = self.snap(self.start + td)
        return key


    def iteritems(self):
        for (k,v) in self.records.iteritems():
            yield (k,v)

    def items(self):
        return list(self.iteritems)

    def put(self,dt,val):
        key = self.getKey(dt)
        self.records[key] = val

    def get(self,dt,*args,**kw):
        key = self.getKey(dt)
        if not self.records.has_key(key):
            if len(args)>=1:
                return args[0]
            else:
                raise ValueError("Key not found %s->%s"%(dt,key))
        return self.records[key]

    def td2frac(self,dt):
        out = 0
        out += dt.days*self.res*24*60*60
        out += dt.seconds*self.res
        out += int(dt.microseconds*self.res/float(self.M))
        return out

    def frac2td(self,frac):
        secs = frac/self.res
        ms = int(frac%self.res*self.M/self.res)
        dt = datetime.timedelta(seconds=secs,microseconds=ms)
        return dt

    def avail_iterkeys(self):
        dx = (self.stop - self.start)/self.npoints
        for i in xrange(0,self.npoints+1):
            yield self.getKey(self.start + dx*i)

    def avail_keys(self):
        return list(self.avail_iterkeys())

    def iterkeys(self):
        for k in self.records.iterkeys():
            yield k

    def keys(self):
        return list(self.iterkeys())

def printf(format,*args): sys.stdout.write(format%args)

def fprintf(fp,format,*args): fp.write(format%args)


class KVNotInDict(object):
    pass


def p64e(obj,compress=COMPRESS,debug=False):
    pdata = cPickle.dumps(obj)
    if compress:
        pdata = zlib.compress(pdata,9)
    b64 = base64.b64encode(pdata)
    return b64

def p64d(b64data,compress=COMPRESS,debug=False):
    pdata = base64.b64decode(b64data)
    if compress:
        pdata = zlib.decompress(pdata)
    obj = cPickle.loads(pdata)
    return obj

def tupleDictList(dict_list,*cols,**kw):
    out = []
    for d in dict_list:
        out.append(tupleDict(d,*cols,**kw))
    return out

def tupleDict(dict_in,*cols,**kw):
    out = []
    for col in cols:
        if not dict_in.has_key(col):
            out.append(KVNotInDict)
        else:
            out.append(dict_in[col])
    return tuple(out)

def dt2sqldt(dt):
    if dt == None:
        return ""
    t = dt.timetuple()
    args = []
    format = "%s-%s-%s %s:%s:%s"
    args.append(pad(4,'0',t.tm_year))
    args.append(pad(2,'0',t.tm_mon))
    args.append(pad(2,'0',t.tm_mday))
    args.append(pad(2,'0',t.tm_hour))
    args.append(pad(2,'0',t.tm_min))
    args.append(pad(2,'0',t.tm_sec))
    return format%tuple(args)
 
def pad(digits,ch,val,*args,**kw):
  str_out=str(val)
  side = kw.pop("side","LEFT")
  if side == "LEFT":
    for i in xrange(0,digits-len(str_out)):
      str_out = ch + str_out
    return str_out
  if side == "RIGHT":
    for i in xrange(0,digits-len(str_out)):
      str_out = str_out + ch
    return str_out

def save_json(json_file,obj):
    json_data = json.dumps(obj, indent=2)
    open(fullPath(json_file),"w").write(json_data)


def load_json(json_file):
    json_data = open(fullPath(json_file),"r").read()
    return json.loads(json_data)

def fullPath(file_path):
    return os.path.abspath(os.path.expanduser(file_path))

def normalize(obj):
    if isinstance(obj,list):
        out = []
        sum = 0.0
        for v in obj:
            sum += float(v)
        for v in obj:
            if sum == 0.0:
                out.append(0.0)
                continue
            out.append(float(v)/sum)
        return out
    if isinstance(obj,dict):
        out = {}
        keys = obj.keys()
        normalized = normalize([obj[k] for k in keys])
        for i in xrange(0,len(keys)):
            out[keys[i]] = normalized[i]
        return out
    return None            

def getDotAttr(obj,getStr):
    o = obj
    for subAttr in getStr.split("."):
        o = getattr(o,subAttr)
    return o

def setQueryParams(dict_in):
    out = ""
    kvout = []
    if len(dict_in) == 0:
        return out

    for (k,v) in dict_in.items():
        kout = urllib.quote(k)
        if isinstance(v,list):
            for i in v:
                vout = urllib.quote("%s"%i)
                kvout.append( (kout,vout) )
        else:
            vout = urllib.quote("%s"%v)
            kvout.append( (kout,vout) )
    out += "?"
    for (kout,vout) in kvout[:-1]:
        out += "%s=%s&"%(kout,vout)
    for (kout,vout) in kvout[-1:]:
        out += "%s=%s"%(kout,vout)
    return out
    
def pp(obj):
    return json.dumps(obj,indent=2)


def frange(fstart,fstop,nsteps):
    if fstop < fstart or nsteps <= 0:
        return
    dx = (float(fstop) - fstart)/nsteps
    hx = fstart - dx/2
    for i in xrange(1,nsteps+1):
        yield hx + dx*i


def int2bin(int_in,width):
    i = 0
    curr = int_in
    out = []
    while True:
        if curr <= 0:
            break        
        if curr%2 == 0:
            out.append("0")
        else:
            out.append("1")
        curr >>= 1
    for i in xrange(0,width - len(out)):
        out.append("0")
    out.reverse()
    outStr = string.join(out,"")
    return outStr

def bin2int(binStr):
    dec = 0
    bits = [int(bit)%2 for bit in binStr]
    bits.reverse()
    for i in xrange(len(bits)-1,-1,-1):
        dec += bits[i]*(1<<i)
    return dec
