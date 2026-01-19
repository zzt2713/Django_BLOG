from django.contrib import admin
from index.models import *
from leaveMeg.models import *
# Register your models here.

admin.site.register([Content,User,Pic,LeaveMeg])
