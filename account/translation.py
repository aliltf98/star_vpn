from modeltranslation.translator import register, TranslationOptions
from .models import UserProfile  # مدل پلن‌های شما

# @register(UserProfile)
# class UserProfileTranslationOptions(TranslationOptions):
#     fields = ('name', 'description') # فیلدهایی که می‌خواهید دو زبانه شوند