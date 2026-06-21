from django.shortcuts import render
from .models import *

# Create your views here.

def home(request):
    context_SocialMedia = SocialMedia.objects.filter(status=True)
    context_MainHeader = MainHeader.objects.get()
    context_MainSectionLayout = MainSectionLayout.objects.filter(status=True)
    context_MainPlansLayout = MainPlansLayout.objects.all()
    context = {'SM':context_SocialMedia,'MainH':context_MainHeader,'MainSL':context_MainSectionLayout,'MainPL':context_MainPlansLayout,}
    return render(request, "home.html", context)

def pages(request, id):
    page = MainSectionLayout.objects.get(page_id=id)

    return render(request, "pages.html", context={'page':page})