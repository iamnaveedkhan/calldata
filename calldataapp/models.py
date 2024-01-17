from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
import random
from django.utils import timezone



class User(AbstractUser):
    cat=((1,'Super'),(2,'Manager'),(3,'TL'),(4,'staff'))
    is_staff = models.BooleanField(default=True)
    manager = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='managed_users')
    tl = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='team_lead_users')
    temp = models.BigIntegerField(blank=True,null=True)
    role=models.IntegerField(verbose_name='Role',choices=cat,default=0)
    mobile=models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.username
    
class Lead(models.Model):
    chy=((1,'callData'),(2,'interested'),(3,'not interested'),(4,'call back'),(5,'completed'))
    status=models.IntegerField(verbose_name='status',default=1,choices=chy)
    statusDate=models.DateField(default=timezone.now)
    name=models.CharField(verbose_name='customer name',max_length=50)
    mob=models.BigIntegerField(verbose_name='Mobile number')
    alternate=models.CharField(max_length=50,verbose_name='Alternate Number',blank=True,null=True)
    shop_name=models.CharField(verbose_name='Model Name',max_length=50,blank=True,null=True)
    city=models.CharField(verbose_name='city',max_length=50)
    state = models.CharField(verbose_name='state',max_length=50)
    order_id=models.CharField(max_length=50,verbose_name='order id',unique=True)
    agent_id=models.ForeignKey(User,on_delete=models.CASCADE,db_column="agent_id",blank=True,null=True)
    manager_id=models.IntegerField(blank=True,null=True)
    tl_id=models.IntegerField(blank=True,null=True)
    create_date=models.DateTimeField(default=timezone.now)
    picked_date=models.DateField(blank=True,null=True)
    comment = models.CharField(max_length=500,blank=True,null=True)
    commentDate = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name
    

    
def validate_mobile_length(value):
    if len(str(value)) > 10:
        raise ValidationError("Mobile number must be 10 digits or fewer.")
    

class Status(models.Model):
    chy=((1,'callData'),(2,'interested'),(3,'not interested'),(4,'call back'),(5,'completed'))
    statusDate = models.DateTimeField(default=timezone.now)
    status = models.IntegerField(default=1,choices=chy)
    addedBy = models.ForeignKey(User,on_delete=models.CASCADE,db_column="addedBy")
    lead = models.ForeignKey(Lead,on_delete=models.CASCADE,related_name='lead_status')

class Comment(models.Model):
    commentDate = models.DateTimeField(default=timezone.now)
    comment = models.CharField(max_length=500)
    addedBy = models.ForeignKey(User,on_delete=models.CASCADE,db_column="addedBy")
    lead = models.ForeignKey(Lead,on_delete=models.CASCADE,related_name='lead_data')
