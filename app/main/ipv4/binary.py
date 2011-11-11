from app.main.models import *
from app.main.tools import *
from app.main.util import *
from app.main.ipv import *

from form import *
import random

def ipmask(self,rc):
    maxdisplayablesubnet = 1<<14
    formkey = "ipv4netform"
    ipnf = rc.session.get(formkey,IPv4NetForm())
    rc.ctx[formkey] = ipnf
    rc.session[formkey] = ipnf
    if rc.form_named()=="IPv4NetForm":
        ipnf= IPv4NetForm(rc.request.POST)
        rc.ctx[formkey] = ipnf
        rc.session[formkey] = ipnf
        if not ipnf.is_valid():
            rc.ctx["operror"] = rc.logger.log("Invalid form")
            return self.render(rc)
        network = IPv4Net(ipnf.cleaned_data["network"])
        ip = network.getIp()
        mask = network.getMask()
        bc = network.getBroadcast()
        lo = network.getLo()
        hi = network.getHi()
        net = network.getSubnet()
        mask = network.getMask()
        netTable = {}
        netTable["ip"] = ip
        netTable["ip_bits"] = ipBits(ip,mask)
        netTable["mask"] = mask
        netTable["mask_bits"] = ipBits(mask,mask)
        netTable["net"] = net
        netTable["net_bits"] = ipBits(net,mask)
        netTable["lo"] = lo
        netTable["lo_bits"] = ipBits(lo,mask)
        netTable["hi"] = hi
        netTable["hi_bits"] = ipBits(hi,mask)
        netTable["bc_bits"] = ipBits(bc,mask)
        netTable["bc"] = bc
        netTable["mask"] = mask
        netTable["mask_bits"] = ipBits(mask,mask)
        rc.ctx["wack"] = network.getWack()
        rc.ctx["nhosts"] = network.getNumberOfHosts()
        rc.ctx["net_table"] = netTable
        rc.ctx["ip_class"] = network.getIp().getClass()

        sbits = ipnf.cleaned_data["desired_subnet_bits"]
        if sbits:
            nsubs = (1<<sbits)-1
        else:
            nsubs = ipnf.cleaned_data["desired_subnets"]
            if nsubs != None:
                if nsubs <1:
                    msg = "Desired Subnets must be greater then 0"
                sbits = needbits(nsubs)

        if sbits:
            abits = 32 - network.getWack()
            if sbits > abits:
                format  = "Sorry subnet required %i bits but only %i "
                format += "were available for subnetting."
                msg = format%(sbits,abits)
                rc.ctx["operror"] = msg
                return self.render(rc)
            swack = network.getWack() + sbits
            hbits = 32-swack
            rc.ctx["subnetnhosts"] = (1<<hbits)-2
            submask = wack2ip(swack)
            rc.ctx["submask"] = submask.getStr()
            rc.ctx["nsubs"] = nsubs
            subnets = []
            if ipnf.cleaned_data["display_subnets"]:
                if nsubs > maxdisplayablesubnet:
                    format  = "Not displaying more then %i subnets"
                    msg = format%maxdisplayablesubnet
                    rc.ctx["operror"] = msg
                    return self.render(rc)
                for i in xrange(0,nsubs):
                    ip = network.getSubnet().getInt()
                    ip += i*(1<<(32-swack))
                    subnet = IPv4Net()
                    subnet.ip = IPv4()
                    subnet.setIp(ip)
                    subnet.setWack(swack)
                    row = {}
                    row["subnet"] = "%s/%s"%(subnet.getIp(),swack)
                    row["bits"] = ipBits(subnet.getIp(),mask,submask=submask)
                    row["bc"] = subnet.getBroadcast()
                    row["lo"] = subnet.getLo()
                    row["hi"] = subnet.getHi()
                    subnets.append(row)
                rc.ctx["subnets"] = subnets
        return self.render(rc)
    return self.render(rc)

def needbits(nsubs):
    n = nsubs - 1
    i = 0
    while n > 0:
        i += 1
        n >>= 1
    return i

def ipBits(ip,mask,submask=IPv4("0.0.0.0")):
    out   = ""
    gray  = "#c0c0c0"
    red   = "#ffc0c0"
    blue  = "#c0e0ff"
    green = "#a0ffa0"
    for i in xrange(31,-1,-1):
        mask_bit = (mask.ip>>i)&1
        ip_bit = (ip.ip>>i)&1
        subnet_bit = (submask.ip>>i)&1
        if mask_bit:
            color = red
        elif subnet_bit:
            color = green
        else:
            color = blue
        out += "            <td bgcolor=\"%s\">%i</td>\n"%(color,ip_bit)
        if i != 0 and i%4 == 0:
            out += "            <td bgcolor=\"%s\">&nbsp;</td>\n"%(color)
        if i != 0 and i%8 == 0:
            out += "            <td bgcolor=\"%s\">&nbsp;</td>\n"%(color)
             
    return out

def dec2bin(self,rc):
    dec2binform = Dec2BinForm()
    rc.ctx["dec2binform"] = dec2binform
    rc.ctx["decval"] = rc.session.get("decval",random.randint(0,255))
    rc.session["decval"] = rc.ctx["decval"] #Store it for later
    if rc.form_named() == "Dec2BinForm":
        dec2binform = Dec2BinForm(rc.request.POST)
        rc.ctx["dec2binform"] = dec2binform
        if not dec2binform.is_valid():
            rc.ctx["operror"] = rc.logger.log("Invalid form")
            return self.render(rc)
        if rc.request.POST["button"] == "Pick new number":
            rc.ctx["decval"] = random.randint(0,255)
            rc.session["decval"] = rc.ctx["decval"]
            return self.render(rc)
        if rc.request.POST["button"] == "Check your guess":
            binval = dec2binform.cleaned_data["binary"]
            if bin2int(binval) == rc.session.get("decval",-1):
                rc.ctx["opsuccess"] = "Binary value is Correct"
                return self.render(rc)
            else:
                expected = int2bin(rc.session.get("decval",-1),8)
                msg = "Error binary should have been %s"%expected
                rc.ctx["operror"] = msg
                return self.render(rc)
        if rc.request.POST["button"] == "Show decimal":
            binval = dec2binform.cleaned_data["binary"]
            decval = bin2int(binval)
            rc.session["decval"] = decval
            rc.ctx["decval"] = decval
            return self.render(rc)
    return self.render(rc)

def bin2dec(self,rc):
    bin2decform = Bin2DecForm()
    rc.ctx["bin2decform"] = bin2decform
    binval = rc.session.get("binval",int2bin(random.randint(0,255),8))
    rc.ctx["binval"] = binval
    rc.session["binval"] = binval #Store it for later
    if rc.form_named() == "Bin2DecForm":
        bin2decform = Bin2DecForm(rc.request.POST)
        rc.ctx["bin2decform"] = bin2decform
        if not bin2decform.is_valid():
            rc.ctx["operror"] = rc.logger.log("Invalid form")
            return self.render(rc)
        if rc.request.POST["button"] == "Pick new number":
            binval = int2bin(random.randint(0,255),8)
            rc.ctx["binval"] = binval
            rc.session["binval"] = binval
            return self.render(rc)
        if rc.request.POST["button"] == "Check your guess":
            decval = bin2decform.cleaned_data["decimal"]
            if int2bin(decval,8) == rc.session.get("binval",""):
                rc.ctx["opsuccess"] = "Binary value is Correct"
                return self.render(rc)
            else:
                expected = bin2int(rc.session.get("binval",""))
                msg = "Error decimal should have been %s"%expected
                rc.ctx["operror"] = msg
                return self.render(rc)
        if rc.request.POST["button"] == "Show binary":
            decval = bin2decform.cleaned_data["decimal"]
            binval = int2bin(decval,8)
            rc.session["binval"] = binval
            rc.ctx["binval"] = binval
            return self.render(rc)
    return self.render(rc)
