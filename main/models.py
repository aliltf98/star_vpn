from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


# Create your models here.

class Gallery(models.Model):
    image = models.ImageField(upload_to='gallery')

    def __str__(self):
        return self.image.name

class Files(models.Model):
    title = models.CharField(max_length=120)
    link = models.CharField(max_length=300, null=True, blank=True)
    description = CKEditor5Field(config_name='extends')
    file = models.FileField(upload_to='pages/files', null=True, blank=True)

    def __str__(self):
        return self.title

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
    description = CKEditor5Field(config_name='extends')
    logo = models.ImageField(upload_to='main/logo')
    promote = models.BooleanField(default=True)

    def __str__(self):
        return self.title if hasattr(self, 'title') else f"Header {self.id}"


class MainSectionLayout(models.Model):
    title = models.CharField(max_length=120)
    short_description = CKEditor5Field(config_name='extends')
    cover = models.ImageField(upload_to='main/cover')
    show_in_home = models.BooleanField(default=False)
    show_in_nav = models.BooleanField(default=False)
    page = models.ForeignKey('PageLayout', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class MainPlansLayout(models.Model):
    title = models.CharField(max_length=120, verbose_name="عنوان پلن")
    description = CKEditor5Field(config_name='extends', verbose_name="توضیحات/امکانات")

    # مشخصات فنی برای اتصال به پنل VPN
    duration_days = models.PositiveIntegerField(default=30, verbose_name="اعتبار (روز)")
    volume_gb = models.PositiveIntegerField(default=0, verbose_name="حجم (گیگابایت - 0 برای نامحدود)")
    user_limit = models.PositiveIntegerField(default=1, verbose_name="محدودیت کاربر همزمان")

    # قیمت‌گذاری
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت اصلی (تومان)")
    old_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True,
                                    verbose_name="قیمت قبلی/خط‌خورده")

    # مدیریت نمایش
    is_active = models.BooleanField(default=True, verbose_name="فعال/قابل خرید")
    is_featured = models.BooleanField(default=False, verbose_name="پیشنهاد ویژه / پرفروش")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "پلن"
        verbose_name_plural = "مدیریت پلن‌ها"
        ordering = ['sort_order', 'price']

    def __str__(self):
        return f"{self.title} - {self.volume_gb}GB ({self.duration_days} روزه)"

    @property
    def has_discount(self):
        return self.old_price is not None and self.old_price > self.price


class PageLayout(models.Model):
    class PageTypes(models.TextChoices):
        about = 'ab', 'about'
        application = 'ap', 'application'
        page = 'pg', 'page'
    page_type = models.CharField(max_length=20, choices=PageTypes.choices)
    description = CKEditor5Field(config_name='extends')
    file = models.ManyToManyField('Files', related_name='pages', blank=True)
    image_gallery = models.ManyToManyField(Gallery, blank=True)

class MainFooter(models.Model):
    description = CKEditor5Field(config_name='extends')
    promote = models.BooleanField(default=True)

    def __str__(self):
        return self.title if hasattr(self, 'title') else f"Footer {self.id}"
