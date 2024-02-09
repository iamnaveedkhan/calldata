from django.urls import path
from calldataapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login',views.user_login),
    path('logout',views.user_logout),
    path('dash',views.dashboard),
    path('newlead',views.newlead),
    path('edit/<cid>',views.edit),
    path('add',views.add_user),
    path('reset',views.resetp),
    path('sendmail',views.send_email),
    path('forget/<tid>',views.forget),
    path('all_lead',views.all_lead),
    path('all_staff',views.all_staff),
    path('viewlead/<cid>',views.viewlead),
    path('view_user/<mid>',views.view_user),
    path('edit_user/<uid>',views.edit_user),
    path('excel_lead',views.excel_lead),
    path('select_lead/<cid>',views.select_lead),
    path('search',views.search),
    path('date_filter',views.date_filter),
    path('allcomment/<id>',views.allcomment),
    path('allstatus/<id>',views.allstatus),
    # path('all_manager',views.all_manager),
    path('view/<cid>',views.view),
    path('picklead',views.pick),
    path('no_interest/<cid>',views.no_interest),
    path('picklead1',views.pick1),
    path('selectlead1/<id>',views.select1),
    path('alllead1',views.alllead1),
    path('moblogin',views.mob_user_login),
    path('csrf',views.csrf),
    path('mobdash',views.mobdash),
    path('editlead1/<cid>',views.mobeditlead),
    path('viewlead1/<cid>',views.mobviewlead),
    path('newlead1',views.mobnewlead),
    path('changepass1',views.changePass),
    path('interested/<id>/<lid>',views.interested),
    path('statuslist/<id>',views.statusList),
    path('mob_user_logout',views.mob_user_logout),
    path('checking/',views.checking),

]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
