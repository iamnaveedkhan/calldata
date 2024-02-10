from calldataapp.models import Lead,User
import datetime,calendar
from django.db.models import Q
from django.core import serializers
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django import forms


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['manager', 'tl', 'email', 'role', 'mobile', 'address', 'city', 'state',
                'bankName', 'ifsc', 'nameInBank', 'accountNumber', 'imei', 'userImage',
                'docImage','first_name','last_name',]
        exclude = ['manager','tl']
    error_messages = {
        'email': {
            'unique': 'This email address is already registered.',
            'invalid': 'Enter a valid email address.',
        },
    }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if not self.instance.userImage:
            self.fields['userImage'].required = True
        if not self.instance.docImage:
            self.fields['docImage'].required = True
        if self.instance and self.instance.userImage is None:
            del self.fields['userImage']
        if self.instance and self.instance.docImage is None:
            del self.fields['docImage']

    def clean(self):
        cleaned_data = super().clean()

        mobile = str(cleaned_data.get('mobile'))
        imei = str(cleaned_data.get('imei'))

        if mobile and (not mobile.isdigit() or len(mobile) != 10):
            self.add_error('mobile', 'Enter Valid Mobile Number.')

        if imei and (not imei.isdigit() or len(imei) != 15):
            self.add_error('imei', 'Enter Valid IMEI Number.')

class filter:
    def __init__(self):
        self.today = datetime.datetime.now()
        self.last_month_start = self.today.replace(day=1) - relativedelta(months=1)
        self.last_month_end = self.today.replace(day=1) - relativedelta(days=1)
        self.last_month2_start = self.today.replace(day=1) - relativedelta(months=2)
        self.last_month2_end = self.last_month_start - relativedelta(days=1)
        self.last_month3_start = self.today.replace(day=1) - relativedelta(months=3)
        self.last_month3_end = self.last_month2_start - relativedelta(days=1)
        self.monday = self.today - datetime.timedelta(days=self.today.weekday())
        self.month_date = self.today.replace(day=1)

    def super(self,request):
        total=Lead.objects.all().count
        last_month = Lead.objects.filter(Q(statusDate__range=(self.last_month_start, self.last_month_end)) & Q(status=5)).count
        last_month2 = Lead.objects.filter(Q(statusDate__range=(self.last_month2_start, self.last_month2_end)) & Q(status=5)).count
        last_month3 = Lead.objects.filter(Q(statusDate__range=(self.last_month3_start, self.last_month3_end)) & Q(status=5)).count
        tooday1 = Lead.objects.filter(Q(statusDate=datetime.datetime.now()) & Q(status=5)).count
        # amt_today=Lead.objects.filter(Q(statusDate=datetime.datetime.now()) & Q(status=5)).aggregate(total_amount=Sum('plan'))['total_amount']
        all=Lead.objects.filter(status=5).count
        # amt_all=Lead.objects.filter(status=5).aggregate(total_amount=Sum('plan'))['total_amount']
        week = Lead.objects.filter(Q(statusDate__range=(self.monday, self.today)) & Q(status=5)).count
        # amt_week = Lead.objects.filter(Q(statusDate__range=(self.monday, self.today)) & Q(status=5)).aggregate(total_amount=Sum('plan'))['total_amount']
        month = Lead.objects.filter(Q(statusDate__range=(self.month_date, self.today)) & Q(status=5)).count
        # amt_month = Lead.objects.filter(Q(statusDate__range=(self.month_date, self.today)) & Q(status=5)).aggregate(total_amount=Sum('plan'))['total_amount']
        active = Lead.objects.filter(status=5).count
        inactive = Lead.objects.filter(~Q(status=5)).count()
        a_list={'all':all,'month':month,'week':week,'today':tooday1,'last_month':last_month,'last_month2':last_month2,'last_month3':last_month3,
            'last_month_name':calendar.month_name[self.last_month_end.month],'last_month2_name':calendar.month_name[self.last_month2_end.month],
            'last_month3_name':calendar.month_name[self.last_month3_end.month],'month_name':calendar.month_name[self.month_date.month],
            'active':active,'inactive':inactive,'total':total}
        return a_list
    
    def manage(self,request):
        tooday1 = Lead.objects.filter((Q(manager_id=request.user.id) | Q(agent_id=request.user.id)) & Q(statusDate=datetime.datetime.now()) & Q(status=5)).count
        all=Lead.objects.filter((Q(manager_id=request.user.id) | Q(agent_id=request.user.id)) & Q(status=5)).count
        week = Lead.objects.filter((Q(manager_id=request.user.id) | Q(agent_id=request.user.id)) & Q(statusDate__range=(self.monday, self.today)) & Q(status=5)).count
        month = Lead.objects.filter((Q(manager_id=request.user.id) | Q(agent_id=request.user.id)) & Q(statusDate__range=(self.month_date, self.today)) & Q(status=5)).count
        last_month = Lead.objects.filter((Q(manager_id=request.user.id) | Q(agent_id=request.user.id)) & Q(statusDate__range=(self.last_month_start, self.last_month_end)) & Q(status=5)).count
        last_month2 = Lead.objects.filter((Q(manager_id=request.user.id) | Q(agent_id=request.user.id)) & Q(statusDate__range=(self.last_month2_start, self.last_month2_end)) & Q(status=5)).count
        last_month3 = Lead.objects.filter((Q(manager_id=request.user.id) | Q(agent_id=request.user.id)) & Q(statusDate__range=(self.last_month3_start, self.last_month3_end)) & Q(status=5)).count
        active = Lead.objects.filter((Q(manager_id=request.user.id) | Q(agent_id=request.user.id)) & Q(status=5)).count
        inactive = Lead.objects.filter((Q(manager_id=request.user.id) | Q(agent_id=request.user.id)) & ~Q(status=5)).count
        m_list={'all':all,'month':month,'week':week,'today':tooday1,'last_month':last_month,'last_month2':last_month2,'last_month3':last_month3,
                'last_month_name':calendar.month_name[self.last_month_end.month],'last_month2_name':calendar.month_name[self.last_month2_end.month],
                'last_month3_name':calendar.month_name[self.last_month3_end.month],'month_name':calendar.month_name[self.month_date.month],
                'active':active,'inactive':inactive}
        return m_list
    

    def staf(self,request):
        tooday1 = Lead.objects.filter(Q(agent_id=request.user.id) & Q(statusDate=datetime.datetime.now()) & Q(status=5)).count
        all=Lead.objects.filter(Q(agent_id=request.user.id) & Q(status=5)).count
        week = Lead.objects.filter(Q(agent_id=request.user.id) & Q(statusDate__range=(self.monday, self.today)) & Q(status=5)).count
        month = Lead.objects.filter(Q(agent_id=request.user.id) & Q(statusDate__range=(self.month_date, self.today)) & Q(status=5)).count
        last_month = Lead.objects.filter(Q(agent_id=request.user.id) & Q(statusDate__range=(self.last_month_start, self.last_month_end)) & Q(status=5)).count
        last_month2 = Lead.objects.filter(Q(agent_id=request.user.id) & Q(statusDate__range=(self.last_month2_start, self.last_month2_end)) & Q(status=5)).count
        last_month3 = Lead.objects.filter(Q(agent_id=request.user.id) & Q(statusDate__range=(self.last_month3_start, self.last_month3_end)) & Q(status=5)).count
        active = Lead.objects.filter(Q(agent_id=request.user.id) & Q(status=5)).count
        inactive = Lead.objects.filter(Q(agent_id=request.user.id) & ~Q(status=5)).count
        s_list={'all':all,'month':month,'week':week,'today':tooday1,'last_month':last_month,'last_month2':last_month2,'last_month3':last_month3,
                'last_month_name':calendar.month_name[self.last_month_end.month],'last_month2_name':calendar.month_name[self.last_month2_end.month],
                'last_month3_name':calendar.month_name[self.last_month3_end.month],'month_name':calendar.month_name[self.month_date.month],
                'active':active,'inactive':inactive}
        return s_list


    def mobile(self,request):
        tooday1 = serializers.serialize('json',Lead.objects.filter(Q(agent_id=request.COOKIES.get('userid')) & Q(statusDate=datetime.datetime.now()) & Q(status=5)))
        all=serializers.serialize('json',Lead.objects.filter(Q(agent_id=request.COOKIES.get('userid')) & Q(status=5)))
        week = serializers.serialize('json',Lead.objects.filter(Q(agent_id=request.COOKIES.get('userid')) & Q(statusDate__range=(self.monday, self.today)) & Q(status=5)))
        month = serializers.serialize('json',Lead.objects.filter(Q(agent_id=request.COOKIES.get('userid')) & Q(statusDate__range=(self.month_date, self.today)) & Q(status=5)))
        
        s_list={'all':all,'month':month,'week':week,'today':tooday1}
        return s_list