from django import forms

class IdForm(forms.Form):
    def __init__(self,*args,**kw):
        forms.Form.__init__(self,*args,**kw)
        form_name = forms.CharField(max_length=32,
                                    required=True,
                                    widget=forms.HiddenInput,
                                    initial=self.__class__.__name__
                                   )
        self.fields["form_name"] = form_name

class ChangePasswdForm(IdForm):
    old_password    = forms.CharField(max_length=64,widget=forms.PasswordInput)
    new_password    = forms.CharField(max_length=64,widget=forms.PasswordInput)
    repeat_password = forms.CharField(max_length=64,widget=forms.PasswordInput)

class ChangeDropPasswdForm(IdForm):
    name = forms.ChoiceField(required=True,choices=())
    new_password    = forms.CharField(max_length=64,widget=forms.PasswordInput)

class LoginForm(IdForm):
    user_name    = forms.CharField(max_length=64,required=True)
    password     = forms.CharField(max_length=64,widget=forms.PasswordInput)

class LogForm(IdForm):
    user = forms.ChoiceField(choices=(),required=False)
    view = forms.ChoiceField(choices=(),required=False)
    msg_like = forms.CharField(max_length=64,required=False)
    start_date = forms.DateTimeField(required=False)
    stop_date = forms.DateTimeField(required=False)
    only_show_exceptions = forms.BooleanField(required=False)
    
