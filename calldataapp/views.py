import datetime,io,os,random,json,pytz
from dateutil.relativedelta import relativedelta
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate,login,logout
from django.db.models import Q
from django.db import IntegrityError
from calldataapp.models import Lead,User,Comment,Status
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from calldata import settings
from calldataapp.forms import filter,UserForm
# from django.contrib.staticfiles import finders
from django.http import JsonResponse
import pandas as pd
from dateutil import parser
from django.contrib.sessions.models import Session
from django.middleware.csrf import get_token
from django.utils import timezone
from django.core.exceptions import PermissionDenied
import csv
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4,letter,landscape,A3
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate, Frame
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Create your views here.
def user_login(request):
    context={}
    if request.user.is_authenticated and request.user.is_active:
        return redirect('/dash')
    else:
        if request.method=='POST':
            uname=request.POST['uname']
            upass=request.POST['upass']
            if uname=="" or upass=="":
                context['err']="Field cannot be empty"
                return render(request,'login.html',context)
            else:
                u=authenticate(username=uname,password=upass)
                if u is not None:
                    if uname==upass:
                        # context['errmsgs']="Click Here TO Reset Your Password"
                        # return render(request,'login.html',context)
                        t=random.randrange(100000,21474836)
                        n=User.objects.get(username=uname)
                        n.temp=t
                        n.save()
                        return redirect("/forget/"+str(t))
                    else:
                        login(request,u)
                        n=User.objects.filter(username=uname)
                        context['data']=n
                        return redirect('/dash')
                else:
                    context['err']="invalid username and password"
                    return render(request,'login.html',context)
            
        else:
            return render(request,'login.html')

# User Logout Function
def user_logout(request):
    logout(request)
    return redirect('/login')
# User Login And Logout Function (End).................................................................................



# Reset And Forget Password Functions (Start).........................................................................

# Sending Mail For Reset Password
def send_email(request):
    context={}
    if request.method=='POST':
        try:
            uemail=request.POST['uemail']
            t=random.randrange(100000,21474836)
            n=User.objects.get(email=uemail)
            n.temp=t
            n.save()
            msg="https://101ewarranty.com/forget/"+str(t)
            send_mail(
            "Reset Password Link ",
            msg,
            "donotreply@101ewarranty.com",
            [uemail],
            fail_silently=False,
            )
            context['success']="Email send successfully"
            return render(request,'send_email.html',context)
        except Exception:
            context['success']="please enter valid email!!!"
            return render(request,'send_email.html',context)
    else:
        return render(request,'send_email.html')


# Forget Password Function
def forget(request,tid):
    context={}
    if request.method=='POST':
        upass=request.POST['upass']
        cpass=request.POST['cpass']
        if upass == cpass:
            u=User.objects.get(temp=tid)
            u.password=make_password(upass)
            u.temp = None
            u.save()
            return redirect('/login')
            
        else:
            context['errmsg']="password and confirm password not matched"
            return render(request,'forget.html',context)
    else:
        return render(request,'forget.html')

# Reset Password Function
def resetp(request):
    context={}
    if request.user.is_authenticated and request.user.is_active:
        if request.method=='POST':
            current=request.POST['current']
            upass=request.POST['upass']
            cpass=request.POST['cpass']
            if upass == cpass:
                try:
                    u=User.objects.get(id=request.user.id)
                    a=authenticate(username=u.username,password=current)
                    if a is not None:
                        u.password=make_password(upass)
                        u.temp = None
                        u.save()
                        context['errmsg']="Password Changed Successfully"
                        return render(request,'login.html',context)
                    else:
                        context['errmsg']="Current Password Not matched"
                        return render(request,'resetpass.html',context)
                except Exception:
                    context['errmsg']="user not found"
                    return render(request,'resetpass.html',context)
                
            else:
                context['errmsg']="password and confirm password not matched"
                return render(request,'resetpass.html',context)
        else:
            return render(request,'resetpass.html')
    else:
        context['err']="Please Login"
        return render(request,'login.html',context)
# Reset And Forget Password Functions (End).............................................................................




# Create Or Edit User Detaile (Start)...................................................................................

# Add User Function
def add_user(request):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    
    if auth_check and request.user.role in [1, 2, 3]:
        a = request.user.id

        if request.method == 'POST':
            form = UserForm(request.POST, request.FILES)
            if form.is_valid():
                form.instance.temp = random.randrange(100000, 21474836)
                
                if request.user.role in [1, 2]:
                    form.instance.manager = request.user
                
                if request.user.role == 3:
                    form.instance.tl = request.user
                
                form.instance.username = form.cleaned_data["email"]
                form.instance.password = make_password(form.cleaned_data["email"])
                form.save()
                
                context['success'] = f"User {form.instance.first_name} is registered successfully"
                return render(request, 'add.html', context)
            else:
                context['form'] = form
                return render(request, 'add.html', context)
        else:
            context['form'] = UserForm()
            return render(request, 'add.html', context)
    else:
        return redirect('/dash')



# Edit User Detail Only Image
def edit_user(request, uid):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    
    if auth_check and request.user.role in [1, 2, 3]:
        a = User.objects.get(id=uid)

        if request.method == 'POST':
            form = UserForm(request.POST, request.FILES, instance=a)
            if form.is_valid():
                form.save()
                context['success'] = f"User {form.instance.first_name} is Updated successfully"
                context['form'] = form
                return render(request, 'edit_user.html', context)
            else:
                print(form.errors)
                context['form'] = form
                return render(request, 'edit_user.html', context)
        else:
            context['form'] = UserForm(instance=a)
            return render(request, 'edit_user.html', context)
    else:
        return redirect('/dash')

# Create Or Edit User Detaile (End).....................................................................................



# User Dashboard Function (Start).......................................................................................
def dashboard(request):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET':
        role_actions = {
            1: lambda: filter().super(request),
            2: lambda: filter().manage(request),
            3: lambda: filter().tl(request),
            4: lambda: filter().staf(request),}
        role_filters = {
            1: Q(),
            2: Q(Q(manager_id=request.user.id) | Q(agent_id=request.user.id)) & Q(status=1),
            3: Q(Q(tl_id=request.user.id) | Q(agent_id=request.user.id)) & Q(status=1),
            4: Q(agent_id=request.user.id) & Q(status=1),}      
        leads = Lead.objects.filter(role_filters.get(request.user.role, Q())).order_by('-id')[:10]
        context['data'] = leads
        context['success']=request.session.get('msg')
        context['err']=request.session.get('errmsg')
        if request.user.role in role_actions:
            context.update(role_actions[request.user.role]())
            request.session.pop('msg', None)
            request.session.pop('errmsg', None)
        return render(request, 'dash.html', context)
    else:
        context['err'] = "Please Login" if not auth_check else "Invalid Request"
        return render(request,'login.html', context)
# User Dashboard Function (End)....................................................................................
    


def newlead(request):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check:
        if request.method == 'POST':
            name = request.POST['name']
            mob = request.POST['d_no']
            alt = request.POST['alt']
            shop = request.POST['shop']
            city = request.POST['city']
            state = request.POST['state']
            if len(str(alt)) != 10 and len(str(mob)) != 10:
                context['errmsg'] = "Contact Number Must Be 10 Digit"
                return render(request, 'newlead.html', context)
            else:
                context = {'today': datetime.datetime.now().date(),'last': datetime.datetime.now().date(),'success': "Lead Created Successfully"}
                role_filters = {
                    1: {'agent_id': request.user,'manager_id': request.user.id},
                    2: {'agent_id': request.user,'manager_id': request.user.id},
                    3: {'tl_id': request.user.id,'agent_id': request.user},
                    4: {'agent_id': request.user,'manager_id': request.user.manager_id,'tl_id': request.user.tl_id}
                }
                lead_data = {
                    'name': name,  'mob': mob,
                    'alternate': alt, 'order_id': "NK"+str(random.randrange(10000000, 99999999)),
                     'shop_name': shop,'city':city,'state':state,'create_date':timezone.now(),'comment':'CREATED','commentDate':timezone.now(),'picked_date':timezone.now()}
                lead_data.update(role_filters.get(request.user.role, {}))
                l = Lead.objects.create(**lead_data)
                l.save()
                return render(request, 'newlead.html', context)
        else:
            context = {'today': datetime.datetime.now().date(),'last': datetime.datetime.now().date() - relativedelta(days=30)}
            return render(request, 'newlead.html', context)
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)

def excel_lead(request):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check:
        if request.method == 'POST':
            if 'excel_file' in request.FILES:
                excel_file = request.FILES['excel_file']
                if excel_file.name.endswith('.csv'):
                    df = pd.read_csv(excel_file)
                elif excel_file.name.endswith('.xls'):
                    df = pd.read_excel(excel_file, engine='xlrd')
                elif excel_file.name.endswith('.xlsx'):
                    df = pd.read_excel(excel_file, engine='openpyxl')
                else:
                    context['errmsg'] = "Invalid file format. Please upload a CSV or Excel file."
                    return render(request, 'newlead.html', context)
                for index, row in df.iterrows():
                    if not Lead.objects.filter(Q(mob=row['cxMobile'])).exists():
                        
                        n = row['name']
                        d = row['cxMobile']
                        alt = row['altNumber']
                        shop = row['shop']
                        city = row['city']
                        state = row['state']
                        lead_data = {
                            'name': n, 'mob': d,
                            'alternate': alt, 'order_id': "NK"+str(random.randrange(10000000, 99999999)),
                            'shop_name': shop,'create_date':timezone.now(),'comment':'CREATED','commentDate':timezone.now(),'city':city,'state':state}
                        l = Lead.objects.create(**lead_data)
                        l.save()
                context = {'today': datetime.datetime.now().date(),'last': datetime.datetime.now().date(),'success': "Lead Created Successfully"}
                return render(request, 'newlead.html', context)
            else:
                context['errmsg'] = "No Excel file uploaded"
                return render(request, 'newlead.html', context)
        else:
            return render(request,'upload_excel.html')
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)

# def select_lead(request,cid):
#     context={}
#     auth_check = request.user.is_authenticated and request.user.is_active
#     if auth_check:
#         if request.method == 'GET':
#             a = Lead.objects.get(order_id=cid)
#             if a.agent_id is None:
#                 context = {'today': datetime.datetime.now().date(),'last': datetime.datetime.now().date(),'success': "Lead Created Successfully"}
#                 role_filters = {
#                     1: {'agent_id': request.user,'manager_id': request.user.id},
#                     2: {'agent_id': request.user,'manager_id': request.user.id},
#                     3: {'tl_id': request.user.id,'agent_id': request.user},
#                     4: {'agent_id': request.user,'manager_id': request.user.manager_id,'tl_id': request.user.tl_id}
#                 }
#                 lead_data = {
#                     'name': a.name, 'mob': a.mob,
#                     'alternate': a.alternate, 'order_id': a.order_id,
#                     'city': a.city, 'state': a.state,
#                      'shop_name': a.shop_name,'picked_date':datetime.datetime.now().date()}
#                 lead_data.update(role_filters.get(request.user.role, {}))
#                 l = Lead.objects.filter(order_id=cid).update(**lead_data)
#                 request.session['msg'] = "Lead Added"
#                 return redirect(f'/view/{a.id}')
#             else:
#                 request.session['msg'] = "Lead Not Available Or Picked"
#                 return redirect('/dash')
#         else:
#             a=Lead.objects.filter(agent_id=None)
#             return render(request,'select_lead.html',{'data':a})
#     else:
#         context['err'] = "Please Login"
#         return render(request, 'login.html', context)

# def pick(request):
#     context={}
#     auth_check = request.user.is_authenticated and request.user.is_active
#     if auth_check and request.method == 'GET':
#         a = Lead.objects.filter(agent_id=None).order_by('-id')
#         context['data']=a
#         context['title']='Pick Lead'
#         return render(request,'select_lead.html',context)
#     else:
#         context['err'] = "Please Login"
#         return render(request, 'login.html', context)
# edit Details (Exept Images) Of Existing Lead
def edit(request, cid):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET':
        role_filters = {
            1: Q(),
            2: Q(manager_id=request.user.id) | Q(agent_id=request.user.id),
            3: Q(tl_id=request.user.id) | Q(agent_id=request.user.id),
            4: Q(agent_id=request.user.id),}
        query = Q(id=cid) & role_filters.get(request.user.role, Q())
        leads = Lead.objects.filter(query)
        if leads:
            context['data'] = leads
            context['success']=request.session.get('msg')
            context['err']=request.session.get('errmsg')
            request.session.pop('msg', None)
            request.session.pop('errmsg', None)
            return render(request, 'edit.html', context)
        else:
            return redirect('/dash')
    elif auth_check and request.method == 'POST':
        name = request.POST['name']
        mob = request.POST['mob']
        alt = request.POST['alt']
        city = request.POST['city']
        state = request.POST['state']
        shop = request.POST['shop']
        if len(str(alt)) != 10 and len(str(mob)) != 10:
            request.session['errmsg'] = "Contact Number Must Be 10 Digit"
        else:
            Lead.objects.filter(id=cid).update(name=name, mob=mob, alternate=alt, city=city, state=state, shop_name=shop)
            request.session['msg'] = "Lead Updated"
        return redirect(f'/edit/{cid}')
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)

def no_interest(request,cid):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET':
        role_filters = {
            1: Q(),
            2: Q(manager_id=request.user.id) | Q(agent_id=request.user.id),
            3: Q(tl_id=request.user.id) | Q(agent_id=request.user.id),
            4: Q(agent_id=request.user.id),}
        query = Q(imei1=cid) & role_filters.get(request.user.role, Q())
        a = Lead.objects.get(query)
        if a:
            a.status = 0
            a.save()
            request.session['msg'] = "Not Interested"
            return redirect('/dash')
        else:
            request.session['errmsg'] = "Not Found"
            return redirect('/dash')
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)
    


def all_lead(request):
    if not (request.user.is_authenticated and request.user.is_active):
        err = "Please Login"
        return render(request, 'login.html', {'err': err})
    role_filters = {
        1: Q(create_date=datetime.datetime.now().date()),
        2: (Q(manager_id=request.user.id) | Q(agent_id=request.user)) & Q(picked_date=datetime.datetime.now().date()),
        3: (Q(agent_id=request.user) | Q(tl_id=request.user.id)) & Q(picked_date=datetime.datetime.now().date()),
        4: Q(agent_id=request.user) & Q(picked_date=datetime.datetime.now().date()),}
    query = role_filters.get(request.user.role, None)
    if query is None:
        return redirect('/dash')
    context = {'today': datetime.datetime.now(),'last': datetime.datetime.now(),'title': "All Leads",}
    context['data'] = Lead.objects.filter(query).order_by('-picked_date')
    return render(request, 'dashboard.html', context)



# Display All Staff Detail of Requested User Or Manager 
def all_staff(request):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    role = request.user.role if auth_check  else None
    queries = {
        1: Q(is_staff=1, role=4),
        2: Q(manager_id=request.user.id, role=4),
        3: Q(tl_id=request.user.id, role=4),
    }
    users = User.objects.filter(queries.get(role, Q()))
    counts = {}

    for user in users:
        created = Lead.objects.filter(agent_id=user.id).count()
        interested = Lead.objects.filter(Q(status=2) & Q(agent_id=user.id)).count()
        notinterested = Lead.objects.filter(Q(status=3) & Q(agent_id=user.id)).count()
        followup = Lead.objects.filter(Q(status=4) & Q(agent_id=user.id)).count()
        completed = Lead.objects.filter(Q(status=5) & Q(agent_id=user.id)).count()
        noncall = Lead.objects.filter(Q(status=1) & Q(agent_id=user.id)).count()

        # Store counts in the dictionary
        counts[user.id] = {
            'created': created,
            'interested': interested,
            'notinterested': notinterested,
            'followup': followup,
            'completed': completed,
            'noncall': noncall,
        }
    print(counts)
    context = {
        'counts':counts,
        'data': users,
        'title': "All Sales Executive" if auth_check else None,
    }
    if auth_check and role in [1,2,3] and not context['data']:
        context['err'] = "You Have No Sales Executive"
    if auth_check and role not in [1,2,3]:
        return redirect('/dash')
    if not auth_check:
        context['err'] = "Please Login"
    return render(request, 'staff.html' if auth_check else 'login.html', context)


def all_manager(request):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    role = request.user.role if auth_check else None

    if auth_check and role == 1:
        users = User.objects.filter(role=2).order_by('-id')
        counts = {}

        for user in users:
            created = Lead.objects.filter(agent_id=user.id).count()
            interested = Lead.objects.filter(Q(status=2) & Q(agent_id=user.id)).count()
            notinterested = Lead.objects.filter(Q(status=3) & Q(agent_id=user.id)).count()
            followup = Lead.objects.filter(Q(status=4) & Q(agent_id=user.id)).count()
            completed = Lead.objects.filter(Q(status=5) & Q(agent_id=user.id)).count()
            noncall = Lead.objects.filter(Q(status=1) & Q(agent_id=user.id)).count()

            # Store counts in the dictionary
            counts[user.id] = {
                'created': created,
                'interested': interested,
                'notinterested': notinterested,
                'followup': followup,
                'completed': completed,
                'noncall': noncall,
            }
        context = {
            'counts':counts,
            'data': users,
            'title': "All Managers"
        }
        return render(request, 'staff.html', context)
    elif auth_check:
        return redirect('/dash')
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)


def all_tl(request):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    role = request.user.role if auth_check else None
    queries = {1: Q(role=3),2: Q(manager_id=request.user.id, role=3),}
    if auth_check and role in [1,2]:
        context = {'data': User.objects.filter(queries.get(role, Q())).order_by('-id'),
                'title': "All TL(s)" if auth_check and role in [1, 2] else None,}
        return render(request, 'staff.html',context)
    elif auth_check:
        return redirect('/dash')
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)
    

def transfer_tl(request,uid):
    context={}
    if request.user.is_authenticated and request.user.is_active:
        if request.user.role==1:
            a=User.objects.filter(Q(id=uid) & Q(role=4))
            b=User.objects.filter(role=3)
            context['data']=a
            context['tl_data']=b
            if request.method=='GET':
                return render(request,'transfer_tl.html',context)
            else:
                tl=request.POST['tl']
                a=User.objects.get(id=uid)
                a.tl_id=tl
                a.save()
                context['success']=("TL Successfully Changed to "+"  "+a.tl.first_name)
                return render(request,'transfer_tl.html',context)
        else:
            return redirect('/dash')
    else:
        context['err']="Please Login"
        return render(request,'login.html',context)

def transfer_manager(request,uid):
    context={}
    if request.user.is_authenticated and request.user.is_active:
        if request.user.role==1:
            a=User.objects.filter(Q(id=uid) & Q(role=3))
            b=User.objects.filter(role=2)
            context['data']=a
            context['m_data']=b
            if request.method=='GET':
                return render(request,'transfer_manager.html',context)
            else:
                manager=request.POST['manager']
                a=User.objects.get(id=uid)
                a.manager_id=manager
                a.save()
                context['success']=("manager Successfully Changed to "+"  "+a.manager.first_name)
                return render(request,'transfer_manager.html',context)
        else:
            return redirect('/dash')
    else:
        context['err']="Please Login"
        return render(request,'login.html',context)



def search(request):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET':
        srch=request.GET.get('srch')
        role_filters = {
            1: Q(),
            2: Q(manager_id=request.user.id) | Q(agent_id=request.user.id),
            3: Q(tl_id=request.user.id) | Q(agent_id=request.user.id),
            4: Q(agent_id=request.user.id),}
        query = (Q(mob__icontains=srch) | Q(city__icontains=srch) | Q(order_id__icontains=srch) | Q(name__icontains=srch) | Q(state__icontains=srch) | Q(alternate__icontains=srch) | Q(shop_name__icontains=srch)) & role_filters.get(request.user.role, Q())
        data = Lead.objects.filter(query)
        today=datetime.datetime.now().date()
        context ={'data':data,'title':"Search",'cid':srch,'today':today,'last':today}
        return render(request, 'dashboard.html',context)
    else:
        context['err'] = "Please Login" if not auth_check else None
        return render(request, 'login.html', context)

def date_filter(request):
    context={}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET':
        f = request.GET.get('from')
        t = request.GET.get('to')
        role_filters = {
            1: Q(),
            2: Q(manager_id=request.user.id) | Q(agent_id=request.user.id),
            3: Q(tl_id=request.user.id) | Q(agent_id=request.user.id),
            4: Q(agent_id=request.user.id),
        }
        query = Q(create_date__range=(f, t)) & role_filters.get(request.user.role, Q())
        data = Lead.objects.filter(query).order_by('-id')
        context = {
            'data': data,
            'today': datetime.datetime.strptime(f, '%Y-%m-%d').date(),
            'last': datetime.datetime.strptime(t, '%Y-%m-%d').date(),
            'title': "Date Filter"
        }
        return render(request, 'dashboard.html', context)
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)


def viewlead(request,cid):
    if not (request.user.is_authenticated and request.user.is_active):
        err = "Please Login"
        return render(request, 'login.html', {'err': err})
    role_filters = {
        1: Q(manager_id=cid) | Q(agent_id=cid) | Q(tl_id=cid),
        2: Q(manager_id=cid) | Q(agent_id=cid),
        3: Q(agent_id=cid) | Q(tl_id=cid)}
    context = {'today': datetime.datetime.now().date(),'last': datetime.datetime.now().date() - relativedelta(days=30),'title': "View Leads",'cid':cid}
    query = role_filters.get(request.user.role, None)
    if query is None:
        return redirect('/dash')
    context['data'] = Lead.objects.filter(query).order_by('-id')
    return render(request, 'dashboard.html', context)


# All Details Of User Or Manager To Manager Or Super Manager
def view_user(request, mid):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET' and request.user.role in [1]:
        users = User.objects.filter(Q(manager_id=mid) | Q(tl_id=mid)).order_by('-id')

        # Initialize a dictionary to store counts for each user
        counts = {}

        for user in users:
            created = Lead.objects.filter(Q(status=1) & Q(agent_id=user.id)).count()
            interested = Lead.objects.filter(Q(status=2) & Q(agent_id=user.id)).count()
            notinterested = Lead.objects.filter(Q(status=3) & Q(agent_id=user.id)).count()
            followup = Lead.objects.filter(Q(status=4) & Q(agent_id=user.id)).count()
            completed = Lead.objects.filter(Q(status=5) & Q(queagent_id=user.idry)).count()

            # Store counts in the dictionary
            counts[user.id] = {
                'created': created,
                'interested': interested,
                'notinterested': notinterested,
                'followup': followup,
                'completed': completed,
            }
        print(counts)
        context = {'counts': counts,'data': users,'title': "View Details",'err': "No Data Found" if not users else None}
        return render(request, 'staff.html', context)
    elif auth_check:
        return redirect('/dash')
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)
# Display All Lead or User Details of Selected User Or Manager to Manager Or Super Manager (End)...................................


def allcomment(request,id):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET' and request.user.role in [1]:
        a = Comment.objects.filter(Q(lead__id=id) & Q(addedBy__id=request.user.id)).order_by('-id')
        context = {'data': a,'title': "All Comments",'err': "You are Not Authorised" if not a else None}
        return render(request, 'allcomments.html', context)
    elif auth_check:
        return redirect('/dash')
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)
    


def allstatus(request,id):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET' and request.user.role in [1]:
        a = Status.objects.filter(Q(lead__id=id) & Q(addedBy__id=request.user.id)).order_by('-id')
        context = {'data': a,'title': "All Comments",'err': "You are Not Authorised" if not a else None}
        return render(request, 'allstatus.html', context)
    elif auth_check:
        return redirect('/dash')
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)




# View Or Search Selected Lead From cid or Inpout (Start)...........................................................

# All Details of Selected Lead From cid
def view(request, cid):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET':
        role_filters = {
            1: Q(),
            2: Q(manager_id=request.user.id) | Q(agent_id=request.user.id),
            3: Q(tl_id=request.user.id) | Q(agent_id=request.user.id),
            4: Q(agent_id=request.user.id),}
        query = Q(id=cid) & role_filters.get(request.user.role, Q())
        a = Lead.objects.filter(query)
        if a:
            context['data'] = a
            return render(request, 'view.html', context)
        else:
            return redirect('/dash')
    elif auth_check:
        return redirect('/dash')
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)
    


def generate_csv(request,first,last):
    context={}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET':
        role_filters = {
            1: Q(),
            2: Q(manager_id=request.user.id) | Q(agent_id=request.user.id),
            3: Q(tl_id=request.user.id) | Q(agent_id=request.user.id),
            4: Q(agent_id=request.user.id),
        }
        if last == '2':
            query = Q(agent_id=first) & role_filters.get(request.user.role, Q())
        elif last == '3':
            query = (Q(mob__icontains=first) | Q(city__icontains=first) | Q(order_id__icontains=first) | Q(name__icontains=first) | Q(state__icontains=first) | Q(alternate__icontains=first) | Q(shop_name__icontains=first)) & role_filters.get(request.user.role, Q())
        else:
            query = Q(create_date__range=(first, last)) & role_filters.get(request.user.role, Q())
        data = Lead.objects.filter(query).order_by('-id')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=data.csv'
        csv_writer = csv.writer(response)

        headers = ['ORDER ID', 'NAME', 'DATE', 'STATUS DATE', 'E-MAIL', 'MOBILE', 'STATE', 'CITY', 'STATUS']
        csv_writer.writerow(headers)
        for lead in data:
            if lead.status == 1:
                status = "Created"
            elif lead.status == 2:
                status = "Interested"
            elif lead.status == 3:
                status = "Not Interested"
            elif lead.status == 4:
                status = "FollowUp"
            elif lead.status == 5:
                status = "Completed"
            row_data = [lead.order_id,lead.name,lead.create_date,lead.statusDate,
                lead.email,lead.mob,lead.state,lead.city,status,]
            csv_writer.writerow(row_data)

        return response
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)
    


def generate_pdf(request,first,last):
    context={}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET':
        role_filters = {
            1: Q(),
            2: Q(manager_id=request.user.id) | Q(agent_id=request.user.id),
            3: Q(tl_id=request.user.id) | Q(agent_id=request.user.id),
            4: Q(agent_id=request.user.id),
        }
        if last == '2':
            query = Q(agent_id=first) & role_filters.get(request.user.role, Q())
        elif last == '3':
            query = (Q(mob__icontains=first) | Q(city__icontains=first) | Q(order_id__icontains=first) | Q(name__icontains=first) | Q(state__icontains=first) | Q(alternate__icontains=first) | Q(shop_name__icontains=first)) & role_filters.get(request.user.role, Q())
        else:
            query = Q(create_date__range=(first, last)) & role_filters.get(request.user.role, Q())
        data = Lead.objects.filter(query).order_by('-id')
        dynamic_data = [[' Sr.No ',' ORDER ID ',' NAME ',' DATE ',' SHOP NAME ',' CITY ',' STATE ',' MOBILE ','STATUS']]  # Header row
        n = 0
        for lead in data:
            n = n + 1
            if lead.status == 1:
                status = "Created"
            elif lead.status == 2:
                status = "Interested"
            elif lead.status == 3:
                status = "Not Interested"
            elif lead.status == 4:
                status = "FollowUp"
            elif lead.status == 5:
                status = "Completed"
            dynamic_data.append([
                f" {str(n)} ",
                f" {str(lead.order_id)} ",
                f" {str(lead.name)} ",
                f" {str(lead.create_date)} ",
                f" {str(lead.shop_name)} ",
                f" {str(lead.city)} ",
                f" {str(lead.state)} ",
                f" {str(lead.mob)} ",
                f" {status} "
            ])

        max_widths = [max(map(len, col)) * 6 for col in zip(*dynamic_data)]

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

        document = SimpleDocTemplate(response, pagesize=(sum(max_widths) + 20, A4[1]))
        table = Table(dynamic_data, colWidths=max_widths, splitByRow=1)

        style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ])

        table.setStyle(style)
        document.build([table])
        return response
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)
    
def userlead(request,cid,pid):
    if not (request.user.is_authenticated and request.user.is_active and request.user.role == 1):
        err = "Please Login"
        return render(request, 'login.html', {'err': err})
    # role_filters = {
    #     1: Q(status=cid) & Q(agent_id=pid),
        # 2: (Q(manager_id=request.user.id) | Q(agent_id=request.user)) & Q(status=cid),
        # 3: (Q(agent_id=request.user) | Q(tl_id=request.user.id)) & Q(status=cid),
        # 4: Q(agent_id=request.user) & Q(status=cid),}
    # query = role_filters.get(request.user.role, None)
    # if query is None:
    #     return redirect('/dash')
    context = {'today': datetime.datetime.now(),'last': datetime.datetime.now(),'title': "User's Leads",}
    context['data'] = Lead.objects.filter(Q(status=cid) & Q(agent_id=pid)).order_by('-picked_date')
    return render(request, 'dashboard.html', context)
    










def alllead1(request):
    # if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
    #     raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(minutes=10)
        b.save()
        if request.method == 'GET':    
            leads = list(Lead.objects.filter(Q(agent_id=request.COOKIES.get('userid'))).order_by('-id').values())
           
            return JsonResponse( leads, safe=False)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
    else:
        return JsonResponse({'err': 'Please Login'}, status=400)
    
def pick1(request):
    # if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
    #     raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(minutes=10)
        b.save()
        if request.method == 'GET':
            a = User.objects.get(id=request.COOKIES.get('userid'))
            if Lead.objects.filter(Q(agent_id=a) & Q(status=1)).count() == 0:
                lead = Lead.objects.filter((Q(state__icontains="bjibdji") | Q(city__icontains="thane")) & Q(agent_id=None))[:10]
                if lead.count() < 10:
                    new_lead_count = 10 - lead.count()
                    additional_leads = Lead.objects.filter(agent_id=None)[:new_lead_count]
                    lead = lead.union(additional_leads)
                for x in lead:
                    x.agent_id = a
                    x.save()
                    print(x.agent_id)
            leads = list(Lead.objects.filter(Q(agent_id=a) & Q(status=1)).values())
            return JsonResponse( leads, safe=False)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
    else:
        return JsonResponse({'err':'please login'},status = 400)
    


def select1(request,id):
    # if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
    #     raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(minutes=10)
        b.save()
        if request.method == 'GET':
            a= User.objects.get(id=request.COOKIES.get('userid'))
            l = Lead.objects.get(id=id)
            l.agent_id=a
            l.save()
            return JsonResponse( 'success', safe=False)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
    else:
        return JsonResponse({'err':'please login'},status = 400)
    

def mob_user_login(request):
    # if not (datetime.time(1, 0) <= timezone.now().time() <= datetime.time(23, 0)):
    #     raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        u=authenticate(username=uname,password=upass)
        if u is not None:
            login(request,u)
            a=list(User.objects.filter(username=uname).values())
            session = request.session.session_key
            return JsonResponse({'session':session,'user':a}, status=200)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
            
    else:
        return JsonResponse({'err': 'Please Login'}, status=400)
    
        

def csrf(request):
    if request.method == 'GET':
        csrf_token = get_token(request)
        sessionId = request.session.session_key
        return JsonResponse({'csrf' : csrf_token,'sessionId' : sessionId}, safe=False)
    

def mobdash(request):
    # if not (datetime.time(1, 0) <= timezone.now().time() <= datetime.time(23, 0)):
    #     raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(minutes=10)
        b.save()
        if request.method == 'GET':
            q = (filter().mobile(request))
            # a = serializers.serialize('json',q)
            a =[]
            for key, value in q.items():
                value_list = json.loads(value)
                count = len(value_list)
                a.append(count)
                print(count)
            print(a)
            return JsonResponse(a,safe=False)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
            
    else:
        return JsonResponse({'err': 'Please Login'}, status=400)



def mobnewlead(request):
    # if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
    #     raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(hour=2)
        b.save()
        if request.method == 'POST':
            a= User.objects.get(id=request.COOKIES.get('userid'))
            name = request.POST['name']
            city = request.POST['city']
            mob = request.POST['mob']
            alt = request.POST['alt']
            state = request.POST['state']
            shop = request.POST['shop']
            comment = request.POST['comment']
            l = Lead.objects.create(agent_id=a,name= name, city= city,mob= mob,
                    alternate= alt,order_id= "OZO"+str(random.randrange(10000000, 99999999)),state= state,
                     shop_name=shop,comment=comment,create_date=timezone.now(),commentDate=timezone.now(),)
            l.save()
            Comment.objects.create(addedBy=a,comment=comment,lead=l)
            return JsonResponse({'status':True
                                 }, status=200)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)    
    else:
        return JsonResponse({'err': 'Please Login'}, status=400)
    

def mobeditlead(request,cid):
    # if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
    #     raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(minutes=10)
        b.save()
        if request.method == 'GET':
            query = Q(id=cid) & Q(agent_id=request.COOKIES.get('userid'))
            leads = list(Lead.objects.filter(query).values())
            if leads:
                return JsonResponse( leads, safe=False)
            else:
                return JsonResponse({'err': 'Please Login'}, status=400)
        else:
            comment = request.POST['comment']
            status = request.POST['status']   
            l = Lead.objects.get(Q(id=cid) & Q(agent_id=request.COOKIES.get('userid')))
            l.comment = f'{status} : {comment}'
            l.commentDate = timezone.now()
            if status == "INTERESTED":
                l.status=2
            if status == "FOLLOW UP":
                l.status = 4
            if status == "NOT INTERESTED":
                l.status= 3
            if status == "SALE COMPLETE":
                l.status= 5
            if status == "CALLBACK":
                l.status= 4
            l.statusDate = timezone.now()
            l.save()
            Comment.objects.create(comment=comment,addedBy_id=request.COOKIES.get('userid'),lead=l)
            return JsonResponse({'status':True
                                 }, status=200)
    else:
        return JsonResponse({'err': 'Please Login'}, status=400)
    


def mobviewlead(request,cid):
    # if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
    #     raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(minutes=10)
        b.save()
        if request.method == 'GET':
            query = Q(id=cid) & Q(agent_id=request.COOKIES.get('userid'))
            leads = list(Lead.objects.filter(query).values())
            if leads:
                return JsonResponse( leads, safe=False)
            else:
                return JsonResponse({'err': 'Please Login'}, status=400)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
    else:
            return JsonResponse({'err': 'Please Login'}, status=400)
            


    


def interested(request,id,lid):
    # if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
    #     raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(minutes=10)
        b.save()
        if request.method == 'GET':
            query = Q(id=lid) & Q(agent_id=request.COOKIES.get('userid'))
            l = Lead.objects.get(query)
            l.status = id
            l.save()
            if l:
                Status.objects.create(status=id,addedBy_id=request.COOKIES.get('userid'),lead=l)
                return JsonResponse( 'success', safe=False)
            else:
                return JsonResponse({'err': 'NO Data'}, status=400)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
    else:
        return JsonResponse({'err': 'Please Login'}, status=400)
    

def statusList(request,id):
    # if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
    #     raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(minutes=10)
        b.save()
        if request.method == 'GET':
            query = Q(status=id) & Q(agent_id=request.COOKIES.get('userid'))
            leads = list(Lead.objects.filter(query).order_by('-id').values())
            if leads:
                return JsonResponse( leads, safe=False)
            else:
                return JsonResponse({'err': 'Please Login'}, status=400)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
    else:
            return JsonResponse({'err': 'Please Login'}, status=400)
    

def changePass(request):
    # if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
    #     raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(hour=2)
        b.save()
        if request.method == 'POST':
            oldpass = request.POST['old']
            newpass = request.POST['new']
            u=User.objects.get(id=request.COOKIES.get('userid'))
            a=authenticate(username=u.username,password=oldpass)
            if a is not None:
                u.password=make_password(newpass)
                u.temp = None
                u.save()
                return JsonResponse({'status':True
                                }, status=200)
            else:
                return JsonResponse({'err': 'Please Login'}, status=400)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)    
    else:
        return JsonResponse({'err': 'Please Login'}, status=400)
    
    
def mob_user_logout(request):
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        if request.method == 'GET':
            b.delete()
            return JsonResponse({'status':True
                                }, status=200)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
    else:
            return JsonResponse({'err': 'Please Login'}, status=400)



def checking(request):
    try:
        if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
            b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
            b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(hour=2)
            b.save()
            if request.method == 'POST':
                a=request.POST['number']
                b=request.POST['name']
                c=request.POST['type']
                d=request.POST['duration']
                e=request.POST['date']
                timestamp_in_seconds = float(e) / 1000.0
                formatted_date = datetime.datetime.utcfromtimestamp(timestamp_in_seconds).replace(tzinfo=timezone.utc)
                print(a,b,c,d,formatted_date)
                leaddata = Lead.objects.get(mob=int(a))
                u=User.objects.get(id=request.COOKIES.get('userid'))
                if leaddata:
                    print(f"Mobile Number = {a}")
                    print(f"Call Duration {b} Seconds")
                    Call.objects.create(duration=d,addedBy=u,lead=leaddata,number=a,callDate=formatted_date)
                    return JsonResponse({'status':True}, status=200)
                else:
                    print(f"lead not found, personal call!!!! {a}")
                    return JsonResponse({'err': 'Please Loginz'}, status=400)
            else:
                return JsonResponse({'err': 'Please Login'}, status=400)    
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({'status':True}, status=200)


def otp(request):

    url = 'https://control.msg91.com/api/v5/otp?mobile=919167827647'
    headers = {
        'accept': 'application/json',
        'authkey': '415844AdRjQ2Wt65c88d64P1',
        'content-type': 'application/json',
    }

    data = {
        "Param1": "value1",
        "Param2": "value2",
        "Param3": "value3"
    }

    response = requests.post(url, headers=headers, json=data)
    print('Status Code:', response.status_code)
    print('Response Content:', response.text)

    
    return HttpResponse("success")
