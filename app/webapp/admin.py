from django.contrib import admin

# Register your models here.

from . models import studRec
from . models import PendingRequests
from . models import HeadOfSecurity

admin.site.register(studRec)
admin.site.register(PendingRequests)
admin.site.register(HeadOfSecurity)




