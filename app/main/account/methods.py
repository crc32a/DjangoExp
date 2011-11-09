from app.main.models import *
from app.main.tools import requireRoles
from app.main.form import *
from django.http import *

def login(self,rc):
    rc.ctx["loginform"] = LoginForm()
    if rc.form_named() == "LoginForm":
        if rc.request.POST["button"] == "Login":
            loginform = LoginForm(rc.request.POST)
            if not loginform.is_valid():
                rc.ctx["operror"] = rc.logger.log("Invalid form LoginForm")
                return self.render(rc)
            uid = loginform.cleaned_data["user_name"]
            passwd = loginform.cleaned_data["password"]
            if not validateUserPassword(uid,passwd):
                rc.ctx["operror"] = rc.logger.log("Invalid login")
                return self.render(rc)
            rc.session["uid"] = uid
            rc.configUser()
            if not rc.user.enabled:
                msg = "User %s not enabled loging denied"%rc.user.uid
                rc.ctx["operror"] = rc.logger.log(msg)
                rc.killsession()
                return self.render(rc)
            rc.ctx["opsuccess"] = rc.logger.log("Successfull login")
            return self.render(rc)
        elif rc.request.POST["button"] == "Logout":
            rc.killsession()
            rc.ctx["uid"] = None
            rc.ctx["role"] = None
            rc.ctx["opsuccess"] = rc.logger.log("Successfully logged out")
            return self.render(rc)
    rc.logger.log("No POST body just returning login form")
    return self.render(rc)

@requireRoles()
def edituser(self,rc):
    rc.ctx["loginform"] = LoginForm()
    if rc.form_named() == "LoginForm":
        if rc.request.POST["button"] == "Submit":
            loginform = LoginForm(rc.request.POST)
            if not loginform.is_valid():
                rc.ctx["operror"] = rc.logger.log("Invalid form LoginForm")
                return self.render(rc)
            uid = loginform.cleaned_data["user_name"]
            passwd = loginform.cleaned_data["password"]
            msg = ""
            try:
                user = User.objects.get(uid=uid)
            except User.DoesNotExist:
                msg += "new user %s created; "%uid
                user = User()
                user.uid = uid
            user.setPasswd(passwd)
            user.save()
            msg += "saving passwd;"
            rc.ctx["opsuccess"] = rc.logger.log(msg)
            return self.render(rc)
        else:
            rc.ctx["operror"] = rc.logger.log("Request wasn't a submit form")
            return self.render(rc)
    rc.logger.log("No POST body just returning login form")
    return self.render(rc)

@requireRoles()
def changepasswd(self,rc):
    rc.ctx["changepasswdform"] = ChangePasswdForm()
    if rc.form_named() == "ChangePasswdForm":
        if rc.request.POST["button"] == "Submit":
            changepasswdform = ChangePasswdForm(rc.request.POST)
            if not changepasswdform.is_valid():
                rc.ctx["changepasswdform"] = changepasswdform
                msg = "Invalid form ChangePasswdForm"
                rc.ctx["operror"] = rc.logger.log(msg)
                return self.render(rc)
            rc.ctx["changepasswdform"] = changepasswdform
            old = changepasswdform.cleaned_data["old_password"]
            n1  = changepasswdform.cleaned_data["new_password"]
            n2  = changepasswdform.cleaned_data["repeat_password"]
            user = rc.user
            if user == None:
                msg = "user %s Doesnt Exists ??? "%uid
                rc.ctx["operror"] = rc.logger.log(msg)
                return self.render(rc)
            if not user.authenticate(old):
                msg = "Old password didn't match sorry"
                rc.ctx["operror"] = rc.logger.log(msg)
                return self.render(rc)
            if n1 != n2:
                msg = "new password didn't match the repeated password"
                rc.cts["operror"] = rc.logger.log(msg)
                return self.render(rc)
            rc.user.setPasswd(n1)
            rc.user.save()
            msg = "Password changed for %s"%user.uid
            rc.ctx["opsuccess"] = rc.logger.log(msg)
            return self.render(rc)
        else:
            rc.ctx["operror"] = rc.logger.log("Request wasn't a submit form")
            return self.render(rc)
    rc.logger.log("No POST body just returning login form")
    return self.render(rc)



def redirectLogin(self,rc):
    return HttpResponseRedirect("/account/login/")

def userInfo(self,rc):
    rc.logger.log("Info displayed")
    return self.render(rc)

def validateUserPassword(uid,passwd):
    try:
        user = User.objects.get(uid=uid)
        isValid = user.authenticate(passwd)
        return isValid
    except User.DoesNotExist:
        return False

