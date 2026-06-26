from django.db import models
from ckeditor.fields import RichTextField


# Create your models here.

class Gallery(models.Model):
    image = models.ImageField(upload_to='gallery')

    def __str__(self):
        return self.image.name


class SocialMedia(models.Model):
    class SocialMediaTypes(models.TextChoices):
        telegram = 'tg', 'telegram'
        WhatsApp = 'wp', 'whatsapp'
        github = 'gb', 'github'
        twitter = 'x', 'twitter'
        eita = 'ei', 'eita'
        bale = 'bl', 'bale'

    type = models.CharField(max_length=120, choices=SocialMediaTypes.choices)
    link = models.URLField()
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.type


class MainHeader(models.Model):
    title = models.CharField(max_length=120)
    description = RichTextField()
    logo = models.ImageField(upload_to='main/logo')

    def __str__(self):
        return self.title


class MainSectionLayout(models.Model):
    title = models.CharField(max_length=120)
    short_description = RichTextField()
    cover = models.ImageField(upload_to='main/cover')
    show_in_home = models.BooleanField(default=False)
    page = models.ForeignKey('PageLayout', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class MainPlansLayout(models.Model):
    title = models.CharField(max_length=120)
    description = RichTextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class PageLayout(models.Model):
    class PageTypes(models.TextChoices):
        about = 'ab', 'about'
        application = 'ap', 'application'
        page = 'pg', 'page'
    page_type = models.CharField(max_length=20, choices=PageTypes.choices)
    description = RichTextField()
    file = models.FileField(upload_to='pages/files', null=True, blank=True)
    image_gallery = models.ManyToManyField(Gallery)

