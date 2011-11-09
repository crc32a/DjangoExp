from django.forms import TextInput
from app.main.models import *
from django.contrib import admin
from django.db import models
from django import forms

class RoleAdmin(admin.ModelAdmin):
    list_display=('name',)

class UserAdmin(admin.ModelAdmin):
    list_display = ('uid',)
    filter_horizontal = ('roles',)
    exclude = ('passwd',)

class ViewClassAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ViewAdmin(admin.ModelAdmin):
    list_display = ('view_class','name',)
    filter_horizontal = ('roles',)
    list_filter = ('view_class','name')

admin.site.register(User,UserAdmin)
admin.site.register(Role,RoleAdmin)
admin.site.register(View,ViewAdmin)
admin.site.register(ViewClass,ViewClassAdmin)
