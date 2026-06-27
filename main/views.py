from django.shortcuts import render
from .models import *


# Create your views here.

def home(request):


    return render(request, "home.html")


def pages(request, id):
    page = MainSectionLayout.objects.get(page_id=id)

    return render(request, "pages.html", context={'page': page})
