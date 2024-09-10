from django.contrib import admin

# Register your models here.

from . models import studRec
from . models import PendingRequests

admin.site.register(studRec)
admin.site.register(PendingRequests)


