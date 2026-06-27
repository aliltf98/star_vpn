from main.models import *


def load_context(request):
    context_SocialMedia = SocialMedia.objects.filter(status=True)
    context_MainHeader = MainHeader.objects.get()
    context_MainSectionLayout = MainSectionLayout.objects.all()
    context_MainPlansLayout = MainPlansLayout.objects.all()
    return {'SM': context_SocialMedia, 'MainH': context_MainHeader, 'MainSL': context_MainSectionLayout, 'MainPL': context_MainPlansLayout}

