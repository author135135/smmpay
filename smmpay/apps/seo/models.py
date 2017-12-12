from django.db import models
from django.utils.translation import ugettext_lazy as _


class PageSeoInformation(models.Model):
    page_url = models.CharField(_('Page URL'), max_length=255, unique=True)
    meta_title = models.CharField(_('Meta title'), max_length=100, blank=True, null=True)
    meta_description = models.CharField(_('Meta description'), max_length=255, blank=True, null=True)
    meta_keywords = models.CharField(_('Meta keywords'), max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'seo_page_seo_information'
        ordering = ('-pk',)
        verbose_name = _('page seo information')
        verbose_name_plural = _('page seo information')

    def __str__(self):
        return self.page_url

    @classmethod
    def get_for_url(cls, path):
        path = path.strip()

        try:
            obj = cls.objects.get(page_url=path)
        except cls.DoesNotExist:
            return False
        return obj

    @classmethod
    def check_for_url(cls, path):
        path = path.strip()

        return cls.objects.filter(page_url=path).exists()
