from django.conf.urls.defaults import *
from django.contrib import admin
from app.main.testview.views import TestView
from app.main.ipv4.views import IPv4View
from app.main.account.views import AccountView
from app.main.bible.views import BibleView
admin.autodiscover()

viewList = []
viewList.append(AccountView('Account','/account/login'))
viewList.append(IPv4View('IPv4 Toys','/ipv4/dec2bin'))
viewList.append(BibleView('Bible View','/bible/reader'))
viewList.append(TestView('Test','/test/hello'))

urls = ['',(r'^admin/',include(admin.site.urls))]

sidelinks = []
for view in viewList:
    urls.extend(view.getUrlRoutes())
    sidelinks.append(view.getSideLink())

for view in viewList:
    view.setSideLinks(sidelinks)


urlpatterns = patterns(*tuple(urls))

