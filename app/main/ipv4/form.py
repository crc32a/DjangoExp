from app.main.form import *
from app.main.ipv import *
from django import forms

class IPv4NetForm(IdForm):
    network = forms.CharField(max_length=32,required=True)
    desired_subnets = forms.IntegerField(required=False)
    desired_subnet_bits = forms.IntegerField(required=False)

    def clean_network(self):
        try:
            data = self.cleaned_data["network"]
            net = IPv4Net(data)
            if net.ip == None:
                msg = "Ip address was invalid"
                raise forms.ValidationError(msg)
            if net.wack == None:
                msg = "Mask or Wack was invalid"
                raise forms.ValidationError(msg)
            return data
        except ValueError:
            msg  = "network must be of the form a.b.c.d/n "
            msg += "or a.b.c.d/e.f.g.h where e f g h are the mask"
            raise forms.ValidationError(msg)


class Bin2DecForm(IdForm):
    decimal = forms.IntegerField(required=False)

class Dec2BinForm(IdForm):
    binary = forms.CharField(max_length=64,required=False)

    def clean_binary(self):
        binset = set(["0","1"])
        data = self.cleaned_data['binary']
        if data == None or data=="":
            return data
        for ch in data:
            if ch not in binset:
                msg = "binary digits must be either 1 or 0"
                raise forms.ValidationError(msg)
        return data


