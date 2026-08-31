from modeltranslation.translator import register, TranslationOptions
from .models import Connection, Category


# @register(Category)
# class CategoryTranslationOptions(TranslationOptions):
#     fields = ('title',)