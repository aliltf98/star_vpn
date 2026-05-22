from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Connection)
admin.site.register(Category)
admin.site.register(UriCode)
admin.site.register(ServiceProfile)
admin.site.register(ConnectionsLog)
