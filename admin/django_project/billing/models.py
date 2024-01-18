import uuid
from django.db import models
from djmoney.models.fields import MoneyField
from django.utils.translation import gettext_lazy as _


CONTENT_CATALOG = 'content\".\"'


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        abstract = True


class ModeifiedMixin(models.Model):
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class DatesMixin(CreatedMixin, ModeifiedMixin):
    class Meta:
        abstract = True


class Tariff(UUIDMixin, DatesMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    price = MoneyField(_('price'), max_digits=6, decimal_places=2, default_currency='RUB')
    duration = models.IntegerField(_('duration'), default=1)
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        db_table = CONTENT_CATALOG + 'tariff'
        verbose_name = _('Tariff')
        verbose_name_plural = _('Tariffs')

    def __str__(self):
        return f"{_('Tariff')} - {self.id}"
