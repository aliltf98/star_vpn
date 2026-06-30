from main.models import *


def load_context(request):
    context_SocialMedia = SocialMedia.objects.filter(status=True)
    context_MainHeader = MainHeader.objects.get(promote=True)
    context_MainSectionLayout = MainSectionLayout.objects.all()
    context_MainPlansLayout = MainPlansLayout.objects.all()
    context_MainFooter = MainFooter.objects.get(promote=True)
    return {'SM': context_SocialMedia, 'MainH': context_MainHeader, 'MainF': context_MainFooter, 'MainSL': context_MainSectionLayout, 'MainPL': context_MainPlansLayout}

