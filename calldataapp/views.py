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
from calldataapp.forms import filter
# from django.contrib.staticfiles import finders
from django.http import JsonResponse
import pandas as pd
from dateutil import parser
from django.contrib.sessions.models import Session
from django.middleware.csrf import get_token
from django.utils import timezone
from django.core.exceptions import PermissionDenied

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
                        context['errmsgs']="Click Here TO Reset Your Password"
                        return render(request,'login.html',context)
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
            fname = request.POST['fname']
            lname = request.POST['lname']
            email = request.POST['email']
            mob = request.POST['mob']
            manage = request.POST['manage']
            t = random.randrange(100000,21474836)
            if len(str(mob)) != 10:
                context['errmsg'] = "Contact Number Must Be 10 Digit"
                return render(request, 'edit_user.html', context)
            try:
                if request.user.role in [1, 2, 3]:
                    user_data = {
                        'first_name': fname,
                        'last_name': lname,
                        'mobile': mob,
                        'email': email,
                        'password': make_password(email),
                        'username': email,
                        'temp':t,}
                    if request.user.role == 3:
                        user_data['tl_id'] = a
                        user_data['manager_id'] = request.user.manager_id
                    elif request.user.role in [1, 2]:
                        user_data['manager_id'] = a
                    user_data['role'] = manage
                    u = User.objects.create(**user_data)
                    u.save()
                    context['success'] = f"User {fname} is registered successfully"
                    return render(request, 'add.html', context)
            except IntegrityError as e:
                error_message = "A user with this email ID already exists. Please choose a different email ID."
                return render(request, 'edit_user.html', {'errmsg': error_message})
        else:
            return render(request, 'add.html')
    else:
        return redirect('/dash')
    context['err'] = "Please Login"
    return render(request, 'login.html', context)



# Edit User Detail Only Image
def edit_user(request, uid):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.user.role in [1, 2, 3]:
        if request.method == 'GET':
            role_actions = {
                1: User.objects.filter(id=uid),
                2: User.objects.filter(Q(id=uid) & (Q(role=3) | Q(role=4))),
                3: User.objects.filter(Q(id=uid) & Q(role=4))}
            user_data = role_actions.get(request.user.role, (None, None))
            if user_data:
                context['data'] = user_data
                context['title'] = "Edit User"
                return render(request, 'edit_user.html', context)
            else:
                return redirect('/dash')
        elif request.method == 'POST':
            fname = request.POST['fname']
            lname = request.POST['lname']
            email = request.POST['email']
            mob = request.POST['mob']
            if len(str(mob)) != 10:
                context['errmsg'] = "Contact Number Must Be 10 Digit"
                return render(request, 'edit_user.html', context)
            else:
                try:
                    if request.user.role == 1:
                        manage = request.POST['manage']
                        User.objects.filter(id=uid).update(first_name=fname, last_name=lname, mobile=mob, email=email, role=manage)
                    else:
                        User.objects.filter(id=uid).update(first_name=fname, last_name=lname, mobile=mob, email=email)

                    context['success'] = f"User {fname} is updated successfully"
                    return render(request, 'edit_user.html', context)
                except IntegrityError as e:
                    error_message = "A user with this email ID already exists. Please choose a different email ID."
                    return render(request, 'edit_user.html', {'errmsg': error_message})
    else:
        return redirect('/dash')
    context['err'] = "Please Login"
    return render(request, 'login.html', context)

# Create Or Edit User Detaile (End).....................................................................................



# User Dashboard Function (Start).......................................................................................
def dashboard(request):
    context = {}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET':
        role_filters = {
            1: Q(),
            2: Q(Q(manager_id=request.user.id) | Q(agent_id=request.user.id)) & Q(status=1),
            3: Q(Q(tl_id=request.user.id) | Q(agent_id=request.user.id)) & Q(status=1),
            4: Q(agent_id=request.user.id) & Q(status=1),}      
        leads = Lead.objects.filter(role_filters.get(request.user.role, Q())).order_by('-id')[:10]
        context['data'] = leads
        context['success']=request.session.get('msg')
        context['err']=request.session.get('errmsg')
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
                     'shop_name': shop,'city':city,'state':state,'create_date':timezone.now(),'comment':'CREATED','commentDate':timezone.now(),}
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
                            'shop_name': shop,'create_date':timezone.now,'comment':'CREATED','commentDate':timezone.now,'city':city,'state':state}
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

def select_lead(request,cid):
    context={}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check:
        if request.method == 'GET':
            a = Lead.objects.get(order_id=cid)
            if a.agent_id is None:
                context = {'today': datetime.datetime.now().date(),'last': datetime.datetime.now().date(),'success': "Lead Created Successfully"}
                role_filters = {
                    1: {'agent_id': request.user,'manager_id': request.user.id},
                    2: {'agent_id': request.user,'manager_id': request.user.id},
                    3: {'tl_id': request.user.id,'agent_id': request.user},
                    4: {'agent_id': request.user,'manager_id': request.user.manager_id,'tl_id': request.user.tl_id}
                }
                lead_data = {
                    'name': a.name, 'mob': a.mob,
                    'alternate': a.alternate, 'order_id': a.order_id,
                    'city': a.city, 'state': a.state,
                     'shop_name': a.shop_name,'picked_date':datetime.datetime.now().date()}
                lead_data.update(role_filters.get(request.user.role, {}))
                l = Lead.objects.filter(order_id=cid).update(**lead_data)
                request.session['msg'] = "Lead Added"
                return redirect(f'/view/{a.id}')
            else:
                request.session['msg'] = "Lead Not Available Or Picked"
                return redirect('/dash')
        else:
            a=Lead.objects.filter(agent_id=None)
            return render(request,'select_lead.html',{'data':a})
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)

def pick(request):
    context={}
    auth_check = request.user.is_authenticated and request.user.is_active
    if auth_check and request.method == 'GET':
        a = Lead.objects.filter(agent_id=None).order_by('-id')
        context['data']=a
        return render(request,'select_lead.html',context)
    else:
        context['err'] = "Please Login"
        return render(request, 'login.html', context)
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
        2: (Q(manager_id=request.user.id) | Q(agent_id=request.user)) & Q(date=datetime.datetime.now().date()),
        3: (Q(agent_id=request.user) | Q(tl_id=request.user.id)) & Q(date=datetime.datetime.now().date()),
        4: Q(agent_id=request.user) & Q(date=datetime.datetime.now().date()),}
    query = role_filters.get(request.user.role, None)
    if query is None:
        return redirect('/dash')
    context = {'today': datetime.datetime.now(),'last': datetime.datetime.now(),'title': "All Leads",}
    context['data'] = Lead.objects.filter(query).order_by('-id')
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
    context = {
        'data': User.objects.filter(queries.get(role, Q())),
        'title': "All Sales Executive" if auth_check else None,
    }
    if auth_check and role in [1,2,3] and not context['data']:
        context['err'] = "You Have No Sales Executive"
    if auth_check and role not in [1,2,3]:
        return redirect('/dash')
    if not auth_check:
        context['err'] = "Please Login"
    return render(request, 'staff.html' if auth_check else 'login.html', context)



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
        query = (Q(mob__icontains=srch) | Q(imei1__icontains=srch) | Q(order_id__icontains=srch) | Q(name__icontains=srch) | Q(email__icontains=srch) | Q(alternate__icontains=srch) | Q(plan__icontains=srch)) & role_filters.get(request.user.role, Q())
        data = Lead.objects.filter(query)
        today=datetime.datetime.now().date()
        return render(request, 'dashboard.html',{'data':data})
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
    context = {'today': datetime.datetime.now().date(),'last': datetime.datetime.now().date() - relativedelta(days=30),'title': "All Leads",}
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
        a = User.objects.filter(Q(manager_id=mid) | Q(tl_id=mid)).order_by('-id')
        context = {'data': a,'title': "View Details",'err': "You are Not Authorised" if not a else None}
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
    






def alllead1(request):
    if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
        raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(minutes=10)
        b.save()
        if request.method == 'GET':    
            leads = list(Lead.objects.filter(Q(agent_id=request.COOKIES.get('userid')) & Q(status=1)).order_by('-id').values())
           
            return JsonResponse( leads, safe=False)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
    else:
        return JsonResponse({'err': 'Please Login'}, status=400)
    
def pick1(request):
    if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
        raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
    if Session.objects.filter(session_key=request.COOKIES.get('sessionId')):
        b= Session.objects.get(session_key=request.COOKIES.get('sessionId'))
        b.expire_date = datetime.datetime.now(pytz.utc) + relativedelta(minutes=10)
        b.save()
        if request.method == 'GET':
            leads = list(Lead.objects.filter(agent_id=None).values())
            return JsonResponse( leads, safe=False)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)
    else:
        return JsonResponse({'err':'please login'},status = 400)
    


def select1(request,id):
    if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
        raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
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
    if not (datetime.time(1, 0) <= timezone.now().time() <= datetime.time(23, 0)):
        raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
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
    if not (datetime.time(1, 0) <= timezone.now().time() <= datetime.time(23, 0)):
        raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
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
    if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
        raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
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
                     shop_name=shop,comment=comment,create_date=timezone.now,commentDate=timezone.now,)
            l.save()
            Comment.objects.create(addedBy=a,comment=comment,lead=l)
            return JsonResponse({'status':True
                                 }, status=200)
        else:
            return JsonResponse({'err': 'Please Login'}, status=400)    
    else:
        return JsonResponse({'err': 'Please Login'}, status=400)
    

def mobeditlead(request,cid):
    if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
        raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
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
    if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
        raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
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
    if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
        raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
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
    if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
        raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
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
    if not (datetime.time(10, 0) <= timezone.now().time() <= datetime.time(19, 0)):
        raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")
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