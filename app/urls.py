from django.conf.urls.defaults import *
from django.contrib import admin
from app.main.testview.views import TestView
from app.main.account.views import AccountView
admin.autodiscover()

viewList = []
viewList.append(AccountView('Account','/account/login'))
viewList.append(TestView('Test','/test/hello'))

urls = ['',(r'^admin/',include(admin.site.urls))]

sidelinks = []
for view in viewList:
    urls.extend(view.getUrlRoutes())
    sidelinks.append(view.getSideLink())

for view in viewList:
    view.setSideLinks(sidelinks)


urlpatterns = patterns(*tuple(urls))

