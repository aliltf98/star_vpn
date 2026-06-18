from django.shortcuts import render
from .models import *

# Create your views here.

def home(request):
    context_SocialMedia = SocialMedia.objects.all()
    context_MainHeader = MainHeader.objects.get()
    context_MainSectionLayout = MainSectionLayout.objects.get()
    context_MainPlansLayout = MainPlansLayout.objects.all()
    context = {'SM':context_SocialMedia,'MainH':context_MainHeader,'MainSL':context_MainSectionLayout,'MainPL':context_MainPlansLayout,}
    return render(request, "home.html", context)