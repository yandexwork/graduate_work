from django.contrib import admin
from .models import Tariff


@admin.register(Tariff)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created', 'is_active')
    search_fields = ('name', 'description', 'id', 'price')
