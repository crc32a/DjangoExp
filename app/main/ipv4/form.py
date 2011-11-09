from app.main.form import *
from django import forms

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


