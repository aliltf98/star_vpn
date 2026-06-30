from django.contrib import admin
from .models import *

# Register your models here.
class HeaderAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        try:
            if MainHeader.objects.filter(promote=True).exists():
                pro = MainHeader.objects.get(promote=True)
                pro.promote = False

                pro.save()
            super().save_model(request, obj, form, change)
        except Exception as e:
            print(e)
class FooterAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        try:
            if MainFooter.objects.filter(promote=True).exists():
                pro = MainFooter.objects.get(promote=True)
                pro.promote = False

                pro.save()
            super().save_model(request, obj, form, change)
        except Exception as e:
            print(e)


admin.site.register(MainHeader)
admin.site.register(MainPlansLayout)
admin.site.register(SocialMedia)
admin.site.register(MainSectionLayout)
admin.site.register(MainFooter)
admin.site.register(PageLayout)
admin.site.register(Gallery)
admin.site.register(Files)
