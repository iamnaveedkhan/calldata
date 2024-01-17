from calldataapp.models import Lead
import datetime
from django.db.models import Q
from django.core import serializers
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncDate
from django.utils import timezone

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


    def mobile(self,request):
        tooday1 = serializers.serialize('json',Lead.objects.filter(Q(agent_id=request.COOKIES.get('userid')) & Q(statusDate=datetime.datetime.now()) & Q(status=5)))
        all=serializers.serialize('json',Lead.objects.filter(Q(agent_id=request.COOKIES.get('userid')) & Q(status=5)))
        week = serializers.serialize('json',Lead.objects.filter(Q(agent_id=request.COOKIES.get('userid')) & Q(statusDate__range=(self.monday, self.today)) & Q(status=5)))
        month = serializers.serialize('json',Lead.objects.filter(Q(agent_id=request.COOKIES.get('userid')) & Q(statusDate__range=(self.month_date, self.today)) & Q(status=5)))
        
        s_list={'all':all,'month':month,'week':week,'today':tooday1}
        return s_list