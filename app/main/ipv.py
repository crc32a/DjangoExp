import string
import re

ipv4_re_str  = r"^([0-9]{1,3})\." # 1st octet
ipv4_re_str += r"([0-9]{1,3})\." # 2nd octet
ipv4_re_str += r"([0-9]{1,3})\." # 3rd second octet
ipv4_re_str += r"([0-9]{1,3})$" # 4th octet
ipv4_re = re.compile(ipv4_re_str)

ipblock_re = re.compile("(.*)/(.*)")

MAXIP = 4294967295

class IPv4(object):
    def __init__(self,*args,**kw):
        self.ip = None
        if len(args)>=1:
            ipIn = args[0]
            if ipIn.__class__.__name__ in set(['int','long']):
                self.setInt(ipIn)
            else:
                self.setStr(ipIn)

    def getInt(self):
        return self.ip

    def setInt(self,ip):
        if ip == None:
            self.ip = None
        if ip < 0 or ip > MAXIP:
            raise ValueError("ip int not in range 0 to %i"%MAXIP)
        self.ip = ip

    def setStr(self,strIn):
        if strIn == None:
            self.ip = None
        self.ip = str2ipv4(strIn)

    def getStr(self):
        if self.ip == None:
            return ""
        return ipv42str(self.ip)

    def getClass(self):
        n = self.ip >> 24

        if 1 <= n <= 126:
            return "A"
        elif 128 <= n <= 191:
            return "B"
        elif 192 <= n <= 223:
            return "C"
        elif 224 <= n <= 239:
            return "D"
        elif 240 <= n <= 254:
            return "E"
        else:
            return "INVALID"

    def __invert__(self):
        inv = self.ip^MAXIP
        return IPv4(inv)

    def __and__(self,obj):
        v = self.ip & obj.ip
        return IPv4(v)

    def __rand__(self,obj):
        v = obj.ip & self.ip
        return IPv4(v)

    def __or__(self,obj):
        v = self.ip | obj.ip
        return IPv4(v)

    def __ror__(self,obj):
        v = obj.ip | self.ip
        return IPv4(v)

    def __str__(self):
        return self.getStr()

    def __repr__(self):
        return self.__str__()

class IPv4Net(object):
    def __init__(self,*args,**kw):
        self.wack = None
        self.ip = None
        if len(args)>=1:
           strIn = args[0]
           m = ipv4_re.match(strIn)
           if m:
               self.setIp(strIn)
               return
           m = ipblock_re.match(strIn)
           if m:
               ip = m.group(1)
               wm = m.group(2)
               self.setIp(ip)
               try:
                   wack = int(wm)
               except ValueError:
                   self.setMask(IPv4(wm))
                   return
               self.setWack(wack)
           else:
               raise ValueError("Invalid arg %s"%strIn)
 
    def setIp(self,ip):
        self.ip = IPv4(ip)

    def getIp(self):
        return self.ip

    def getWack(self):
        return self.wack

    def setWack(self,wack):
        if wack < 0 or wack > 32:
            raise ValueError("Invalid wack range. wack must be in [0,32]")
        self.wack = wack

    def setMask(self,ip):
        self.wack = mask2wack(ip)
    
    def getMask(self):
        ip = wack2ip(self.wack)
        return ip

    def getStr(self):
        out = ""
        if self.ip == None:
            return out
        out += self.getIp().getStr()
        if self.wack != None:
            out += "/%s"%self.getWack()
        return out

    def getSubnet(self):
        return self.ip&self.getMask()


    def getBroadcast(self):
        return self.getIp()|~self.getMask()

    def getSubnet(self):
        return self.getIp()&self.getMask()

    def getHost(self):
        return self.getIp()&~self.getMask()

    def getLo(self):
        n = self.getSubnet().getInt() + 1
        return IPv4(n)

    def getHi(self):
        n = self.getBroadcast().getInt() - 1
        return IPv4(n)

    def getNumberOfHosts(self):
        lo = self.getSubnet().getInt() + 1
        hi = self.getBroadcast().getInt() - 1
        return hi - lo + 1

    def __str__(self):
        return self.getStr()

    def __repr__(self):
        return self.__str__()

def wack2ip(wack):
    if wack < 0 or wack > 32:
        raise ValueError("Wack not in range [0,32]")
    ip = 0
    for i in xrange(0,wack):
        bitval = 1<<(31-i)
        ip += bitval
    return IPv4(ip)

def mask2wack(ipIn):
    n = ipIn.ip
    wack = 0
    for i in xrange(31,-1,-1):
        bit = (n >> i)&1
        if bit == 1:
            wack += 1
            n -= 1 << i
        if bit == 0:
            if n > 0:
                raise ValueError("invalid Mask")
            break
    return wack

def ipv42str(ip):
    octStr = []
    if ip < 0 or ip > MAXIP:
        raise ValueError("ip int not in range 0 to %s"%MAXIP)
    shifter = 24
    for i in xrange(0,4):
        oct = (ip >> shifter)&255
        octStr.append("%i"%oct)
        shifter -= 8
    out = string.join(octStr,".")
    return out


def str2ipv4(str_in):
    ip = 0
    m = ipv4_re.match(str_in)
    if not m:
        raise ValueError("String %s was not in a.b.c.d number format"%str_in)
    shifter = 0
    octStrs = [m.group(i) for i in xrange(1,5)]
    octStrs.reverse()
    for octStr in octStrs:
        try:
            oct = int(octStr)
        except ValueError:
            format = "count not parse int from \"%s\" \"%s\""
            raise ValueError(format%(octStr,str_in))
        if oct < 0 or oct > 255:
            raise ValueError("%s is not a valid 8bit value"%oct)
        ip += oct << shifter
        shifter += 8 
    return ip       
