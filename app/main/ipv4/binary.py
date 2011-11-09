from app.main.models import *
from app.main.tools import *
from app.main.util import *
from form import *
import random

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
