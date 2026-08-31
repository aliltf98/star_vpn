from modeltranslation.translator import register, TranslationOptions
from .models import MainHeader, MainFooter, MainPlansLayout, MainSectionLayout, PageLayout, Files

@register(MainHeader)
class MainHeaderTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(MainFooter)
class MainFooterTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(MainPlansLayout)
class MainPlansLayoutTranslationOptions(TranslationOptions):
    fields = ('title','description')

@register(MainSectionLayout)
class MainSectionLayoutTranslationOptions(TranslationOptions):
    fields = ('title','short_description')

@register(PageLayout)
class PageLayoutTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(Files)
class FilesTranslationOptions(TranslationOptions):
    fields = ('title','description',)

